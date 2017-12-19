import os
from setuptools import setup, find_packages

NAME = "knowledge_base"
execfile('{0}/__version__.py'.format(NAME))
VERSION = str_version

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
        'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX'
    ]
    , license='GPL v3'
    , install_requires=['pyCTS', 'surf>=1.1.9', 'docopt']
    , long_description=read('README.md')
)
