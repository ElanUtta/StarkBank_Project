from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class Description(BaseModel):
    key: str
    value: str


class Invoice(BaseModel):
    amount: int
    brcode: str
    created: datetime
    descriptions: List[Description]
    discountAmount: int
    discounts: List  # Assuming this should be a list of some type
    due: datetime
    expiration: int
    fee: int
    fine: int
    fineAmount: int
    id: str
    interest: int
    interestAmount: int
    link: str
    name: str
    nominalAmount: int
    pdf: str
    rules: List  # Assuming this should be a list of some type
    splits: List  # Assuming this should be a list of some type
    status: str
    tags: List[str]
    taxId: str
    transactionIds: List[str]
    updated: datetime


class Log(BaseModel):
    created: datetime
    errors: List  # Assuming this should be a list of some type
    id: str
    invoice: Invoice
    type: str


class Event(BaseModel):
    is_delivered: bool
    created: datetime
    id: str
    log: Log
    subscription: str
    workspaceId: str


class WebhookPayload(BaseModel):
    event: Event
