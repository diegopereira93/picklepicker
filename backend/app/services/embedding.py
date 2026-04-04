"""Embedding manager with multi-provider fallback strategy.

Provider priority:
1. Gemini (if GEMINI_API_KEY set) — gemini-embedding-001 (768 dims)
2. Local sentence-transformers — all-MiniLM-L6-v2 (384 dims padded to 768)
3. Jina AI (if JINA_API_KEY set) — jina-embeddings-v2-base-en (768 dims)
4. Hugging Face (if HUGGINGFACE_API_KEY set) — all-MiniLM-L6-v2 (384 dims padded to 768)
5. Zero vector fallback (768 dims)
"""

import os
from typing import List, Optional

import httpx
import structlog

logger = structlog.get_logger()

# Cache for local model
_local_model = None


def _get_local_model():
    """Lazy load sentence-transformers model."""
    global _local_model
    if _local_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _local_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("local_embedding_model_loaded", model="all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence_transformers_not_installed")
            return None
    return _local_model


class EmbeddingManager:
    """Gerenciador de embeddings com estratégia de fallback entre provedores."""

    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
    JINA_API_URL = "https://api.jina.ai/v1/embeddings"
    HF_API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2"
    DIMENSIONS = 768
    GEMINI_TIMEOUT = 3.0
    JINA_TIMEOUT = 30.0
    HF_TIMEOUT = 30.0

    def __init__(self):
        self._gemini_key = os.environ.get("GEMINI_API_KEY")
        self._jina_key = os.environ.get("JINA_API_KEY")
        self._hf_key = os.environ.get("HUGGINGFACE_API_KEY")

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using best available provider.

        Raises ValueError for empty text.
        Raises RuntimeError only when ALL providers fail (zero vector is returned instead).
        """
        if not text or not text.strip():
            raise ValueError("Texto vazio não pode ser processado")

        # Provider 1: Gemini (if configured)
        if self._gemini_key:
            try:
                embedding = await self._try_gemini(text)
                logger.info("embedding_provider", provider="gemini", dimensions=self.DIMENSIONS)
                return embedding
            except Exception as e:
                logger.warning("gemini_failed", error=str(e), falling_back="jina")

        # Provider 2: Jina AI (FREE: works without key, 1M tokens/day)
        try:
            embedding = await self._try_jina(text)
            logger.info("embedding_provider", provider="jina", dimensions=self.DIMENSIONS)
            return embedding
        except Exception as e:
            logger.warning("jina_failed", error=str(e), falling_back="huggingface")

        # Provider 3: Hugging Face (FREE: works without key, 30k calls/month)
        try:
            embedding = await self._try_huggingface(text)
            logger.info("embedding_provider", provider="huggingface", dimensions=self.DIMENSIONS)
            return embedding
        except Exception as e:
            logger.error("huggingface_failed", error=str(e))

        # Final fallback: zero vector
        logger.warning("embedding_fallback_zero_vector")
        return [0.0] * self.DIMENSIONS

    async def _try_gemini(self, text: str) -> List[float]:
        """Generate embedding via Gemini API (requires GEMINI_API_KEY)."""
        if not self._gemini_key:
            raise RuntimeError("GEMINI_API_KEY não configurada")

        payload = {
            "model": "models/gemini-embedding-001",
            "content": {
                "parts": [{"text": text}]
            },
            "taskType": "RETRIEVAL_QUERY",
            "outputDimensionality": self.DIMENSIONS,
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self._gemini_key
        }

        async with httpx.AsyncClient(timeout=self.GEMINI_TIMEOUT) as client:
            response = await client.post(
                self.GEMINI_API_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            if "embedding" not in data or "values" not in data["embedding"]:
                raise RuntimeError("Resposta Gemini inválida: sem embedding")

            embedding = data["embedding"]["values"]

            if len(embedding) != self.DIMENSIONS:
                raise RuntimeError(
                    f"Dimensão inesperada: {len(embedding)}, esperado: {self.DIMENSIONS}"
                )

            return embedding

    async def _try_jina(self, text: str) -> List[float]:
        """Generate embedding via Jina AI (free, works without API key)."""
        headers = {"Content-Type": "application/json"}
        if self._jina_key:
            headers["Authorization"] = f"Bearer {self._jina_key}"

        payload = {
            "model": "jina-embeddings-v2-base-en",
            "input": [text]
        }

        async with httpx.AsyncClient(timeout=self.JINA_TIMEOUT) as client:
            response = await client.post(
                self.JINA_API_URL,
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    embedding = data["data"][0]["embedding"]
                    # Pad or truncate to DIMENSIONS
                    if len(embedding) < self.DIMENSIONS:
                        return embedding + [0.0] * (self.DIMENSIONS - len(embedding))
                    return embedding[: self.DIMENSIONS]

            raise RuntimeError(f"Jina API error {response.status_code}: {response.text[:200]}")

    async def _try_huggingface(self, text: str) -> List[float]:
        """Generate embedding via HuggingFace Inference API (free, works without API key)."""
        headers = {}
        if self._hf_key:
            headers["Authorization"] = f"Bearer {self._hf_key}"

        async with httpx.AsyncClient(timeout=self.HF_TIMEOUT) as client:
            response = await client.post(
                self.HF_API_URL,
                json={"inputs": text},
                headers=headers
            )

            if response.status_code == 200:
                embeddings = response.json()
                if isinstance(embeddings, list) and len(embeddings) > 0:
                    embedding = embeddings[0] if isinstance(embeddings[0], list) else embeddings
                    # Pad from 384 to 768
                    if len(embedding) < self.DIMENSIONS:
                        return embedding + [0.0] * (self.DIMENSIONS - len(embedding))
                    return embedding[: self.DIMENSIONS]

            raise RuntimeError(
                f"HuggingFace API error {response.status_code}: {response.text[:200]}"
            )
