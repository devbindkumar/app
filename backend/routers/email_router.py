"""
Email notification API endpoints for testing and admin control.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

from routers.auth import get_current_user, require_role, UserRole
from routers.email_service import (
    send_email,
    send_new_user_notification,
    send_password_reset_email,
    send_budget_alert,
    send_suspicious_login_alert,
    RESEND_API_KEY
)

router = APIRouter(tags=["Email"])


class TestEmailRequest(BaseModel):
    recipient_email: EmailStr
    email_type: str  # "welcome", "password_reset", "budget_alert", "login_alert"
    
    # Optional data for specific email types
    name: Optional[str] = "Test User"
    campaign_name: Optional[str] = "Test Campaign"
    campaign_id: Optional[str] = "test-123"
    percentage_used: Optional[float] = 85.5
    remaining_budget: Optional[float] = 145.50


@router.get("/email/status")
async def get_email_status(current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))):
    """Check if email service is configured"""
    return {
        "configured": bool(RESEND_API_KEY),
        "provider": "Resend" if RESEND_API_KEY else "None",
        "status": "active" if RESEND_API_KEY else "emails_logged_only"
    }


@router.post("/email/test")
async def send_test_email(
    request: TestEmailRequest,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """
    Send a test email (Super Admin only).
    Useful for verifying email configuration and templates.
    """
    try:
        if request.email_type == "welcome":
            result = await send_new_user_notification(
                admin_email=request.recipient_email,
                admin_name=current_user.get("name", "Admin"),
                new_user_name=request.name,
                new_user_email="newuser@example.com",
                new_user_role="advertiser"
            )
        elif request.email_type == "password_reset":
            result = await send_password_reset_email(
                user_email=request.recipient_email,
                user_name=request.name,
                reset_token="test-reset-token-12345"
            )
        elif request.email_type == "budget_alert":
            result = await send_budget_alert(
                user_email=request.recipient_email,
                user_name=request.name,
                campaign_name=request.campaign_name,
                campaign_id=request.campaign_id,
                percentage_used=request.percentage_used,
                remaining_budget=request.remaining_budget
            )
        elif request.email_type == "login_alert":
            result = await send_suspicious_login_alert(
                user_email=request.recipient_email,
                user_name=request.name,
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown email type: {request.email_type}")
        
        return {
            "status": "sent" if result.get("status") == "success" else result.get("status"),
            "email_type": request.email_type,
            "recipient": request.recipient_email,
            "result": result
        }
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
