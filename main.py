
from fastapi import APIRouter, FastAPI
from Routes.RAG_routes import router
from Routes.chatbot import chatrouter

app = FastAPI()


app.include_router(router)
app.include_router(chatrouter)
