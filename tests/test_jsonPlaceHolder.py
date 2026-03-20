import pytest


def test_get_posts(session, json_api):
    response = session.get(f"{json_api}/posts")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("post_id", [1, 2, 3])
def test_get_post(session, json_api, post_id):
    response = session.get(f"{json_api}/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["id"] == post_id


def test_create_post(session, json_api):
    payload = {
        "title": "test",
        "body": "test body",
        "userId": 1
    }

    response = session.post(f"{json_api}/posts", json=payload)

    assert response.status_code == 201
    assert response.json()["title"] == payload["title"]


@pytest.mark.parametrize("user_id", [1, 2])
def test_filter_posts(session, json_api, user_id):
    response = session.get(f"{json_api}/posts", params={"userId": user_id})

    assert response.status_code == 200

    for post in response.json():
        assert post["userId"] == user_id


def test_delete_post(session, json_api):
    response = session.delete(f"{json_api}/posts/1")

    assert response.status_code == 200