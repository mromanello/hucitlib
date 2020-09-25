#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com


class ResourceNotFound(Exception):
    """Raised when the resource identified by the URN is not in the KB."""
