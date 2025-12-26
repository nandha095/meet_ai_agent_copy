from pydantic import BaseModel, EmailStr

class ProposalEmailRequest(BaseModel):
    email: EmailStr
