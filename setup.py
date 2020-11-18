import os
from setuptools import setup, find_packages

NAME = "hucitlib"
exec(open("{0}/__version__.py".format(NAME)).read())
VERSION = str_version


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="hucitlib",
    author="Matteo Romanello",
    author_email="matteo.romanello@gmail.com",
    url="https://github.com/mromanello/hucit_kb/",
    version=VERSION,
    packages=find_packages(),
    package_data={"hucitlib": ["data/*.*", "data/kb/*.*", "config/*.*"]},
    entry_points={"console_scripts": ["hucit = hucitlib.cli:main"]},
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.6",
        "Operating System :: POSIX",
    ],
    license="GPL v3"
    # TODO: find a way to install Thibault's fork of surf from here
    # so that it works when installing by pip.
    ,
    install_requires=[
        "pyCTS",
        "surf>=1.2.0",
        "docopt",
        "tqdm",
        "retrying",
        "rdflib>=4.2.1",
        "MyCapytain"
    ],
    long_description=read("README.md"),
)
