from setuptools import setup, find_packages

setup(
    name='mass-lidar',
    version='1.1.0',
    url='https://github.com/mass-pg/mass-lidar',
    author='mass-pg',
    author_email='',
    description='Lidar sensor',
    packages=find_packages(),
    install_requires=[
        'mass-common~=1.7.1'
    ]
)
