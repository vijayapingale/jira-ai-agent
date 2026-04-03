"""
Main ingestion pipeline for Confluence content
"""

from typing import List, Dict, Any, Optional
import asyncio
from app.ingestion.confluence_loader import ConfluenceLoader
from app.ingestion.chunking import TextChunker, DocumentChunk
from app.db.vector_store import VectorStore
from app.db.embeddings import EmbeddingsGenerator
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConfluenceIngestionPipeline:
    """Pipeline for ingesting Confluence content into vector store"""
    
    def __init__(
        self,
        confluence_loader: ConfluenceLoader,
        text_chunker: TextChunker,
        embeddings_generator: EmbeddingsGenerator,
        vector_store: VectorStore
    ):
        self.confluence_loader = confluence_loader
        self.text_chunker = text_chunker
        self.embeddings_generator = embeddings_generator
        self.vector_store = vector_store
    
    async def ingest_space(self, space_key: str, chunking_strategy: str = "paragraphs") -> Dict[str, Any]:
        """Ingest all pages from a Confluence space"""
        
        logger.info(f"Starting ingestion for space: {space_key}")
        
        try:
            # Get all pages in the space
            pages = await self.confluence_loader.get_pages_in_space(space_key)
            logger.info(f"Found {len(pages)} pages in space {space_key}")
            
            # Process each page
            total_chunks = 0
            successful_pages = 0
            
            for page in pages:
                try:
                    result = await self.ingest_page(page["id"], chunking_strategy)
                    total_chunks += result["chunks_created"]
                    successful_pages += 1
                    
                    logger.info(f"Processed page {page['id']}: {result['chunks_created']} chunks")
                    
                except Exception as e:
                    logger.error(f"Failed to process page {page['id']}: {str(e)}")
                    continue
            
            return {
                "space_key": space_key,
                "total_pages": len(pages),
                "successful_pages": successful_pages,
                "total_chunks": total_chunks,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Failed to ingest space {space_key}: {str(e)}")
            return {
                "space_key": space_key,
                "status": "failed",
                "error": str(e)
            }
    
    async def ingest_page(self, page_id: str, chunking_strategy: str = "paragraphs") -> Dict[str, Any]:
        """Ingest a single Confluence page"""
        
        logger.info(f"Ingesting page: {page_id}")
        
        try:
            # Get page content
            page = await self.confluence_loader.get_page_content(page_id)
            if not page:
                raise ValueError(f"Page {page_id} not found")
            
            # Clean HTML content
            clean_content = self.text_chunker.clean_html_content(page["content"])
            
            # Chunk the content
            if chunking_strategy == "tokens":
                chunks = self.text_chunker.chunk_by_tokens(clean_content, "confluence", page_id)
            elif chunking_strategy == "semantic":
                chunks = self.text_chunker.chunk_by_semantic_boundaries(clean_content, "confluence", page_id)
            else:  # paragraphs (default)
                chunks = self.text_chunker.chunk_by_paragraphs(clean_content, "confluence", page_id)
            
            logger.info(f"Created {len(chunks)} chunks for page {page_id}")
            
            # Generate embeddings for chunks
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = await self.embeddings_generator.generate_embeddings(chunk_texts)
            
            # Prepare documents for vector store
            documents = []
            for i, chunk in enumerate(chunks):
                document = {
                    "id": f"{page_id}_chunk_{i}",
                    "content": chunk.content,
                    "embedding": embeddings[i],
                    "metadata": {
                        "source": "confluence",
                        "page_id": page_id,
                        "page_title": page["title"],
                        "chunk_index": chunk.chunk_index,
                        "chunking_strategy": chunking_strategy
                    }
                }
                documents.append(document)
            
            # Add to vector store
            document_ids = await self.vector_store.add_documents(documents)
            
            return {
                "page_id": page_id,
                "page_title": page["title"],
                "chunks_created": len(chunks),
                "document_ids": document_ids,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to ingest page {page_id}: {str(e)}")
            return {
                "page_id": page_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def reindex_space(self, space_key: str) -> Dict[str, Any]:
        """Re-index a space (delete existing content and re-ingest)"""
        
        logger.info(f"Re-indexing space: {space_key}")
        
        try:
            # TODO: Implement deletion of existing documents from the space
            # This would involve:
            # 1. Querying vector store for documents from this space
            # 2. Deleting them in batches
            
            # Re-ingest the space
            result = await self.ingest_space(space_key)
            result["reindexed"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to re-index space {space_key}: {str(e)}")
            return {
                "space_key": space_key,
                "status": "failed",
                "error": str(e)
            }
    
    async def search_ingested_content(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search the ingested content"""
        
        try:
            results = await self.vector_store.search(query, top_k)
            return results
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
