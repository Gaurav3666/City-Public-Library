
import sqlite3

from fastapi import APIRouter, HTTPException, status

from app.database import get_connection
from app.schema import BookCreate, BookUpdate

router = APIRouter(prefix="/books", tags=["Books"])


def _get_book_or_404(book_id: int):
    conn = None

    try:
        conn = get_connection()

        row = conn.execute(
            """
            SELECT b.book_id, b.title, b.isbn, b.published_year,
                   GROUP_CONCAT(a.name, ', ') AS authors
            FROM books b
            LEFT JOIN book_authors ba ON ba.book_id = b.book_id
            LEFT JOIN authors a ON a.author_id = ba.author_id
            WHERE b.book_id = ?
            GROUP BY b.book_id, b.title, b.isbn, b.published_year
            """,
            (book_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "BOOK_NOT_FOUND",
                    "message": "Book not found.",
                },
            )

        return dict(row)

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to retrieve book.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.get("/")
def list_books():
    conn = None

    try:
        conn = get_connection()

        rows = conn.execute(
            """
            SELECT b.book_id, b.title, b.isbn, b.published_year,
                   GROUP_CONCAT(a.name, ', ') AS authors,
                   COUNT(DISTINCT bc.copy_id) AS total_copies,
                   SUM(
                       CASE WHEN bc.status = 'available'
                       THEN 1 ELSE 0 END
                   ) AS available_copies
            FROM books b
            LEFT JOIN book_authors ba ON ba.book_id = b.book_id
            LEFT JOIN authors a ON a.author_id = ba.author_id
            LEFT JOIN book_copies bc ON bc.book_id = b.book_id
            GROUP BY b.book_id, b.title, b.isbn, b.published_year
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
                "message": "Unable to retrieve books.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    conn = None

    try:
        conn = get_connection()

        with conn:
            cursor = conn.execute(
                """
                INSERT INTO books (title, isbn, published_year)
                VALUES (?, ?, ?)
                """,
                (book.title, book.isbn, book.published_year),
            )
            book_id = cursor.lastrowid

        return {
            "message": "Book created successfully",
            "book": _get_book_or_404(book_id),
        }

    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "BOOK_CONFLICT",
                "message": "A book with this ISBN may already exist.",
            },
        ) from exc

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to create book.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.get("/{book_id}")
def get_book(book_id: int):
    return {"book": _get_book_or_404(book_id)}


@router.put("/{book_id}")
def update_book(book_id: int, book: BookUpdate):
    conn = None

    try:
        conn = get_connection()

        with conn:
            cursor = conn.execute(
                """
                UPDATE books
                SET title = ?, isbn = ?, published_year = ?
                WHERE book_id = ?
                """,
                (book.title, book.isbn, book.published_year, book_id),
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "BOOK_NOT_FOUND",
                        "message": "Book not found.",
                    },
                )

        return {
            "message": "Book updated successfully",
            "book": _get_book_or_404(book_id),
        }

    except HTTPException:
        raise

    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "BOOK_CONFLICT",
                "message": "A book with this ISBN may already exist.",
            },
        ) from exc

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to update book.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.delete("/{book_id}")
def delete_book(book_id: int):
    conn = None

    try:
        conn = get_connection()

        with conn:
            book = conn.execute(
                "SELECT book_id FROM books WHERE book_id = ?",
                (book_id,),
            ).fetchone()

            if book is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "BOOK_NOT_FOUND",
                        "message": "Book not found.",
                    },
                )

            copy_count = conn.execute(
                "SELECT COUNT(*) FROM book_copies WHERE book_id = ?",
                (book_id,),
            ).fetchone()[0]

            if copy_count > 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "BOOK_HAS_COPIES",
                        "message": "Cannot delete a book that has physical copies.",
                    },
                )

            conn.execute(
                "DELETE FROM book_authors WHERE book_id = ?",
                (book_id,),
            )
            conn.execute(
                "DELETE FROM books WHERE book_id = ?",
                (book_id,),
            )

        return {"message": "Book deleted successfully", "book_id": book_id}

    except HTTPException:
        raise

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to delete book.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()

