from setuptools import setup, find_packages

setup(
    name='mass-control',
    version='1.2.0',
    url='https://github.com/mass-pg/mass-control',
    author='mass-pg',
    author_email='',
    description='Path to commands translation layer',
    packages=find_packages(),
    install_requires=[
        'mass-common~=1.7.1',
    ]
)
