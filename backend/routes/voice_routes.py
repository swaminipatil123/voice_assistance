from flask import Blueprint, request, Response, jsonify, render_template_string
from backend.services.telephony_service import telephony_service
from backend.services.college_data_service import college_data_service
from backend.services.ai_service import ai_service
from backend.services.speech_to_text import speech_to_text_service
from backend.services.text_to_speech import text_to_speech_service
from backend.services.db_service import db_service
from backend.utils.logger import logger

voice_bp = Blueprint("voice", __name__)

def _get_request_param(param_name: str, default: str = "") -> str:
    """Helper to extract a parameter from form, json, or query string."""
    val = request.values.get(param_name)
    if val is None and request.is_json:
        val = request.json.get(param_name)
    return str(val).strip() if val is not None else default


@voice_bp.route("/voice/incoming", methods=["GET", "POST"])
def voice_incoming():
    """
    Initial webhook triggered when a student calls SVKM's NMIMS Global University, Dhule.
    Plays the main IVR menu and gathers keypad digits 1 to 6 in the selected language.
    """
    call_sid = _get_request_param("CallSid", "SIMULATED_CALL")
    from_number = _get_request_param("From", "Caller")
    lang = _get_request_param("lang", "en")
    logger.info(f"Incoming call received from {from_number} (SID: {call_sid}, lang: {lang}) at /voice/incoming")
    
    # Log to SQLite
    db_service.log_call(call_sid, from_number)
    db_service.log_interaction(call_sid, "system", f"Call connected, playing main NMIMS Dhule IVR menu (lang: {lang})")

    twiml_xml = telephony_service.create_welcome_menu_response(
        college_name="SVKM's NMIMS Global University, Dhule",
        action_url=f"/voice/menu?lang={lang}",
        lang=lang
    )
    return Response(twiml_xml, mimetype="application/xml")


@voice_bp.route("/voice/menu", methods=["GET", "POST"])
def voice_menu():
    """
    Processes main menu keypad input:
    - 1: College Information
    - 2: Admission Information
    - 3: Examination Information
    - 4: Courses and Departments (Opens School Sub-menu: 1 Eng, 2 Pharm, 3 Commerce)
    - 5: AI Voice Assistant
    - 6: Language Selection (English, Hindi, Marathi)
    - 9: Return to main menu
    """
    digit = _get_request_param("Digits")
    call_sid = _get_request_param("CallSid", "SIMULATED_CALL")
    lang = _get_request_param("lang", "en")
    logger.info(f"Keypad input received: {digit} (lang={lang}) for call {call_sid}")
    if digit:
        db_service.log_interaction(call_sid, "caller", f"Pressed DTMF key {digit}")

    if not digit:
        return Response(
            telephony_service.create_welcome_menu_response(action_url=f"/voice/menu?lang={lang}", lang=lang),
            mimetype="application/xml"
        )

    if digit == "1":
        info_text = college_data_service.get_speech_summary("college_info", lang=lang)
        xml = telephony_service.create_info_response(info_text, menu_url=f"/voice/incoming?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")

    elif digit == "2":
        info_text = college_data_service.get_speech_summary("admission", lang=lang)
        xml = telephony_service.create_info_response(info_text, menu_url=f"/voice/incoming?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")

    elif digit == "3":
        info_text = college_data_service.get_speech_summary("examination", lang=lang)
        xml = telephony_service.create_info_response(info_text, menu_url=f"/voice/incoming?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")

    elif digit == "4":
        xml = telephony_service.create_courses_menu_response(action_url=f"/voice/courses_menu?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")

    elif digit == "5":
        xml = telephony_service.create_ai_greeting_response(process_url=f"/voice/process?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")

    elif digit == "6":
        # Enter Language Selection Menu
        xml = telephony_service.create_language_selection_response(action_url="/voice/language")
        return Response(xml, mimetype="application/xml")

    elif digit == "9":
        return Response(
            telephony_service.create_welcome_menu_response(action_url=f"/voice/menu?lang={lang}", lang=lang),
            mimetype="application/xml"
        )

    else:
        xml = telephony_service.create_invalid_input_response(retry_url=f"/voice/incoming?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")


@voice_bp.route("/voice/language", methods=["GET", "POST"])
def voice_language():
    """
    Handles Language Selection DTMF:
    - 1: English (en)
    - 2: Hindi (hi)
    - 3: Marathi (mr)
    """
    digit = _get_request_param("Digits")
    call_sid = _get_request_param("CallSid", "SIMULATED_CALL")
    lang_map = {"1": "en", "2": "hi", "3": "mr"}
    selected_lang = lang_map.get(digit, "en")
    
    db_service.log_interaction(call_sid, "caller", f"Language selected: {selected_lang} (Digit: {digit})")
    logger.info(f"Caller selected language '{selected_lang}' (CallSid: {call_sid})")
    
    xml = telephony_service.create_welcome_menu_response(
        action_url=f"/voice/menu?lang={selected_lang}",
        lang=selected_lang
    )
    return Response(xml, mimetype="application/xml")


