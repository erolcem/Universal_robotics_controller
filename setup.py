#!/usr/bin/env python3
"""Setup script for UR Robot Controller."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

"""
UR Robot Controller Setup
A comprehensive Python library for controlling Universal Robots through RTDE.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open('requirements.txt') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

setup(
    name="ur-robot-controller",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive Python library for controlling Universal Robots through RTDE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ur-robot-controller",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/ur-robot-controller/issues",
        "Documentation": "https://github.com/yourusername/ur-robot-controller#readme",
        "Source Code": "https://github.com/yourusername/ur-robot-controller",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ur-check-status=scripts.check_robot_status:main",
            "ur-visual-test=scripts.visual_test:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.jsonl", "*.md"],
    },
    keywords="robotics universal-robots ur rtde control automation",
    zip_safe=False,
)
