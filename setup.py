from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ErrorFile',
    version='0.1.2',
    packages=find_packages(),
    author='Hellohistory',
    author_email='etojsyc521@gmail.com',
    description='一个用于检测图片、PDF、Excel和Word等文件是否损坏的Python包',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Hellohistory/Errorfile',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='error file check corrupt damage inspector',
    python_requires='>=3.7',
    install_requires=[
        'pypdf2',
        'Pillow',
        'openpyxl',
        'xlrd',
        'python-docx',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/Hellohistory/Errorfile/issues',
        'Source': 'https://github.com/Hellohistory/Errorfile',
    },
)