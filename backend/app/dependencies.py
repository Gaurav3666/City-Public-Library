
import hmac
import os
import sqlite3

import jwt
from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth import decode_access_token
from app.database import get_connection

load_dotenv()

bearer_scheme = HTTPBearer(auto_error=False)


def _decode(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "AUTH_REQUIRED",
                "message": "Bearer token required.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return decode_access_token(credentials.credentials)
    except (jwt.InvalidTokenError, RuntimeError) as exc:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired token.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_member(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    payload = _decode(credentials)

    if payload.get("type") != "member":
        raise HTTPException(
            status_code=403,
            detail={
                "code": "MEMBER_ACCESS_REQUIRED",
                "message": "Member access required.",
            },
        )

    conn = None

    try:
        member_id = int(payload["sub"])
        conn = get_connection()

        row = conn.execute(
            """
            SELECT member_id, name, email, is_active
            FROM members
            WHERE member_id = ?
            """,
            (member_id,),
        ).fetchone()

    except (KeyError, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_TOKEN_SUBJECT",
                "message": "Invalid token subject.",
            },
        ) from exc

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to verify member.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()

    if row is None or row["is_active"] != 1:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "MEMBER_INACTIVE",
                "message": "Member not found or inactive.",
            },
        )

    return dict(row)


def get_current_librarian(request: Request) -> dict:
    staff_id = request.session.get("staff_id")
    session_role = request.session.get("role")

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

    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Unable to verify librarian session.",
            },
        ) from exc

    finally:
        if conn is not None:
            conn.close()

    if (
        row is None
        or row["role"] not in ("librarian", "admin")
        or row["role"] != session_role
    ):
        request.session.clear()

        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_SESSION",
                "message": "Librarian session is invalid.",
            },
        )

    return dict(row)


def require_partner(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    x_api_secret: str | None = Header(default=None, alias="X-API-Secret"),
) -> bool:
    expected_key = os.getenv("PARTNER_API_KEY")
    expected_secret = os.getenv("PARTNER_API_SECRET")

    if not expected_key or not expected_secret:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "PARTNER_AUTH_NOT_CONFIGURED",
                "message": "Partner authentication is not configured.",
            },
        )

    valid_key = (
        x_api_key is not None
        and hmac.compare_digest(x_api_key, expected_key)
    )
    valid_secret = (
        x_api_secret is not None
        and hmac.compare_digest(x_api_secret, expected_secret)
    )

    if not valid_key or not valid_secret:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_PARTNER_CREDENTIALS",
                "message": "Invalid partner API credentials.",
            },
        )

    return True

