import json
from pathlib import Path
from backend.config import Config
from backend.utils.logger import logger

class CollegeDataService:
    """Service to load, cache, and query verified SVKM's NMIMS Global University, Dhule data."""

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Config.DATA_DIR

    def _load_json(self, filename: str) -> dict:
        filepath = self.data_dir / filename
        try:
            if not filepath.exists():
                logger.warning(f"Data file not found: {filepath}")
                return {}
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return {}

    def get_university_info(self) -> dict:
        data = self._load_json("university.json")
        return data if data else self._load_json("college_info.json")

    def get_engineering_info(self) -> dict:
        return self._load_json("engineering.json")

    def get_pharmacy_info(self) -> dict:
        return self._load_json("pharmacy.json")

    def get_commerce_info(self) -> dict:
        return self._load_json("commerce.json")

    def get_contact_info(self) -> dict:
        return self._load_json("contact.json")

    def get_admission_info(self) -> dict:
        return self._load_json("admission.json")

    def get_examination_info(self) -> dict:
        return self._load_json("examination.json")

    def get_faq_info(self) -> dict:
        return self._load_json("faq.json")

    def get_college_name(self) -> str:
        u = self.get_university_info()
        return u.get("university_name", "SVKM's NMIMS Global University") + ", Dhule"

    def get_speech_summary(self, category: str, lang: str = "en") -> str:
        """Returns concise spoken text suitable for phone IVR menus in English, Hindi, or Marathi."""
        lang = (lang or "en").lower().strip()
        if lang not in ("en", "hi", "mr"):
            lang = "en"

        if lang == "hi":
            if category == "college_info":
                return (
                    "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले परिसर महाराष्ट्र के धुले में मुंबई-आगरा राष्ट्रीय राजमार्ग पर स्थित है। "
                    "हमारी आधिकारिक वेबसाइट svkmnmimsngu.ac.in (svkmnmimsgu.ac.in - एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन) है।"
                )
            elif category == "admission":
                return (
                    "प्रवेश की जानकारी: एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले में प्रवेश आधिकारिक विश्वविद्यालय पोर्टल के माध्यम से ऑनलाइन आयोजित किए जाते हैं। "
                    "कृपया सत्यापित तिथियों और दिशानिर्देशों के लिए आधिकारिक वेबसाइट svkmnmimsngu.ac.in (svkmnmimsgu.ac.in - एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन) देखें।"
                )
            elif category == "examination":
                return (
                    "परीक्षा की जानकारी: परीक्षाएं शैक्षणिक कैलेंडर के अनुसार आयोजित की जाती हैं। "
                    "समय सारिणी और कार्यक्रम आधिकारिक तौर पर छात्र पोर्टल पर जारी किए जाते हैं।"
                )
            elif category == "courses":
                return (
                    "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले तीन स्कूलों में पाठ्यक्रम प्रदान करता है: "
                    "इंजीनियरिंग, फार्मेसी, और कॉमर्स। "
                    "इंजीनियरिंग पाठ्यक्रमों के लिए 1 दबाएं। "
                    "फार्मेसी पाठ्यक्रमों के लिए 2 दबाएं। "
                    "कॉमर्स पाठ्यक्रमों के लिए 3 दबाएं। "
                    "मुख्य मेनू पर लौटने के लिए 4 दबाएं।"
                )
            elif category == "courses_engineering":
                return (
                    "स्कूल ऑफ टेक्नोलॉजी, मैनेजमेंट एंड इंजीनियरिंग धुले परिसर में कंप्यूटर इंजीनियरिंग, "
                    "आर्टिफिशियल इंटेलिजेंस और डेटा साइंस, बी.टेक प्लस एमबीए टेक, एमसीए, एम.टेक और पीएचडी पाठ्यक्रम उपलब्ध हैं।"
                )
            elif category == "courses_pharmacy":
                return (
                    "स्कूल ऑफ फार्मेसी एंड टेक्नोलॉजी मैनेजमेंट धुले में डी.फार्म, बी.फार्म, "
                    "बी.फार्म प्लस एमबीए फार्मा टेक, एम.फार्म और फार्मास्यूटिकल साइंसेज में पीएचडी पाठ्यक्रम उपलब्ध हैं।"
                )
            elif category == "courses_commerce":
                return (
                    "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले का स्कूल ऑफ कॉमर्स "
                    "बैचलर ऑफ बिजनेस एडमिनिस्ट्रेशन (बीबीए) और बैचलर इन कंप्यूटर एप्लीकेशंस (बीसीए) प्रदान करता है।"
                )
            return "मेरे पास इस समय इस बारे में सत्यापित जानकारी नहीं है। कृपया आधिकारिक एनएमआईएमएस धुले वेबसाइट देखें या कॉलेज से संपर्क करें।"

        elif lang == "mr":
            if category == "college_info":
                return (
                    "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे परिसर महाराष्ट्रातील धुळे येथे मुंबई-आग्रा राष्ट्रीय महामार्गावर स्थित आहे. "
                    "विद्यापीठामध्ये स्कूल ऑफ टेक्नॉलॉजी, मॅनेजमेंट अँड इंजिनिअरिंग, स्कूल ऑफ फार्मसी अँड टेक्नॉलॉजी मॅनेजमेंट, आणि स्कूल ऑफ कॉमर्स यांचा समावेश आहे. "
                    "आमचे अधिकृत संकेतस्थळ svkmnmimsngu.ac.in (svkmnmimsgu.ac.in - एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन) आहे."
                )
            elif category == "admission":
                return (
                    "प्रवेश माहिती: एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे येथील प्रवेश प्रक्रिया विद्यापीठाच्या अधिकृत पोर्टलवर ऑनलाइन पद्धतीने पार पडते. "
                    "अधिकृत तारखा व नियमावलीसाठी कृपया svkmnmimsngu.ac.in (svkmnmimsgu.ac.in - एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन) हे संकेतस्थळ तपासा."
                )
            elif category == "examination":
                return (
                    "परीक्षा माहिती: परीक्षा शैक्षणिक दिनदर्शिकेनुसार घेतल्या जातात. "
                    "वेळापत्रक आणि सूचना अधिकृत विद्यार्थी पोर्टलवर जाहीर केल्या जातात."
                )
            elif category == "courses":
                return (
                    "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे तीन विद्याशाखांमध्ये अभ्यासक्रम चालवते: "
                    "इंजिनिअरिंग, फार्मसी, आणि कॉमर्स. "
                    "इंजिनिअरिंग अभ्यासक्रमांसाठी 1 दाबा. "
                    "फार्मसी अभ्यासक्रमांसाठी 2 दाबा. "
                    "कॉमर्स अभ्यासक्रमांसाठी 3 दाबा. "
                    "मुख्य मेनूवर परत जाण्यासाठी 4 दाबा."
                )
            elif category == "courses_engineering":
                return (
                    "स्कूल ऑफ टेक्नॉलॉजी, मॅनेजमेंट अँड इंजिनिअरिंग धुळे येथे कॉम्प्युटर इंजिनिअरिंग, "
                    "एआय अँड डेटा सायन्स, सीएसई डेटा सायन्स, इंटिग्रेटेड बी.टेक प्लस एमबीए टेक, एमसीए, एम.टेक आणि पीएच.डी. अभ्यासक्रम उपलब्ध आहेत."
                )
            elif category == "courses_pharmacy":
                return (
                    "स्कूल ऑफ फार्मसी अँड टेक्नॉलॉजी मॅनेजमेंट धुळे येथे डी.फार्म, बी.फार्म, "
                    "बी.फार्म प्लस एमबीए फार्मा टेक, एम.फार्म आणि फार्मास्युटिकल सायन्सेसमध्ये पीएच.डी. उपलब्ध आहे."
                )
            elif category == "courses_commerce":
                return (
                    "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे चे स्कूल ऑफ कॉमर्स "
                    "बॅचलर ऑफ बिझनेस ॲडमिनिस्ट्रेशन (बीबीए) आणि बॅचलर इन कॉम्प्युटर ॲप्लिकेशन्स (बीसीए) अभ्यासक्रम चालवते."
                )
            return "माझ्याकडे या क्षणी याबद्दल पडताळलेली माहिती नाही. कृपया अधिकृत एनएमआईएमएस धुळे संकेतस्थळ तपासा किंवा महाविद्यालयाशी संपर्क साधा."

        # Default: English
        fallback = "I don't have verified information about that at the moment. Please check the official NMIMS Dhule website or contact the college."

        if category == "college_info":
            u = self.get_university_info()
            c = self.get_contact_info()
            name = "SVKM's NMIMS Global University, Dhule"
            loc = c.get("address", "Mumbai-Agra National Highway, Dhule, Maharashtra")
            return (
                f"{name} is located at {loc}. "
                f"The university comprises the School of Technology, Management and Engineering, "
                f"the School of Pharmacy and Technology Management, and the School of Commerce. "
                f"Our official website is svkmnmimsngu.ac.in (svkmnmimsgu.ac.in), pronounced as S V K M, N M I M S, S N G U, dot A C, dot I N."
            )

        elif category == "admission":
            adm = self.get_admission_info()
            process = adm.get("general_process", "Admissions are conducted through online registration on the university admission portal.")
            return f"Admission Information: {process} Please refer to the official website svkmnmimsngu.ac.in (svkmnmimsgu.ac.in), pronounced as S V K M, N M I M S, S N G U, dot A C, dot I N for verified cutoff dates and guidelines."

        elif category == "examination":
            exam = self.get_examination_info()
            overview = exam.get("examination_overview", "Examinations are conducted according to the academic calendar.")
            notices = exam.get("exam_notices", "Timetables and schedules are officially released on the student portal.")
            return f"Examination Information: {overview} {notices} For specific date sheets, please refer to the student portal."

        elif category == "courses":
            return (
                "SVKM's NMIMS Global University, Dhule offers programs across three schools: "
                "The School of Technology, Management and Engineering, "
                "the School of Pharmacy and Technology Management, and "
                "the School of Commerce. "
                "Press 1 for Engineering courses. "
                "Press 2 for Pharmacy courses. "
                "Press 3 for Commerce courses. "
                "Or Press 4 to return to the main menu."
            )

        elif category == "courses_engineering":
            eng = self.get_engineering_info()
            btech = eng.get("btech_programs", [])
            btech_str = ", ".join(btech[:4])
            return (
                f"The School of Technology, Management and Engineering at the Dhule campus offers "
                f"B.Tech programs in {btech_str}, Electrical, IT, and Mechanical Engineering. "
                f"We also offer B.Tech plus MBA dual degrees, MCA, M.Tech, and Ph.D. in Technology."
            )

        elif category == "courses_pharmacy":
            pharm = self.get_pharmacy_info()
            ug = ", ".join(pharm.get("undergraduate_programs", ["B.Pharm", "B.Pharm + MBA", "B.Tech Cosmetic Technology"]))
            return (
                f"The School of Pharmacy and Technology Management at the Dhule campus offers "
                f"D.Pharm, {ug}, M.Pharm in four specializations, and Ph.D. in Pharmaceutical Sciences."
            )

        elif category == "courses_commerce":
            return (
                "The School of Commerce at SVKM's NMIMS Global University, Dhule offers "
                "Bachelor of Business Administration, or BBA, and Bachelor in Computer Applications, or BCA."
            )

        return fallback

    def get_all_context(self) -> str:
        """Returns structured verified text for the AI system prompt."""
        university = self.get_university_info()
        engineering = self.get_engineering_info()
        pharmacy = self.get_pharmacy_info()
        commerce = self.get_commerce_info()
        contact = self.get_contact_info()
        admission = self.get_admission_info()
        examination = self.get_examination_info()

        sections = [
            "CAMPUS IDENTITY & RESTRICTION:\n"
            "- Institution: SVKM's NMIMS Global University, Dhule\n"
            "- Campus: Dhule, Maharashtra, India\n"
            "- CRITICAL RULE: This assistant is ONLY for the Dhule campus. Do NOT mix information with NMIMS Shirpur or Babulde.\n"
            f"- Official Website: {university.get('website', 'https://www.svkmnmimsgu.ac.in/')}\n"
            f"- Spoken Website: {university.get('website_spoken', 'svkmnmimsgu.ac.in')}\n"
            f"- Location & Address: {contact.get('address', university.get('location', 'Dhule, Maharashtra'))}",

            f"SCHOOL OF TECHNOLOGY, MANAGEMENT & ENGINEERING (STME) - DHULE:\n"
            f"- B.Tech Programs: {json.dumps(engineering.get('btech_programs', []))}\n"
            f"- Dual Degree Programs (B.Tech + MBA): {json.dumps(engineering.get('dual_degree_programs', []))}\n"
            f"- Postgraduate Programs: {json.dumps(engineering.get('postgraduate_programs', []))}\n"
            f"- Doctoral Programs: {json.dumps(engineering.get('doctoral_programs', []))}\n"
            f"- Contact: {json.dumps(engineering.get('contact', {}))}",

            f"SCHOOL OF PHARMACY & TECHNOLOGY MANAGEMENT (SPTM) - DHULE:\n"
            f"- Diploma Programs: {json.dumps(pharmacy.get('diploma_programs', []))}\n"
            f"- Undergraduate Programs: {json.dumps(pharmacy.get('undergraduate_programs', []))}\n"
            f"- Postgraduate Programs: {json.dumps(pharmacy.get('postgraduate_programs', []))}\n"
            f"- Doctoral Programs: {json.dumps(pharmacy.get('doctoral_programs', []))}\n"
            f"- Contact: {json.dumps(pharmacy.get('contact', {}))}",

            f"SCHOOL OF COMMERCE - DHULE:\n"
            f"- Undergraduate Programs: {json.dumps(commerce.get('undergraduate_programs', []))}\n"
            f"- Contact: {json.dumps(commerce.get('contact', {}))}",

            f"OFFICIAL CONTACT NUMBERS:\n"
            f"- STME: {contact.get('departments_contact', {}).get('School of Technology Management and Engineering', '02562 350620')}\n"
            f"- SPTM: {contact.get('departments_contact', {}).get('School of Pharmacy and Technology Management', '02562 350640')}\n"
            f"- Commerce: {contact.get('departments_contact', {}).get('School of Commerce', '02562 350600')}\n"
            f"- How to reach: {contact.get('how_to_reach', '')}",

            f"ADMISSION:\n{json.dumps(admission, indent=2)}",
            f"EXAMINATION:\n{json.dumps(examination, indent=2)}"
        ]
        return "\n\n".join(sections)

    def get_relevant_context(self, user_question: str) -> str:
        """Dynamically filters verified Dhule knowledge based on caller question."""
        q = user_question.lower()
        selected = [
            "CAMPUS IDENTITY: SVKM's NMIMS Global University, Dhule (Maharashtra, India). "
            "Official Website: svkmnmimsgu.ac.in. "
            "STRICT NOTE: This is Dhule campus only. Never refer to Shirpur campus."
        ]

        # 1. Engineering / Tech / MCA / M.Tech
        if any(w in q for w in ["eng", "tech", "computer", "ai", "machine learning", "data science", "civil", "mechanical", "electrical", "mca", "m.tech", "stme"]):
            selected.append(f"ENGINEERING DATA:\n{json.dumps(self.get_engineering_info(), indent=2)}")

        # 2. Pharmacy / Cosmetic / Pharma Tech / D.Pharm / B.Pharm / M.Pharm
        if any(w in q for w in ["pharm", "cosmetic", "sptm", "drug", "medicine"]):
            selected.append(f"PHARMACY DATA:\n{json.dumps(self.get_pharmacy_info(), indent=2)}")

        # 3. Commerce / BBA / BCA
        if any(w in q for w in ["commerce", "bba", "bca", "business", "application"]):
            selected.append(f"COMMERCE DATA:\n{json.dumps(self.get_commerce_info(), indent=2)}")

        # 4. Contact / Address / Location / Website / Reach
        if any(w in q for w in ["where", "location", "address", "website", "contact", "phone", "number", "reach", "station", "airport"]):
            selected.append(f"CONTACT & LOCATION DATA:\n{json.dumps(self.get_contact_info(), indent=2)}")

        # 5. Admission / Eligibility / 12th / Process / Fees / Dates
        if any(w in q for w in ["admit", "admission", "apply", "eligib", "12th", "after 12", "cutoff", "fee", "intake"]):
            selected.append(f"ADMISSION DATA:\n{json.dumps(self.get_admission_info(), indent=2)}")

        # 6. Examination / Result / Schedule
        if any(w in q for w in ["exam", "test", "result", "schedule", "grade"]):
            selected.append(f"EXAMINATION DATA:\n{json.dumps(self.get_examination_info(), indent=2)}")

        if len(selected) == 1:
            return self.get_all_context()

        return "\n\n".join(selected)

college_data_service = CollegeDataService()
