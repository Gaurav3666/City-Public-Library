
from app.database import get_connection


def verify_database():
    connection = get_connection()

    try:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        print("\n=== City Public Library Database ===")
        print("\nTables found:")

        for table in tables:
            print(f"- {table['name']}")

        expected_tables = {
            "branches",
            "books",
            "authors",
            "book_authors",
            "book_copies",
            "members",
            "staff",
            "loans",
            "fines",
        }

        actual_tables = {table["name"] for table in tables}
        missing_tables = expected_tables - actual_tables

        if missing_tables:
            print("\nMissing tables:")
            for table_name in sorted(missing_tables):
                print(f"- {table_name}")
        else:
            print("\nAll expected tables exist.")

        print("\nRecord counts:")

        for table_name in sorted(expected_tables & actual_tables):
            row = connection.execute(
                f"SELECT COUNT(*) AS total FROM [{table_name}]"
            ).fetchone()
            print(f"{table_name}: {row['total']}")

        foreign_key_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if foreign_key_errors:
            print("\nForeign key violations found:")
            for error in foreign_key_errors:
                print(tuple(error))
        else:
            print("\nNo foreign key violations found.")

    finally:
        connection.close()


if __name__ == "__main__":
    verify_database()
