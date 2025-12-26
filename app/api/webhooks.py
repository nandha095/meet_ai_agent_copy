from fastapi import APIRouter

router = APIRouter()

@router.post("/email")
def email_webhook():
    return {"message": "Webhook received"}
