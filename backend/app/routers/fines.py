
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_connection
from app.dependencies import get_current_member

router = APIRouter(prefix="/fines", tags=["Fines"])


@router.get("/my")
def get_my_fines(
    member: dict = Depends(get_current_member),
):
    conn = None

    try:
        conn = get_connection()

        rows = conn.execute(
            """
            SELECT f.fine_id, f.loan_id, f.amount,
                   f.status, f.created_at, f.paid_at,
                   l.copy_id, b.title, l.due_date, l.returned_at
            FROM fines f
            JOIN loans l ON l.loan_id = f.loan_id
            JOIN book_copies bc ON bc.copy_id = l.copy_id
            JOIN books b ON b.book_id = bc.book_id
            WHERE l.member_id = ?
            ORDER BY f.created_at DESC, f.fine_id DESC
            """,
            (member["member_id"],),
        ).fetchall()

        total_unpaid = sum(
            row["amount"] for row in rows if row["status"] == "unpaid"
        )

        return {
            "count": len(rows),
            "total_unpaid": total_unpaid,
            "currency": "INR",
            "fines": [dict(row) for row in rows],
        }

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to retrieve fines.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.post("/{fine_id}/pay")
def pay_fine(
    fine_id: int,
    member: dict = Depends(get_current_member),
):
    conn = None

    try:
        conn = get_connection()

        with conn:
            fine = conn.execute(
                """
                SELECT f.fine_id, f.amount, f.status, l.member_id
                FROM fines f
                JOIN loans l ON l.loan_id = f.loan_id
                WHERE f.fine_id = ?
                """,
                (fine_id,),
            ).fetchone()

            if fine is None or fine["member_id"] != member["member_id"]:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "FINE_NOT_FOUND",
                        "message": "Fine not found.",
                    },
                )

            if fine["status"] == "paid":
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "FINE_ALREADY_PAID",
                        "message": "This fine has already been paid.",
                    },
                )

            conn.execute(
                """
                UPDATE fines
                SET status = 'paid', paid_at = date('now')
                WHERE fine_id = ? AND status = 'unpaid'
                """,
                (fine_id,),
            )

        return {
            "message": "Fine marked as paid successfully",
            "fine_id": fine_id,
            "amount": fine["amount"],
            "currency": "INR",
            "status": "paid",
        }

    except HTTPException:
        raise

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to process fine payment.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()

