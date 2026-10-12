
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_connection
from app.dependencies import get_current_librarian

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/overdue")
def overdue_loans(
    librarian: dict = Depends(get_current_librarian),
):
    conn = None

    try:
        conn = get_connection()

        rows = conn.execute(
            """
            SELECT l.loan_id,
                   m.member_id,
                   m.name AS member_name,
                   m.email,
                   b.title,
                   bc.copy_id,
                   br.name AS branch_name,
                   l.checkout_date,
                   l.due_date,
                   CAST(
                       julianday(date('now')) - julianday(l.due_date)
                       AS INTEGER
                   ) AS overdue_days
            FROM loans l
            JOIN members m ON m.member_id = l.member_id
            JOIN book_copies bc ON bc.copy_id = l.copy_id
            JOIN books b ON b.book_id = bc.book_id
            JOIN branches br ON br.branch_id = bc.branch_id
            WHERE l.returned_at IS NULL
              AND l.due_date < date('now')
            ORDER BY l.due_date ASC, l.loan_id ASC
            """
        ).fetchall()

        return {
            "count": len(rows),
            "overdue_loans": [dict(row) for row in rows],
        }

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to generate overdue report.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.get("/most-borrowed")
def most_borrowed(
    limit: int = Query(default=10, ge=1, le=100),
    librarian: dict = Depends(get_current_librarian),
):
    conn = None

    try:
        conn = get_connection()

        rows = conn.execute(
            """
            SELECT b.book_id,
                   b.title,
                   COUNT(l.loan_id) AS borrow_count
            FROM books b
            LEFT JOIN book_copies bc ON bc.book_id = b.book_id
            LEFT JOIN loans l ON l.copy_id = bc.copy_id
            GROUP BY b.book_id, b.title
            ORDER BY borrow_count DESC, b.title ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return {
            "count": len(rows),
            "most_borrowed": [dict(row) for row in rows],
        }

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to generate borrowing report.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()

