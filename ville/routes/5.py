#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *
from type1 import DessinRoute as Type1

class DessinRoute(Type1):
  def __init__(self):
    Type1.__init__(self)

  def filtre(self, routes):
    return len(routes)==5

  def fabrique(self, routes):
    for route in routes:
      route.fabrique()
