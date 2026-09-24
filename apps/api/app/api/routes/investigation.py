from fastapi import APIRouter

router = APIRouter()


@router.get("/{case_id}/evidence")
async def get_evidence(case_id: str):
    return {"detail": "Not implemented"}


@router.get("/{case_id}/graph")
async def get_graph(case_id: str):
    return {"detail": "Not implemented"}


@router.get("/{case_id}/patterns")
async def get_patterns(case_id: str):
    return {"detail": "Not implemented"}


@router.get("/{case_id}/similar-cases")
async def get_similar_cases(case_id: str):
    return {"detail": "Not implemented"}