from fastapi import APIRouter, HTTPException
from app.services.action_service import create_case

router = APIRouter(prefix="/{case_id}", tags=["cases"])


@router.post("/")
async def create_new_case(case_id: str):
    """Create a new investigation case."""
    try:
        result = await create_case(case_id=case_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_case(case_id: str):
    """Get case details."""
    raise HTTPException(status_code=404, detail="Case not found")


@router.post("/investigate")
async def investigate_case(case_id: str):
    """Start investigation for a case."""
    raise HTTPException(status_code=500, detail="Investigation not implemented yet")


@router.get("/evidence")
async def get_case_evidence(case_id: str):
    """Get case evidence."""
    raise HTTPException(status_code=500, detail="Evidence not implemented yet")


@router.get("/risk")
async def get_case_risk(case_id: str):
    """Get case risk assessment."""
    raise HTTPException(status_code=500, detail="Risk not implemented yet")

@router.get("/patterns")
async def get_case_patterns(case_id: str):
    """Get case patterns."""
    raise HTTPException(status_code=500, detail="Patterns not implemented yet")

@router.get("/next-action")
async def get_next_action(case_id: str):
    """Get next action for a case."""
    raise HTTPException(status_code=500, detail="Next action not implemented yet")