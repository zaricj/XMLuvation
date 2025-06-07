#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['PySide6>=6.1.2',

]

test_requirements = [ ]

setup(
    author="Jovan Zaric",
    author_email='jovanzaric98@hotmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Win32 (MS Windows)',
        'Environment :: MacOS X',
        'Environment :: X11 Applications',
        'Environment :: Web Environment',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development',
        'Topic :: Communications :: Email',
        'Topic :: Office/Business',
    ],
    description="XML file searcher with xpath expressions and writing results to a csv file",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='xmluvation',
    name='xmluvation',
    packages=find_packages(include=['xmluvation', 'xmluvation.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/zaricj/xmluvation',
    version='0.1.0',
    zip_safe=False,
)
