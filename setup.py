#!/usr/bin/env python3
"""Setup script for UR Robot Controller."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ur-robot-controller",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Python library for controlling Universal Robots arms via RTDE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ur-robot-controller",
    packages=find_packages(),
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
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translators",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "ur-rtde>=1.6.0",
        "PyYAML>=6.0",
        "numpy>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "flake8>=7.0.0",
            "black",
            "isort",
        ],
        "visualization": [
            "matplotlib>=3.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ur-setup-physical=scripts.setup_physical_robot:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.jsonl", "*.md"],
    },
)
