#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ["PySide6==6.9.1",
"altgraph==0.17.4"
"auto-py-to-exe==2.46.0",
"bottle==0.13.3",
"bottle-websocket==0.2.9",
"certifi==2025.4.26",
"cffi==1.17.1",
"charset-normalizer==3.4.2",
"Eel==0.18.1",
"future==1.0.0",
"gevent==25.5.1",
"gevent-websocket==0.10.1",
"greenlet==3.2.3",
"idna==3.10",
"lxml==5.4.0",
"numpy==2.3.0",
"packaging==25.0",
"pandas==2.3.0",
"pefile==2023.2.7",
"pyarrow==20.0.0",
"pycparser==2.22",
"pyinstaller==6.14.1",
"pyinstaller-hooks-contrib==2025.5",
"pyparsing==3.2.3",
"python-dateutil==2.9.0.post0",
"pytz==2025.2",
"pywin32-ctypes==0.2.3",
"requests==2.32.4",
"setuptools==80.9.0",
"shiboken6==6.9.1",
"six==1.17.0",
"typing_extensions==4.14.0",
"tzdata==2025.2",
"urllib3==2.4.0",
"zope.event==5.0",
"zope.interface==7.2"
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
    version='1.0.4',
    zip_safe=False,
)
