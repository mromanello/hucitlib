import os
from setuptools import setup, find_packages
#import citation_extractor
#VERSION = citation_extractor.__version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='hucit_knowledge_base'
	,author='Matteo Romanello'
	,author_email='matteo.romanello@gmail.com'
	,url='https://github.com/mromanello/hucit_kb/'
    ,version=""
    ,packages=find_packages()
    ,package_data={'knowledge_base': ['data/*.*'
                                          ,'data/kb/*.*']}
    ,long_description=read('README.md')
)