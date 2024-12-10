from typing import Dict, List, Optional, Any, Tuple
import logging
from semantic_kernel.memory import MemoryStore, MemoryRecord
from semantic_kernel.connectors.memory.chroma import ChromaMemoryStore
import chromadb
from chromadb.config import Settings
import networkx as nx
import json

logger = logging.getLogger(__name__)

class KnowledgeStore:
    """
    Knowledge store implementation that integrates with multiple databases,
    supports RAG (Retrieval Augmented Generation), and GraphRAG capabilities.
    """

    def __init__(self, 
                 chroma_settings: Optional[Dict[str, Any]] = None,
                 collection_name: str = "semantic_knowledge"):
        """
        Initialize the knowledge store
        
        Args:
            chroma_settings: Optional settings for ChromaDB
            collection_name: Name of the collection to use
        """
        self.settings = chroma_settings or {}
        self.collection_name = collection_name
        
        # Initialize ChromaDB client for vector storage
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="data/chroma",
            anonymized_telemetry=False,
            **self.settings
        ))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # Initialize knowledge graph
        self.knowledge_graph = nx.DiGraph()
        
        logger.info(f"Initialized knowledge store with collection: {collection_name}")

    async def add_knowledge(self,
                          collection: str,
                          record: MemoryRecord,
                          relationships: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Add knowledge to the store with optional relationships
        
        Args:
            collection: Collection to add to
            record: Memory record containing the knowledge
            relationships: Optional list of relationships to other knowledge
            
        Returns:
            str: ID of saved record
        """
        try:
            # Save vector embedding
            store = ChromaMemoryStore(client=self.client)
            key = await store.upsert_async(collection, record)
            
            # Add node to knowledge graph
            self.knowledge_graph.add_node(key, 
                                        text=record.text,
                                        metadata=record.metadata)
            
            # Add relationships if provided
            if relationships:
                for rel in relationships:
                    self.knowledge_graph.add_edge(
                        key,
                        rel["target_id"],
                        type=rel["type"],
                        metadata=rel.get("metadata", {})
                    )
            
            return key
        except Exception as e:
            logger.error(f"Failed to add knowledge: {str(e)}")
            raise

    async def search_knowledge(self,
                             collection: str,
                             query: str,
                             limit: int = 10,
                             min_relevance: float = 0.7,
                             use_graph: bool = True) -> List[Tuple[MemoryRecord, List[Dict[str, Any]]]]:
        """
        Search knowledge using RAG and optionally GraphRAG
        
        Args:
            collection: Collection to search in
            query: Search query
            limit: Maximum number of results
            min_relevance: Minimum relevance score
            use_graph: Whether to use GraphRAG for enhanced retrieval
            
        Returns:
            List[Tuple[MemoryRecord, List[Dict[str, Any]]]]: Matching records with related knowledge
        """
        try:
            store = ChromaMemoryStore(client=self.client)
            results = []
            
            # Get initial vector search results
            vector_results = await store.search_async(
                collection=collection,
                query=query,
                limit=limit,
                min_relevance_score=min_relevance
            )
            
            for record in vector_results:
                related_knowledge = []
                
                if use_graph and record.id in self.knowledge_graph:
                    # Get neighboring nodes up to 2 hops away
                    neighbors = nx.single_source_shortest_path_length(
                        self.knowledge_graph, record.id, cutoff=2
                    )
                    
                    for neighbor_id, distance in neighbors.items():
                        if neighbor_id != record.id:
                            neighbor_data = self.knowledge_graph.nodes[neighbor_id]
                            path = nx.shortest_path(
                                self.knowledge_graph, record.id, neighbor_id
                            )
                            
                            # Get relationship types along the path
                            relationships = []
                            for i in range(len(path)-1):
                                edge_data = self.knowledge_graph.edges[path[i], path[i+1]]
                                relationships.append(edge_data["type"])
                            
                            related_knowledge.append({
                                "id": neighbor_id,
                                "text": neighbor_data["text"],
                                "metadata": neighbor_data["metadata"],
                                "distance": distance,
                                "relationships": relationships
                            })
                
                results.append((record, related_knowledge))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search knowledge: {str(e)}")
            raise

    async def get_knowledge(self,
                          collection: str,
                          key: str,
                          with_embedding: bool = False,
                          with_relationships: bool = True) -> Optional[Tuple[MemoryRecord, List[Dict[str, Any]]]]:
        """
        Retrieve specific knowledge by key
        
        Args:
            collection: Collection to retrieve from
            key: Key of the knowledge record
            with_embedding: Whether to include embeddings
            with_relationships: Whether to include relationships
            
        Returns:
            Optional[Tuple[MemoryRecord, List[Dict[str, Any]]]]: Retrieved knowledge if found
        """
        try:
            store = ChromaMemoryStore(client=self.client)
            record = await store.get_async(collection, key, with_embedding)
            
            if record:
                related_knowledge = []
                
                if with_relationships and key in self.knowledge_graph:
                    # Get direct neighbors
                    for _, neighbor_id, edge_data in self.knowledge_graph.edges(key, data=True):
                        neighbor_data = self.knowledge_graph.nodes[neighbor_id]
                        related_knowledge.append({
                            "id": neighbor_id,
                            "text": neighbor_data["text"],
                            "metadata": neighbor_data["metadata"],
                            "relationship": edge_data["type"],
                            "relationship_metadata": edge_data.get("metadata", {})
                        })
                
                return (record, related_knowledge)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get knowledge: {str(e)}")
            raise

    async def remove_knowledge(self,
                             collection: str,
                             key: str) -> None:
        """
        Remove knowledge and its relationships
        
        Args:
            collection: Collection to remove from
            key: Key of the knowledge to remove
        """
        try:
            # Remove from vector store
            store = ChromaMemoryStore(client=self.client)
            await store.remove_async(collection, key)
            
            # Remove from knowledge graph
            if key in self.knowledge_graph:
                self.knowledge_graph.remove_node(key)
                
        except Exception as e:
            logger.error(f"Failed to remove knowledge: {str(e)}")
            raise

    def get_related_knowledge(self,
                            key: str,
                            max_distance: int = 2,
                            relationship_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get knowledge related to a specific key through the knowledge graph
        
        Args:
            key: Starting key
            max_distance: Maximum distance to traverse
            relationship_types: Optional filter for relationship types
            
        Returns:
            List[Dict[str, Any]]: Related knowledge items
        """
        try:
            if key not in self.knowledge_graph:
                return []
                
            related = []
            neighbors = nx.single_source_shortest_path_length(
                self.knowledge_graph, key, cutoff=max_distance
            )
            
            for neighbor_id, distance in neighbors.items():
                if neighbor_id != key:
                    path = nx.shortest_path(self.knowledge_graph, key, neighbor_id)
                    relationships = []
                    
                    # Check relationship types along path
                    include = True
                    for i in range(len(path)-1):
                        edge_data = self.knowledge_graph.edges[path[i], path[i+1]]
                        rel_type = edge_data["type"]
                        relationships.append(rel_type)
                        
                        if relationship_types and rel_type not in relationship_types:
                            include = False
                            break
                    
                    if include:
                        neighbor_data = self.knowledge_graph.nodes[neighbor_id]
                        related.append({
                            "id": neighbor_id,
                            "text": neighbor_data["text"],
                            "metadata": neighbor_data["metadata"],
                            "distance": distance,
                            "relationships": relationships
                        })
            
            return related
            
        except Exception as e:
            logger.error(f"Failed to get related knowledge: {str(e)}")
            raise

    def export_knowledge_graph(self, 
                             format: str = "networkx") -> Any:
        """
        Export the knowledge graph in specified format
        
        Args:
            format: Format to export ("networkx", "dict", or "json")
            
        Returns:
            Knowledge graph in specified format
        """
        try:
            if format == "networkx":
                return self.knowledge_graph
            elif format == "dict":
                return nx.node_link_data(self.knowledge_graph)
            elif format == "json":
                return json.dumps(nx.node_link_data(self.knowledge_graph))
            else:
                raise ValueError(f"Unsupported export format: {format}")
        except Exception as e:
            logger.error(f"Failed to export knowledge graph: {str(e)}")
            raise
