import os
from setuptools import setup, find_packages

NAME = "knowledge_base"
exec(open('{0}/__version__.py'.format(NAME)).read())
VERSION = str_version

# TODO: update for python3

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='hucitlib'
	, author='Matteo Romanello'
	, author_email='matteo.romanello@gmail.com'
	, url='https://github.com/mromanello/hucit_kb/'
    , version=VERSION
    , packages=find_packages()
    , package_data={'knowledge_base': [
                                    'data/*.*'
                                    , 'data/kb/*.*'
                                    , 'config/*.*'
                                    ]}
    , entry_points={
        'console_scripts':[
            'hucit = knowledge_base.cli:main'
        ]
    }
    , classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX'
    ]
    , license='GPL v3'
    # TODO: find a way to install Thibault's fork of surf from here
    # so that it works when installing by pip.
    , install_requires=['pyCTS', 'surf>=1.2.0', 'docopt']
    , long_description=read('README.md')
)
