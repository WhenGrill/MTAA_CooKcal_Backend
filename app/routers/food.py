from fastapi import APIRouter

router = APIRouter(
    prefix="/food",
    tags=["Food"]
)
