import pytest
from backend.services.ai_service import ai_service

# --------------------------------------------------------------------------
# General University Tests
# --------------------------------------------------------------------------

def test_q1_university_name():
    ans = ai_service.answer_question("What is the name of the university?")
    assert "SVKM" in ans
    assert "NMIMS" in ans
    assert "Dhule" in ans

def test_q2_where_is_nmims_dhule():
    ans = ai_service.answer_question("Where is NMIMS Dhule?")
    assert "Dhule" in ans
    assert any(term in ans for term in ["Maharashtra", "Highway", "Survey"])

def test_q3_official_website():
    ans = ai_service.answer_question("What is the official website?")
    assert "svkmnmimsgu.ac.in" in ans

# --------------------------------------------------------------------------
# Engineering (STME) Tests
# --------------------------------------------------------------------------

def test_q4_engineering_courses_available():
    ans = ai_service.answer_question("What engineering courses are available?")
    assert "Civil" in ans
    assert "Computer" in ans
    assert "Mechanical" in ans

def test_q5_do_you_have_computer_engineering():
    ans = ai_service.answer_question("Do you have Computer Engineering?")
    assert "Computer Engineering" in ans

def test_q6_do_you_have_ai_and_machine_learning():
    ans = ai_service.answer_question("Do you have AI and Machine Learning?")
    assert "AI and Machine Learning" in ans or "AI & ML" in ans

def test_q7_is_data_science_available():
    ans = ai_service.answer_question("Is Data Science available?")
    assert "Data Science" in ans

def test_q8_is_information_technology_available():
    ans = ai_service.answer_question("Is Information Technology available?")
    assert "Information Technology" in ans

def test_q9_do_you_offer_mca():
    ans = ai_service.answer_question("Do you offer MCA?")
    assert "MCA" in ans or "Master of Computer Applications" in ans

def test_q10_what_mtech_programs_are_available():
    ans = ai_service.answer_question("What M.Tech programs are available?")
    assert "Civil" in ans
    assert "Computer" in ans
    assert "Mechanical" in ans

# --------------------------------------------------------------------------
# Pharmacy (SPTM) Tests
# --------------------------------------------------------------------------

def test_q11_does_nmims_dhule_have_pharmacy():
    ans = ai_service.answer_question("Does NMIMS Dhule have pharmacy?")
    assert "School of Pharmacy" in ans or "D.Pharm" in ans or "B.Pharm" in ans

def test_q12_what_is_bpharm():
    ans = ai_service.answer_question("What is B.Pharm?")
    assert "Bachelor of Pharmacy" in ans

def test_q13_do_you_have_dpharm():
    ans = ai_service.answer_question("Do you have D.Pharm?")
    assert "D.Pharm" in ans
    assert "Diploma in Pharmacy" in ans

def test_q14_do_you_offer_mpharm():
    ans = ai_service.answer_question("Do you offer M.Pharm?")
    assert "Pharmaceutics" in ans
    assert "Pharmacology" in ans

def test_q15_is_cosmetic_technology_available():
    ans = ai_service.answer_question("Is Cosmetic Technology available?")
    assert "Cosmetic Technology" in ans

def test_q16_phd_pharmaceutical_sciences():
    ans = ai_service.answer_question("Is there a Ph.D. in Pharmaceutical Sciences?")
    assert "Ph.D." in ans
    assert "Pharmaceutical Sciences" in ans

# --------------------------------------------------------------------------
# Commerce (SOC) Tests
# --------------------------------------------------------------------------

def test_q17_do_you_have_bba():
    ans = ai_service.answer_question("Do you have BBA?")
    assert "BBA" in ans or "Business Administration" in ans

def test_q18_do_you_have_bca():
    ans = ai_service.answer_question("Do you have BCA?")
    assert "BCA" in ans or "Computer Applications" in ans

def test_q19_which_courses_are_available_in_commerce():
    ans = ai_service.answer_question("Which courses are available in Commerce?")
    assert "BBA" in ans
    assert "BCA" in ans

# --------------------------------------------------------------------------
# Unknown / Unverified Information Tests (Zero Hallucination)
# --------------------------------------------------------------------------

def test_q20_fees_unknown_no_hallucination():
    ans = ai_service.answer_question("What is the fee for B.Tech Computer Engineering?")
    assert "don't have verified information" in ans.lower()
    assert "svkmnmimsgu.ac.in" in ans.lower() or "website" in ans.lower() or "contact" in ans.lower()

def test_q21_hod_name_unknown_no_hallucination():
    ans = ai_service.answer_question("Who is the current HOD?")
    assert "don't have verified information" in ans.lower()

def test_q22_tomorrow_exam_unknown_no_hallucination():
    ans = ai_service.answer_question("What is tomorrow's exam?")
    assert "don't have verified information" in ans.lower()

def test_q23_exact_placement_percentage_unknown_no_hallucination():
    ans = ai_service.answer_question("What is the exact placement percentage?")
    assert "don't have verified information" in ans.lower()

def test_q24_website_pronunciation():
    from backend.services.text_to_speech import sanitize_for_speech
    
    # Check AI question response for user prompt
    ans_pron = ai_service.answer_question("it not pronounce the website of collage svkmnmimsgu.ac.in in right way so correct it")
    assert "svkmnmimsgu.ac.in" in ans_pron
    assert "S V K M, N M I M S, S N G U, dot A C, dot I N" in ans_pron

    # Check typo tolerance (svkmnmimsngu.ac.in)
    ans_typo = ai_service.answer_question("how to pronounce svkmnmimsngu.ac.in")
    assert "svkmnmimsgu.ac.in" in ans_typo
    assert "S V K M, N M I M S, S N G U, dot A C, dot I N" in ans_typo

    # Check sanitize_for_speech for TTS normalization
    en_spoken = sanitize_for_speech("The official website is svkmnmimsgu.ac.in.", lang="en")
    assert "S V K M, N M I M S, S N G U, dot A C, dot I N" in en_spoken
    assert "svkmnmimsgu" not in en_spoken

    en_spoken_ngu = sanitize_for_speech("The official website is svkmnmimsngu.ac.in.", lang="en")
    assert "S V K M, N M I M S, S N G U, dot A C, dot I N" in en_spoken_ngu
    assert "svkmnmimsngu" not in en_spoken_ngu

    hi_spoken = sanitize_for_speech("हमारी आधिकारिक वेबसाइट svkmnmimsngu.ac.in (एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन) है।", lang="hi")
    assert "एस वी के एम, एन एम आई एम एस, एस एन जी यू, डॉट एसी डॉट इन" in hi_spoken
    assert "svkmnmimsngu" not in hi_spoken

    mr_spoken = sanitize_for_speech("आमचे अधिकृत संकेतस्थळ svkmnmimsngu.ac.in आहे.", lang="mr")
    assert "एस व्ही के एम, एन एम आय एम एस, एस एन जी यू, डॉट एसी डॉट इन" in mr_spoken
    assert "svkmnmimsngu" not in mr_spoken
