from fastapi import APIRouter

router = APIRouter(prefix="/status", tags=["Health"]) 

@router.get("/health")
async def check_healthy():
    return {"status": "healthy"}


 
