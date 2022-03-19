from fastapi import APIRouter

router = APIRouter(
    prefix="/foodlist",
    tags=["Food List"]
)
