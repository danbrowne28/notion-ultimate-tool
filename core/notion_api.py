"""Notion API wrapper with caching and rate limiting."""

import time
from typing import Dict, List, Optional, Any
from notion_client import Client
from notion_client.errors import APIResponseError, RequestTimeoutError

from .config import Config
from .database import LocalCache
from .utils import RateLimiter, Logger


class NotionAPI:
    """Unified Notion API wrapper with intelligent caching and rate limiting."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize Notion API client.
        
        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or Config()
        self.client = Client(auth=self.config.notion_token)
        self.cache = LocalCache(self.config.cache_db_path)
        self.rate_limiter = RateLimiter(max_requests_per_second=3)
        self.logger = Logger("NotionAPI")
        
    def _execute_with_retry(self, func, *args, max_retries=3, **kwargs):
        """Execute API call with automatic retry on rate limit."""
        for attempt in range(max_retries):
            try:
                self.rate_limiter.wait()
                return func(*args, **kwargs)
            except APIResponseError as e:
                if e.code == "rate_limited" and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
            except RequestTimeoutError as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Timeout, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(1)
                else:
                    raise
        
    def query_database(
        self, 
        database_id: Optional[str] = None,
        filter_dict: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None,
        use_cache: bool = True,
        cache_ttl: int = 300  # 5 minutes default
    ) -> List[Dict]:
        """Query Notion database with caching.
        
        Args:
            database_id: Database ID (uses config default if None)
            filter_dict: Notion filter object
            sorts: List of sort objects
            use_cache: Whether to use cache
            cache_ttl: Cache time-to-live in seconds
            
        Returns:
            List of page objects
        """
        db_id = database_id or self.config.database_id
        
        # Check cache first
        if use_cache:
            cache_key = self.cache.generate_key("query", db_id, filter_dict, sorts)
            cached = self.cache.get(cache_key, max_age=cache_ttl)
            if cached:
                self.logger.debug(f"Cache hit for query {cache_key[:8]}...")
                return cached
        
        # Query API
        self.logger.info(f"Querying database {db_id[:8]}...")
        results = []
        has_more = True
        start_cursor = None
        
        while has_more:
            response = self._execute_with_retry(
                self.client.databases.query,
                database_id=db_id,
                filter=filter_dict,
                sorts=sorts,
                start_cursor=start_cursor
            )
            results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")
        
        # Cache results
        if use_cache:
            self.cache.set(cache_key, results)
        
        self.logger.info(f"Retrieved {len(results)} pages")
        return results
    
    def get_page(self, page_id: str, use_cache: bool = True) -> Dict:
        """Get page by ID with caching."""
        if use_cache:
            cache_key = self.cache.generate_key("page", page_id)
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        page = self._execute_with_retry(self.client.pages.retrieve, page_id=page_id)
        
        if use_cache:
            self.cache.set(cache_key, page)
        
        return page
    
    def update_page(self, page_id: str, properties: Dict) -> Dict:
        """Update page properties and invalidate cache."""
        self.logger.info(f"Updating page {page_id[:8]}...")
        
        result = self._execute_with_retry(
            self.client.pages.update,
            page_id=page_id,
            properties=properties
        )
        
        # Invalidate cache
        self.cache.invalidate(f"page:{page_id}")
        self.cache.invalidate_pattern("query:*")  # Invalidate all queries
        
        self.logger.info(f"Page {page_id[:8]} updated successfully")
        return result
    
    def create_page(self, database_id: str, properties: Dict, children: Optional[List] = None) -> Dict:
        """Create new page in database."""
        self.logger.info(f"Creating page in database {database_id[:8]}...")
        
        result = self._execute_with_retry(
            self.client.pages.create,
            parent={"database_id": database_id},
            properties=properties,
            children=children or []
        )
        
        # Invalidate query caches
        self.cache.invalidate_pattern("query:*")
        
        self.logger.info(f"Page created: {result['id']}")
        return result
    
    def batch_update_pages(
        self, 
        updates: List[Dict[str, Any]],
        delay_between_requests: float = 0.4
    ) -> List[Dict]:
        """Batch update multiple pages with rate limiting.
        
        Args:
            updates: List of dicts with 'page_id' and 'properties' keys
            delay_between_requests: Delay between requests in seconds
            
        Returns:
            List of update results
        """
        results = []
        total = len(updates)
        
        for i, update in enumerate(updates, 1):
            self.logger.info(f"Updating {i}/{total}: {update['page_id'][:8]}...")
            
            try:
                result = self.update_page(update["page_id"], update["properties"])
                results.append({"success": True, "page_id": update["page_id"], "result": result})
            except Exception as e:
                self.logger.error(f"Failed to update {update['page_id'][:8]}: {e}")
                results.append({"success": False, "page_id": update["page_id"], "error": str(e)})
            
            # Rate limiting
            if i < total:
                time.sleep(delay_between_requests)
        
        success_count = sum(1 for r in results if r["success"])
        self.logger.info(f"Batch update complete: {success_count}/{total} successful")
        
        return results
    
    def get_database_schema(self, database_id: Optional[str] = None) -> Dict:
        """Get database schema/properties."""
        db_id = database_id or self.config.database_id
        
        db = self._execute_with_retry(self.client.databases.retrieve, database_id=db_id)
        return db.get("properties", {})
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear()
        self.logger.info("Cache cleared")
