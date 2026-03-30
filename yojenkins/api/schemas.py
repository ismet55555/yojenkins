"""Pydantic request/response models for the API."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    jenkins_url: str
    username: str
    api_token: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
