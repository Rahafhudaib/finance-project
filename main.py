from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routes.RAG_routes import router
from Routes.chatbot import chatrouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(chatrouter)