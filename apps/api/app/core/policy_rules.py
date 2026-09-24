"""Versioned default policy rules.

Policy rules are DATA (not code): each rule is a plain dict with a stable
``rule_id``, a human readable ``description``, a set of ``conditions`` and the
consequences (``action``, ``route``, ``approval_required``). Kept separate from
the engine so rules can be versioned, audited and swapped without code changes
(AGENTS.md section 18).

# PLACEHOLDER(policy-thresholds): thresholds below are conservative defaults
# that MUST be confirmed with the fraud team before production. They are
# intentionally not presented as calibrated fraud probabilities.
"""

POLICY_VERSION = "1.0"

DEFAULT_POLICY_RULES: list[dict] = [
    {
        "rule_id": "R-1",
        "description": "High input risk score with matching out-of-region or "
        "card-not-present pattern warrants customer verification.",
        "conditions": {"input_risk_score_min": 0.7, "pattern_any": ["out_of_region", "card_not_present"]},
        "action": "verify_customer",
        "route": "L1",
        "approval_required": True,
    },
    {
        "rule_id": "R-2",
        "description": "Confirmed high-value fraud proxemity triggers step-up "
        "authentication on the flagged card before any decline.",
        "conditions": {"exposure_usd_min": 1000.0, "verdict": "fraud"},
        "action": "step_up_authentication",
        "route": "L2",
        "approval_required": True,
    },
    {
        "rule_id": "R-3",
        "description": "Account-takeover pattern detected on the customer is "
        "ineligible for a same-day card-only action; escalate to L2.",
        "conditions": {"pattern_eq": "account_takeover"},
        "action": "block_card",
        "route": "L2",
        "approval_required": True,
    },
    {
        "rule_id": "R-4",
        "description": "Low risk score with no fraud pattern and customer "
        "confirmation can close the case as legitimate without a SAR.",
        "conditions": {"risk_score_max": 0.3, "pattern_none": True, "verdict": "legitimate"},
        "action": "close_case_legitimate",
        "route": "auto",
        "approval_required": False,
    },
    {
        "rule_id": "R-5",
        "description": "Exposure above the SAR reporting threshold must reach "
        "the compliance desk (L2) before execution.",
        "conditions": {"exposure_usd_min": 10000.0},
        "action": "file_sar",
        "route": "L2",
        "approval_required": True,
    },
    {
        "rule_id": "R-6",
        "description": "No evidence yet and risk unknown: gather more evidence "
        "before proposing any action (evidence-first).",
        "conditions": {"evidence_count": 0},
        "action": "gather_more_evidence",
        "route": "auto",
        "approval_required": False,
    },
]