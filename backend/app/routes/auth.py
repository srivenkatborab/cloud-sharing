"""
Authentication routes: register, confirm, login, profile.

Uses CognitoManager from cloudshare-lib and subscribes new users
to the SNS topic so they receive email notifications.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from botocore.exceptions import ClientError

from cloudshare import CognitoManager, NotificationManager
from app.config import settings
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Shared instances (boto3 uses EC2 IAM role for credentials)
cognito = CognitoManager(
    user_pool_id=settings.COGNITO_USER_POOL_ID,
    client_id=settings.COGNITO_CLIENT_ID,
    region=settings.AWS_REGION,
)
notif_manager = NotificationManager(
    topic_arn=settings.SNS_TOPIC_ARN,
    region=settings.AWS_REGION,
)


# --- Request / Response schemas ---

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class ConfirmRequest(BaseModel):
    email: EmailStr
    code: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    id_token: str
    refresh_token: str
    token_type: str


# --- Endpoints ---

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    """Register a new user with Cognito.

    Sends a 6-digit confirmation code to the user's email.
    The user must then call /api/auth/confirm before logging in.
    """
    try:
        cognito.register_user(body.email, body.password)
        # Subscribe the new user's email to SNS so they receive notifications
        try:
            notif_manager.subscribe_email(body.email)
        except ClientError:
            # Non-fatal: SNS subscription failure should not block registration
            pass
        return {"message": "Registration successful. Check your email for a confirmation code."}
    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        if error_code == "UsernameExistsException":
            raise HTTPException(status_code=409, detail="An account with this email already exists.")
        if error_code == "InvalidPasswordException":
            raise HTTPException(status_code=422, detail="Password does not meet requirements.")
        raise HTTPException(status_code=400, detail=str(exc.response["Error"]["Message"]))


@router.post("/confirm")
async def confirm(body: ConfirmRequest):
    """Confirm a user's email address using the Cognito verification code."""
    try:
        cognito.confirm_user(body.email, body.code)
        return {"message": "Email confirmed. You can now log in."}
    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        if error_code == "CodeMismatchException":
            raise HTTPException(status_code=400, detail="Invalid confirmation code.")
        if error_code == "ExpiredCodeException":
            raise HTTPException(status_code=400, detail="Confirmation code has expired.")
        raise HTTPException(status_code=400, detail=str(exc.response["Error"]["Message"]))


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    """Authenticate a user and return Cognito JWT tokens."""
    try:
        tokens = cognito.authenticate_user(body.email, body.password)
        return tokens
    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        if error_code in ("NotAuthorizedException", "UserNotFoundException"):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        if error_code == "UserNotConfirmedException":
            raise HTTPException(status_code=403, detail="Please confirm your email before logging in.")
        raise HTTPException(status_code=400, detail=str(exc.response["Error"]["Message"]))


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return {
        "username": current_user.get("username"),
        "email": current_user.get("email", current_user.get("username")),
        "sub": current_user.get("sub"),
    }
