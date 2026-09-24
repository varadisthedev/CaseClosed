from fastapi import APIRouter, HTTPException
from app.services.investigation_service import run_investigation, check_approval_required

router = APIRouter(tags=["investigation"])


@router.post("/{case_id}")
async def start_investigation(case_id: str):
    """Start investigation for a case."""
    try:
        result = await run_investigation(case_id=case_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{case_id}/evidence")
async def get_evidence(case_id: str):
    """Get investigation evidence."""
    raise HTTPException(status_code=500, detail="Evidence not implemented yet")


@router.get("/{case_id}/graph")
async def get_graph(case_id: str):
    """Get graph evidence."""
    raise HTTPException(status_code=500, detail="Graph not implemented yet")


@router.get("/{case_id}/patterns")
async def get_patterns(case_id: str):
    """Get detected patterns."""
    raise HTTPException(status_code=500, detail="Patterns not implemented yet")


@router.get("/{case_id}/similar-cases")
async def get_similar_cases(case_id: str):
    """Get similar cases."""
    raise HTTPException(status_code=500, detail="Similar cases not implemented yet")


@router.post("/{case_id}/evidence/request")
async def request_evidence(case_id: str):
    """Request additional evidence."""
    raise HTTPException(status_code=500, detail="Evidence request not implemented yet")