# coding: utf-8
from setuptools import setup, find_packages

setup(
    name='sshtoy',
    version = '1.0.5',
    description= 'Connecting to remote host with one command.',
    author = 'Xiong Harry',
    author_email = 'xiongharry@gmail.com',
    url = 'https://github.com/xiongharry/sshtoy',
    packages=find_packages(),
    entry_points={
            'console_scripts': [
                'h = sshtoy.main:main',
            ]
        },
    install_requires=[
            'prettytable>=0.6.1',
            ],
    classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ],
)
