import requests
from backend.config import Config
from backend.services.college_data_service import college_data_service
from backend.utils.logger import logger

SYSTEM_PROMPT = """You are the AI voice assistant for SVKM's NMIMS Global University, Dhule, Maharashtra, India.
Your job is to assist callers with verified information specifically for the DHULE campus over a phone call.

CRITICAL CAMPUS RULE:
This assistant represents ONLY SVKM's NMIMS Global University, Dhule.
Do NOT mention, confuse, or mix information with NMIMS Shirpur, Mukesh Patel Technology Park, Babulde, or other campuses.

STRICT ZERO-HALLUCINATION RULES:
Use ONLY the verified college information provided in the context below.
Never invent or assume:
- Course fees or fee structures
- Admission dates or deadlines
- Examination dates, time tables, or tomorrow's exams
- Seat intake or cutoff numbers
- Specific eligibility percentages unless stated in context
- Faculty names or HOD names
- Unverified phone numbers or email addresses
- Hostel availability or hostel fees
- Placement percentages or statistics
- Scholarships, ranking, or accreditations

If the caller asks for information that is NOT available in the verified context, you MUST answer:
"I don't have verified information about that at the moment. Please check the official NMIMS Dhule website or contact the college."

OFFICIAL WEBSITE RULE:
If asked about the official website or its pronunciation, state clearly with phonetic letter-by-letter spelling for voice:
- English: "The official website of SVKM's NMIMS Global University, Dhule is svkmnmimsngu.ac.in (svkmnmimsgu.ac.in), pronounced as S V K M, N M I M S, S N G U, dot A C, dot I N."
- Hindi: "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले की आधिकारिक वेबसाइट svkmnmimsngu.ac.in (svkmnmimsgu.ac.in) है, जिसे 'एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन' बोला जाता है।"
- Marathi: "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे चे अधिकृत संकेतस्थळ svkmnmimsngu.ac.in (svkmnmimsgu.ac.in) आहे, ज्याचा उच्चार 'एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन' असा केला जातो."
Note: The official university website is svkmnmimsngu.ac.in (also accessible via svkmnmimsgu.ac.in).

PHONE CONVERSATION STYLE:
- Keep responses short, concise, and natural (1 to 3 spoken sentences).
- Speak politely and clearly as a professional college telephone receptionist.
- Never use bullet points, asterisks, markdown syntax, or URLs with http/https in spoken text.
- Do not mention databases, prompt rules, APIs, or system internal records."""

