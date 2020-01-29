from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dbreak',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/jrhege/dbreak',
    author='Johnathon Hege',
    description='Console for live debugging of development databases',
    long_description=long_description,
    long_description_content_type='text/markdown',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords="development database",
    python_requires='>=3.6',

    install_requires=[
        'tabulate>=0.8.6'
    ],

    tests_require=[
        "pytest>=5.3.5"
    ],

    entry_points={
        "connection_wrappers": [
            "dbapi = dbreak.dbapi:DBAPIWrapper"
        ]
    }
)
