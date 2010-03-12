#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *

class DessinRoute:
  def __init__(self):
    pass

  def filtre(self, routes, cptA, cptB):
    return len(routes)==2 and (cptA==1 or cptB==1)
    
  def fabrique(self, route, routes, cptA, cptB):
    route.fabrique()