@voice_bp.route("/voice/courses_menu", methods=["GET", "POST"])
def voice_courses_menu():
    """
    Sub-menu for Courses & Departments (Option 4):
    - 1: Engineering courses (STME)
    - 2: Pharmacy courses (SPTM)
    - 3: Commerce courses (SOC)
    - 4 or 9: Return to main menu
    - 5: Direct transfer to AI assistant
    """
    digit = _get_request_param("Digits")
    call_sid = _get_request_param("CallSid", "SIMULATED_CALL")
    lang = _get_request_param("lang", "en")
    logger.info(f"Courses sub-menu input received: {digit} (lang={lang}) for call {call_sid}")
    if digit:
        db_service.log_interaction(call_sid, "caller", f"Courses sub-menu pressed DTMF key {digit}")

    if digit == "1":
        speech = college_data_service.get_speech_summary("courses_engineering", lang=lang)
        xml = telephony_service.create_info_response(speech, menu_url=f"/voice/incoming?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")

    elif digit == "2":
        speech = college_data_service.get_speech_summary("courses_pharmacy", lang=lang)
        xml = telephony_service.create_info_response(speech, menu_url=f"/voice/incoming?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")

    elif digit == "3":
        speech = college_data_service.get_speech_summary("courses_commerce", lang=lang)
        xml = telephony_service.create_info_response(speech, menu_url=f"/voice/incoming?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")

    elif digit == "5":
        xml = telephony_service.create_ai_greeting_response(process_url=f"/voice/process?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")

    elif digit in ("4", "9", "0"):
        return Response(
            telephony_service.create_welcome_menu_response(action_url=f"/voice/menu?lang={lang}", lang=lang),
            mimetype="application/xml"
        )

    else:
        xml = telephony_service.create_invalid_input_response(retry_url=f"/voice/courses_menu?lang={lang}", lang=lang)
        return Response(xml, mimetype="application/xml")


@voice_bp.route("/voice/ai", methods=["GET", "POST"])
def voice_ai():
    """Direct entry point for AI voice assistant mode."""
    lang = _get_request_param("lang", "en")
    xml = telephony_service.create_ai_greeting_response(process_url=f"/voice/process?lang={lang}", lang=lang)
    return Response(xml, mimetype="application/xml")


@voice_bp.route("/voice/process", methods=["GET", "POST"])
def voice_process():
    """
    Processes caller speech:
    1. Extracts speech transcription (or DTMF if digit 9 pressed).
    2. Queries Gemini / Dhule College Knowledge Base in selected language.
    3. Generates grounded spoken answer in English, Hindi, or Marathi.
    4. Continues conversation or allows exit.
    """
    digit = _get_request_param("Digits")
    call_sid = _get_request_param("CallSid", "SIMULATED_CALL")
    lang = _get_request_param("lang", "en")

    if digit == "9":
        db_service.log_interaction(call_sid, "caller", "Pressed 9 to return to main menu")
        return Response(
            telephony_service.create_welcome_menu_response(action_url=f"/voice/menu?lang={lang}", lang=lang),
            mimetype="application/xml"
        )

    raw_speech = (
        _get_request_param("SpeechResult") or 
        _get_request_param("question") or 
        _get_request_param("text") or
        _get_request_param("SpeechText")
    )

    transcribed_text = speech_to_text_service.speech_to_text(raw_speech)
    logger.info(f"AI Assistant received user query: '{transcribed_text}' (lang={lang})")

    if not transcribed_text:
        if lang == "hi":
            reprompt_text = "मुझे कोई प्रश्न सुनाई नहीं दिया। कृपया अपना प्रश्न बोलें।"
        elif lang == "mr":
            reprompt_text = "मला कोणताही प्रश्न ऐकू आला नाही. कृपया आपला प्रश्न बोला."
        else:
            reprompt_text = "I could not hear any question. Please speak your question."
        reprompt_xml = telephony_service.create_ai_continuation_response(
            answer_text=reprompt_text,
            process_url=f"/voice/process?lang={lang}",
            menu_url=f"/voice/incoming?lang={lang}",
            lang=lang
        )
        return Response(reprompt_xml, mimetype="application/xml")

    if any(transcribed_text.lower().strip().startswith(w) for w in ["bye", "goodbye", "no thank you", "nothing else", "exit", "अलविदा", "नमस्कार"]):
        goodbye_xml = telephony_service.create_goodbye_response(lang=lang)
        return Response(goodbye_xml, mimetype="application/xml")

    # Generate answer grounded in verified Dhule college knowledge in English, Hindi, or Marathi
    ai_answer = ai_service.answer_question(transcribed_text, lang=lang)
    logger.info(f"AI Generated response ({lang}): '{ai_answer}'")
    db_service.log_interaction(call_sid, "caller", transcribed_text)
    db_service.log_interaction(call_sid, "ai_assistant", ai_answer)

    # Optional local TTS audio synthesis
    text_to_speech_service.text_to_speech(ai_answer, lang=lang)

    # Return telephony XML with answer and follow-up prompt
    continuation_xml = telephony_service.create_ai_continuation_response(
        answer_text=ai_answer,
        process_url=f"/voice/process?lang={lang}",
        menu_url=f"/voice/incoming?lang={lang}",
        lang=lang
    )
    return Response(continuation_xml, mimetype="application/xml")


# --------------------------------------------------------------------------
# Local IVR Test Simulator Routes
# --------------------------------------------------------------------------

