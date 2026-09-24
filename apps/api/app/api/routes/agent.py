from fastapi import APIRouter

router = APIRouter()


@router.post("/investigate/{case_id}")
async def run_agent_investigation(case_id: str):
    return {"detail": "Not implemented"}