
import sqlite3
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_connection
from app.dependencies import get_current_member, get_current_librarian
from app.schema import LoanCreate, LoanReturn

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
def checkout_book(
    loan: LoanCreate,
    librarian: dict = Depends(get_current_librarian),
):
    conn = None

    try:
        conn = get_connection()
        conn.execute("BEGIN IMMEDIATE")

        member = conn.execute(
            """
            SELECT member_id, is_active
            FROM members
            WHERE member_id = ?
            """,
            (loan.member_id,),
        ).fetchone()

        if member is None or member["is_active"] != 1:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "MEMBER_NOT_FOUND",
                    "message": "Active member not found.",
                },
            )

        active_count = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM loans
            WHERE member_id = ? AND returned_at IS NULL
            """,
            (loan.member_id,),
        ).fetchone()["total"]

        if active_count >= 3:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "LOAN_LIMIT_REACHED",
                    "message": "A member can have at most 3 active loans.",
                },
            )

        copy = conn.execute(
            """
            SELECT copy_id, status
            FROM book_copies
            WHERE copy_id = ?
            """,
            (loan.copy_id,),
        ).fetchone()

        if copy is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "COPY_NOT_FOUND",
                    "message": "Physical copy not found.",
                },
            )

        if copy["status"] != "available":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "COPY_UNAVAILABLE",
                    "message": "This copy is not available.",
                },
            )

        checkout_date = date.today()
        due_date = checkout_date + timedelta(days=14)

        cursor = conn.execute(
            """
            INSERT INTO loans
                (copy_id, member_id, staff_id, checkout_date, due_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                loan.copy_id,
                loan.member_id,
                librarian["staff_id"],
                checkout_date.isoformat(),
                due_date.isoformat(),
            ),
        )

        update_cursor = conn.execute(
            """
            UPDATE book_copies
            SET status = 'issued'
            WHERE copy_id = ? AND status = 'available'
            """,
            (loan.copy_id,),
        )

        if update_cursor.rowcount != 1:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "COPY_UNAVAILABLE",
                    "message": "This copy is no longer available.",
                },
            )

        loan_id = cursor.lastrowid
        conn.commit()

        return {
            "message": "Book checked out successfully",
            "loan_id": loan_id,
            "member_id": loan.member_id,
            "copy_id": loan.copy_id,
            "staff_id": librarian["staff_id"],
            "checkout_date": checkout_date.isoformat(),
            "due_date": due_date.isoformat(),
        }

    except HTTPException:
        if conn is not None:
            conn.rollback()
        raise

    except sqlite3.IntegrityError as exc:
        if conn is not None:
            conn.rollback()

        raise HTTPException(
            status_code=409,
            detail={
                "code": "LOAN_CONFLICT",
                "message": "A database constraint prevented checkout.",
            },
        ) from exc

    except sqlite3.Error as exc:
        if conn is not None:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to check out book.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.post("/{loan_id}/return")
def return_book(
    loan_id: int,
    payload: LoanReturn | None = None,
    librarian: dict = Depends(get_current_librarian),
):
    conn = None

    try:
        conn = get_connection()
        conn.execute("BEGIN IMMEDIATE")

        loan = conn.execute(
            """
            SELECT loan_id, copy_id, checkout_date, due_date, returned_at
            FROM loans
            WHERE loan_id = ?
            """,
            (loan_id,),
        ).fetchone()

        if loan is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "LOAN_NOT_FOUND",
                    "message": "Loan not found.",
                },
            )

        if loan["returned_at"] is not None:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "ALREADY_RETURNED",
                    "message": "This loan has already been returned.",
                },
            )

        returned = (
            payload.returned_at
            if payload is not None and payload.returned_at is not None
            else date.today()
        )

        checkout = date.fromisoformat(loan["checkout_date"])
        due = date.fromisoformat(loan["due_date"])

        if returned < checkout:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_RETURN_DATE",
                    "message": "Return date cannot be before checkout date.",
                },
            )

        late_days = max(0, (returned - due).days)
        fine_amount = late_days * 10

        conn.execute(
            "UPDATE loans SET returned_at = ? WHERE loan_id = ?",
            (returned.isoformat(), loan_id),
        )

        conn.execute(
            """
            UPDATE book_copies
            SET status = 'available'
            WHERE copy_id = ?
            """,
            (loan["copy_id"],),
        )

        if fine_amount > 0:
            conn.execute(
                """
                INSERT INTO fines (loan_id, amount, status, created_at)
                VALUES (?, ?, 'unpaid', ?)
                """,
                (loan_id, fine_amount, returned.isoformat()),
            )

        conn.commit()

        return {
            "message": "Book returned successfully",
            "loan_id": loan_id,
            "returned_at": returned.isoformat(),
            "late_days": late_days,
            "fine_amount": fine_amount,
            "fine_currency": "INR",
        }

    except HTTPException:
        if conn is not None:
            conn.rollback()
        raise

    except sqlite3.IntegrityError as exc:
        if conn is not None:
            conn.rollback()

        raise HTTPException(
            status_code=409,
            detail={
                "code": "RETURN_CONFLICT",
                "message": "A fine or return record conflicts with existing data.",
            },
        ) from exc

    except (sqlite3.Error, ValueError) as exc:
        if conn is not None:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "code": "RETURN_ERROR",
                "message": "Unable to return book.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.get("/my")
def my_loans(
    member: dict = Depends(get_current_member),
):
    conn = None

    try:
        conn = get_connection()
        print("CURRENT MEMBER:", member)
        print("MEMBER ID USED:", member["member_id"])

        rows = conn.execute(
            """
            SELECT l.loan_id, l.member_id, l.copy_id, b.title,
            bc.branch_id, l.checkout_date,
            l.due_date, l.returned_at
            FROM loans l
            JOIN book_copies bc ON bc.copy_id = l.copy_id
            JOIN books b ON b.book_id = bc.book_id
            WHERE l.member_id = ?
            ORDER BY l.checkout_date DESC, l.loan_id DESC
            """,
            (member["member_id"],),
        ).fetchall()

        return {
            "count": len(rows),
            "loans": [dict(row) for row in rows],
        }

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to retrieve loans.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()
