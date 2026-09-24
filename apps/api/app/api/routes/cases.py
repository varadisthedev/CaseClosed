from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def create_case():
    return {"detail": "Not implemented"}


@router.get("/{case_id}")
async def get_case(case_id: str):
    return {"detail": "Not implemented"}


@router.post("/{case_id}/investigate")
async def investigate_case(case_id: str):
    return {"detail": "Not implemented"}