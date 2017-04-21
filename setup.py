import os
from setuptools import setup, find_packages

NAME = "knowledge_base"
execfile('{0}/__version__.py'.format(NAME))
VERSION = str_version

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='hucit_knowledge_base'
	,author='Matteo Romanello'
	,author_email='matteo.romanello@gmail.com'
	,url='https://github.com/mromanello/hucit_kb/'
    ,version=VERSION
    ,packages=find_packages()
    ,package_data={'knowledge_base': [
                                    'data/*.*'
                                    , 'data/kb/*.*'
                                    , 'config/*.*'
                                    ]}
    ,entry_points={
        'console_scripts':[
            'hucit = knowledge_base.cli:main'
        ]
    }
    ,install_requires=[
    					'pyCTS'
    					, 'surf>=1.1.9'
    				]
    ,long_description=read('README.md')
)
