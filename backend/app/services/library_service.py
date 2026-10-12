
from datetime import date
import sqlite3


FINE_PER_DAY = 10
MAX_ACTIVE_LOANS = 3
LOAN_PERIOD_DAYS = 14


def calculate_fine(due_date: str, returned_at: str) -> dict:
    """
    Calculate the fine for a returned book.

    Fine is ₹10 for each day after the due date.
    """
    due = date.fromisoformat(due_date)
    returned = date.fromisoformat(returned_at)

    if returned < due:
        late_days = 0
    else:
        late_days = max(0, (returned - due).days)

    return {
        "late_days": late_days,
        "fine_amount": late_days * FINE_PER_DAY,
    }


def get_active_loan_count(
    connection: sqlite3.Connection,
    member_id: int,
) -> int:
    """Return the number of books currently borrowed by a member."""
    row = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM loans
        WHERE member_id = ?
          AND returned_at IS NULL
        """,
        (member_id,),
    ).fetchone()

    return int(row["total"])


def can_borrow_book(
    connection: sqlite3.Connection,
    member_id: int,
) -> bool:
    """Check whether a member is below the active-loan limit."""
    return get_active_loan_count(
        connection,
        member_id,
    ) < MAX_ACTIVE_LOANS


def get_copy_status(
    connection: sqlite3.Connection,
    copy_id: int,
) -> str | None:
    """Return a copy's status, or None if the copy does not exist."""
    row = connection.execute(
        """
        SELECT status
        FROM book_copies
        WHERE copy_id = ?
        """,
        (copy_id,),
    ).fetchone()

    if row is None:
        return None

    return str(row["status"])


def is_member_active(
    connection: sqlite3.Connection,
    member_id: int,
) -> bool:
    """Check whether a member exists and is active."""
    row = connection.execute(
        """
        SELECT is_active
        FROM members
        WHERE member_id = ?
        """,
        (member_id,),
    ).fetchone()

    return row is not None and bool(row["is_active"])
