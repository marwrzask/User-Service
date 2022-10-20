import pytest
from fastapi.testclient import TestClient
from app.main import app, Session, engine, User

client = TestClient(app)



client.post("/v1/users",
            json={
                "countryCode": "PL",
                "dateOfBirth": "12.07.1938",
                "firstname": "Lewy",
                "nickname": "Lev",
                "gender": "male",
                "email": "lewan@example.com"})

client.post("/v1/users",
            json={
                "countryCode": "GER",
                "dateOfBirth": "12.07.1920",
                "firstname": "Hans",
                "nickname": "Hun",
                "gender": "male",
                "email": "hansi@example.com"
            })

client.post("/v1/users",
            json={
                "countryCode": "POLAND",
                "dateOfBirth": "12.07.2222",
                "firstname": "Ala",
                "nickname": "Lalina",
                "gender": "male",
                "email": "ferdek@example.com"
            })


def test_user_post_valid():
    response = client.post("/v1/users",
                           json={"firstname": "Bartek",
                                 "nickname": "Kapustka"})

    data = response.json()
    assert response.status_code == 201
    assert data["firstname"] == "Bartek"
    assert data["nickname"] == "Kapustka"
    assert data["id"] is not None
    assert data["gender"] is None


def test_user_post_with_wrong_parameter():
    response = client.post("/v1/users",
                           json={"firstname": "Robert",
                                 "email": "lewy"})

    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'email'],
                                           'msg': 'value is not a valid email address',
                                           'type': 'value_error.email'}]}


def test_delete_user_account_by_id():
    response = client.delete("v1/users/4")
    assert response.status_code == 200
    assert response.json() == {
        "dateOfBirth": None,
        "firstname": "Bartek",
        "gender": None,
        "id": 4,
        "nickname": "Kapustka",
        "countryCode": None,
        "email": None
    }


def test_delete_user_invalid_id_provided():
    response = client.delete("v1/users/10")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with ID=10 not found"}


def test_get_single_user_by_id():
    response = client.get("v1/users/1")
    assert response.status_code == 200
    assert response.json() == {
        "countryCode": "PL",
        "dateOfBirth": "12.07.1938",
        "firstname": "Lewy",
        "nickname": "Lev",
        "gender": "male",
        "email": "lewan@example.com",
        'id': 1}


def test_get_single_user_invalid_id():
    response = client.get("v1/users/8")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with ID=8 not found"}


def test_put_user_invalid_id_provided():
    response = client.put("v1/users/8")
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body'],
                                           'msg': 'field required',
                                           'type': 'value_error.missing'}]}



@pytest.mark.parametrize('localhost, response_code', [
    ("/v1/users?id=2", 200),
    ("/v1/users?id=3", 200),
    ("/v1/users/30", 404),
    ("/v1/users?id=1&id=2", 200),
    ("/v1/users?nickname=Lev", 200),
    ("/v1/users?email=lewan@example.com", 200),
    ("/v1/users?email=lewandowski", 422),
    ("/v1/users", 200)])
def test_paramatrize(localhost, response_code):
    response = client.get(localhost)
    assert response.status_code == response_code
