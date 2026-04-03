"""
Embeddings generation for vector search
"""

from typing import List
import numpy as np
from app.core.config import settings


class EmbeddingsGenerator:
    """Service for generating text embeddings"""
    
    def __init__(self):
        self.model_name = "text-embedding-ada-002"  # or other embedding model
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        
        # TODO: Implement embedding generation
        # This would involve:
        # 1. Calling OpenAI embedding API or local model
        # 2. Handling API errors and rate limits
        # 3. Returning embedding as list of floats
        
        # Placeholder embedding (1536 dimensions for OpenAI ada-002)
        return [0.1] * 1536
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        
        # TODO: Implement batch embedding generation
        # This would involve:
        # 1. Processing texts in batches
        # 2. Making parallel API calls when possible
        # 3. Handling partial failures
        
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
