from fastapi import APIRouter, HTTPException
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

FAISS_INDEX_PATH = "faiss_index"

router = APIRouter(prefix="/rag", tags=["RAG"])


class URLsRequest(BaseModel):
    urls: list[str]


@router.post("/ingest-urls")
async def upload_and_store_url_pages(request: URLsRequest):
    try:
        loader = UnstructuredURLLoader(
            urls=request.urls,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        documents = loader.load()
        if not documents:
            raise HTTPException(status_code=400, detail="No documents found at the provided URLs.")

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        documents = splitter.split_documents(documents)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        vectorstore = FAISS.from_documents(documents, embeddings)
        vectorstore.save_local(FAISS_INDEX_PATH)

        return {"message": "Documents processed and stored successfully.", "chunks_created": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))