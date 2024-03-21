from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ErrorFile',
    version='0.1.1',
    packages=find_packages(),
    author='Hellohistory',
    author_email='etojsyc521@gmail.com',
    description='This is a package for handling error files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Hellohistory/Errorfile',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    keywords='error file',
    python_requires='>=3.6',
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