@voice_bp.route("/test/ivr", methods=["GET"])
def test_ivr_ui():
    """Interactive web dialer simulator for testing NMIMS Dhule IVR with multilingual options."""
    html_template = r"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>SVKM's NMIMS Global University, Dhule - Voice Assistant</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        :root {
          --bg: #0b1329;
          --card: #152238;
          --text: #f8fafc;
          --accent: #38bdf8;
          --gold: #f59e0b;
          --btn-bg: #1e293b;
          --btn-hover: #334155;
          --call-green: #16a34a;
          --end-red: #dc2626;
        }
        body {
          font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          background: var(--bg);
          color: var(--text);
          margin: 0;
          padding: 20px;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
        }
        .phone-wrapper {
          background: var(--card);
          border-radius: 28px;
          padding: 24px;
          width: 100%;
          max-width: 440px;
          box-shadow: 0 25px 50px -12px rgba(0,0,0,0.6);
          border: 1px solid rgba(56, 189, 248, 0.2);
        }
        .header-title {
          text-align: center;
          margin-bottom: 12px;
        }
        .header-title h3 {
          margin: 0;
          font-size: 18px;
          color: #fff;
          font-weight: 700;
        }
        .header-title p {
          font-size: 11px;
          color: var(--accent);
          margin: 4px 0;
          font-weight: 600;
          letter-spacing: 0.5px;
          text-transform: uppercase;
        }
        /* Multilingual Language Switcher */
        .lang-bar {
          display: flex;
          gap: 6px;
          margin-bottom: 12px;
          background: rgba(0, 0, 0, 0.3);
          padding: 4px;
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .lang-btn {
          flex: 1;
          background: transparent;
          color: #94a3b8;
          border: none;
          padding: 8px 6px;
          border-radius: 8px;
          font-size: 12px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
        }
        .lang-btn:hover {
          color: #fff;
          background: rgba(255, 255, 255, 0.06);
        }
        .lang-btn.active {
          background: var(--accent);
          color: #0b1329;
          box-shadow: 0 2px 8px rgba(56, 189, 248, 0.4);
        }
        .screen {
          background: #060b17;
          border-radius: 16px;
          padding: 16px;
          min-height: 180px;
          max-height: 230px;
          overflow-y: auto;
          margin-bottom: 16px;
          border: 1px solid rgba(255,255,255,0.08);
          font-size: 13px;
          line-height: 1.5;
        }
        .screen-title {
          font-size: 11px;
          color: var(--gold);
          text-transform: uppercase;
          letter-spacing: 1px;
          margin-bottom: 6px;
          font-weight: 700;
        }
        .screen-log { margin: 4px 0; }
        .bot { color: #38bdf8; }
        .user { color: #4ade80; }
        .sys { color: #94a3b8; font-style: italic; }
        .speech-box {
          display: flex;
          gap: 6px;
          margin-bottom: 8px;
        }
        .speech-input {
          flex: 1;
          padding: 10px 12px;
          border-radius: 10px;
          border: 1px solid #334155;
          background: #090f1d;
          color: white;
          font-size: 13px;
        }
        .speech-btn {
          background: var(--accent);
          color: #0b1329;
          border: none;
          padding: 10px 14px;
          border-radius: 10px;
          font-weight: 700;
          cursor: pointer;
        }
        .speech-btn:hover { background: #7dd3fc; }
        .mic-btn {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 10px 12px;
          border-radius: 10px;
          font-weight: 700;
          cursor: pointer;
        }
        .mic-btn.recording { background: #ef4444; animation: pulse 1s infinite; }
        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.05); }
          100% { transform: scale(1); }
        }
        .chips-container {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-bottom: 12px;
        }
        .chip {
          background: rgba(56, 189, 248, 0.12);
          border: 1px solid rgba(56, 189, 248, 0.3);
          color: #7dd3fc;
          font-size: 11px;
          padding: 4px 8px;
          border-radius: 14px;
          cursor: pointer;
          transition: background 0.15s;
        }
        .chip:hover { background: rgba(56, 189, 248, 0.25); color: #fff; }
        .ai-direct-btn {
          width: 100%;
          background: linear-gradient(135deg, #0284c7, #2563eb);
          color: white;
          border: none;
          padding: 10px;
          border-radius: 12px;
          font-weight: 700;
          font-size: 13px;
          margin-bottom: 12px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }
        .ai-direct-btn:hover { background: linear-gradient(135deg, #0369a1, #1d4ed8); }
        .keypad {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 10px;
          margin-bottom: 14px;
        }
        .key-btn {
          background: var(--btn-bg);
          color: white;
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: 50%;
          height: 56px;
          width: 56px;
          margin: 0 auto;
          font-size: 18px;
          font-weight: bold;
          cursor: pointer;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          transition: background 0.15s, transform 0.1s;
        }
        .key-btn:hover { background: var(--btn-hover); }
        .key-btn:active { transform: scale(0.94); }
        .sub-key { font-size: 8px; color: #94a3b8; font-weight: normal; margin-top: 1px; }
        .action-row {
          display: flex;
          justify-content: space-around;
        }
        .call-btn, .end-btn {
          color: white;
          border: none;
          border-radius: 30px;
          padding: 11px 20px;
          font-size: 14px;
          font-weight: 700;
          cursor: pointer;
          flex: 1;
          margin: 0 4px;
        }
        .call-btn { background: var(--call-green); }
        .end-btn { background: var(--end-red); }
        .help-list {
          font-size: 11px;
          color: #94a3b8;
          margin-top: 12px;
          line-height: 1.4;
          background: rgba(0,0,0,0.2);
          padding: 8px 12px;
          border-radius: 8px;
        }
      </style>
    </head>
    <body>
      <div class="phone-wrapper">
        <div class="header-title">
          <h3>SVKM's NMIMS Global University</h3>
          <p>Dhule Campus • Voice Assistant IVR</p>
        </div>

        <!-- Language Selector Bar -->
        <div class="lang-bar">
          <button class="lang-btn active" id="langBtnEn" onclick="switchLanguage('en')">🇬🇧 English</button>
          <button class="lang-btn" id="langBtnHi" onclick="switchLanguage('hi')">🇮🇳 हिन्दी</button>
          <button class="lang-btn" id="langBtnMr" onclick="switchLanguage('mr')">🚩 मराठी</button>
        </div>

        <div class="screen" id="callScreen">
          <div class="screen-title" id="screenTitle">Call Status: Idle</div>
          <div class="screen-log sys" id="initialScreenLog">Click "Start Call" to dial the NMIMS Dhule assistant...</div>
        </div>

        <button class="ai-direct-btn" id="aiDirectBtn" onclick="pressKey('5')">
          🤖 Talk to AI Voice Assistant (Press 5)
        </button>

        <div class="speech-box">
          <input type="text" id="voiceQuestion" class="speech-input" placeholder="Ask AI (e.g. Do you have Computer Engineering?)" disabled />
          <button id="micBtn" class="mic-btn" onclick="toggleMic()" title="Speak with microphone" disabled>🎙️ Mic</button>
          <button id="sendSpeechBtn" class="speech-btn" onclick="sendSpeech()" disabled>Ask</button>
        </div>

        <div class="chips-container" id="sampleChips">
          <!-- Dynamically populated per language -->
        </div>

        <div class="keypad">
          <button class="key-btn" onclick="pressKey('1')">1<span class="sub-key" id="subKey1">INFO / ENG</span></button>
          <button class="key-btn" onclick="pressKey('2')">2<span class="sub-key" id="subKey2">ADMIS / PHARM</span></button>
          <button class="key-btn" onclick="pressKey('3')">3<span class="sub-key" id="subKey3">EXAM / COMM</span></button>
          <button class="key-btn" onclick="pressKey('4')">4<span class="sub-key" id="subKey4">COURSES</span></button>
          <button class="key-btn" onclick="pressKey('5')">5<span class="sub-key" id="subKey5">AI BOT</span></button>
          <button class="key-btn" onclick="pressKey('6')">6<span class="sub-key" id="subKey6">LANG / भाषा</span></button>
          <button class="key-btn" onclick="pressKey('7')">7<span class="sub-key">PQRS</span></button>
          <button class="key-btn" onclick="pressKey('8')">8<span class="sub-key">TUV</span></button>
          <button class="key-btn" onclick="pressKey('9')">9<span class="sub-key" id="subKey9">MAIN MENU</span></button>
          <button class="key-btn" onclick="pressKey('*')">*<span class="sub-key"></span></button>
          <button class="key-btn" onclick="pressKey('0')">0<span class="sub-key">+</span></button>
          <button class="key-btn" onclick="pressKey('#')">#<span class="sub-key"></span></button>
        </div>

        <div class="action-row">
          <button class="call-btn" id="startCallBtn" onclick="startCall()">📞 Start Call</button>
          <button class="end-btn" id="endCallBtn" onclick="endCall()" disabled>🛑 End Call</button>
        </div>

        <div class="help-list" id="helpList">
          <b>Main Menu:</b> 1: Info | 2: Admissions | 3: Exams | 4: Courses | 5: AI Assistant | 6: Language<br>
          <b>Language Options:</b> 1: English | 2: Hindi (हिंदी) | 3: Marathi (मराठी)
        </div>
      </div>

      <script>
        let callActive = false;
        let inSubMenu = false;
        let inLangMenu = false;
        let isRecording = false;
        let recognition = null;
        let hangupTimer = null;
        let currentLang = 'en';

        const screen = document.getElementById("callScreen");
        const speechInput = document.getElementById("voiceQuestion");
        const speechBtn = document.getElementById("sendSpeechBtn");
        const micBtn = document.getElementById("micBtn");
        const startBtn = document.getElementById("startCallBtn");
        const endBtn = document.getElementById("endCallBtn");
        const sampleChipsContainer = document.getElementById("sampleChips");

        const localizedPresets = {
          en: [
            { label: "🎓 Computer Engg", text: "Do you have Computer Engineering?" },
            { label: "💊 Pharmacy", text: "Does NMIMS Dhule have pharmacy?" },
            { label: "💻 BCA", text: "Do you offer BCA?" },
            { label: "🌐 Website", text: "What is the official website?" },
            { label: "🔊 Pronounce Website", text: "How do you pronounce the official website svkmnmimsgu.ac.in?" },
            { label: "❓ Fee Policy", text: "What is the fee for B.Tech?" }
          ],
          hi: [
            { label: "🎓 कंप्यूटर इंजीनियरिंग", text: "क्या आपके पास कंप्यूटर इंजीनियरिंग है?" },
            { label: "💊 फार्मेसी कोर्स", text: "क्या एनएमआईएमएस धुले में फार्मेसी है?" },
            { label: "💻 बीसीए कोर्स", text: "क्या आप बीसीए प्रदान करते हैं?" },
            { label: "🌐 आधिकारिक वेबसाइट", text: "कॉलेज की आधिकारिक वेबसाइट क्या है?" },
            { label: "🔊 वेबसाइट का उच्चारण", text: "वेबसाइट svkmnmimsgu.ac.in का सही उच्चारण क्या है?" },
            { label: "❓ फीस की जानकारी", text: "बी.टेक की फीस क्या है?" }
          ],
          mr: [
            { label: "🎓 कॉम्प्युटर इंजिनिअरिंग", text: "धुळे कॅम्पसमध्ये कॉम्प्युटर इंजिनिअरिंग आहे का?" },
            { label: "💊 फार्मसी अभ्यासक्रम", text: "एनएमआयएमएस धुळे येथे फार्मसी आहे का?" },
            { label: "💻 बीसीए अभ्यासक्रम", text: "आपण बीसीए अभ्यासक्रम चालवता का?" },
            { label: "🌐 अधिकृत संकेतस्थळ", text: "अधिकृत संकेतस्थळ कोणते आहे?" },
            { label: "🔊 संकेतस्थळ उच्चार", text: "संकेतस्थळ svkmnmimsgu.ac.in चा योग्य उच्चार काय आहे?" },
            { label: "❓ फी विषयी माहिती", text: "बी.टेक ची फी किती आहे?" }
          ]
        };

        function renderChips() {
          sampleChipsContainer.innerHTML = "";
          const list = localizedPresets[currentLang] || localizedPresets.en;
          list.forEach(p => {
            const btn = document.createElement("button");
            btn.className = "chip";
            btn.textContent = p.label;
            btn.onclick = () => askPreset(p.text);
            sampleChipsContainer.appendChild(btn);
          });
        }
        renderChips();

        function updateUiLanguage(lang) {
          currentLang = lang;
          document.getElementById("langBtnEn").classList.toggle("active", lang === 'en');
          document.getElementById("langBtnHi").classList.toggle("active", lang === 'hi');
          document.getElementById("langBtnMr").classList.toggle("active", lang === 'mr');

          if (recognition) {
            recognition.lang = (lang === 'hi') ? 'hi-IN' : (lang === 'mr' ? 'mr-IN' : 'en-IN');
          }

          if (lang === 'hi') {
            speechInput.placeholder = "एआई से पूछें (उदा. क्या आपके पास कंप्यूटर इंजीनियरिंग है?)";
            document.getElementById("aiDirectBtn").textContent = "🤖 एआई सहायक से बात करें (दबाएं 5)";
            document.getElementById("subKey1").textContent = "जानकारी / इंजी";
            document.getElementById("subKey2").textContent = "प्रवेश / फार्म";
            document.getElementById("subKey3").textContent = "परीक्षा / कॉम";
            document.getElementById("subKey4").textContent = "पाठ्यक्रम";
            document.getElementById("subKey5").textContent = "एआई बॉट";
            document.getElementById("subKey6").textContent = "भाषा बदलें";
            document.getElementById("subKey9").textContent = "मुख्य मेनू";
            document.getElementById("helpList").innerHTML = "<b>मुख्य मेनू:</b> 1: जानकारी | 2: प्रवेश | 3: परीक्षा | 4: पाठ्यक्रम | 5: एआई | 6: भाषा<br><b>भाषा विकल्प:</b> 1: English | 2: हिन्दी | 3: मराठी";
          } else if (lang === 'mr') {
            speechInput.placeholder = "एआई ला विचारा (उदा. धुळे कॅम्पसमध्ये बीसीए आहे का?)";
            document.getElementById("aiDirectBtn").textContent = "🤖 एआई सहाय्यकाशी बोला (दाबा 5)";
            document.getElementById("subKey1").textContent = "माहिती / इंजी";
            document.getElementById("subKey2").textContent = "प्रवेश / फार्म";
            document.getElementById("subKey3").textContent = "परीक्षा / कॉम";
            document.getElementById("subKey4").textContent = "अभ्यासक्रम";
            document.getElementById("subKey5").textContent = "एआई बॉट";
            document.getElementById("subKey6").textContent = "भाषा बदला";
            document.getElementById("subKey9").textContent = "मुख्य मेनू";
            document.getElementById("helpList").innerHTML = "<b>मुख्य मेनू:</b> 1: माहिती | 2: प्रवेश | 3: परीक्षा | 4: अभ्यासक्रम | 5: एआई | 6: भाषा<br><b>भाषा पर्याय:</b> 1: English | 2: हिन्दी | 3: मराठी";
          } else {
            speechInput.placeholder = "Ask AI (e.g. Do you have Computer Engineering?)";
            document.getElementById("aiDirectBtn").textContent = "🤖 Talk to AI Voice Assistant (Press 5)";
            document.getElementById("subKey1").textContent = "INFO / ENG";
            document.getElementById("subKey2").textContent = "ADMIS / PHARM";
            document.getElementById("subKey3").textContent = "EXAM / COMM";
            document.getElementById("subKey4").textContent = "COURSES";
            document.getElementById("subKey5").textContent = "AI BOT";
            document.getElementById("subKey6").textContent = "LANG / भाषा";
            document.getElementById("subKey9").textContent = "MAIN MENU";
            document.getElementById("helpList").innerHTML = "<b>Main Menu:</b> 1: Info | 2: Admissions | 3: Exams | 4: Courses | 5: AI Assistant | 6: Language<br><b>Language Options:</b> 1: English | 2: Hindi (हिंदी) | 3: Marathi (मराठी)";
          }

          renderChips();
        }

        async function switchLanguage(lang) {
          updateUiLanguage(lang);
          if (callActive) {
            log("Language switched to: " + (lang === 'hi' ? 'हिन्दी (Hindi)' : (lang === 'mr' ? 'मराठी (Marathi)' : 'English')), "sys");
            inLangMenu = false;
            inSubMenu = false;
            try {
              const res = await fetch("/voice/incoming?lang=" + encodeURIComponent(lang), { method: "POST" });
              const xmlText = await res.text();
              parseAndPlayTwiML(xmlText);
            } catch(err) {
              log("Language switch error: " + err, "sys");
            }
          }
        }

        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
          const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
          recognition = new SpeechRec();
          recognition.continuous = false;
          recognition.interimResults = false;
          recognition.lang = 'en-IN';

          recognition.onstart = function() {
            isRecording = true;
            micBtn.classList.add("recording");
            micBtn.textContent = "🛑 Stop";
            log("🎙️ Listening to your voice... Speak now!", "sys");
          };

          recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            speechInput.value = transcript;
            sendSpeech();
          };

          recognition.onerror = function(event) {
            log("Microphone notice: " + (event.error || "error"), "sys");
            isRecording = false;
            micBtn.classList.remove("recording");
            micBtn.textContent = "🎙️ Mic";
          };

          recognition.onend = function() {
            isRecording = false;
            micBtn.classList.remove("recording");
            micBtn.textContent = "🎙️ Mic";
          };
        }

        function toggleMic() {
          if (!callActive) {
            alert("Please start the call first.");
            return;
          }
          if (!recognition) {
            alert("Microphone speech recognition is not supported in this browser. You can type in the input box!");
            return;
          }
          if (isRecording) {
            recognition.stop();
          } else {
            recognition.lang = (currentLang === 'hi') ? 'hi-IN' : (currentLang === 'mr' ? 'mr-IN' : 'en-IN');
            recognition.start();
          }
        }

        function log(msg, type) {
          const div = document.createElement("div");
          div.className = "screen-log " + type;
          div.textContent = msg;
          screen.appendChild(div);
          screen.scrollTop = screen.scrollHeight;
        }

        async function startCall() {
          callActive = true;
          inSubMenu = false;
          inLangMenu = false;
          screen.innerHTML = '<div class="screen-title">Call Status: Connected (00:01)</div>';
          log("Dialing SVKM's NMIMS Global University, Dhule...", "sys");
          startBtn.disabled = true;
          endBtn.disabled = false;
          speechInput.disabled = false;
          speechBtn.disabled = false;
          if (micBtn) micBtn.disabled = false;

          try {
            const res = await fetch("/voice/incoming?lang=" + encodeURIComponent(currentLang), { method: "POST" });
            const xmlText = await res.text();
            parseAndPlayTwiML(xmlText);
          } catch(err) {
            log("Connection error: " + err, "sys");
          }
        }

        async function pressKey(digit) {
          if (!callActive) {
            await startCall();
            await new Promise(r => setTimeout(r, 600));
          }
          log("Pressed: " + digit, "user");

          let targetUrl = "/voice/menu?lang=" + encodeURIComponent(currentLang);
          let postBody = "Digits=" + encodeURIComponent(digit) + "&lang=" + encodeURIComponent(currentLang);

          if (inLangMenu) {
            targetUrl = "/voice/language";
            inLangMenu = false;
            let newLang = 'en';
            if (digit === '2') newLang = 'hi';
            else if (digit === '3') newLang = 'mr';
            
            updateUiLanguage(newLang);
            log("Selected language: " + (newLang === 'hi' ? 'हिन्दी (Hindi)' : (newLang === 'mr' ? 'मराठी (Marathi)' : 'English')), "sys");
            postBody = "Digits=" + encodeURIComponent(digit) + "&lang=" + encodeURIComponent(newLang);
          } else if (inSubMenu && digit !== '5' && digit !== '9') {
            targetUrl = "/voice/courses_menu?lang=" + encodeURIComponent(currentLang);
          }

          try {
            const res = await fetch(targetUrl, {
              method: "POST",
              headers: { "Content-Type": "application/x-www-form-urlencoded" },
              body: postBody
            });
            const xmlText = await res.text();
            parseAndPlayTwiML(xmlText);
          } catch(err) {
            log("Keypad error: " + err, "sys");
          }
        }

        async function askPreset(text) {
          if (!callActive) {
            await startCall();
            await new Promise(r => setTimeout(r, 600));
          }
          speechInput.value = text;
          sendSpeech();
        }

        async function sendSpeech() {
          const text = speechInput.value.trim();
          if (!text) return;
          if (!callActive) {
            await startCall();
            await new Promise(r => setTimeout(r, 600));
          }
          log("Caller: " + text, "user");
          speechInput.value = "";

          try {
            const res = await fetch("/voice/process", {
              method: "POST",
              headers: { "Content-Type": "application/x-www-form-urlencoded" },
              body: "SpeechResult=" + encodeURIComponent(text) + "&lang=" + encodeURIComponent(currentLang)
            });
            const xmlText = await res.text();
            parseAndPlayTwiML(xmlText);
          } catch(err) {
            log("Speech error: " + err, "sys");
          }
        }

        speechInput.addEventListener("keypress", function(e) {
          if (e.key === "Enter") sendSpeech();
        });

        function sanitizeForSpeech(text, lang) {
          if (!text) return "";
          let spoken = text;
          const l = (lang || "").toLowerCase();

          if (l.startsWith("hi")) {
            spoken = spoken.replace(/https?:\/\/(www\.)?svkmnmimsn?gu\.ac\.in\/?/gi, " एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन ");
            spoken = spoken.replace(/svkmnmimsn?gu\.ac\.in\s*\([^)]*\)/gi, " एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन ");
            spoken = spoken.replace(/svkmnmimsn?gu\.ac\.in/gi, " एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन ");
          } else if (l.startsWith("mr")) {
            spoken = spoken.replace(/https?:\/\/(www\.)?svkmnmimsn?gu\.ac\.in\/?/gi, " एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन ");
            spoken = spoken.replace(/svkmnmimsn?gu\.ac\.in\s*\([^)]*\)/gi, " एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन ");
            spoken = spoken.replace(/svkmnmimsn?gu\.ac\.in/gi, " एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन ");
          } else {
            spoken = spoken.replace(/svkmnmimsn?gu\.ac\.in\s*,?\s*\(?pronounced as\s+[^)]+\)?/gi, " S V K M, N M I M S, S N G U, dot A C, dot I N ");
            spoken = spoken.replace(/https?:\/\/(www\.)?svkmnmimsn?gu\.ac\.in\/?/gi, " S V K M, N M I M S, S N G U, dot A C, dot I N ");
            spoken = spoken.replace(/svkmnmimsn?gu\.ac\.in\s*\([^)]*\)/gi, " S V K M, N M I M S, S N G U, dot A C, dot I N ");
            spoken = spoken.replace(/svkmnmimsn?gu\.ac\.in/gi, " S V K M, N M I M S, S N G U, dot A C, dot I N ");
          }
          return spoken.replace(/\s+/g, " ").trim();
        }

        function parseAndPlayTwiML(xml) {
          if (hangupTimer) {
            clearTimeout(hangupTimer);
            hangupTimer = null;
          }

          if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
          }

          const parser = new DOMParser();
          const doc = parser.parseFromString(xml, "application/xml");
          
          const gather = doc.querySelector("Gather");
          const sayTagsToSpeak = [];

          if (gather) {
            const allSayTags = Array.from(doc.querySelectorAll("Say"));
            for (const say of allSayTags) {
              if (gather.contains(say) || (say.compareDocumentPosition(gather) & Node.DOCUMENT_POSITION_FOLLOWING)) {
                sayTagsToSpeak.push(say);
              }
            }
          } else {
            sayTagsToSpeak.push(...Array.from(doc.querySelectorAll("Say")));
          }

          sayTagsToSpeak.forEach(tag => {
            const msg = tag.textContent.trim();
            const tagLang = tag.getAttribute("language") || (currentLang === 'hi' ? 'hi-IN' : (currentLang === 'mr' ? 'mr-IN' : 'en-IN'));
            if (msg) {
              log("IVR: " + msg, "bot");
              if ('speechSynthesis' in window) {
                const spokenText = sanitizeForSpeech(msg, tagLang);
                const utterance = new SpeechSynthesisUtterance(spokenText);
                utterance.lang = tagLang;
                utterance.rate = 0.95;
                window.speechSynthesis.speak(utterance);
              }
            }
          });

          if (gather) {
            const action = gather.getAttribute("action") || "";
            inSubMenu = action.includes("courses_menu");
            inLangMenu = action.includes("language");

            speechInput.disabled = false;
            speechBtn.disabled = false;
            if (micBtn) micBtn.disabled = false;

            const input = gather.getAttribute("input") || "";
            if (input.includes("speech")) {
              speechInput.focus();
              log("🤖 AI Assistant is listening. Speak into mic or type above.", "sys");
            } else if (inLangMenu) {
              log("🌐 Select language: 1 for English, 2 for Hindi, 3 for Marathi.", "sys");
            } else {
              log("📞 Awaiting keypad selection (1–6) or ask question above.", "sys");
            }
          } else {
            if (doc.querySelector("Hangup")) {
              hangupTimer = setTimeout(() => {
                if (callActive) {
                  log("Call disconnected.", "sys");
                  endCall(false);
                }
              }, 4000);
            }
          }
        }

        function endCall(userInitiated = true) {
          if (hangupTimer) {
            clearTimeout(hangupTimer);
            hangupTimer = null;
          }
          if (isRecording && recognition) {
            recognition.stop();
          }
          callActive = false;
          inSubMenu = false;
          inLangMenu = false;
          speechInput.disabled = true;
          speechBtn.disabled = true;
          if (micBtn) micBtn.disabled = true;
          startBtn.disabled = false;
          endBtn.disabled = true;
          if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
          }
          if (userInitiated) {
            log("Call ended by user.", "sys");
          }
        }

        document.addEventListener("keydown", function(e) {
          if (document.activeElement === speechInput) return;
          if (['0','1','2','3','4','5','6','7','8','9','*','#'].includes(e.key)) {
            pressKey(e.key);
          }
        });
      </script>
    </body>
    </html>
    """
    return render_template_string(html_template)


@voice_bp.route("/test/ivr/simulate", methods=["POST"])
def simulate_ivr():
    """
    Programmatic simulation API for testing NMIMS Dhule IVR with multilingual support.
    """
    data = request.get_json(force=True, silent=True) or {}
    action = data.get("action", "incoming")
    lang = data.get("lang", "en")

    if action == "incoming":
        name = "SVKM's NMIMS Global University, Dhule"
        if lang == "hi":
            msg = f"एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले में आपका स्वागत है। कॉलेज जानकारी के लिए 1 दबाएं। प्रवेश के लिए 2 दबाएं। परीक्षा के लिए 3 दबाएं। पाठ्यक्रम के लिए 4 दबाएं। एआई सहायक के लिए 5 दबाएं। भाषा के लिए 6 दबाएं।"
        elif lang == "mr":
            msg = f"एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे मध्ये आपले स्वागत आहे. माहितीसाठी 1 दाबा. प्रवेशासाठी 2 दाबा. परीक्षेसाठी 3 दाबा. अभ्यासक्रमासाठी 4 दाबा. एआई साठी 5 दाबा. भाषेसाठी 6 दाबा."
        else:
            msg = f"Welcome to {name}. Press 1 for College Information. Press 2 for Admission Information. Press 3 for Examination Information. Press 4 for Courses and Departments. Press 5 to talk to our AI Assistant. Press 6 for Language Options."
        return jsonify({
            "status": "success",
            "step": "welcome_menu",
            "lang": lang,
            "message": msg,
            "options": {"1": "College Info", "2": "Admission", "3": "Exams", "4": "Courses Sub-Menu", "5": "AI Assistant", "6": "Language"}
        })

    elif action == "language":
        digit = str(data.get("digit", "1"))
        lang_map = {"1": "en", "2": "hi", "3": "mr"}
        selected_lang = lang_map.get(digit, "en")
        return jsonify({
            "status": "success",
            "step": "language_selected",
            "selected_lang": selected_lang
        })

    elif action == "menu":
        digit = str(data.get("digit", "1"))
        if digit == "1":
            return jsonify({
                "status": "success",
                "step": "information",
                "category": "college_info",
                "lang": lang,
                "response": college_data_service.get_speech_summary("college_info", lang=lang)
            })
        elif digit == "2":
            return jsonify({
                "status": "success",
                "step": "information",
                "category": "admission",
                "lang": lang,
                "response": college_data_service.get_speech_summary("admission", lang=lang)
            })
        elif digit == "3":
            return jsonify({
                "status": "success",
                "step": "information",
                "category": "examination",
                "lang": lang,
                "response": college_data_service.get_speech_summary("examination", lang=lang)
            })
        elif digit == "4":
            return jsonify({
                "status": "success",
                "step": "courses_submenu",
                "lang": lang,
                "message": "Press 1 for Engineering courses. Press 2 for Pharmacy courses. Press 3 for Commerce courses. Press 4 to return to the main menu.",
                "options": {"1": "Engineering", "2": "Pharmacy", "3": "Commerce", "4": "Main Menu"}
            })
        elif digit == "5":
            return jsonify({
                "status": "success",
                "step": "ai_greeting",
                "lang": lang,
                "response": "Hello. You are now connected to the SVKM NMIMS Global University, Dhule AI Assistant. Please ask your question."
            })
        elif digit == "6":
            return jsonify({
                "status": "success",
                "step": "language_selection",
                "message": "For English press 1. हिंदी के लिए 2 दबाएं। मराठीसाठी 3 दाबा।"
            })
        else:
            return jsonify({
                "status": "invalid_input",
                "digit": digit,
                "response": "I am sorry, that is not a valid option."
            }), 400

    elif action == "courses_menu":
        digit = str(data.get("digit", "1"))
        categories = {"1": "courses_engineering", "2": "courses_pharmacy", "3": "courses_commerce"}
        if digit in categories:
            return jsonify({
                "status": "success",
                "step": "courses_detail",
                "category": categories[digit],
                "lang": lang,
                "response": college_data_service.get_speech_summary(categories[digit], lang=lang)
            })
        elif digit in ("4", "9"):
            return jsonify({
                "status": "success",
                "step": "returned_to_main_menu",
                "lang": lang
            })
        else:
            return jsonify({"status": "invalid_input", "digit": digit}), 400

    elif action in ("process", "ai"):
        user_query = data.get("query", "")
        answer = ai_service.answer_question(user_query, lang=lang)
        return jsonify({
            "status": "success",
            "step": "ai_response",
            "lang": lang,
            "query": user_query,
            "response": answer,
            "follow_up": "Would you like to ask another question? Please speak your question, or press 9 to return to the main menu."
        })

    return jsonify({"error": f"Unknown simulation action '{action}'"}), 400
