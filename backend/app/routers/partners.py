
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_connection
from app.dependencies import require_partner

router = APIRouter(prefix="/partner", tags=["Partner Catalogue"])


@router.get("/books")
def partner_books(
    authenticated: bool = Depends(require_partner),
):
    conn = None

    try:
        conn = get_connection()

        rows = conn.execute(
            """
            SELECT b.book_id,
                   b.title,
                   b.isbn,
                   b.published_year,
                   GROUP_CONCAT(DISTINCT a.name) AS authors,
                   COUNT(DISTINCT bc.copy_id) AS total_copies,
                   SUM(
                       CASE
                           WHEN bc.status = 'available' THEN 1
                           ELSE 0
                       END
                   ) AS available_copies
            FROM books b
            LEFT JOIN book_authors ba ON ba.book_id = b.book_id
            LEFT JOIN authors a ON a.author_id = ba.author_id
            LEFT JOIN book_copies bc ON bc.book_id = b.book_id
            GROUP BY
                b.book_id,
                b.title,
                b.isbn,
                b.published_year
            ORDER BY b.title
            """
        ).fetchall()

        return {
            "count": len(rows),
            "books": [dict(row) for row in rows],
        }

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to retrieve partner catalogue.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()

