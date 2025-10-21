from setuptools import setup, find_packages

setup(
    name="scoring-algorithms",
    version="1.0.0",
    description="Shared scoring algorithms for location-based business analysis",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="."),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
)
