#!/usr/bin/env python
"""
This script provides utility functions for monitoring and handling file changes
within the Telegram bot framework. It is designed to be executed as a standalone
script or imported as a module to leverage its file watching capabilities.
"""
# -*- coding: utf-8 -*-

def check_port(host, port):
    """
    Check if a port is open on a remote host.

    Args:
        host (str): The remote host to check.
        port (int): The port number to check.

    Returns:
        bool: True if the port is open, False otherwise.
    """
    # import the socket module
    import socket

    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # set the timeout for the socket
    s.settimeout(1)

    # try to connect to the remote host and port
    try:
        s.connect((host, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()
        
if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print('Usage: python util_watch.py <host> <port>')
        # sys.exit(1)
        # do a unit test if no arguments are provided
        sys.argv.append('127.0.0.1')
        sys.argv.append(80)

    host = sys.argv[1]
    port = int(sys.argv[2])

    if check_port(host, port):
        print('Port {} is open on host {}'.format(port, host))
    else:
        print('Port {} is closed on host {}'.format(port, host))