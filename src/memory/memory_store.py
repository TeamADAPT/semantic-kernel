from typing import Dict, List, Optional, Any
import logging
from semantic_kernel.memory import MemoryStore, MemoryRecord
from semantic_kernel.memory.memory_record import MemoryRecord
from semantic_kernel.connectors.memory.chroma import ChromaMemoryStore
import chromadb
from chromadb.config import Settings
import json

logger = logging.getLogger(__name__)

class EnhancedMemoryStore:
    """
    Enhanced memory store implementation that supports both short-term and long-term memory,
    with integration for multiple databases and RAG capabilities.
    """

    def __init__(self, 
                 chroma_settings: Optional[Dict[str, Any]] = None,
                 collection_name: str = "semantic_memory"):
        """
        Initialize the enhanced memory store
        
        Args:
            chroma_settings: Optional settings for ChromaDB
            collection_name: Name of the collection to use
        """
        self.settings = chroma_settings or {}
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="data/chroma",
            anonymized_telemetry=False,
            **self.settings
        ))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # Initialize memory stores for different types
        self.short_term_store = ChromaMemoryStore(client=self.client)
        self.long_term_store = ChromaMemoryStore(client=self.client)
        
        logger.info(f"Initialized enhanced memory store with collection: {collection_name}")

    async def save_short_term_memory(self, 
                                   collection: str,
                                   record: MemoryRecord,
                                   ttl: Optional[int] = 3600) -> str:
        """
        Save a memory record to short-term memory
        
        Args:
            collection: Collection to save to
            record: Memory record to save
            ttl: Time to live in seconds (default 1 hour)
            
        Returns:
            str: ID of saved record
        """
        try:
            # Add TTL metadata
            record.metadata["ttl"] = ttl
            record.metadata["memory_type"] = "short_term"
            
            # Save to short-term store
            return await self.short_term_store.upsert_async(collection, record)
        except Exception as e:
            logger.error(f"Failed to save short-term memory: {str(e)}")
            raise

    async def save_long_term_memory(self,
                                  collection: str,
                                  record: MemoryRecord) -> str:
        """
        Save a memory record to long-term memory
        
        Args:
            collection: Collection to save to
            record: Memory record to save
            
        Returns:
            str: ID of saved record
        """
        try:
            # Add memory type metadata
            record.metadata["memory_type"] = "long_term"
            
            # Save to long-term store
            return await self.long_term_store.upsert_async(collection, record)
        except Exception as e:
            logger.error(f"Failed to save long-term memory: {str(e)}")
            raise

    async def search_memory(self,
                          collection: str,
                          query: str,
                          limit: int = 10,
                          min_relevance: float = 0.7,
                          memory_type: Optional[str] = None) -> List[MemoryRecord]:
        """
        Search memories across both short-term and long-term stores
        
        Args:
            collection: Collection to search in
            query: Search query
            limit: Maximum number of results
            min_relevance: Minimum relevance score
            memory_type: Optional filter for memory type ("short_term" or "long_term")
            
        Returns:
            List[MemoryRecord]: Matching memory records
        """
        try:
            results = []
            
            # Search in appropriate stores based on memory_type
            if memory_type == "short_term" or memory_type is None:
                short_term_results = await self.short_term_store.search_async(
                    collection=collection,
                    query=query,
                    limit=limit,
                    min_relevance_score=min_relevance,
                    filter={"memory_type": "short_term"}
                )
                results.extend(short_term_results)
                
            if memory_type == "long_term" or memory_type is None:
                long_term_results = await self.long_term_store.search_async(
                    collection=collection,
                    query=query,
                    limit=limit,
                    min_relevance_score=min_relevance,
                    filter={"memory_type": "long_term"}
                )
                results.extend(long_term_results)
            
            # Sort by relevance and limit results
            results.sort(key=lambda x: x.relevance, reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search memory: {str(e)}")
            raise

    async def get_memory(self,
                        collection: str,
                        key: str,
                        with_embedding: bool = False) -> Optional[MemoryRecord]:
        """
        Retrieve a specific memory record by key
        
        Args:
            collection: Collection to retrieve from
            key: Key of the memory record
            with_embedding: Whether to include embeddings
            
        Returns:
            Optional[MemoryRecord]: Retrieved memory record if found
        """
        try:
            # Try short-term first
            record = await self.short_term_store.get_async(collection, key, with_embedding)
            if record:
                return record
                
            # Try long-term if not found in short-term
            return await self.long_term_store.get_async(collection, key, with_embedding)
        except Exception as e:
            logger.error(f"Failed to get memory: {str(e)}")
            raise

    async def remove_memory(self,
                          collection: str,
                          key: str) -> None:
        """
        Remove a memory record from both stores
        
        Args:
            collection: Collection to remove from
            key: Key of the memory record to remove
        """
        try:
            # Remove from both stores
            await self.short_term_store.remove_async(collection, key)
            await self.long_term_store.remove_async(collection, key)
        except Exception as e:
            logger.error(f"Failed to remove memory: {str(e)}")
            raise

    async def get_collections(self) -> List[str]:
        """
        Get list of all collections
        
        Returns:
            List[str]: List of collection names
        """
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Failed to get collections: {str(e)}")
            raise
