from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='chapman-py',  # Required
    version='0.1.0',  # Required

    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='A Markov-chain class', # Optional
    long_description=long_description,  # Optional
    url='https://github.com/gordanz/chapman',  # Optional
    author='Gordan Zitkovic',
    author_email='gordanz@math.utexas.edu',  # Optional
    #keywords='sample setuptools development',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    python_requires='>=3.5, <4',
    install_requires=['numpy','scipy','networkx>=2.3'],  # Optional
    project_urls={  # Optional
        'Source': 'https://github.com/gordanz/chapman/'
    },
)
