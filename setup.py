from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

CORE_DEPENDENCIES = []

PLUGIN_DEPENDENCIES = {
    "pdf": ["pypdf2~=3.0.1"],
    "image": ["Pillow>=10.4.0,<10.5.0"],
    "office": ["openpyxl~=3.1.2", "xlrd~=1.2.0", "python-docx~=0.8.11", "python-pptx~=1.0.2"],
    "archive": ["rarfile~=4.2", "py7zr~=0.20.8"],
    "media": ["mutagen~=1.47.0"],
}

all_dependencies = sorted(
    {dependency for deps in PLUGIN_DEPENDENCIES.values() for dependency in deps}
)

setup(
    name="ErrorFile",
    version="0.2.2",
    packages=find_packages(),
    author="Hellohistory",
    description="Python library for detecting corrupted files across multiple formats.",
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
    install_requires=CORE_DEPENDENCIES,
    extras_require={
        **PLUGIN_DEPENDENCIES,
        "all": all_dependencies,
    },
    project_urls={
        "Bug Reports": "https://github.com/Hellohistory/Errorfile/issues",
        "Source": "https://github.com/Hellohistory/Errorfile",
    },
)
