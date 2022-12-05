import json
import os
import pytest

import main


@pytest.fixture
def client():
    main.app.testing = True
    return main.app.test_client()


@pytest.fixture
def config():
    return main.get_config()


@pytest.fixture
def test_html():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    top_page_html = os.path.join(base_dir, 'test_files/test_top_page.html')
    product_page_html = os.path.join(base_dir, 'test_files/test_product_page.html')
    return top_page_html, product_page_html


def test_extract_scrape_data(test_html):
    top_page_source, product_page_source = test_html
    r = main.extract_scrape_data(top_page_source, product_page_source)

    assert type(r) == dict
    assert 'all_data' in r.keys()
    assert 'products_data' in r.keys()


def test_make_message(test_html):
    top_page_source, product_page_source = test_html
    data = main.extract_scrape_data(top_page_source, product_page_source)

    r = main.make_message(data)
    assert '確定拠出年金レポート' in r

    with pytest.raises(KeyError):
        data = {}
        main.make_message(data)


def test_send_line():
    r = main.send_line('test')
    assert r == 200


def test_scraping():
    r = main.scraping()
    assert 1 == 1

# def test_main(client):
#     r = client.get("/")
#     result = json.loads(r.data.decode()).get('result')
#
#     assert result == "success"
#     assert r.status_code == 200
