from fastapi import FastAPI,APIRouter
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


router = APIRouter(Prefix="/rag", tags=["RAG"])

 

