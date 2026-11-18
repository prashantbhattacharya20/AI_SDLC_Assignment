from enum import Enum


class UserRole(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"


class ExpenseStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ExpenseCategory(str, Enum):
    TRAVEL = "Travel"
    MEALS = "Meals"
    EQUIPMENT = "Equipment"
    SOFTWARE = "Software"
    UTILITIES = "Utilities"
    OTHER = "Other"


class DecisionAction(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
