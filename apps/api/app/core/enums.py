from enum import Enum


class StrEnum(str, Enum):
    """String enum base so values serialize cleanly in JSON/Pydantic."""

    def __str__(self) -> str:
        return self.value


class TriggerType(StrEnum):
    RISK_SCORE = "risk_score"
    CUSTOMER_REPORT = "customer_report"
    ANALYST_REQUEST = "analyst_request"


class CaseStatus(StrEnum):
    OPEN = "open"
    CLOSED_FRAUD = "closed_fraud"
    CLOSED_LEGITIMATE = "closed_legitimate"
    ESCALATED = "escalated"


class Verdict(StrEnum):
    FRAUD = "fraud"
    LEGITIMATE = "legitimate"
    UNCERTAIN = "uncertain"


class Pattern(StrEnum):
    CARD_TESTING = "card_testing"
    CARD_NOT_PRESENT_FRAUD = "card_not_present_fraud"
    CARD_NOT_PRESENT_NEW_DEVICE = "card_not_present_new_device"
    OUT_OF_REGION_USE = "out_of_region_use"
    ACCOUNT_TAKEOVER = "account_takeover"
    UNDOCUMENTED = "undocumented"
    NONE = "none"


class PriorOutcome(StrEnum):
    CONFIRMED_FRAUD = "confirmed_fraud"
    CLEARED = "cleared"


class EvidenceSource(StrEnum):
    GRAPH = "graph"
    DOCUMENT = "document"
    CUSTOMER = "customer"
    EXTERNAL = "external"


class EvidenceRequestType(StrEnum):
    CUSTOMER_VALIDATION = "customer_validation"
    STEP_UP_AUTH = "step_up_auth"
    ANALYST_INFO = "analyst_info"


class EvidenceRequestStatus(StrEnum):
    PENDING = "pending"
    RESPONDED = "responded"
    EXPIRED = "expired"


class ActionType(StrEnum):
    ALLOW_TRANSACTION = "ALLOW_TRANSACTION"
    DECLINE_TRANSACTION = "DECLINE_TRANSACTION"
    MONITOR_CARD = "MONITOR_CARD"
    MONITOR_CONNECTED_CARDS = "MONITOR_CONNECTED_CARDS"
    WARN_CUSTOMER = "WARN_CUSTOMER"
    VERIFY_WITH_CUSTOMER = "VERIFY_WITH_CUSTOMER"
    STEP_UP_AUTH = "STEP_UP_AUTH"
    BLOCK_CARD = "BLOCK_CARD"
    BLOCK_ALL_CARDS = "BLOCK_ALL_CARDS"
    GENERATE_REPORT = "GENERATE_REPORT"
    CREATE_CASE = "CREATE_CASE"
    FILE_REPORT = "FILE_REPORT"
    ESCALATE_TO_ANALYST = "ESCALATE_TO_ANALYST"
    CLOSE_NO_FRAUD = "CLOSE_NO_FRAUD"


class ApprovalRoute(StrEnum):
    AUTO = "auto"
    L1 = "L1"
    L2 = "L2"


class ActionPhase(StrEnum):
    INITIAL = "initial"
    FINAL = "final"


class ActionState(StrEnum):
    RECOMMENDED = "RECOMMENDED"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    AUTHORIZED = "AUTHORIZED"
    EXECUTABLE = "EXECUTABLE"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentSourceType(StrEnum):
    POLICY = "policy"
    REGULATORY = "regulatory"
    PATTERN = "pattern"
    CASE_NOTE = "case_note"
