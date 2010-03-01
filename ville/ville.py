#!/usr/bin/env python
# -*- coding: utf-8 -*-
import direct.directbase.DirectStart
from pandac.PandaModules import *

from weakref import proxy

import random
  
class Ville:
  points = None
  rayon = None
  lignes = None
  
  def __init__(self, rayon):
    self.rayon = rayon
    self.points = [self.pointAlea((0.0,0.0,0.0))]
    self.lignes = []
    self.ajouteRouteAlea()
      
  def pointAlea(self, pt):
    x,y,z = pt
    return ((random.random()*2-1)*self.rayon+x, (random.random()*2-1)*self.rayon+y, 0.0+z)
      
  def equationDroite(self, dep, arr):
    if arr[0] == dep[0]:
      arr = list(arr)
      arr[0]+=0.0001
    m = (arr[1] - dep[1]) / (arr[0] - dep[0])
    b = dep[1] - m*dep[0]
    return m, b
    
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
      
      
  def intersectionne(self, A, B):
    d = (Vec3(*A)-Vec3(*B)).lengthSquared()
    deb = A
    fin = B

    coll = None
    for C,D in self.lignes:
      r = self.intersection(A, B, C, D)
      if r!=None:
        coll=r
    return coll!=None
      
      

  def ajouteRouteAlea(self):
    depx, depy, depz = random.choice(self.points)
    autres = self.points[:]
    autres.remove((depx, depy, depz))
    if len(autres)>0:
      arrx, arry, arrz = random.choice(autres)
      autres.remove((arrx, arry, arrz))
    while len(autres)>0 and self.intersectionne((depx, depy, depz),(arrx, arry, arrz)):
      arrx, arry, arrz = random.choice(autres)
      autres.remove((arrx, arry, arrz))
    else:
      arrx, arry, arrz = self.pointAlea((depx, depy, depz))
    if not self.intersectionne((depx, depy, depz),(arrx, arry, arrz)):
      self.points.append((arrx, arry, arrz))
      self.points.append(((arrx+depx)/2, (arry+depy)/2, (arrz+depz)/2))
      lseg = LineSegs()
      lseg.moveTo(depx, depy, depz)
      lseg.drawTo(arrx, arry, arrz)
      self.lignes.append(((depx, depy, depz),(arrx, arry, arrz)))
      render.attachNewNode(lseg.create())
      
  def ping(self, task):
    self.ajouteRouteAlea()
    return task.cont      

ville=Ville(25)
taskMgr.add(ville.ping, 'PingVille')
run()
