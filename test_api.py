import pytest
import requests
from tests.utils import generate_seller_id

BASE_URL = "https://qa-internship.avito.com"

@pytest.fixture(scope="session")
def seller_id():
    return generate_seller_id()

@pytest.fixture(scope="session")
def created_item(seller_id):
    payload = {
        "sellerID": seller_id,
        "name": "Test item",
        "price": 100,
        "statistics": {"contacts": 1, "likes": 2, "viewCount": 3}
    }
    r = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    assert r.status_code == 200  # item must be created
    return payload

@pytest.fixture(scope="session")
def created_item_id(created_item):
    r = requests.get(f"{BASE_URL}/api/1/{created_item['sellerID']}/item")
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    return data[-1]["id"]

# ---------------- POST TESTS ----------------

def test_post_valid_item(seller_id):
    r = requests.post(f"{BASE_URL}/api/1/item", json={
        "sellerID": seller_id,
        "name": "Phone",
        "price": 500
    })
    assert r.status_code == 200

@pytest.mark.parametrize("invalid_payload", [
    {},  # empty body
    {"name": "No seller"},  # no sellerID
    {"sellerID": "string", "price": 50},  # wrong type
    {"sellerID": 123456, "name": "", "price": 50},  # empty name
    {"sellerID": 123456, "name": "Bad", "price": -1},  # negative price
])
def test_post_invalid_item(invalid_payload):
    r = requests.post(f"{BASE_URL}/api/1/item", json=invalid_payload)
    assert r.status_code in (400, 500)

# ---------------- GET BY ID ----------------

def test_get_item_valid(created_item_id):
    r = requests.get(f"{BASE_URL}/api/1/item/{created_item_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == created_item_id

@pytest.mark.parametrize("invalid_id", [
    "123", "not-uuid", "", "____"
])
def test_get_item_invalid(invalid_id):
    r = requests.get(f"{BASE_URL}/api/1/item/{invalid_id}")
    assert r.status_code in (400, 404)

# ---------------- GET BY SELLER ----------------

def test_get_items_by_seller(seller_id):
    r = requests.get(f"{BASE_URL}/api/1/{seller_id}/item")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

# -------------- STATISTICS ----------------

def test_get_statistics(created_item_id):
    r = requests.get(f"{BASE_URL}/api/1/statistic/{created_item_id}")
    assert r.status_code == 200
    data = r.json()
    assert all(k in data for k in ("likes", "viewCount", "contacts"))

@pytest.mark.parametrize("bad_id", ["", "string", "111"])
def test_get_statistics_bad_id(bad_id):
    r = requests.get(f"{BASE_URL}/api/1/statistic/{bad_id}")
    assert r.status_code in (400, 404)
