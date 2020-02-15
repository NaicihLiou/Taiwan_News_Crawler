import os

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='Taiwan_News_Crawler',
    version='2020.02.15',
    keywords='news crawler Taiwan politics',
    description='A political news crawler for 34 Taiwanese stream media.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='RitaLiou',
    author_email='imritaliou@gmail.com',    
    url='https://github.com/milkpool/Taiwan_News_Crawler',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests', 'bs4', 'selenium'],
    license='MIT'
)
