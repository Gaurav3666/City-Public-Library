
import sqlite3

from app.auth import hash_password
from app.database import get_connection


DEMO_PASSWORD = "LibraryDemo@123"

MEMBER_EMAILS = [
    "aarav@example.com",
    "meera@example.com",
    "kabir@example.com",
]

STAFF_EMAILS = [
    "librarian1@example.com",
    "librarian2@example.com",
    "admin@example.com",
]


def main():
    connection = None

    try:
        connection = get_connection()

        with connection:
            member_hash = hash_password(DEMO_PASSWORD)
            staff_hash = hash_password(DEMO_PASSWORD)

            member_placeholders = ", ".join(
                "?" for _ in MEMBER_EMAILS
            )
            staff_placeholders = ", ".join(
                "?" for _ in STAFF_EMAILS
            )

            member_cursor = connection.execute(
                f"""
                UPDATE members
                SET password_hash = ?
                WHERE email IN ({member_placeholders})
                """,
                (member_hash, *MEMBER_EMAILS),
            )

            staff_cursor = connection.execute(
                f"""
                UPDATE staff
                SET password_hash = ?
                WHERE email IN ({staff_placeholders})
                """,
                (staff_hash, *STAFF_EMAILS),
            )

        print(
            f"Member accounts updated: {member_cursor.rowcount}"
        )
        print(
            f"Staff accounts updated: {staff_cursor.rowcount}"
        )
        print("Demo password: LibraryDemo@123")

    except sqlite3.Error as error:
        print(f"Database error: {error}")
        raise

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
