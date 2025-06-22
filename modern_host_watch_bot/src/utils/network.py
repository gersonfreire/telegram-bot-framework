"""
Network utilities for host monitoring.
"""
import asyncio
import socket
import subprocess
import platform
from typing import Tuple, Optional
import time
import logging

logger = logging.getLogger(__name__)


class NetworkChecker:
    """Network connectivity checker."""
    
    def __init__(self, timeout: float = 1.0):
        self.timeout = timeout
    
    async def ping_host(self, host: str) -> Tuple[bool, Optional[int]]:
        """
        Ping a host and return status and response time.
        
        Args:
            host: Host address to ping
            
        Returns:
            Tuple of (is_online, response_time_ms)
        """
        try:
            start_time = time.time()
            
            # Use different ping command based on OS
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", str(int(self.timeout * 1000)), host]
            else:
                cmd = ["ping", "-c", "1", "-W", str(int(self.timeout)), host]
            
            # Run ping command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.timeout + 1
            )
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            is_online = process.returncode == 0
            
            if is_online:
                logger.debug(f"Host {host} is online (response time: {response_time_ms}ms)")
            else:
                logger.debug(f"Host {host} is offline")
            
            return is_online, response_time_ms
            
        except asyncio.TimeoutError:
            logger.warning(f"Ping timeout for host {host}")
            return False, None
        except Exception as e:
            logger.error(f"Error pinging host {host}: {e}")
            return False, None
    
    async def check_port(self, host: str, port: int) -> bool:
        """
        Check if a TCP port is open on a host.
        
        Args:
            host: Host address
            port: Port number to check
            
        Returns:
            True if port is open, False otherwise
        """
        try:
            # Create socket with timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Try to connect
            result = sock.connect_ex((host, port))
            sock.close()
            
            is_open = result == 0
            
            if is_open:
                logger.debug(f"Port {port} is open on {host}")
            else:
                logger.debug(f"Port {port} is closed on {host}")
            
            return is_open
            
        except Exception as e:
            logger.error(f"Error checking port {port} on {host}: {e}")
            return False
    
    async def check_host_comprehensive(self, host: str, port: int) -> Tuple[bool, bool, Optional[int]]:
        """
        Perform comprehensive host check including ping and port check.
        
        Args:
            host: Host address
            port: Port to check
            
        Returns:
            Tuple of (ping_success, port_open, response_time_ms)
        """
        # Run ping and port check concurrently
        ping_task = asyncio.create_task(self.ping_host(host))
        port_task = asyncio.create_task(self.check_port(host, port))
        
        try:
            ping_result, port_result = await asyncio.gather(
                ping_task, port_task, return_exceptions=True
            )
            
            # Handle ping result
            if isinstance(ping_result, Exception):
                logger.error(f"Ping error for {host}: {ping_result}")
                ping_success, response_time = False, None
            else:
                ping_success, response_time = ping_result
            
            # Handle port result
            if isinstance(port_result, Exception):
                logger.error(f"Port check error for {host}: {port_result}")
                port_open = False
            else:
                port_open = port_result
            
            return ping_success, port_open, response_time
            
        except Exception as e:
            logger.error(f"Error in comprehensive check for {host}: {e}")
            return False, False, None


# Global instance
network_checker = NetworkChecker() 