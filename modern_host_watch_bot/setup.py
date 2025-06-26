#!/usr/bin/env python3
"""
Setup script for Modern Host Watch Bot.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = (this_directory / "requirements.txt").read_text().splitlines()

setup(
    name="modern-host-watch-bot",
    version="1.0.0",
    author="Modern Host Watch Bot Team",
    author_email="team@modernhostwatchbot.com",
    description="A modern Telegram bot for monitoring hosts and services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/modern-host-watch-bot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Monitoring",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.12.0",
            "isort>=5.13.2",
            "mypy>=1.8.0",
            "coverage>=7.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "modern-host-watch-bot=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.toml"],
    },
    keywords=[
        "telegram",
        "bot",
        "monitoring",
        "host",
        "ping",
        "network",
        "ssh",
        "system",
        "administration",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/modern-host-watch-bot/issues",
        "Source": "https://github.com/yourusername/modern-host-watch-bot",
        "Documentation": "https://github.com/yourusername/modern-host-watch-bot/docs",
    },
) 