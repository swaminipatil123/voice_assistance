from twilio.twiml.voice_response import VoiceResponse, Gather
from backend.config import Config
from backend.utils.logger import logger

class TelephonyService:
    """Service to generate telephony/IVR markup (TwiML) for SVKM's NMIMS Global University, Dhule in English, Hindi, and Marathi."""

    def __init__(self, voice: str = None, language: str = None):
        self.default_voice = voice or Config.DEFAULT_VOICE
        self.default_language = language or Config.DEFAULT_LANGUAGE

    def get_voice_and_lang(self, lang: str = "en"):
        """Maps language code to appropriate Polly voice and BCP-47 tag."""
        l = (lang or "en").lower().strip()
        if l == "hi":
            return "Polly.Aditi", "hi-IN"
        elif l == "mr":
            return "Polly.Aditi", "mr-IN"
        return "Polly.Aditi", "en-IN"

    def create_language_selection_response(self, action_url: str = "/voice/language") -> str:
        """
        Creates language selection menu:
        1: English, 2: Hindi (हिंदी), 3: Marathi (मराठी).
        """
        response = VoiceResponse()
        gather = Gather(
            num_digits=1,
            action=action_url,
            method="POST",
            timeout=8
        )
        gather.say("For English, press 1.", voice="Polly.Aditi", language="en-IN")
        gather.say("हिंदी के लिए 2 दबाएं।", voice="Polly.Aditi", language="hi-IN")
        gather.say("मराठीसाठी 3 दाबा.", voice="Polly.Aditi", language="mr-IN")
        response.append(gather)

        response.say("Continuing in English.", voice="Polly.Aditi", language="en-IN")
        response.redirect("/voice/incoming?lang=en", method="POST")
        return str(response)

    def create_welcome_menu_response(self, college_name: str = "SVKM's NMIMS Global University, Dhule", action_url: str = "/voice/menu", lang: str = "en") -> str:
        """
        Creates opening IVR menu response:
        Welcomes caller and gathers digits 1 to 6 (English, Hindi, Marathi).
        """
        voice, twiml_lang = self.get_voice_and_lang(lang)
        response = VoiceResponse()
        
        target_url = action_url
        if "lang=" not in target_url:
            separator = "&" if "?" in target_url else "?"
            target_url = f"{target_url}{separator}lang={lang}"

        gather = Gather(
            num_digits=1,
            action=target_url,
            method="POST",
            timeout=8
        )

        if lang == "hi":
            greeting_text = (
                "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले में आपका स्वागत है। "
                "कॉलेज की जानकारी के लिए 1 दबाएं। "
                "प्रवेश जानकारी के लिए 2 दबाएं। "
                "परीक्षा जानकारी के लिए 3 दबाएं। "
                "पाठ्यक्रम और विभागों के लिए 4 दबाएं। "
                "हमारे एआई सहायक से बात करने के लिए 5 दबाएं। "
                "भाषा बदलने के लिए 6 दबाएं।"
            )
            fallback_text = "हमें कोई इनपुट नहीं मिला। कृपया दोबारा कॉल करें। धन्यवाद।"
        elif lang == "mr":
            greeting_text = (
                "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे मध्ये आपले स्वागत आहे. "
                "कॉलेजच्या माहितीसाठी 1 दाबा. "
                "प्रवेश माहितीसाठी 2 दाबा. "
                "परीक्षा माहितीसाठी 3 दाबा. "
                "अभ्यासक्रम आणि विभागांसाठी 4 दाबा. "
                "आमच्या एआई सहाय्यकाशी बोलण्यासाठी 5 दाबा. "
                "भाषा बदलण्यासाठी 6 दाबा."
            )
            fallback_text = "कोणतेही इनपुट मिळाले नाही. कृपया पुन्हा कॉल करा. धन्यवाद."
        else:
            greeting_text = (
                "Welcome to SVKM's NMIMS Global University, Dhule. "
                "Press 1 for College Information. "
                "Press 2 for Admission Information. "
                "Press 3 for Examination Information. "
                "Press 4 for Courses and Departments. "
                "Press 5 to talk to our AI Assistant. "
                "Press 6 for Language Options: Hindi, Marathi, or English."
            )
            fallback_text = "We did not receive any input. Please call back again. Goodbye."

        gather.say(greeting_text, voice=voice, language=twiml_lang)
        response.append(gather)

        response.say(fallback_text, voice=voice, language=twiml_lang)
        response.hangup()
        return str(response)

    def create_courses_menu_response(self, action_url: str = "/voice/courses_menu", lang: str = "en") -> str:
        """
        Sub-menu for Option 4 (Courses and Departments):
        Press 1 for Engineering, 2 for Pharmacy, 3 for Commerce, 4 for Main Menu.
        """
        voice, twiml_lang = self.get_voice_and_lang(lang)
        response = VoiceResponse()

        target_url = action_url
        if "lang=" not in target_url:
            separator = "&" if "?" in target_url else "?"
            target_url = f"{target_url}{separator}lang={lang}"

        gather = Gather(
            num_digits=1,
            action=target_url,
            method="POST",
            timeout=8
        )

        if lang == "hi":
            menu_text = (
                "इंजीनियरिंग पाठ्यक्रमों के लिए 1 दबाएं। "
                "फार्मेसी पाठ्यक्रमों के लिए 2 दबाएं। "
                "कॉमर्स पाठ्यक्रमों के लिए 3 दबाएं। "
                "मुख्य मेनू पर लौटने के लिए 4 दबाएं।"
            )
        elif lang == "mr":
            menu_text = (
                "इंजिनिअरिंग अभ्यासक्रमांसाठी 1 दाबा. "
                "फार्मसी अभ्यासक्रमांसाठी 2 दाबा. "
                "कॉमर्स अभ्यासक्रमांसाठी 3 दाबा. "
                "मुख्य मेनूवर परत जाण्यासाठी 4 दाबा."
            )
        else:
            menu_text = (
                "Press 1 for Engineering courses. "
                "Press 2 for Pharmacy courses. "
                "Press 3 for Commerce courses. "
                "Press 4 to return to the main menu."
            )

        gather.say(menu_text, voice=voice, language=twiml_lang)
        response.append(gather)

        response.redirect(f"/voice/incoming?lang={lang}", method="POST")
        return str(response)

    def create_info_response(self, speech_text: str, menu_url: str = "/voice/incoming", lang: str = "en") -> str:
        """
        Creates spoken response for information selections with repeat / return option.
        """
        voice, twiml_lang = self.get_voice_and_lang(lang)
        response = VoiceResponse()
        response.say(speech_text, voice=voice, language=twiml_lang)
        response.pause(length=1)

        target_url = menu_url
        if "lang=" not in target_url:
            separator = "&" if "?" in target_url else "?"
            target_url = f"{target_url}{separator}lang={lang}"

        gather = Gather(num_digits=1, action=target_url, method="POST", timeout=5)

        if lang == "hi":
            repeat_text = "मुख्य मेनू पर लौटने के लिए 9 दबाएं। कॉल समाप्त करने के लिए आप फोन रख सकते हैं।"
            bye_text = "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले को कॉल करने के लिए धन्यवाद। अलविदा।"
        elif lang == "mr":
            repeat_text = "मुख्य मेनूवर परत जाण्यासाठी 9 दाबा. कॉल समाप्त करण्यासाठी आपण फोन ठेवू शकता."
            bye_text = "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे येथे संपर्क केल्याबद्दल धन्यवाद. नमस्कार."
        else:
            repeat_text = "To return to the main menu, press 9. To end the call, you may hang up now."
            bye_text = "Thank you for calling SVKM's NMIMS Global University, Dhule. Goodbye."

        gather.say(repeat_text, voice=voice, language=twiml_lang)
        response.append(gather)

        response.say(bye_text, voice=voice, language=twiml_lang)
        response.hangup()
        return str(response)

    def create_ai_greeting_response(self, process_url: str = "/voice/process", lang: str = "en") -> str:
        """
        Option 5 entry: Greeting and speech gathering.
        """
        voice, twiml_lang = self.get_voice_and_lang(lang)
        response = VoiceResponse()

        target_url = process_url
        if "lang=" not in target_url:
            separator = "&" if "?" in target_url else "?"
            target_url = f"{target_url}{separator}lang={lang}"

        gather = Gather(
            input="speech",
            action=target_url,
            method="POST",
            timeout=5,
            speech_timeout="auto",
            language=twiml_lang
        )

        if lang == "hi":
            greeting = "नमस्ते। आप एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले एआई सहायक से जुड़े हैं। कृपया अपना प्रश्न पूछें।"
            reprompt = "मुझे कुछ सुनाई नहीं दिया। कृपया पुनः प्रयास करें।"
        elif lang == "mr":
            greeting = "नमस्कार. आपण एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे एआई सहाय्यकाशी जोडलेले आहात. कृपया आपला प्रश्न विचारा."
            reprompt = "मला काही ऐकू आले नाही. कृपया पुन्हा प्रयत्न करा."
        else:
            greeting = "Hello. You are now connected to the SVKM NMIMS Global University, Dhule AI Assistant. Please ask your question."
            reprompt = "I didn't hear anything. Let's try again."

        gather.say(greeting, voice=voice, language=twiml_lang)
        response.append(gather)

        response.say(reprompt, voice=voice, language=twiml_lang)
        response.redirect(target_url, method="POST")
        return str(response)

    def create_ai_continuation_response(self, answer_text: str, process_url: str = "/voice/process", menu_url: str = "/voice/incoming", lang: str = "en") -> str:
        """Plays AI answer and continues listening for the next voice query or menu return."""
        voice, twiml_lang = self.get_voice_and_lang(lang)
        response = VoiceResponse()
        response.say(answer_text, voice=voice, language=twiml_lang)
        response.pause(length=1)

        target_url = process_url
        if "lang=" not in target_url:
            separator = "&" if "?" in target_url else "?"
            target_url = f"{target_url}{separator}lang={lang}"

        gather = Gather(
            input="speech dtmf",
            action=target_url,
            method="POST",
            timeout=6,
            speech_timeout="auto",
            language=twiml_lang,
            num_digits=1
        )

        if lang == "hi":
            followup = "क्या आप कोई अन्य प्रश्न पूछना चाहते हैं? कृपया अपना प्रश्न बोलें, या मुख्य मेनू पर लौटने के लिए 9 दबाएं।"
            goodbye = "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले से संपर्क करने के लिए धन्यवाद। आपका दिन शुभ हो। अलविदा!"
        elif lang == "mr":
            followup = "आपल्याला दुसरा प्रश्न विचारायचा आहे का? कृपया आपला प्रश्न बोला, किंवा मुख्य मेनूवर परत जाण्यासाठी 9 दाबा."
            goodbye = "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे येथे संपर्क केल्याबद्दल धन्यवाद. आपला दिवस शुभ जावो. नमस्कार!"
        else:
            followup = "Would you like to ask another question? Please speak your question, or press 9 to return to the main menu."
            goodbye = "Thank you for contacting SVKM's NMIMS Global University, Dhule. Have a wonderful day. Goodbye!"

        gather.say(followup, voice=voice, language=twiml_lang)
        response.append(gather)

        response.say(goodbye, voice=voice, language=twiml_lang)
        response.hangup()
        return str(response)

    def create_invalid_input_response(self, retry_url: str = "/voice/incoming", lang: str = "en") -> str:
        """Handles invalid keypad selections."""
        voice, twiml_lang = self.get_voice_and_lang(lang)
        response = VoiceResponse()

        target_url = retry_url
        if "lang=" not in target_url:
            separator = "&" if "?" in target_url else "?"
            target_url = f"{target_url}{separator}lang={lang}"

        if lang == "hi":
            msg = "क्षमा करें, यह एक मान्य विकल्प नहीं है।"
        elif lang == "mr":
            msg = "क्षमस्व, हा वैध पर्याय नाही."
        else:
            msg = "I am sorry, that is not a valid option."

        response.say(msg, voice=voice, language=twiml_lang)
        response.redirect(target_url, method="POST")
        return str(response)

    def create_goodbye_response(self, message: str = None, lang: str = "en") -> str:
        """Ends the call politely."""
        voice, twiml_lang = self.get_voice_and_lang(lang)
        response = VoiceResponse()
        if not message:
            if lang == "hi":
                message = "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले से संपर्क करने के लिए धन्यवाद। अलविदा!"
            elif lang == "mr":
                message = "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे येथे संपर्क केल्याबद्दल धन्यवाद. नमस्कार!"
            else:
                message = "Thank you for contacting SVKM's NMIMS Global University, Dhule. Goodbye!"
        response.say(message, voice=voice, language=twiml_lang)
        response.hangup()
        return str(response)

telephony_service = TelephonyService()
