import pytest
import logging
from semantic_kernel.memory import MemoryRecord
from src.memory.memory_store import EnhancedMemoryStore

logger = logging.getLogger(__name__)

@pytest.fixture
async def memory_store():
    """Create a memory store instance for testing"""
    store = EnhancedMemoryStore(collection_name="test_memory")
    return store

@pytest.mark.asyncio
async def test_save_short_term_memory(memory_store):
    """Test saving a record to short-term memory"""
    try:
        record = MemoryRecord(
            id="test1",
            text="Test short-term memory",
            embedding=[0.1, 0.2, 0.3],
            metadata={"source": "test"}
        )
        
        result = await memory_store.save_short_term_memory("test_collection", record)
        assert result == "test1"
        logger.info("Short-term memory save test passed successfully")
    except Exception as e:
        logger.error(f"Short-term memory save test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_save_long_term_memory(memory_store):
    """Test saving a record to long-term memory"""
    try:
        record = MemoryRecord(
            id="test2",
            text="Test long-term memory",
            embedding=[0.4, 0.5, 0.6],
            metadata={"source": "test"}
        )
        
        result = await memory_store.save_long_term_memory("test_collection", record)
        assert result == "test2"
        logger.info("Long-term memory save test passed successfully")
    except Exception as e:
        logger.error(f"Long-term memory save test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_search_memory(memory_store):
    """Test searching memories"""
    try:
        # Save test records
        short_term_record = MemoryRecord(
            id="test3",
            text="Short term test memory for search",
            embedding=[0.1, 0.2, 0.3],
            metadata={"source": "test"}
        )
        long_term_record = MemoryRecord(
            id="test4",
            text="Long term test memory for search",
            embedding=[0.4, 0.5, 0.6],
            metadata={"source": "test"}
        )
        
        await memory_store.save_short_term_memory("test_collection", short_term_record)
        await memory_store.save_long_term_memory("test_collection", long_term_record)
        
        # Test search
        results = await memory_store.search_memory(
            collection="test_collection",
            query="test memory",
            limit=10
        )
        
        assert len(results) > 0
        logger.info("Memory search test passed successfully")
    except Exception as e:
        logger.error(f"Memory search test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_get_memory(memory_store):
    """Test retrieving a specific memory"""
    try:
        # Save test record
        record = MemoryRecord(
            id="test5",
            text="Test memory for retrieval",
            embedding=[0.7, 0.8, 0.9],
            metadata={"source": "test"}
        )
        
        await memory_store.save_short_term_memory("test_collection", record)
        
        # Test retrieval
        result = await memory_store.get_memory("test_collection", "test5")
        assert result is not None
        assert result.id == "test5"
        assert result.text == "Test memory for retrieval"
        logger.info("Memory retrieval test passed successfully")
    except Exception as e:
        logger.error(f"Memory retrieval test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_remove_memory(memory_store):
    """Test removing a memory"""
    try:
        # Save test record
        record = MemoryRecord(
            id="test6",
            text="Test memory for removal",
            embedding=[0.1, 0.2, 0.3],
            metadata={"source": "test"}
        )
        
        await memory_store.save_short_term_memory("test_collection", record)
        
        # Test removal
        await memory_store.remove_memory("test_collection", "test6")
        
        # Verify removal
        result = await memory_store.get_memory("test_collection", "test6")
        assert result is None
        logger.info("Memory removal test passed successfully")
    except Exception as e:
        logger.error(f"Memory removal test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_memory_ttl(memory_store):
    """Test time-to-live functionality for short-term memory"""
    try:
        record = MemoryRecord(
            id="test7",
            text="Test memory with TTL",
            embedding=[0.1, 0.2, 0.3],
            metadata={"source": "test"}
        )
        
        # Save with 1 second TTL
        await memory_store.save_short_term_memory(
            "test_collection",
            record,
            ttl=1
        )
        
        # Verify immediate retrieval works
        result = await memory_store.get_memory("test_collection", "test7")
        assert result is not None
        
        # Wait for TTL to expire
        import asyncio
        await asyncio.sleep(2)
        
        # Verify memory has expired
        result = await memory_store.get_memory("test_collection", "test7")
        assert result is None
        logger.info("Memory TTL test passed successfully")
    except Exception as e:
        logger.error(f"Memory TTL test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_get_collections(memory_store):
    """Test retrieving list of collections"""
    try:
        collections = await memory_store.get_collections()
        assert isinstance(collections, list)
        assert "test_collection" in collections
        logger.info("Get collections test passed successfully")
    except Exception as e:
        logger.error(f"Get collections test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_error_handling(memory_store):
    """Test error handling scenarios"""
    try:
        # Test invalid collection
        with pytest.raises(Exception):
            await memory_store.search_memory("invalid_collection", "test")
            
        # Test invalid memory key
        with pytest.raises(Exception):
            await memory_store.get_memory("test_collection", "invalid_key")
            
        # Test invalid TTL
        with pytest.raises(Exception):
            record = MemoryRecord(
                id="test8",
                text="Test invalid TTL",
                embedding=[0.1, 0.2, 0.3],
                metadata={"source": "test"}
            )
            await memory_store.save_short_term_memory(
                "test_collection",
                record,
                ttl=-1
            )
            
        logger.info("Error handling tests passed successfully")
    except Exception as e:
        logger.error(f"Error handling tests failed: {str(e)}")
        raise
