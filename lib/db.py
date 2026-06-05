from __future__ import annotations

from typing import Any


def _get_customer_columns(connection) -> set[str]:
    with connection.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM oc_customer")
        return {row["Field"] for row in cursor.fetchall()}


def create_customer(connection, customer_data: dict[str, Any]) -> int:
    columns = _get_customer_columns(connection)
    payload = {
        "customer_group_id": 1,
        "store_id": 0,
        "language_id": 1,
        "firstname": "Test",
        "lastname": "User",
        "email": "test@example.com",
        "telephone": "+70000000000",
        "fax": "",
        "password": "test-password",
        "salt": "",
        "cart": "",
        "wishlist": "",
        "newsletter": 0,
        "address_id": 0,
        "custom_field": "",
        "ip": "127.0.0.1",
        "status": 1,
        "safe": 0,
        "token": "",
        "code": "",
    }
    payload.update(customer_data)

    insert_order = [
        "customer_group_id",
        "store_id",
        "language_id",
        "firstname",
        "lastname",
        "email",
        "telephone",
        "fax",
        "password",
        "salt",
        "cart",
        "wishlist",
        "newsletter",
        "address_id",
        "custom_field",
        "ip",
        "status",
        "safe",
        "token",
        "code",
    ]
    insert_columns = [column for column in insert_order if column in columns]
    placeholders = ", ".join(["%s"] * len(insert_columns))
    values = [payload[column] for column in insert_columns]
    if "date_added" in columns:
        insert_columns.append("date_added")
        placeholders = f"{placeholders}, NOW()"

    sql = f"INSERT INTO oc_customer ({', '.join(insert_columns)}) VALUES ({placeholders})"

    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        connection.commit()
        return cursor.lastrowid


def get_customer_by_id(connection, customer_id: int) -> dict[str, Any] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM oc_customer WHERE customer_id = %s",
            (customer_id,),
        )
        return cursor.fetchone()


def update_customer(connection, customer_id: int, customer_data: dict[str, Any]) -> bool:
    columns = _get_customer_columns(connection)
    allowed_fields = ["firstname", "lastname", "email", "telephone"]
    update_fields = [
        field for field in allowed_fields if field in customer_data and field in columns
    ]
    if not update_fields:
        raise ValueError("No valid customer fields provided for update")

    assignments = ", ".join(f"{field} = %s" for field in update_fields)
    values = [customer_data[field] for field in update_fields]
    values.append(customer_id)

    with connection.cursor() as cursor:
        cursor.execute(
            f"UPDATE oc_customer SET {assignments} WHERE customer_id = %s",
            values,
        )
        connection.commit()
        return cursor.rowcount > 0


def delete_customer(connection, customer_id: int) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM oc_customer WHERE customer_id = %s",
            (customer_id,),
        )
        connection.commit()
        return cursor.rowcount > 0


def get_missing_customer_id(connection) -> int:
    with connection.cursor() as cursor:
        cursor.execute("SELECT COALESCE(MAX(customer_id), 0) + 1000 AS next_id FROM oc_customer")
        row = cursor.fetchone()
        return int(row["next_id"])
