"""Setup script for Notion Ultimate Tool."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="notion-ultimate-tool",
    version="2.0.0",
    description="FREE, open-source, MCP-enabled Notion productivity system with AI automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dan Browne",
    author_email="",
    url="https://github.com/danbrowne28/notion-ultimate-tool",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "notion-client>=2.2.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "rich>=13.7.0",
        "click>=8.1.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "mcp": [
            "mcp>=0.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "notion-tool=notion_tool:main",
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
    ],
    keywords="notion productivity task-management automation ai mcp adhd",
    project_urls={
        "Bug Reports": "https://github.com/danbrowne28/notion-ultimate-tool/issues",
        "Source": "https://github.com/danbrowne28/notion-ultimate-tool",
        "Documentation": "https://github.com/danbrowne28/notion-ultimate-tool#readme",
    },
)
