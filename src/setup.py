from setuptools import find_packages, setup

setup(
    name='WarriorBeatCli',
    version='0.1',
    py_modules=['run'],
    packages=find_packages(),
    install_requires=[
        'Click',
        'GitPython',
        'psutil',
        'tabulate',
        'art',
        'docker'
    ],
    entry_points='''
        [console_scripts]
        wb=run:cli
    '''
)
