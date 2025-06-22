"""
SSH utilities for remote command execution.
"""
import asyncio
import paramiko
from typing import Optional, Tuple
import logging
from cryptography.fernet import Fernet
from ..config.settings import settings

logger = logging.getLogger(__name__)


class SSHManager:
    """SSH connection and command execution manager."""
    
    def __init__(self):
        self.encryption_key = Fernet(settings.encryption_key.encode())
    
    def encrypt_password(self, password: str) -> str:
        """Encrypt SSH password."""
        return self.encryption_key.encrypt(password.encode()).decode()
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt SSH password."""
        return self.encryption_key.decrypt(encrypted_password.encode()).decode()
    
    async def execute_ssh_command(
        self, 
        host: str, 
        username: str, 
        encrypted_password: str, 
        command: str, 
        port: int = 22,
        timeout: int = 30
    ) -> Tuple[bool, str, str]:
        """
        Execute a command via SSH.
        
        Args:
            host: Host address
            username: SSH username
            encrypted_password: Encrypted SSH password
            command: Command to execute
            port: SSH port
            timeout: Connection timeout
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Decrypt password
            password = self.decrypt_password(encrypted_password)
            
            # Connect to host
            ssh.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout
            )
            
            # Execute command
            stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
            
            # Get output
            stdout_str = stdout.read().decode('utf-8')
            stderr_str = stderr.read().decode('utf-8')
            
            # Wait for command to complete
            exit_code = stdout.channel.recv_exit_status()
            
            success = exit_code == 0
            
            if success:
                logger.info(f"SSH command executed successfully on {host}")
            else:
                logger.warning(f"SSH command failed on {host} with exit code {exit_code}")
            
            return success, stdout_str, stderr_str
            
        except paramiko.AuthenticationException:
            error_msg = f"Authentication failed for {username}@{host}"
            logger.error(error_msg)
            return False, "", error_msg
        except paramiko.SSHException as e:
            error_msg = f"SSH error on {host}: {e}"
            logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Error executing SSH command on {host}: {e}"
            logger.error(error_msg)
            return False, "", error_msg
        finally:
            ssh.close()
    
    async def test_ssh_connection(
        self, 
        host: str, 
        username: str, 
        encrypted_password: str, 
        port: int = 22
    ) -> bool:
        """
        Test SSH connection without executing commands.
        
        Args:
            host: Host address
            username: SSH username
            encrypted_password: Encrypted SSH password
            port: SSH port
            
        Returns:
            True if connection successful, False otherwise
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            password = self.decrypt_password(encrypted_password)
            
            ssh.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=10
            )
            
            logger.info(f"SSH connection test successful for {username}@{host}")
            return True
            
        except Exception as e:
            logger.error(f"SSH connection test failed for {username}@{host}: {e}")
            return False
        finally:
            ssh.close()


# Global instance
ssh_manager = SSHManager() 