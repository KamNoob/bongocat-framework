from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bongocat",
    version="1.0.0",
    author="BongoCat Team",
    author_email="team@bongocat.dev",
    description="Advanced Web Scraping Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bongocat/bongocat",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "selenium>=4.0.0",
        "pandas>=1.5.0",
        "click>=8.0.0",
        "flask>=2.2.0",
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "bongocat=bongocat.cli:main",
        ],
    },
)