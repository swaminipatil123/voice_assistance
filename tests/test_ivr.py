import pytest
from backend.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_voice_incoming(client):
    """Test initial incoming phone call webhook for SVKM's NMIMS Global University, Dhule."""
    response = client.post("/voice/incoming")
    assert response.status_code == 200
    assert "application/xml" in response.content_type
    xml = response.data.decode("utf-8")
    assert "<Gather" in xml
    assert "Welcome to SVKM's NMIMS Global University, Dhule" in xml
    assert "Press 1 for College Information" in xml
    assert "Press 4 for Courses and Departments" in xml
    assert "Press 5 to talk to our AI Assistant" in xml

def test_voice_menu_options(client):
    """Test main menu keypad DTMF inputs 1 to 5."""
    # Option 1: College Info
    res1 = client.post("/voice/menu", data={"Digits": "1"})
    assert res1.status_code == 200
    xml1 = res1.data.decode("utf-8")
    assert "SVKM's NMIMS Global University, Dhule" in xml1
    assert "svkmnmimsgu.ac.in" in xml1

    # Option 2: Admission Info
    res2 = client.post("/voice/menu", data={"Digits": "2"})
    assert res2.status_code == 200
    assert "Admission Information" in res2.data.decode("utf-8")

    # Option 3: Examination Info
    res3 = client.post("/voice/menu", data={"Digits": "3"})
    assert res3.status_code == 200
    assert "Examination Information" in res3.data.decode("utf-8")

    # Option 4: Courses Sub-menu
    res4 = client.post("/voice/menu", data={"Digits": "4"})
    assert res4.status_code == 200
    xml4 = res4.data.decode("utf-8")
    assert "Press 1 for Engineering courses" in xml4
    assert "Press 2 for Pharmacy courses" in xml4
    assert "Press 3 for Commerce courses" in xml4

    # Option 5: AI Assistant Greeting
    res5 = client.post("/voice/menu", data={"Digits": "5"})
    assert res5.status_code == 200
    xml5 = res5.data.decode("utf-8")
    assert "connected to the SVKM NMIMS Global University, Dhule AI Assistant" in xml5
    assert 'input="speech"' in xml5

def test_courses_sub_menu(client):
    """Test Option 4 courses sub-menu options."""
    # Sub-menu 1: Engineering
    res_eng = client.post("/voice/courses_menu", data={"Digits": "1"})
    assert res_eng.status_code == 200
    assert "School of Technology, Management and Engineering" in res_eng.data.decode("utf-8")

    # Sub-menu 2: Pharmacy
    res_pharm = client.post("/voice/courses_menu", data={"Digits": "2"})
    assert res_pharm.status_code == 200
    assert "School of Pharmacy and Technology Management" in res_pharm.data.decode("utf-8")

    # Sub-menu 3: Commerce
    res_comm = client.post("/voice/courses_menu", data={"Digits": "3"})
    assert res_comm.status_code == 200
    assert "School of Commerce" in res_comm.data.decode("utf-8")
    assert "BBA" in res_comm.data.decode("utf-8")
    assert "BCA" in res_comm.data.decode("utf-8")

    # Sub-menu 4: Return to main menu
    res_back = client.post("/voice/courses_menu", data={"Digits": "4"})
    assert res_back.status_code == 200
    assert "Welcome to SVKM's NMIMS Global University, Dhule" in res_back.data.decode("utf-8")

def test_voice_menu_invalid(client):
    """Test invalid keypad selection."""
    res = client.post("/voice/menu", data={"Digits": "7"})
    assert res.status_code == 200
    assert "not a valid option" in res.data.decode("utf-8")

def test_ivr_simulation_api(client):
    """Test programmatic simulation endpoint."""
    res = client.post("/test/ivr/simulate", json={"action": "incoming"})
    assert res.status_code == 200
    data = res.get_json()
    assert "SVKM's NMIMS Global University, Dhule" in data["message"]

    res_courses = client.post("/test/ivr/simulate", json={"action": "menu", "digit": "4"})
    assert res_courses.status_code == 200
    assert res_courses.get_json()["step"] == "courses_submenu"

    res_pharm = client.post("/test/ivr/simulate", json={"action": "courses_menu", "digit": "2"})
    assert res_pharm.status_code == 200
    assert res_pharm.get_json()["category"] == "courses_pharmacy"
