# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='nsnqt',
    version='0.0.1',
    description='Package for quantified trading',
    long_description=README.md,
    author='He Jun, Shen Xuhui, Wang Xian',
    author_email='harry0519@gmail.com',
    url='https://github.com/harry0519/nsnqt',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

