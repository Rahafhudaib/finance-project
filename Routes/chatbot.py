from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from fastapi import Depends,APIRouter, HTTPException
from pydantic import BaseModel
from helpers.config import get_settings, Settings
from langchain_community.vectorstores import FAISS
from Routes.RAG_routes import FAISS_INDEX_PATH


chatrouter = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    question: str


@chatrouter.post("/chat")
async def chat_with_news(request: ChatRequest, settings: Settings = Depends(get_settings)):
    embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    try:
            vectorstore = FAISS.load_local(
                FAISS_INDEX_PATH, 
                embeddings, 
                allow_dangerous_deserialization=True  # ضروري في النسخ الحديثة من LangChain للسماح بقراءة الملف المحلي
            )
    except Exception:
            raise HTTPException(status_code=400, detail="FAISS index not found. Please process URLs first.")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    template = """Use the following context to answer the question. If you cannot find the answer in the context, just say that you don't know.

Context:
{context}

Question: {question}

Answer:"""
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(api_key=settings.openai_api_key, base_url="https://openrouter.ai/api/v1",
    model="openrouter/free",
    temperature=0.7)
    def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

    retrieved_docs = retriever.invoke(request.question)
    formatted_context = format_docs(retrieved_docs)

    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({
            "context": formatted_context,
            "question": request.question
        })

    sources = list(set([doc.metadata.get("source", "Unknown") for doc in retrieved_docs]))


    return {
            "answer": answer,
            "sources": sources
        }
