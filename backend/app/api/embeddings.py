from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.embedding import EmbeddingManager
from app.services.search import semantic_search
import structlog

router = APIRouter(prefix="/api/v1/embeddings", tags=["embeddings"])
logger = structlog.get_logger()


class EmbeddingRequest(BaseModel):
    text: str


class EmbeddingResponse(BaseModel):
    embedding: List[float]
    provider: str
    dimensions: int


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    threshold: float = 0.7


class SearchResult(BaseModel):
    id: int
    name: str
    price: Optional[float]
    similarity: float


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int


@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    try:
        manager = EmbeddingManager()
        provider = "unknown"

        if manager._gemini_key:
            try:
                embedding = await manager._try_gemini(request.text)
                provider = "gemini"
            except Exception:
                pass

        if provider == "unknown":
            try:
                embedding = await manager._try_jina(request.text)
                provider = "jina"
            except Exception:
                pass

        if provider == "unknown":
            try:
                embedding = await manager._try_huggingface(request.text)
                provider = "huggingface"
            except Exception:
                pass

        if provider == "unknown":
            embedding = [0.0] * EmbeddingManager.DIMENSIONS
            provider = "zero_vector"

        return EmbeddingResponse(
            embedding=embedding,
            provider=provider,
            dimensions=len(embedding)
        )
    except ValueError as e:
        logger.warning("invalid_request", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        raise HTTPException(status_code=500, detail="Erro interno")


@router.post("/search", response_model=SearchResponse)
async def search_embeddings(request: SearchRequest):
    try:
        results = await semantic_search(
            query_text=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )

        search_results = [
            SearchResult(
                id=r["id"],
                name=r["name"],
                price=r.get("price"),
                similarity=r["similarity"]
            )
            for r in results
        ]

        return SearchResponse(
            results=search_results,
            total=len(search_results)
        )
    except RuntimeError as e:
        logger.error("search_failed", error=str(e))
        raise HTTPException(status_code=503, detail="Serviço de busca indisponível")
    except Exception as e:
        logger.error("search_error", error=str(e))
        raise HTTPException(status_code=500, detail="Erro na busca semântica")


@router.get("/health")
async def health_check():
    manager = EmbeddingManager()
    status = {
        "gemini_configured": bool(manager._gemini_key),
        "jina_configured": bool(manager._jina_key),
        "status": "healthy" if manager._gemini_key or manager._jina_key else "degraded"
    }
    return status