class AIService:
    """Service to generate grounded voice answers for SVKM's NMIMS Global University, Dhule."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key if api_key is not None else Config.GEMINI_API_KEY
        self.model = model if model is not None else Config.GEMINI_MODEL

    def detect_language(self, text: str, requested_lang: str = None) -> str:
        """Determines language: English ('en'), Hindi ('hi'), or Marathi ('mr')."""
        if requested_lang in ("hi", "mr"):
            return requested_lang

        has_devanagari = any('\u0900' <= char <= '\u097f' for char in text)
        if has_devanagari:
            marathi_markers = ["आहे", "नाही", "माहिती", "कुठे", "कॅम्पस", "सांगा", "अभ्यासक्रम", "प्रवेश", "परीक्षा", "का"]
            if any(marker in text for marker in marathi_markers):
                return "mr"
            return "hi"

        t = text.lower()
        if any(w in t for w in [" aahe", "kaay ", "kiti ", "kuthe "]):
            return "mr"
        if any(w in t for w in ["kya ", "kaha ", "kaise ", "batao ", "hai kya"]):
            return "hi"

        return requested_lang or "en"

    def answer_question(self, user_question: str, lang: str = "en") -> str:
        """Process caller's question with verified Dhule knowledge context in English, Hindi, or Marathi."""
        if not user_question or not user_question.strip():
            detected = self.detect_language("", lang)
            if detected == "hi":
                return "क्षमा करें, मैं आपका प्रश्न ठीक से नहीं सुन पाया। क्या आप कृपया इसे दोहरा सकते हैं?"
            elif detected == "mr":
                return "क्षमस्व, मला तुमचा प्रश्न व्यवस्थित ऐकू आला नाही. कृपया पुन्हा सांगू शकाल का?"
            return "I'm sorry, I could not hear your question clearly. Could you please repeat it?"

        detected_lang = self.detect_language(user_question, lang)
        context = college_data_service.get_relevant_context(user_question)

        # If Gemini API key is configured, query the Gemini API
        if self.api_key:
            try:
                answer = self._call_gemini_api(user_question, context, detected_lang)
                if answer:
                    return answer
            except Exception as e:
                logger.error(f"Gemini API request error: {e}. Falling back to Dhule verified knowledge processor.")

        # Grounded local fallback engine
        return self._local_dhule_knowledge_fallback(user_question, detected_lang)

    def _call_gemini_api(self, question: str, context: str, lang: str = "en") -> str:
        """Call Gemini generateContent REST endpoint."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        lang_instruction = ""
        if lang == "hi":
            lang_instruction = "IMPORTANT: Answer in polite Hindi (Devanagari script).\n"
        elif lang == "mr":
            lang_instruction = "IMPORTANT: Answer in polite Marathi (Devanagari script).\n"

        prompt_content = (
            f"VERIFIED DHULE CAMPUS DATA:\n{context}\n\n"
            f"{lang_instruction}"
            f"CALLER QUESTION:\n{question}\n\n"
            f"ANSWER (short spoken phone answer strictly adhering to verified data):"
        )

        body = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "parts": [{"text": prompt_content}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 200
            }
        }

        response = requests.post(url, headers=headers, json=body, timeout=12)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    ans = parts[0]["text"].strip()
                    return ans.replace("*", "").replace("#", "").replace("`", "")
        return ""

    def _local_dhule_knowledge_fallback(self, question: str, lang: str = "en") -> str:
        """
        Deterministic, grounded knowledge answering for SVKM's NMIMS Global University, Dhule.
        Supports English, Hindi, and Marathi with 0% hallucination.
        """
        q = question.lower().strip()
        eng = college_data_service.get_engineering_info()
        pharm = college_data_service.get_pharmacy_info()
        comm = college_data_service.get_commerce_info()
        cont = college_data_service.get_contact_info()

        # Unknown / unverified checks - STRICT NO HALLUCINATION
        unverified_triggers = [
            "fee", "fees", "cost", "tuition", "hod", "head of department", 
            "tomorrow", "tomorrow's exam", "today's exam", "exam schedule tomorrow",
            "placement percentage", "average package", "highest package", "placement stat",
            "hostel", "mess", "canteen", "scholarship", "intake", "seat", "seats", "ranking",
            "principal", "director", "chancellor name", "फीस", "शुल्क", "हॉस्टल", "मेस", "प्लेसमेंट"
        ]
        if any(trigger in q for trigger in unverified_triggers):
            if lang == "hi":
                return "मेरे पास इस समय इस बारे में सत्यापित जानकारी नहीं है। कृपया आधिकारिक एनएमआईएमएस धुले वेबसाइट देखें या कॉलेज से संपर्क करें।"
            elif lang == "mr":
                return "माझ्याकडे या क्षणी याबद्दल पडताळलेली माहिती नाही. कृपया अधिकृत एनएमआयएमएस धुळे संकेतस्थळ तपासा किंवा महाविद्यालयाशी संपर्क साधा।"
            return "I don't have verified information about that at the moment. Please check the official NMIMS Dhule website or contact the college."

        # 1. University Name
        if any(w in q for w in ["name of the university", "what is the name", "university name", "college name", "नाम क्या है", "नाव काय आहे", "विद्यापीठाचे नाव"]):
            if lang == "hi":
                return "विश्वविद्यालय का नाम एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले है।"
            elif lang == "mr":
                return "विद्यापीठाचे नाव एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे असे आहे."
            return "The university is SVKM's NMIMS Global University, Dhule."

        # 2. Location / Where is NMIMS Dhule
        if any(w in q for w in ["where is", "where are you", "location", "address", "which city", "कहाँ है", "कहाँ स्थित है", "कुठे आहे", "पत्ता"]):
            addr = cont.get("address", "Survey No. 499 Behind Gurudwara, Mumbai-Agra National Highway, Dhule, Maharashtra")
            if lang == "hi":
                return f"एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले मुंबई-आगरा राष्ट्रीय राजमार्ग, गुरुद्वारे के पीछे, धुले, महाराष्ट्र में स्थित है।"
            elif lang == "mr":
                return f"एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे हे मुंबई-आग्रा राष्ट्रीय महामार्गावर, गुरुद्वाराच्या मागे, धुळे, महाराष्ट्र येथे स्थित आहे."
            return f"SVKM's NMIMS Global University, Dhule is located at {addr}."

        # 3. Official Website & Website Pronunciation
        if any(w in q for w in ["website", "web site", "url", "portal", "link", "वेबसाइट", "संकेतस्थळ", "svkmnmimsgu", "svkmnmimsngu", "pronounce"]):
            if any(w in q for w in ["pronounce", "pronunciation", "उच्चारण", "उच्चार", "how to say", "how to read", "correct"]):
                if lang == "hi":
                    return "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले की आधिकारिक वेबसाइट svkmnmimsngu.ac.in (svkmnmimsgu.ac.in) है, जिसे अक्षर-दर-अक्षर 'एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन' बोला जाता है।"
                elif lang == "mr":
                    return "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे चे अधिकृत संकेतस्थळ svkmnmimsngu.ac.in (svkmnmimsgu.ac.in) आहे, ज्याचा उच्चार 'एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन' असा केला जातो."
                return "The official website of SVKM's NMIMS Global University, Dhule is svkmnmimsngu.ac.in (also accessible at svkmnmimsgu.ac.in), pronounced letter-by-letter as S V K M, N M I M S, S N G U, dot A C, dot I N."
            if lang == "hi":
                return "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले की आधिकारिक वेबसाइट svkmnmimsngu.ac.in (svkmnmimsgu.ac.in - एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन) है।"
            elif lang == "mr":
                return "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे चे अधिकृत संकेतस्थळ svkmnmimsngu.ac.in (svkmnmimsgu.ac.in - एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन) आहे."
            return "The official website of SVKM's NMIMS Global University, Dhule is svkmnmimsngu.ac.in (svkmnmimsgu.ac.in), pronounced as S V K M, N M I M S, S N G U, dot A C, dot I N."

        # 4. How to contact / phone numbers
        if any(w in q for w in ["contact", "phone number", "helpline", "call", "office number", "संपर्क", "फोन नंबर", "कॉल"]):
            if lang == "hi":
                return "आप धुले परिसर से संपर्क कर सकते हैं: टेक्नोलॉजी 02562 350620, फार्मेसी 02562 350640, और कॉमर्स 02562 350600।"
            elif lang == "mr":
                return "आपण धुळे कॅम्पसशी संपर्क साधू शकता: टेक्नॉलॉजी 02562 350620, फार्मसी 02562 350640, आणि कॉमर्स 02562 350600."
            return (
                f"You can contact the Dhule campus at: Technology 02562 350620, "
                f"Pharmacy 02562 350640, and Commerce 02562 350600."
            )

        # 5. After 12th Courses
        if any(w in q for w in ["after 12", "after 12th", "undergraduate", "ug course", "after twelfth", "12वीं के बाद", "१२ वी नंतर"]):
            if lang == "hi":
                return "12वीं के बाद धुले परिसर में इंजीनियरिंग के बी.टेक कार्यक्रम, डी.फार्म, बी.फार्म, बी.फार्म प्लस एमबीए फार्मा टेक, बी.टेक कॉस्मेटिक टेक्नोलॉजी, बीबीए और बीसीए उपलब्ध हैं।"
            elif lang == "mr":
                return "१२ वी नंतर धुळे कॅम्पसमध्ये बी.टेक इंजिनिअरिंग, डी.फार्म, बी.फार्म, बी.फार्म प्लस एमबीए फार्मा टेक, बी.टेक कॉस्मेटिक टेक्नॉलॉजी, बीबीए आणि बीसीए अभ्यासक्रम उपलब्ध आहेत."
            return (
                "After 12th, the Dhule campus offers B.Tech programs in engineering, "
                "D.Pharm, B.Pharm, B.Pharm with MBA in Pharma Tech, B.Tech in Cosmetic Technology, "
                "BBA, and BCA in Commerce."
            )

        # 6. Computer Courses / Computer Engineering queries
        if any(w in q for w in ["computer courses", "computer program", "what computer", "कंप्यूटर कोर्स"]):
            if lang == "hi":
                return "कंप्यूटर कार्यक्रमों के लिए धुले परिसर बी.टेक कंप्यूटर इंजीनियरिंग, बी.टेक सीएसई एआई एंड एमएल, बी.टेक सीएसई डेटा साइंस, आईटी, बी.टेक प्लस एमबीए और एमसीए प्रदान करता है।"
            elif lang == "mr":
                return "कॉम्प्युटर अभ्यासक्रमांसाठी धुळे कॅम्पस बी.टेक कॉम्प्युटर इंजिनिअरिंग, बी.टेक सीएसई एआय अँड एमएल, सीएसई डेटा सायन्स, माहिती तंत्रज्ञान आणि एमसीए चालवते."
            return (
                "For computer programs, the Dhule campus offers B.Tech Computer Engineering, "
                "B.Tech CSE with AI and Machine Learning, B.Tech CSE with Data Science, "
                "Information Technology, Dual Degree B.Tech plus MBA, and MCA."
            )

        if "computer engineering" in q or "कंप्यूटर इंजीनियरिंग" in q or "कॉम्प्युटर इंजिनिअरिंग" in q:
            if lang == "hi":
                return "धुले परिसर में बी.टेक कंप्यूटर इंजीनियरिंग उपलब्ध है। इसके अलावा सीएसई एआई एंड मशीन लर्निंग, सीएसई डेटा साइंस, आईटी और संबंधित पाठ्यक्रम भी उपलब्ध हैं।"
            elif lang == "mr":
                return "धुळे कॅम्पसमध्ये बी.टेक कॉम्प्युटर इंजिनिअरिंग उपलब्ध आहे. तसेच सीएसई एआय अँड मशीन लर्निंग, सीएसई डेटा सायन्स आणि माहिती तंत्रज्ञान उपलब्ध आहे."
            return (
                "At the Dhule campus, B.Tech Computer Engineering is available. "
                "The university also offers B.Tech Computer Science and Engineering with AI and Machine Learning, "
                "Computer Science and Engineering with Data Science, Information Technology, and related postgraduate programs."
            )

        # 7. AI & ML
        if any(w in q for w in ["ai and machine learning", "ai & ml", "artificial intelligence", "aiml", "एआई"]):
            if lang == "hi":
                return "हाँ, धुले परिसर बी.टेक कंप्यूटर साइंस एंड इंजीनियरिंग (एआई एंड मशीन लर्निंग) प्रदान करता है।"
            elif lang == "mr":
                return "होय, धुळे कॅम्पसमध्ये बी.टेक कॉम्प्युटर सायन्स अँड इंजिनिअरिंग (एआय अँड मशीन लर्निंग) उपलब्ध आहे."
            return "Yes, the Dhule campus offers B.Tech in Computer Science and Engineering with AI and Machine Learning, as well as a dual degree B.Tech plus MBA in AI and Machine Learning."

        # 8. Data Science
        if "data science" in q or "डेटा साइंस" in q or "डेटा सायन्स" in q:
            if lang == "hi":
                return "हाँ, विश्वविद्यालय बी.टेक सीएसई (डेटा साइंस) और बी.टेक प्लस एमबीए (डेटा साइंस) प्रदान करता है।"
            elif lang == "mr":
                return "होय, विद्यापीठ बी.टेक सीएसई (डेटा सायन्स) अभ्यासक्रम चालवते."
            return "Yes, the university offers B.Tech in Computer Science and Engineering with Data Science, as well as a dual degree B.Tech plus MBA in Data Science."

        # 9. Information Technology
        if "information technology" in q or " it " in f" {q} ":
            return "Yes, B.Tech in Information Technology, B.Tech plus MBA in Information Technology, and M.Tech in Information Technology are offered at the Dhule campus."

        # 10. MCA
        if "mca" in q or "master of computer applications" in q or "एमसीए" in q:
            if lang == "hi":
                return "हाँ, स्कूल ऑफ टेक्नोलॉजी, मैनेजमेंट एंड इंजीनियरिंग, धुले में एमसीए (मास्टर ऑफ कंप्यूटर एप्लीकेशंस) उपलब्ध है।"
            elif lang == "mr":
                return "होय, स्कूल ऑफ टेक्नॉलॉजी, मॅनेजमेंट अँड इंजिनिअरिंग, धुळे येथे एमसीए उपलब्ध आहे."
            return "Yes, Master of Computer Applications, or MCA, is offered by the School of Technology, Management and Engineering at the Dhule campus."

        # 11. M.Tech
        if "m.tech" in q or "mtech" in q or "एमटेक" in q:
            return "M.Tech programs are available in Civil Engineering, Computer Engineering, Electrical Engineering, Information Technology, and Mechanical Engineering."

        # 12. Engineering courses / branches
        if any(w in q for w in ["engineering courses", "engineering branches", "b.tech", "btech", "engineering programs", "इंजीनियरिंग", "इंजिनिअरिंग"]):
            if lang == "hi":
                return "स्कूल ऑफ टेक्नोलॉजी, मैनेजमेंट एंड इंजीनियरिंग धुले में बी.टेक सिविल, कंप्यूटर, सीएसई एआई-एमएल, डेटा साइंस, इलेक्ट्रिकल, आईटी और मैकेनिकल इंजीनियरिंग उपलब्ध हैं।"
            elif lang == "mr":
                return "स्कूल ऑफ टेक्नॉलॉजी, मॅनेजमेंट अँड इंजिनिअरिंग धुळे येथे बी.टेक सिव्हिल, कॉम्प्युटर, सीएसई एआय-एमएल, डेटा सायन्स, इलेक्ट्रिकल, आयटी आणि मेकॅनिकल इंजिनिअरिंग उपलब्ध आहेत."
            return (
                "The School of Technology, Management and Engineering at SVKM's NMIMS Global University, Dhule "
                "offers B.Tech programs in Civil Engineering, Computer Engineering, Computer Science and Engineering with AI and Machine Learning, "
                "Computer Science and Engineering with Data Science, Electrical Engineering, Information Technology, and Mechanical Engineering."
            )

        # 13. Cosmetic Technology
        if "cosmetic" in q or "कॉस्मेटिक" in q:
            return "Yes. B.Tech in Cosmetic Technology is offered under the School of Pharmacy and Technology Management at the Dhule campus."

        # 14. B.Pharm
        if "what is b.pharm" in q or "what is bpharm" in q:
            return "B.Pharm is a Bachelor of Pharmacy undergraduate program offered by the School of Pharmacy and Technology Management at the Dhule campus."

        # 15. D.Pharm
        if "d.pharm" in q or "dpharm" in q or "diploma in pharmacy" in q:
            return "Yes. The School of Pharmacy and Technology Management at the Dhule campus offers D.Pharm, which is a Diploma in Pharmacy."

        # 16. M.Pharm
        if "m.pharm" in q or "mpharm" in q or "master of pharmacy" in q:
            return "Yes. The School of Pharmacy and Technology Management offers M.Pharm in Pharmaceutics, Pharmaceutical Quality Assurance, Pharmacology, and Pharmaceutical Chemistry."

        # 17. Ph.D. in Pharmaceutical Sciences / Pharmacy PhD
        if "ph.d" in q or "phd" in q:
            if "pharm" in q or "फार्म" in q:
                return "Yes. A doctoral program, Ph.D. in Pharmaceutical Sciences, is offered by the School of Pharmacy and Technology Management."
            return "SVKM's NMIMS Global University, Dhule offers Ph.D. in Technology and Engineering, as well as Ph.D. in Pharmaceutical Sciences."

        # 18. Pharmacy available
        if "pharm" in q or "फार्मेसी" in q or "फार्मसी" in q:
            if lang == "hi":
                return "हाँ, स्कूल ऑफ फार्मेसी एंड टेक्नोलॉजी मैनेजमेंट धुले में डी.फार्म, बी.फार्म, बी.फार्म प्लस एमबीए फार्मा टेक, एम.फार्म और पीएचडी उपलब्ध हैं।"
            elif lang == "mr":
                return "होय, स्कूल ऑफ फार्मसी अँड टेक्नॉलॉजी मॅनेजमेंट धुळे येथे डी.फार्म, बी.फार्म, बी.फार्म प्लस एमबीए फार्मा टेक, एम.फार्म आणि पीएच.डी. उपलब्ध आहेत."
            return (
                "Yes. The School of Pharmacy and Technology Management offers D.Pharm, B.Pharm, "
                "B.Pharm with MBA in Pharma Tech, B.Tech in Cosmetic Technology, M.Pharm programs, and Ph.D. in Pharmaceutical Sciences."
            )

        # 19. BBA
        if "bba" in q or "business administration" in q or "बीबीए" in q:
            if lang == "hi":
                return "हाँ, स्कूल ऑफ कॉमर्स धुले परिसर में बैचलर ऑफ बिजनेस एडमिनिस्ट्रेशन (बीबीए) प्रदान करता है।"
            elif lang == "mr":
                return "होय, स्कूल ऑफ कॉमर्स धुळे कॅम्पसमध्ये बॅचलर ऑफ बिझनेस ॲडमिनिस्ट्रेशन (बीबीए) अभ्यासक्रम चालवते."
            return "Yes, the School of Commerce offers Bachelor of Business Administration, or BBA, at the Dhule campus."

        # 20. BCA
        if "bca" in q or "computer applications" in q or "बीसीए" in q:
            if lang == "hi":
                return "हाँ, स्कूल ऑफ कॉमर्स धुले में बैचलर इन कंप्यूटर एप्लीकेशंस (बीसीए) उपलब्ध है।"
            elif lang == "mr":
                return "होय, स्कूल ऑफ कॉमर्स धुळे येथे बॅचलर इन कॉम्प्युटर ॲप्लिकेशन्स (बीसीए) उपलब्ध आहे."
            return "Yes. The School of Commerce offers Bachelor in Computer Applications, or BCA."

        # 21. Commerce courses
        if "commerce" in q or "कॉमर्स" in q:
            if lang == "hi":
                return "स्कूल ऑफ कॉमर्स धुले में बैचलर ऑफ बिजनेस एडमिनिस्ट्रेशन (बीबीए) और बैचलर इन कंप्यूटर एप्लीकेशंस (बीसीए) उपलब्ध हैं।"
            elif lang == "mr":
                return "स्कूल ऑफ कॉमर्स धुळे येथे बीबीए आणि बीसीए अभ्यासक्रम चालवले जातात."
            return "Which courses are available in Commerce? Under the School of Commerce, the Dhule campus offers Bachelor of Business Administration (BBA) and Bachelor in Computer Applications (BCA)."

        # 22. General courses
        if any(w in q for w in ["what courses", "courses available", "programs", "कौन से कोर्स", "कोणते कोर्सेस"]):
            if lang == "hi":
                return "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले तीन स्कूलों में पाठ्यक्रम प्रदान करता है: इंजीनियरिंग, फार्मेसी, और कॉमर्स।"
            elif lang == "mr":
                return "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे तीन विद्याशाखांमध्ये अभ्यासक्रम चालवते: इंजिनिअरिंग, फार्मसी, आणि कॉमर्स."
            return (
                "SVKM's NMIMS Global University, Dhule offers programs across three schools: "
                "Technology Management and Engineering, Pharmacy and Technology Management, and Commerce."
            )

        # 23. Admission
        if any(w in q for w in ["admission", "how to apply", "eligib", "एडमिशन", "प्रवेश"]):
            if lang == "hi":
                return "प्रवेश विश्वविद्यालय के प्रवेश पोर्टल पर ऑनलाइन पंजीकरण के माध्यम से आयोजित किए जाते हैं। कृपया आधिकारिक वेबसाइट svkmnmimsgu.ac.in देखें।"
            elif lang == "mr":
                return "प्रवेश प्रक्रिया विद्यापीठाच्या प्रवेश पोर्टलवर ऑनलाइन नोंदणीद्वारे पार पडते. कृपया अधिकृत संकेतस्थळ svkmnmimsgu.ac.in तपासा."
            return (
                "Admissions are conducted through registration on the university admission portal. "
                "Please check the official website svkmnmimsgu.ac.in for verified cutoff and application guidelines."
            )

        # 24. Default fallback: NO HALLUCINATION
        if lang == "hi":
            return "मेरे पास इस समय इस बारे में सत्यापित जानकारी नहीं है। कृपया आधिकारिक एनएमआईएमएस धुले वेबसाइट देखें या कॉलेज से संपर्क करें।"
        elif lang == "mr":
            return "माझ्याकडे या क्षणी याबद्दल पडताळलेली माहिती नाही. कृपया अधिकृत एनएमआयएमएस धुळे संकेतस्थळ तपासा किंवा महाविद्यालयाशी संपर्क साधा।"
        return "I don't have verified information about that at the moment. Please check the official NMIMS Dhule website or contact the college."

ai_service = AIService()
