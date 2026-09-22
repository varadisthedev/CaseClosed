from fastapi import APIRouter

router = APIRouter()


@router.get("/{case_id}/next-action")
async def get_next_action(case_id: str):
    return {"detail": "Not implemented"}


@router.post("/{case_id}/evidence/request")
async def request_evidence(case_id: str):
    return {"detail": "Not implemented"}


@router.post("/{case_id}/actions/approve")
async def approve_action(case_id: str):
    return {"detail": "Not implemented"}


@router.post("/{case_id}/actions/execute")
async def execute_action(case_id: str):
    return {"detail": "Not implemented"}