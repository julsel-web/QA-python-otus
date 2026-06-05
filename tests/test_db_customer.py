import uuid

import pytest

from lib.db import (
    create_customer,
    delete_customer,
    get_customer_by_id,
    get_missing_customer_id,
    update_customer,
)


@pytest.fixture
def customer_data():
    suffix = uuid.uuid4().hex[:8]
    return {
        "firstname": "Test",
        "lastname": f"User{suffix}",
        "email": f"otus_{suffix}@example.com",
        "telephone": f"+7999{suffix[:7]}",
    }


def test_create_customer(connection, customer_data):
    customer_id = create_customer(connection, customer_data)

    try:
        created_customer = get_customer_by_id(connection, customer_id)

        assert created_customer is not None
        assert created_customer["customer_id"] == customer_id
        assert created_customer["firstname"] == customer_data["firstname"]
        assert created_customer["lastname"] == customer_data["lastname"]
        assert created_customer["email"] == customer_data["email"]
        assert created_customer["telephone"] == customer_data["telephone"]
    finally:
        delete_customer(connection, customer_id)


def test_update_existing_customer(connection, customer_data):
    customer_id = create_customer(connection, customer_data)
    updated_data = {
        "firstname": "Updated",
        "lastname": "Customer",
        "email": f"updated_{uuid.uuid4().hex[:8]}@example.com",
        "telephone": "+75555555555",
    }

    try:
        assert update_customer(connection, customer_id, updated_data) is True

        updated_customer = get_customer_by_id(connection, customer_id)

        assert updated_customer is not None
        assert updated_customer["firstname"] == updated_data["firstname"]
        assert updated_customer["lastname"] == updated_data["lastname"]
        assert updated_customer["email"] == updated_data["email"]
        assert updated_customer["telephone"] == updated_data["telephone"]
    finally:
        delete_customer(connection, customer_id)


def test_update_nonexistent_customer(connection):
    missing_customer_id = get_missing_customer_id(connection)
    updated_data = {
        "firstname": "Missing",
        "lastname": "Customer",
        "email": f"missing_{uuid.uuid4().hex[:8]}@example.com",
        "telephone": "+74444444444",
    }

    assert update_customer(connection, missing_customer_id, updated_data) is False


def test_delete_existing_customer(connection, customer_data):
    customer_id = create_customer(connection, customer_data)

    assert delete_customer(connection, customer_id) is True
    assert get_customer_by_id(connection, customer_id) is None


def test_delete_nonexistent_customer(connection):
    missing_customer_id = get_missing_customer_id(connection)

    assert delete_customer(connection, missing_customer_id) is False
