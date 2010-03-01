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
        Px=A[0]+r*(B[0]-A[0])
        Py=A[1]+r*(B[1]-A[1])
        P = Px, Py, 0.0
        d2 = (Vec3(*A)-Vec3(*P)).lengthSquared()
        if coll==None or d2<d:
          coll=P
          d=d2
    return coll
      
  def ajouteBatiments(self, A, B):
    i=0.0
    rayon = 0.5
    pas = 1.0/(Vec3(*B)-Vec3(*A)).length()*rayon
    Px=A[0]-5*(B[0]-A[0])
    Py=A[1]-5*(B[1]-A[1])
    prev=Vec3(Px, Py, 0.0)
    while i<=1.0:
      i+=pas
      Px=A[0]+i*(B[0]-A[0])
      Py=A[1]+i*(B[1]-A[1])
      if (Vec3(Px, Py, 0.0)-prev).length()>3*rayon+random.random()*rayon*5:
        prev=Vec3(Px, Py, 0.0)
        mdl = loader.loadModel("sphere.egg")
        mdl.setPos(Px, Py, 0.0)
        mdl.reparentTo(render)

  def ajouteRouteAlea(self):
    depx, depy, depz = random.choice(self.points)
    autres = self.points[:]
    autres.remove((depx, depy, depz))
    if len(autres)>0:
      arrx, arry, arrz = random.choice(autres)
      autres.remove((arrx, arry, arrz))
    while len(autres)>0 and self.intersectionne((depx, depy, depz),(arrx, arry, arrz))!=None:
      arrx, arry, arrz = random.choice(autres)
      autres.remove((arrx, arry, arrz))
    else:
      arrx, arry, arrz = self.pointAlea((depx, depy, depz))
    
    r=self.intersectionne((depx, depy, depz),(arrx, arry, arrz))
    if r!=None:
      arrx, arry, arrz = r
      
    if (Vec3(depx, depy, depz)-Vec3(arrx, arry, arrz)).lengthSquared() > 2.0:
      if (arrx, arry, arrz) not in self.points:
        self.points.append((arrx, arry, arrz))
      if ((arrx+depx)/2, (arry+depy)/2, (arrz+depz)/2) not in self.points:
        self.points.append(((arrx+depx)/2, (arry+depy)/2, (arrz+depz)/2))
      lseg = LineSegs()
      lseg.moveTo(depx, depy, depz)
      lseg.drawTo(arrx, arry, arrz)
      self.ajouteBatiments((depx, depy, depz), (arrx, arry, arrz))
      if ((depx, depy, depz),(arrx, arry, arrz)) not in self.lignes:
        self.lignes.append(((depx, depy, depz),(arrx, arry, arrz)))
      else:
        print "danger !"
      render.attachNewNode(lseg.create())
      
  def ping(self, task):
    self.ajouteRouteAlea()
    return task.cont      

ville=Ville(25)
taskMgr.add(ville.ping, 'PingVille')
run()
