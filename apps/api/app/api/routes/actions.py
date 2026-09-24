from fastapi import APIRouter, HTTPException, status
from app.services.action_service import block_card, step_up_authentication, contact_customer, file_sar, create_case
from app.services.policy_service import PolicyService, PolicyViolationError
from app.core.enums import ActionState, ApprovalRoute

router = APIRouter(prefix="/{case_id}/actions", tags=["actions"])


@router.post("/block-card", response_model=dict)
async def approve_block_card(case_id: str, **kwargs):
    """Approve and execute block card action."""
    try:
        result = await block_card(case_id=case_id, **kwargs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/step-up-authentication", response_model=dict)
async def approve_step_up(case_id: str, **kwargs):
    """Approve and execute step up authentication action."""
    try:
        result = await step_up_authentication(case_id=case_id, **kwargs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contact-customer", response_model=dict)
async def approve_contact_customer(case_id: str, **kwargs):
    """Approve and execute contact customer action."""
    try:
        result = await contact_customer(case_id=case_id, **kwargs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file-sar", response_model=dict)
async def approve_file_sar(case_id: str, **kwargs):
    """Approve and execute file SAR action."""
    try:
        result = await file_sar(case_id=case_id, **kwargs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-case", response_model=dict)
async def create_new_case(case_id: str, **kwargs):
    """Approve and execute create case action."""
    try:
        result = await create_case(case_id=case_id, **kwargs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))