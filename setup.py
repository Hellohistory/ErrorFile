from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ErrorFile",
    version="0.2.2",
    packages=find_packages(),
    author="Hellohistory",
    description="一个用于检测图片、文档、压缩包与媒体文件是否损坏的Python包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hellohistory/Errorfile",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="error file check corrupt damage inspector",
    python_requires=">=3.7",
    install_requires=[
        "pypdf2",
        "Pillow>=10.4.0,<10.5.0",
        "openpyxl",
        "xlrd",
        "python-docx",
        "python-pptx",
        "rarfile",
        "mutagen",
        "py7zr",
    ],
    project_urls={
        "Bug Reports": "https://github.com/Hellohistory/Errorfile/issues",
        "Source": "https://github.com/Hellohistory/Errorfile",
    },
)
