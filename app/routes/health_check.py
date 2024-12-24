from fastapi import APIRouter

router = APIRouter()


@router.get("/health_check")
async def health_check():
    """
    Health check endpoint to only verify server connectivity (should return Ok with code 200).
    """
    return {"status": "ok"}
