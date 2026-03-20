import pytest


def test_get_breweries(session, brewery_api):
    response = session.get(brewery_api)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("city", ["san diego", "new york"])
def test_breweries_by_city(session, brewery_api, city):
    response = session.get(brewery_api, params={"by_city": city})

    assert response.status_code == 200
    data = response.json()
    assert data, "Ответ пустой"

    for brewery in data:
        assert "name" in brewery
        assert "city" in brewery
        assert brewery["city"].lower() == city.lower()


def test_single_brewery(session, brewery_api):
    city = "cincinnati"
    response = session.get(brewery_api, params={"by_city": city})

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    brewery = data[0]
    assert "id" in brewery
    assert "name" in brewery
    assert "city" in brewery


@pytest.mark.parametrize("brewery_type", ["micro", "brewpub"])
def test_breweries_by_type(session, brewery_api, brewery_type):
    response = session.get(brewery_api, params={"by_type": brewery_type})

    assert response.status_code == 200

    data = response.json()
    assert data, "Ответ пустой"

    for brewery in data:
        assert "id" in brewery
        assert "name" in brewery
        assert "brewery_type" in brewery


def test_search_brewery(session, brewery_api):
    response = session.get(f"{brewery_api}/search", params={"query": "dog"})

    assert response.status_code == 200