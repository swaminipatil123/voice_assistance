# SVKM's NMIMS Global University, Dhule — AI Voice Assistant with IVR

An AI-powered telephone Interactive Voice Response (IVR) assistant customized specifically for **SVKM's NMIMS Global University, Dhule, Maharashtra, India**. 

Students can call the university phone number, navigate the IVR menu using their mobile keypad (DTMF), explore courses across all three Dhule schools, or connect directly to an AI voice receptionist powered by Google Gemini to ask spoken questions in natural language.

> **IMPORTANT CAMPUS NOTICE:**  
> This assistant represents **ONLY** the **Dhule Campus** of SVKM's NMIMS Global University (located on the Mumbai-Agra National Highway, Dhule). It is strictly isolated from NMIMS Shirpur / Mukesh Patel Technology Park, Babulde, or any other campus.

---

## 1. Official University Source & Identity

* **Institution:** SVKM's NMIMS Global University, Dhule
* **Location:** Survey No. 499, Plot No 01, 02 & 03 Behind Gurudwara, Mumbai-Agra National Highway, Dhule - 424001, Maharashtra, India
* **Primary Official Website:** [https://www.svkmnmimsngu.ac.in/](https://www.svkmnmimsgu.ac.in/) (spoken letter-by-letter as `S V K M, N M I M S,S N G U, dot A C, dot I N`)
* **Schools on Campus:**
  1. **School of Technology, Management & Engineering (STME)**
  2. **School of Pharmacy & Technology Management (SPTM)**
  3. **School of Commerce (SOC)**

---

## 2. Features

* **Real Phone Call Support:** Integrates with standard telephony providers (Twilio, Exotel, Plivo) using standard TwiML/voice webhooks.
* **5-Option DTMF Main IVR Menu:**
  * **Press 1:** College Information (Dhule campus location, overview, official website)
  * **Press 2:** Admission Information (admission portal registration process and guidelines)
  * **Press 3:** Examination Information (examination schedules, notifications on portal)
  * **Press 4:** Courses & Departments (opens school-specific sub-menu)
  * **Press 5:** AI Voice Assistant (natural conversational voice queries)
  * **Press 9:** Return to main menu at any time
* **Courses Sub-Menu (Option 4):**
  * **Press 1:** Engineering courses (STME)
  * **Press 2:** Pharmacy courses (SPTM)
  * **Press 3:** Commerce courses (SOC)
  * **Press 4:** Return to main menu
* **AI Voice Assistant:**
  * Identifies as: *"SVKM NMIMS Global University, Dhule AI Assistant"*
  * Grounded exclusively in verified Dhule datasets (`data/*.json`).
  * Strict zero-hallucination policy for unverified questions (fees, cutoffs, specific dates, HOD names, etc.).
* **SQLite Call Logging:** Records call sessions and conversation transcripts in `college_voice.db`.
* **Interactive Local Phone Simulator (`/test/ivr`):** Graphical keypad dialer with live speech recognition and voice synthesis for testing in your web browser.

---

## 3. Academic Structure (Dhule Campus)

### School of Technology, Management & Engineering (STME)
* **B.Tech Programs:**
  * B.Tech Civil Engineering
  * B.Tech Computer Engineering
  * B.Tech Computer Science & Engineering — AI & ML
  * B.Tech Computer Science & Engineering — Data Science
  * B.Tech Electrical Engineering
  * B.Tech Information Technology
  * B.Tech Mechanical Engineering
* **Dual Degree Programs (B.Tech + MBA):**
  * B.Tech + MBA — Computer Engineering
  * B.Tech + MBA — Computer Science & Engineering — AI & ML
  * B.Tech + MBA — Computer Science & Engineering — Data Science
  * B.Tech + MBA — Information Technology
* **Postgraduate:**
  * Master of Computer Applications (MCA)
  * M.Tech Civil Engineering
  * M.Tech Computer Engineering
  * M.Tech Electrical Engineering
  * M.Tech Information Technology
  * M.Tech Mechanical Engineering
* **Doctoral:**
  * Ph.D. in Technology / Engineering

### School of Pharmacy & Technology Management (SPTM)
* **Diploma:**
  * D.Pharm — Diploma in Pharmacy
* **Undergraduate:**
  * B.Pharm — Bachelor of Pharmacy
  * B.Pharm + MBA — Pharma Tech
  * B.Tech — Cosmetic Technology
* **Postgraduate:**
  * M.Pharm — Pharmaceutics
  * M.Pharm — Pharmaceutical Quality Assurance
  * M.Pharm — Pharmacology
  * M.Pharm — Pharmaceutical Chemistry
* **Doctoral:**
  * Ph.D. in Pharmaceutical Sciences

### School of Commerce (SOC)
* **Undergraduate:**
  * Bachelor of Business Administration (BBA)
  * Bachelor in Computer Applications (BCA)

---

## 4. Structured College Datasets (`data/`)

Every data file contains source metadata verified against the official university portal:
* [`data/university.json`](file:///c:/Users/swami/OneDrive/Desktop/voice_assistance/data/university.json): University identity, campus location, official website.
* [`data/engineering.json`](file:///c:/Users/swami/OneDrive/Desktop/voice_assistance/data/engineering.json): All B.Tech, Dual Degree, MCA, M.Tech, and Ph.D. programs with contact numbers.
* [`data/pharmacy.json`](file:///c:/Users/swami/OneDrive/Desktop/voice_assistance/data/pharmacy.json): D.Pharm, B.Pharm, Pharma Tech, Cosmetic Tech, M.Pharm, and Ph.D.
* [`data/commerce.json`](file:///c:/Users/swami/OneDrive/Desktop/voice_assistance/data/commerce.json): BBA and BCA program details with contact numbers.
* [`data/contact.json`](file:///c:/Users/swami/OneDrive/Desktop/voice_assistance/data/contact.json): School-wise phone numbers, full address, and directions.
* [`data/admission.json`](file:///c:/Users/swami/OneDrive/Desktop/voice_assistance/data/admission.json): Official admission portal registration workflow.
* [`data/examination.json`](file:///c:/Users/swami/OneDrive/Desktop/voice_assistance/data/examination.json): Academic calendar and examination portal notice guidelines.
* [`data/faq.json`](file:///c:/Users/swami/OneDrive/Desktop/voice_assistance/data/faq.json): Verified answers to top questions.

---

## 5. How to Run Locally

### 1. Start the Flask Server:
```powershell
.\venv\Scripts\python.exe backend/app.py
```

### 2. Verify Health Status:
```powershell
curl http://127.0.0.1:5000/health
```

### 3. Open the Interactive Phone Simulator:
Navigate to:
```text
http://127.0.0.1:5000/test/ivr
```
* **Language Selection**:
  * Use the top language selector bar: **🇬🇧 English**, **🇮🇳 हिन्दी**, or **🚩 मराठी** to switch speech recognition and voice narration.
  * Or on the IVR keypad, press **6** to enter the Language Selection menu (1: English, 2: Hindi, 3: Marathi).
* Click **"📞 Start Call"**
* Use keypad:
  * Press **1** for Dhule Campus Information (in selected language)
  * Press **2** for Admission Information (in selected language)
  * Press **3** for Examination Information (in selected language)
  * Press **4** to open the **Courses Sub-Menu** (1: Engineering, 2: Pharmacy, 3: Commerce, 4: Back)
  * Press **5** to enter the **AI Voice Assistant**
  * Press **6** to change the **Language / भाषा** (English, Hindi, Marathi)
* In AI mode:
  * **English**: Ask *"Do you offer B.Tech in Computer Engineering?"*, *"What is the admission helpline?"*
  * **हिन्दी**: Ask *"धुले कैंपस में कौन से कोर्सेज हैं?"*, *"एडमिशन के लिए फोन नंबर क्या है?"*
  * **मराठी**: Ask *"धुळे कॅम्पसमध्ये बी फार्मसी आहे का?"*, *"प्रवेशासाठी अधिकृत संपर्क क्रमांक काय आहे?"*
* Click **"🛑 End Call"** to hang up.

---

## 6. Automated Testing

Run the full Pytest suite covering all AI queries, IVR sub-menus, and multilingual capabilities:
```powershell
.\venv\Scripts\python.exe -m pytest tests -v
```

All 35 tests pass cleanly in ~1 second.

---

## 7. Connecting a Real Phone Number (Twilio / Exotel / Plivo)

1. Expose the local server via ngrok:
   ```bash
   ngrok http 5000
   ```
2. Log in to your Twilio Console -> **Phone Numbers** -> **Active Numbers** -> click your phone number.
3. Under **Voice Configuration**:
   * **A CALL COMES IN:** Select `Webhook`
   * **URL:** `https://your-ngrok-subdomain.ngrok-free.app/voice/incoming`
   * **HTTP Method:** `HTTP POST`
4. Click **Save**.
5. Dial the number from your mobile phone to experience the live IVR and voice assistant!
