from setuptools import setup, find_packages

setup(
    name='mass-camera',
    version='1.1.0',
    url='https://github.com/mass-pg/mass-camera',
    author='mass-pg',
    author_email='',
    description='Camera sensor',
    packages=find_packages(),
    install_requires=[
        'mass-common~=1.7.1',
        'opencv-python==4.5.5.64',
        'open3d==0.15.1',
        'testresources==2.0.1'
    ]
)
