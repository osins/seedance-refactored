"""Connection pool management for API requests"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional


class ConnectionPoolManager:
    """Manage connection pooling for API requests"""

    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 20, max_retries: int = 3):
        """
        Initialize connection pool manager.
        
        Args:
            pool_connections: Number of connection pools
            pool_maxsize: Maximum number of connections in pool
            max_retries: Maximum number of retries for failed requests
        """
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.max_retries = max_retries

    def create_session(self) -> requests.Session:
        """
        Create a requests session with connection pooling configured.
        
        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        # Create adapter with connection pooling settings
        adapter = HTTPAdapter(
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize,
            max_retries=retry_strategy
        )
        
        # Mount adapters for HTTP and HTTPS
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "Content-Type": "application/json"
        })
        
        return session

    def configure_session_headers(self, session: requests.Session, additional_headers: Optional[dict] = None):
        """
        Configure headers for a session.
        
        Args:
            session: requests.Session object to configure
            additional_headers: Additional headers to add to the session
        """
        if additional_headers:
            session.headers.update(additional_headers)