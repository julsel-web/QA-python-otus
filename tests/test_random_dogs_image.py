import pytest


def test_dog_image(session, dog_api):
    response = session.get(f"{dog_api}/breeds/image/random")

    assert response.status_code == 200
    assert response.json()["status"] == "success"

@pytest.mark.parametrize("breed", ["hound", "husky", "pug"])
def test_by_breed(session, dog_api, breed):
    response = session.get(f"{dog_api}/breed/{breed}/images/random")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert breed in data["message"]


def test_all_breeds(session, dog_api):
    response = session.get(f"{dog_api}/breeds/list/all")

    assert response.status_code == 200
    assert isinstance(response.json()["message"], dict)


@pytest.mark.parametrize("breed", ["hound", "retriever"])
def test_breed_images(session, dog_api, breed):
    response = session.get(f"{dog_api}/breed/{breed}/images")

    assert response.status_code == 200
    assert isinstance(response.json()["message"], list)


def test_sub_breeds(session, dog_api):
    response = session.get(f"{dog_api}/breed/hound/list")

    assert response.status_code == 200













