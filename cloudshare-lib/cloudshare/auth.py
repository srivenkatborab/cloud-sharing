"""
CognitoManager: OOP wrapper for Amazon Cognito User Pool operations.

Handles user registration, email confirmation, authentication,
and token validation for the file sharing application.
"""

import boto3
from botocore.exceptions import ClientError
from typing import Optional


class CognitoManager:
    """Manages user authentication using Amazon Cognito User Pools.

    Provides register, confirm, and login operations. Returned tokens
    (access_token, id_token) are used by the FastAPI backend to
    authorise requests.

    Attributes:
        user_pool_id (str): Cognito User Pool ID.
        client_id (str): Cognito App Client ID (no secret).
        region (str): AWS region of the User Pool.
        client (boto3.client): The underlying boto3 Cognito IDP client.
    """

    def __init__(self, user_pool_id: str, client_id: str, region: str = "us-east-1"):
        """Initialise the CognitoManager.

        Args:
            user_pool_id: Cognito User Pool ID (e.g. 'us-east-1_xxxxxxx').
            client_id: App Client ID (public client, no secret required).
            region: AWS region string.
        """
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.region = region
        # boto3 picks up credentials from the EC2 IAM role automatically
        self.client = boto3.client("cognito-idp", region_name=region)

    def register_user(self, email: str, password: str) -> dict:
        """Register a new user in the Cognito User Pool.

        Sends a confirmation code to the user's email address.
        The user must call confirm_user() before they can log in.

        Args:
            email: User's email address (used as the username).
            password: Password (must meet User Pool password policy).

        Returns:
            Cognito sign-up response dict.

        Raises:
            ClientError: If registration fails (e.g. user already exists).
        """
        response = self.client.sign_up(
            ClientId=self.client_id,
            Username=email,
            Password=password,
            UserAttributes=[{"Name": "email", "Value": email}],
        )
        return response

    def confirm_user(self, email: str, confirmation_code: str) -> bool:
        """Confirm a user's email address using the code sent by Cognito.

        Args:
            email: The user's email address (username).
            confirmation_code: 6-digit code delivered to the user's email.

        Returns:
            True if confirmation succeeded.

        Raises:
            ClientError: If the code is wrong or expired.
        """
        self.client.confirm_sign_up(
            ClientId=self.client_id,
            Username=email,
            ConfirmationCode=confirmation_code,
        )
        return True

    def authenticate_user(self, email: str, password: str) -> dict:
        """Authenticate a user and return JWT tokens.

        Uses the USER_PASSWORD_AUTH flow which does not require
        a Cognito App Client secret.

        Args:
            email: User's email / username.
            password: User's password.

        Returns:
            Dict with 'access_token', 'id_token', and 'refresh_token'.

        Raises:
            ClientError: If credentials are invalid.
        """
        response = self.client.initiate_auth(
            ClientId=self.client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
        )
        result = response["AuthenticationResult"]
        return {
            "access_token": result["AccessToken"],
            "id_token": result["IdToken"],
            "refresh_token": result["RefreshToken"],
            "token_type": result["TokenType"],
        }

    def get_user(self, access_token: str) -> dict:
        """Retrieve the user's profile using their access token.

        Args:
            access_token: A valid Cognito access token.

        Returns:
            Dict with 'username' and 'email' fields.

        Raises:
            ClientError: If the token is invalid or expired.
        """
        response = self.client.get_user(AccessToken=access_token)
        attrs = {a["Name"]: a["Value"] for a in response["UserAttributes"]}
        return {
            "username": response["Username"],
            "email": attrs.get("email", response["Username"]),
            "sub": attrs.get("sub"),
        }
