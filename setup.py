#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='fruitbasket',
    version='0.1.0',
    description="Simple python vfx pipeline tool to setup and maintain project structure. ",
    long_description=readme + '\n\n' + history,
    author="Ian Matthew Hartman",
    author_email='ian.hartman95@gmail.com',
    url='https://github.com/Hartman-/fruitbasket',
    packages=[
        'fruitbasket',
    ],
    package_dir={'fruitbasket':
                 'fruitbasket'},
    entry_points={
        'console_scripts': [
            'fruitbasket=fruitbasket.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='fruitbasket',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
