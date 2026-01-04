"""FastAPI entrypoint fixture."""
from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter()


def helper():
    """Helper function called by route handlers."""
    return {"status": "processed"}


@app.get("/")
def root():
    """Root endpoint - should be detected as entrypoint."""
    return helper()


@app.post("/items")
def create_item(name: str):
    """Create item - should be detected as entrypoint."""
    helper()
    return {"name": name}


@router.get("/users")
def list_users():
    """List users via router - should be detected as entrypoint."""
    return helper()


@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Delete user via router - should be detected as entrypoint."""
    helper()
    return {"deleted": user_id}


app.include_router(router)
