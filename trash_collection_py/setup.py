"""Setup script for trash collection VRP."""

from setuptools import setup, find_packages

setup(
    name='trash-collection-vrp',
    version='1.0.0',
    description='Trash Collection Vehicle Routing Problem Solver',
    author='VRP Team',
    packages=find_packages(),
    install_requires=[
        'requests>=2.31.0',
        'numpy>=1.24.0',
        'typing-extensions>=4.5.0',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'trash-vrp=src.main:main',
        ],
    },
)

