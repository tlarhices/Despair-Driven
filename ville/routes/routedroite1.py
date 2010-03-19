#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *

from type1 import DessinRoute as Type1

class DessinRoute(Type1):
  def __init__(self):
    Type1.__init__(self)

  def filtre(self, routes):
    return len(routes)==2
    
  def fabrique(self, routes):
    for route in routes:
      if route.racine!=None:
        #route.supprime()
        route.lampadaires=[]
        route.feuxtricolores=[]
    racine, lampadaires, feuxtricolores = self.tronconDroit(route, routes, route.pointA, route.pointB)
    racine.reparentTo(render)
    for route in routes:
      route.racine = racine
      route.lampadaires+=lampadaires
      route.feuxtricolores+=feuxtricolores

