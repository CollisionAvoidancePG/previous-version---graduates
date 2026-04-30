from setuptools import setup, find_packages

setup(
    name='mass-epn',
    version='1.6.0',
    url='https://github.com/mass-pg/mass-epn',
    author='mass-pg',
    author_email='',
    description='Evolution Planer and Navigator',
    packages=find_packages(exclude=['*ros*']),
    install_requires=[
        'mass-common==1.7.1',
        'mass-map==1.4.1',
        'scipy==1.8.0'
    ]
)
