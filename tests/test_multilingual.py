import pytest
from backend.app import create_app
from backend.services.ai_service import ai_service
from backend.services.college_data_service import college_data_service

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_multilingual_incoming_welcome_menus(client):
    """Test incoming call welcome menu in English, Hindi, and Marathi."""
    # English
    res_en = client.post("/voice/incoming?lang=en")
    assert res_en.status_code == 200
    xml_en = res_en.data.decode("utf-8")
    assert "Welcome to SVKM's NMIMS Global University, Dhule" in xml_en
    assert "language=\"en-IN\"" in xml_en

    # Hindi
    res_hi = client.post("/voice/incoming?lang=hi")
    assert res_hi.status_code == 200
    xml_hi = res_hi.data.decode("utf-8")
    assert "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले में आपका स्वागत है" in xml_hi
    assert "language=\"hi-IN\"" in xml_hi

    # Marathi
    res_mr = client.post("/voice/incoming?lang=mr")
    assert res_mr.status_code == 200
    xml_mr = res_mr.data.decode("utf-8")
    assert "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे मध्ये आपले स्वागत आहे" in xml_mr
    assert "language=\"mr-IN\"" in xml_mr

def test_language_selection_flow(client):
    """Test pressing 6 to open language menu and selecting Hindi or Marathi."""
    # Press 6 from main menu
    res_opt6 = client.post("/voice/menu", data={"Digits": "6"})
    assert res_opt6.status_code == 200
    xml_opt6 = res_opt6.data.decode("utf-8")
    assert "For English, press 1" in xml_opt6
    assert "हिंदी के लिए 2 दबाएं" in xml_opt6
    assert "मराठीसाठी 3 दाबा" in xml_opt6

    # Select 2 for Hindi
    res_hi_selected = client.post("/voice/language", data={"Digits": "2"})
    assert res_hi_selected.status_code == 200
    xml_hi_selected = res_hi_selected.data.decode("utf-8")
    assert "एसवीकेएम एनएमआईएमएस ग्लोबल यूनिवर्सिटी, धुले में आपका स्वागत है" in xml_hi_selected

    # Select 3 for Marathi
    res_mr_selected = client.post("/voice/language", data={"Digits": "3"})
    assert res_mr_selected.status_code == 200
    xml_mr_selected = res_mr_selected.data.decode("utf-8")
    assert "एसव्हीकेएम एनएमआयएमएस ग्लोबल युनिव्हर्सिटी, धुळे मध्ये आपले स्वागत आहे" in xml_mr_selected

def test_multilingual_menu_options(client):
    """Test IVR menu responses in Hindi and Marathi."""
    # Option 1: College Info in Hindi
    res_hi1 = client.post("/voice/menu", data={"Digits": "1", "lang": "hi"})
    assert res_hi1.status_code == 200
    xml_hi1 = res_hi1.data.decode("utf-8")
    assert "धुले परिसर" in xml_hi1
    assert "svkmnmimsgu.ac.in" in xml_hi1

    # Option 1: College Info in Marathi
    res_mr1 = client.post("/voice/menu", data={"Digits": "1", "lang": "mr"})
    assert res_mr1.status_code == 200
    xml_mr1 = res_mr1.data.decode("utf-8")
    assert "धुळे परिसर" in xml_mr1
    assert "svkmnmimsgu.ac.in" in xml_mr1

    # Option 4: Courses sub-menu in Marathi
    res_mr4 = client.post("/voice/menu", data={"Digits": "4", "lang": "mr"})
    assert res_mr4.status_code == 200
    xml_mr4 = res_mr4.data.decode("utf-8")
    assert "इंजिनिअरिंग अभ्यासक्रमांसाठी 1 दाबा" in xml_mr4

    # Option 4 -> 2: Pharmacy courses in Hindi
    res_hi_pharm = client.post("/voice/courses_menu", data={"Digits": "2", "lang": "hi"})
    assert res_hi_pharm.status_code == 200
    xml_hi_pharm = res_hi_pharm.data.decode("utf-8")
    assert "स्कूल ऑफ फार्मेसी एंड टेक्नोलॉजी मैनेजमेंट" in xml_hi_pharm

def test_multilingual_ai_service():
    """Test AI assistant queries in Hindi, Marathi, and English."""
    # Hindi query
    ans_hi = ai_service.answer_question("क्या आपके पास कंप्यूटर इंजीनियरिंग है?", lang="hi")
    assert "कंप्यूटर इंजीनियरिंग" in ans_hi

    # Marathi query
    ans_mr = ai_service.answer_question("धुळे कॅम्पसमध्ये कॉम्प्युटर इंजिनिअरिंग आहे का?", lang="mr")
    assert "कॉम्प्युटर इंजिनिअरिंग" in ans_mr

    # Unknown fee query in Hindi (Strict Zero Hallucination)
    ans_fee_hi = ai_service.answer_question("बीटेक की फीस क्या है?", lang="hi")
    assert "सत्यापित जानकारी" in ans_fee_hi

    # Unknown fee query in Marathi (Strict Zero Hallucination)
    ans_fee_mr = ai_service.answer_question("बीटेक ची फी किती आहे?", lang="mr")
    assert "पडताळलेली माहिती" in ans_fee_mr

    # English query
    ans_en = ai_service.answer_question("What is the official website?", lang="en")
    assert "svkmnmimsgu.ac.in" in ans_en
    assert "S V K M, N M I M S, S N G U, dot A C, dot I N" in ans_en

    # Hindi website pronunciation query
    ans_hi_site = ai_service.answer_question("कॉलेज की वेबसाइट का उच्चारण क्या है?", lang="hi")
    assert "svkmnmimsgu.ac.in" in ans_hi_site
    assert "एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन" in ans_hi_site

    # Marathi website pronunciation query
    ans_mr_site = ai_service.answer_question("संकेतस्थळाचा उच्चार काय आहे?", lang="mr")
    assert "svkmnmimsgu.ac.in" in ans_mr_site
    assert "एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन" in ans_mr_site
