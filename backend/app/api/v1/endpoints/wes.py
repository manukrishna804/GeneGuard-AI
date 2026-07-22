from fastapi import APIRouter

router = APIRouter(
    prefix="/wes",
    tags=["WES"]
)


@router.get("/")
def get_wes():
    return {
        "message": "WES module"
    }