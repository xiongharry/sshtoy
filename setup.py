# coding: utf-8
from setuptools import setup

setup(
    name='sshtoy',
    version = '1.0.3',
    description= 'SSH tools for managing remote hosts',
    author = 'Xiong Harry',
    author_email = 'xiongharry@gmail.com',
    url = 'https://github.com/xiongharry/sshtoy',
    py_modules = ['h'],
    entry_points={
            'console_scripts': [
                'h = h:main',
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
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ],
)
