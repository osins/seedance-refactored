"""Session management for API clients"""

import requests
from typing import Optional, Dict, Any
from ..client.connection_pool import ConnectionPoolManager
from ..client.retry_mechanism import apply_retry_to_session, create_retry_strategy


class SessionManagement:
    """Manage sessions for API requests"""

    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 20, max_retries: int = 3):
        """
        Initialize session management.
        
        Args:
            pool_connections: Number of connection pools
            pool_maxsize: Maximum number of connections in pool
            max_retries: Maximum number of retries for failed requests
        """
        self.connection_pool_manager = ConnectionPoolManager(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries
        )

    def create_session(self, additional_headers: Optional[Dict[str, Any]] = None) -> requests.Session:
        """
        Create a managed session with connection pooling and retry strategies.
        
        Args:
            additional_headers: Additional headers to add to the session
            
        Returns:
            Managed requests.Session object
        """
        session = self.connection_pool_manager.create_session()
        
        # Apply retry strategy to the session
        retry_strategy = create_retry_strategy()
        apply_retry_to_session(session, retry_strategy)
        
        # Add any additional headers
        if additional_headers:
            session.headers.update(additional_headers)
        
        return session

    def close_session(self, session: requests.Session):
        """
        Close a session and clean up resources.
        
        Args:
            session: Session to close
        """
        session.close()

    def reset_session(self, session: requests.Session, additional_headers: Optional[Dict[str, Any]] = None):
        """
        Reset a session with new configuration.
        
        Args:
            session: Session to reset
            additional_headers: New headers to add to the session
        """
        # Clear existing headers except for the content-type
        content_type = session.headers.get('Content-Type')
        session.headers.clear()
        if content_type:
            session.headers['Content-Type'] = content_type
        
        # Add any additional headers
        if additional_headers:
            session.headers.update(additional_headers)

    def copy_session(self, original_session: requests.Session) -> requests.Session:
        """
        Create a copy of an existing session with the same configuration.
        
        Args:
            original_session: Session to copy
            
        Returns:
            New session with same configuration as original
        """
        new_session = requests.Session()
        
        # Copy headers
        new_session.headers.update(original_session.headers)
        
        # Copy cookies
        new_session.cookies.update(original_session.cookies)
        
        # Apply the same connection pooling and retry strategy
        retry_strategy = create_retry_strategy()
        apply_retry_to_session(new_session, retry_strategy)
        
        return new_session