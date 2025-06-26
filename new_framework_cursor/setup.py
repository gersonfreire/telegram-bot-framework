from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tlgfwk",
    version="1.0.0",
    author="Telegram Bot Framework Contributors",
    author_email="contact@tlgfwk.dev",
    description="A comprehensive Python framework for building Telegram bots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gersonfreire/telegram-bot-framework",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=7.0.0",
        ],
        "payments": [
            "stripe>=7.0.0",
            "paypal-python-sdk>=1.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tlgfwk=tlgfwk.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 