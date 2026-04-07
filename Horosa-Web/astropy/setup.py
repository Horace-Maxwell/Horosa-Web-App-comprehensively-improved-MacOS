from distutils.core import setup
from setuptools import find_packages


setup(
    name = "astrostudy",
    version = "0.0.1",
    description = "astro test",
    author = "zjf",
    author_email = "zjfchine@foxmail.com",
    license = 'AGPL-3.0-only',
    install_requires = [],
    packages = find_packages(where='./'),
    package_dir = {'': '.'}
)
