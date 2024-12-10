#!/usr/bin/env python3

import os
import sys
import time
import logging
import psycopg2
import pymongo
import redis
import requests
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/semantic-kernel-db.log')
    ]
)
logger = logging.getLogger(__name__)

def get_env_vars() -> Dict[str, str]:
    """Get required environment variables."""
    required_vars = [
        'POSTGRES_CONNECTION',
        'MONGODB_URI',
        'REDIS_URL',
        'VECTOR_STORE_URL'
    ]
    
    env_vars = {}
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            logger.error(f"Missing required environment variable: {var}")
            sys.exit(1)
        env_vars[var] = value
    
    return env_vars

def verify_postgres(conn_string: str, max_retries: int = 5) -> None:
    """Verify PostgreSQL connection."""
    for attempt in range(max_retries):
        try:
            with psycopg2.connect(conn_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    logger.info("PostgreSQL connection successful")
                    return
        except Exception as e:
            logger.warning(f"PostgreSQL connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                logger.error("Failed to connect to PostgreSQL")
                sys.exit(1)

def verify_mongodb(uri: str, max_retries: int = 5) -> None:
    """Verify MongoDB connection."""
    for attempt in range(max_retries):
        try:
            client = pymongo.MongoClient(uri)
            client.admin.command('ping')
            logger.info("MongoDB connection successful")
            client.close()
            return
        except Exception as e:
            logger.warning(f"MongoDB connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                logger.error("Failed to connect to MongoDB")
                sys.exit(1)

def verify_redis(url: str, max_retries: int = 5) -> None:
    """Verify Redis connection."""
    for attempt in range(max_retries):
        try:
            client = redis.from_url(url)
            client.ping()
            logger.info("Redis connection successful")
            client.close()
            return
        except Exception as e:
            logger.warning(f"Redis connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                logger.error("Failed to connect to Redis")
                sys.exit(1)

def verify_chromadb(url: str, max_retries: int = 5) -> None:
    """Verify ChromaDB connection."""
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{url}/api/v1/heartbeat")
            if response.status_code == 200:
                logger.info("ChromaDB connection successful")
                return
            raise Exception(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            logger.warning(f"ChromaDB connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                logger.error("Failed to connect to ChromaDB")
                sys.exit(1)

def verify_required_tables(conn_string: str) -> None:
    """Verify required PostgreSQL tables exist."""
    required_tables = [
        'vector_embeddings',
        'vector_metadata',
        'vector_indexes'
    ]
    
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                for table in required_tables:
                    cur.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = '{table}'
                        )
                    """)
                    exists = cur.fetchone()[0]
                    if not exists:
                        logger.error(f"Required table missing: {table}")
                        sys.exit(1)
                logger.info("All required PostgreSQL tables verified")
    except Exception as e:
        logger.error(f"Failed to verify required tables: {str(e)}")
        sys.exit(1)

def verify_mongodb_collections(uri: str) -> None:
    """Verify required MongoDB collections exist."""
    required_collections = [
        'memory_store',
        'knowledge_graph',
        'relationships'
    ]
    
    try:
        client = pymongo.MongoClient(uri)
        db = client.get_database()
        
        for collection in required_collections:
            if collection not in db.list_collection_names():
                logger.error(f"Required collection missing: {collection}")
                sys.exit(1)
        
        logger.info("All required MongoDB collections verified")
        client.close()
    except Exception as e:
        logger.error(f"Failed to verify MongoDB collections: {str(e)}")
        sys.exit(1)

def main():
    """Main verification routine."""
    try:
        logger.info("Starting database verification")
        
        # Get environment variables
        env_vars = get_env_vars()
        
        # Verify all connections
        verify_postgres(env_vars['POSTGRES_CONNECTION'])
        verify_mongodb(env_vars['MONGODB_URI'])
        verify_redis(env_vars['REDIS_URL'])
        verify_chromadb(env_vars['VECTOR_STORE_URL'])
        
        # Verify required database objects
        verify_required_tables(env_vars['POSTGRES_CONNECTION'])
        verify_mongodb_collections(env_vars['MONGODB_URI'])
        
        logger.info("All database verifications passed successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
