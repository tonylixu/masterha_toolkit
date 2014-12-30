#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'configobj',
    'six',
    'validator',
    'argparse'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='masterha_toolkit',
    version='0.2.0',
    description='Tools for MySQL MasterHA failover and monitoring',
    long_description=readme + '\n\n' + history,
    author='Tyler Mitchell',
    author_email='zastari@gmail.com',
    url='https://github.com/zastari/masterha_toolkit',
    packages=find_packages(exclude=["build", "dist", "docs", "tests"]),
    package_dir={'masterha_toolkit':
                 'masterha_toolkit'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='masterha_toolkit',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points = {
        'console_scripts': ['masterha_dispatch=masterha_toolkit.dispatch:main']
    }
)
