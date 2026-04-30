from setuptools import setup, find_packages

setup(
    name='mass-panel',
    version='1.1.0',
    url='https://github.com/mass-pg/mass-panel',
    author='mass-pg',
    author_email='',
    description='GUI for displaying telemetry and controlling the unit',
    packages=find_packages(exclude=['*ros*']),
    package_data={'': ['*.css', '*.html', '*.js', '*.png']},
    install_requires=[
        'Flask==2.2.2',
        'turbo-flask==0.8.0',
        'mass-common~=1.7.1'
    ]
)
