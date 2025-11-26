"""Setup configuration for instrument workflow simulator."""
from setuptools import setup, find_packages

setup(
    name="instrument-workflow-sim",
    version="0.1.0",
    description="Discrete-event simulation for diagnostic instrument workflows",
    author="Systems Engineering Team",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "simpy>=4.0.1",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.10",
        "jsonschema>=4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "pytest-mock>=3.6.1",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
