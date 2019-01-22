from setuptools import find_packages, setup

setup(
    name='WarriorBeatCli',
    version='1.1.2',
    py_modules=['run'],
    packages=find_packages(),
    install_requires=[
        'Click',
        'GitPython',
        'psutil',
        'tabulate',
        'art',
        'docker',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        wb=run:cli
    '''
)
