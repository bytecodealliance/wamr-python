# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="wamr-python",
    version="0.1.0",
    description="A WebAssembly runtime powered by WAMR",
    long_description=readme,
    author="The WAMR Project Developers",
    author_email="hello@bytecodealliance.org",
    url="https://github.com/lum1n0us/wamr-python",
    license=license,
    packages=["wamr"],
)
