from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """
    健康检查端点，用于确认服务是否正常运行。
    """
    return {"status": "ok"}
