from enum import Enum


class UserRole(str, Enum):
    ENGINEER = "engineer"
    SECURITY = "security"
    DIRECTOR = "director"
    ACCOUNTANT = "accountant"
    ADMIN = "admin"


class RequestStatus(str, Enum):
    DRAFT = "draft"
    PENDING_SECURITY = "pending_security"
    PENDING_DIRECTOR = "pending_director"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    COUNTERPARTY_REJECTED = "counterparty_rejected"


class CounterpartyStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
