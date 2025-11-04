#!/usr/bin/env python3
"""
Setup script for EasyPiper - Pythonic wrapper for Piper robotic arm control
"""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Read the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='easy_piper',
    version='0.1.0',
    author='Charith Munasinghe',
    author_email='',
    description='Pythonic wrapper for Piper robotic arm control with automatic CAN setup',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/charithmu/easy_piper',  # Update with your actual username
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.21.0',
        'python-can>=3.3.4',
    ],
    extras_require={
        'recorder': [
            'h5py>=3.8.0',
        ],
        'viz': [
            'matplotlib>=3.5.0',
        ],
        'dev': [
            'pytest>=6.0',
            'black>=22.0',
            'flake8>=4.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'piper-recorder=easy_piper.piper_recorder:main',
            'piper-analyze=easy_piper.piper_analyze:main',
        ],
    },
    include_package_data=True,
    package_data={
        'easy_piper': ['*.sh', '*.md'],
        '': ['scripts/*.sh'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='robotics piper arm control can-bus imitation-learning',
)
