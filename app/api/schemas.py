from pydantic import BaseModel, EmailStr

#  proposal email request

class ProposalEmailRequest(BaseModel):
    email: str
    subject: str
    body: str
    provider: str

#  Forgot password request
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


#  Reset password request
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

