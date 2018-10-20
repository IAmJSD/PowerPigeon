from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().strip().splitlines()

setup(
    name='PowerPigeon',
    version='0.1.1',
    packages=['powerpigeon'],
    url='https://github.com/JakeMakesStuff/PowerPigeon',
    license='MPL-2.0',
    author='Jake Gealer',
    install_requires=requirements,
    author_email='jake@gealer.email',
    description='PowerPigeon is a model-based RethinkDB handler.'
)
