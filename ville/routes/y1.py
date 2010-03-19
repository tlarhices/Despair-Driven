#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *

from type1 import DessinRoute as Type1

class DessinRoute(Type1):
  def __init__(self):
    Type1.__init__(self)

  def filtre(self, routes):
    return len(routes)==3
    
  def intersection(self, A, B, C, D):
    Ax, Ay, Az = A
    Bx, By, Bz = B
    Cx, Cy, Cz = C
    Dx, Dy, Dz = D
    
    try:
      r=((Ay-Cy)*(Dx-Cx)-(Ax-Cx)*(Dy-Cy))/((Bx-Ax)*(Dy-Cy)-(By-Ay)*(Dx-Cx))
    except:
      r=0.5
    try:
      s=((Ay-Cy)*(Bx-Ax)-(Ax-Cx)*(By-Ay))/((Bx-Ax)*(Dy-Cy)-(By-Ay)*(Dx-Cx))
    except:
      s=0.5
    if 0<r and r<1 and 0<s and s<1:
      return r
    else:
      return None

    
  def calculRayon(self, routes):
    print
    print "calc ray"
    nA1,nB1 = routes[0].getNormales(routes)
    nA1=nA1*(routes[0].taille*self.largeurVoie)
    nB1=nB1*(routes[0].taille*self.largeurVoie)
    nA2,nB2 = routes[1].getNormales(routes)
    nA2=nA2*(routes[1].taille*self.largeurVoie)
    nB2=nB2*(routes[1].taille*self.largeurVoie)
    nA3,nB3 = routes[2].getNormales(routes)
    nA3=nA3*(routes[2].taille*self.largeurVoie)
    nB3=nB3*(routes[2].taille*self.largeurVoie)
    c1,c2,c3 = self.detecteCote(routes)
    if c1==0:
      n1=nA1
      pa1 = routes[0].pointA
      pb1 = routes[0].pointB
    else:
      n1=nB1
      pb1 = routes[0].pointA
      pa1 = routes[0].pointB
    if c2==0:
      n2=nA2
      pa2 = routes[1].pointA
      pb2 = routes[1].pointB
    else:
      n2=nB2
      pb2 = routes[1].pointA
      pa2 = routes[1].pointB
    if c3==0:
      n3=nA3
      pa3 = routes[2].pointA
      pb3 = routes[2].pointB
    else:
      n3=nB3
      pb3 = routes[2].pointA
      pa3 = routes[2].pointB
    
    print self.intersection(pa1+n1, pb1+n1, pa2-n2, pb2-n2)
    print "###"
    
  def fabrique(self, routes):
    self.calculRayon(routes)
    for route in routes:
      route.fabrique()
