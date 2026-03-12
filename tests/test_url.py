import pytest
import requests
from lxml import etree
from bs4 import BeautifulSoup



@pytest.fixture
def need_url():
    return ["https://dog.ceo/dog-api/",
        "https://www.openbrewerydb.org/",
        "https://jsonplaceholder.typicode.com/"
            ]

@pytest.mark.parametrize("url_index",[0,1,2])
def test_get_url(need_url, url_index):
    url = need_url[url_index]
    response = requests.get(url)
    assert response.status_code == 200

@pytest.mark.parametrize("url_index", [0, 1, 2])
def test_get_html(need_url, url_index):
        url = need_url[url_index]
        body = requests.get(url).content
        assert body != ''

        parser = etree.HTMLParser()
        bode_html = etree.fromstring(body, parser)
        assert bode_html is not None

@pytest.mark.parametrize("url_index", [0, 1, 2])
def test_image_url(need_url, url_index):
    url = need_url[url_index]
    body = BeautifulSoup(requests.get(url).content, 'html.parser')

    img = body.find('img')
    assert img is not None

    for i in img:
        src = i.get('src')
        assert src is not None

@pytest.mark.parametrize("url_index", [0,1,2])
def test_botton_url(need_url, url_index):
    response = requests.get(need_url[url_index])
    body = BeautifulSoup(response.text, 'html.parser')
    links = body.find_all('a')
    assert links












