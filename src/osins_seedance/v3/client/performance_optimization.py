"""Performance optimization features for API clients"""

import time
from typing import Callable, Any
import functools


class PerformanceOptimization:
    """Implement performance optimizations for API clients"""

    def __init__(self):
        self.metrics = {}

    def measure_execution_time(self, func: Callable) -> Callable:
        """
        Decorator to measure execution time of functions.
        
        Args:
            func: Function to measure
            
        Returns:
            Wrapped function with timing
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Store metrics
            func_name = func.__name__
            if func_name not in self.metrics:
                self.metrics[func_name] = []
            self.metrics[func_name].append(execution_time)
            
            print(f"{func_name} executed in {execution_time:.4f} seconds")
            return result
        return wrapper

    def get_average_execution_time(self, func_name: str) -> float:
        """
        Get average execution time for a function.
        
        Args:
            func_name: Name of the function
            
        Returns:
            Average execution time in seconds
        """
        if func_name in self.metrics and self.metrics[func_name]:
            times = self.metrics[func_name]
            return sum(times) / len(times)
        return 0.0

    def get_total_calls(self, func_name: str) -> int:
        """
        Get total number of calls for a function.
        
        Args:
            func_name: Name of the function
            
        Returns:
            Total number of calls
        """
        return len(self.metrics.get(func_name, []))

    def cleanup_metrics(self):
        """Clean up stored metrics."""
        self.metrics.clear()

    def batch_requests(self, requests_list: list, batch_size: int = 10) -> list:
        """
        Batch multiple requests together to improve performance.
        
        Args:
            requests_list: List of requests to batch
            batch_size: Size of each batch
            
        Returns:
            List of responses
        """
        results = []
        for i in range(0, len(requests_list), batch_size):
            batch = requests_list[i:i + batch_size]
            # Process batch (this is a simplified version)
            batch_results = [req() for req in batch]  # Execute each request in batch
            results.extend(batch_results)
        return results

    def enable_compression(self, session):
        """
        Enable compression for session requests.
        
        Args:
            session: requests.Session object to enable compression for
        """
        session.headers.update({
            'Accept-Encoding': 'gzip, deflate'
        })

    def set_connection_keep_alive(self, session):
        """
        Set connection keep-alive for session.
        
        Args:
            session: requests.Session object to configure
        """
        session.headers.update({
            'Connection': 'keep-alive'
        })