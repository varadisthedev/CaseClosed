from fastapi import APIRouter

router = APIRouter()


@router.get("/{case_id}/risk")
async def get_risk(case_id: str):
    return {"detail": "Not implemented"}