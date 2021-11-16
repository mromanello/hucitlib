
#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

from collections import namedtuple
VersionSpec = namedtuple('VersionSpec', ['major', 'minor', 'revision'])
version = VersionSpec(0, 3, 0)
str_version = '.'.join(map(str, version))
