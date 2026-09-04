
from fastapi import APIRouter, FastAPI

app = FastAPI()


app.include_router(Routes.RAG_routes.router)

