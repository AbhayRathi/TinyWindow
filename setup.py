"""Setup configuration for TinyWindow."""

from setuptools import setup, find_packages

setup(
    name="tinywindow",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "flake8>=6.1.0",
            "black>=23.7.0",
            "mypy>=1.5.0",
        ],
    },
    python_requires=">=3.10",
)
