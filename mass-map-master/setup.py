from setuptools import setup, find_packages

setup(
    name='mass-map',
    version='1.4.1',
    url='https://github.com/mass-pg/mass-map',
    author='mass-pg',
    author_email='',
    description='Map data supplier',
    packages=find_packages(),
    install_requires=[
        'overpy==0.6',
        'mass-common>=1.7.1'
    ]
)
