from typing import Union, List, Optional

from pydantic import EmailStr, BaseModel, HttpUrl


class SendEmailRequest(BaseModel):
    to: Union[EmailStr | List[EmailStr]]
    sender: EmailStr
    cc: Optional[Union[EmailStr | List[EmailStr]]] = []
    ccn: Optional[Union[EmailStr | List[EmailStr]]] = []
    subject: str
    plain_message: str
    html_message: Optional[str] = ""
    attachments: Optional[Union[HttpUrl | List[HttpUrl]]] = []


class SendEmailResponse(BaseModel):
    status: str
    error: Optional[str] = None
    error_description: Optional[str] = None
