from setuptools import setup, find_packages

setup(
    name='mass-common',
    version='1.7.1',
    url='https://github.com/mass-pg/mass-common',
    author='mass-pg',
    author_email='',
    description='Common code used between repositories',
    packages=find_packages(),
    package_data={'': ['*.conf']},
    install_requires=[
        'numpy==1.21.2',
        'plotly==5.7.0',
        'pyproj==3.4.0',
        'shapely==1.8.0'
    ]
)
