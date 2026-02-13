"""
Setup script for x402 Bazaar Auto-GPT Plugin
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="x402-autogpt-plugin",
    version="0.1.0",
    description="Auto-GPT plugin for x402 Bazaar - access 70+ paid APIs with automatic USDC payments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="x402 Bazaar",
    author_email="hello@x402-bazaar.com",
    url="https://x402-api.onrender.com",
    project_urls={
        "Homepage": "https://x402-api.onrender.com",
        "Documentation": "https://github.com/x402-bazaar/x402-autogpt-plugin#readme",
        "Repository": "https://github.com/x402-bazaar/x402-autogpt-plugin",
        "Issues": "https://github.com/x402-bazaar/x402-autogpt-plugin/issues",
        "Marketplace": "https://x402-bazaar.vercel.app",
    },
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "auto-gpt-plugin-template>=0.0.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
            "types-requests>=2.28.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
    ],
    keywords=[
        "autogpt",
        "plugin",
        "x402",
        "api-marketplace",
        "web3",
        "usdc",
        "base",
        "payment-protocol",
        "autonomous-agents",
    ],
    entry_points={
        "autogpt_plugins": [
            "x402_bazaar = x402_bazaar:register",
        ],
    },
)
