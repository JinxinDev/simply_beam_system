# setup.py
from setuptools import setup, find_packages

setup(
    name="simply_beam_system",
    version="0.1.0",
    author="Jinxin Chen",
    author_email="jchen161@stevens.edu",
    description="A simple beam design system using an LLM.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JinxinDev/simply_beam_system",  # Updated URL
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "openai",
        "python-dotenv",
        # Add other dependencies as needed, e.g., "numpy", "scipy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Or another license, if you prefer
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules"

    ],
    python_requires=">=3.7",  # Or your minimum supported Python version
)