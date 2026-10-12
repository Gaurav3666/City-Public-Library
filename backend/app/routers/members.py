
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_connection
from app.dependencies import get_current_member
from app.schema import MemberCreate, MemberLogin, StaffLogin

router = APIRouter(prefix="/members", tags=["Members"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_member(member: MemberCreate):
    conn = None

    try:
        conn = get_connection()

        with conn:
            cursor = conn.execute(
                """
                INSERT INTO members (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (
                    member.name.strip(),
                    str(member.email).lower(),
                    hash_password(member.password),
                ),
            )
            member_id = cursor.lastrowid

        return {
            "message": "Member registered successfully",
            "member_id": member_id,
            "name": member.name.strip(),
            "email": str(member.email).lower(),
        }

    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "MEMBER_CONFLICT",
                "message": "Email may already be registered.",
            },
        ) from exc

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to register member.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.post("/login")
def login_member(credentials: MemberLogin):
    conn = None

    try:
        conn = get_connection()

        row = conn.execute(
            """
            SELECT member_id, email, password_hash, is_active
            FROM members
            WHERE email = ?
            """,
            (str(credentials.email).lower(),),
        ).fetchone()

        if row is None or not verify_password(
            credentials.password, row["password_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        if row["is_active"] != 1:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "MEMBER_INACTIVE",
                    "message": "Member account is inactive.",
                },
            )

        return {
            "access_token": create_access_token(
                row["member_id"], "member"
            ),
            "token_type": "bearer",
            "expires_in": 1800,
        }

    except HTTPException:
        raise

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to log in.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.get("/me")
def get_my_profile(
    current_member: dict = Depends(get_current_member),
):
    return {"member": current_member}


@router.post("/staff/login")
def login_staff(credentials: StaffLogin, request: Request):
    conn = None

    try:
        conn = get_connection()

        row = conn.execute(
            """
            SELECT staff_id, name, email, password_hash, role, branch_id
            FROM staff
            WHERE email = ?
            """,
            (str(credentials.email).lower(),),
        ).fetchone()

        if row is None or not verify_password(
            credentials.password, row["password_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password.",
                },
            )

        if row["role"] not in ("librarian", "admin"):
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "STAFF_ROLE_FORBIDDEN",
                    "message": "Staff role is not permitted.",
                },
            )

        # Clear any previous session before creating a new staff session.
        request.session.clear()
        request.session["staff_id"] = row["staff_id"]
        request.session["role"] = row["role"]

        return {
            "message": "Librarian login successful",
            "staff": {
                "staff_id": row["staff_id"],
                "name": row["name"],
                "email": row["email"],
                "role": row["role"],
                "branch_id": row["branch_id"],
            },
            "authentication": "session",
            "expires_in": 1800,
        }

    except HTTPException:
        raise

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to log in staff.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()


@router.post("/staff/logout")
def logout_staff(request: Request):
    if not request.session.get("staff_id"):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "SESSION_REQUIRED",
                "message": "No active librarian session.",
            },
        )

    request.session.clear()

    return {"message": "Librarian logged out successfully"}


@router.get("/staff/me")
def get_staff_profile(request: Request):
    staff_id = request.session.get("staff_id")

    if staff_id is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "SESSION_REQUIRED",
                "message": "Librarian session required. Please log in.",
            },
        )

    conn = None

    try:
        conn = get_connection()

        row = conn.execute(
            """
            SELECT staff_id, name, email, role, branch_id
            FROM staff
            WHERE staff_id = ?
            """,
            (staff_id,),
        ).fetchone()

        if row is None or row["role"] not in ("librarian", "admin"):
            request.session.clear()
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "INVALID_SESSION",
                    "message": "Librarian session is invalid.",
                },
            )

        return {"staff": dict(row)}

    except HTTPException:
        raise

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to retrieve staff profile.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()

