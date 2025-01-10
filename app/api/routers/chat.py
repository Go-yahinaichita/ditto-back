from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/")
async def get_chat():
    return {"message": "Hello, World!"}
