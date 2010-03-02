#!/usr/bin/env python
# -*- coding: utf-8 -*-
import direct.directbase.DirectStart
from pandac.PandaModules import *

from weakref import proxy

import random
import math

class Ville:
  points = None
  rayon = None
  lignes = None
  batiments = None
  
  def __init__(self, rayon):
    self.rayon = rayon
    self.points = [self.pointAlea((0.0,0.0,0.0))]
    self.lignes = []
    self.batiments = []
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
    
  def collisionBatimentBatiment(self, position, rayon):
    position = Vec3(*position)
    for pos, taille, noeud in self.batiments:
      if (rayon+taille)*(rayon+taille)>(position-Vec3(*pos)).lengthSquared():
        return noeud
    return False
    
  def collisionLigneBatiment(self, pointA, pointB):
    for centre, rayon, noeud in self.batiments:
      if self.collisionLigneCercle(pointA, pointB, centre, rayon):
        return True
    return False
    
  def collisionBatimentLigne(self, position, rayon):
    for pointA, pointB in self.lignes:
      if self.collisionLigneCercle(pointA, pointB, position, rayon):
        return True
    return False

  def collisionLigneCercle(self, pointA, pointB, centre, rayon):
    ax,ay,az = pointA
    bx,by,bz = pointB
    cx,cy,cz = centre
    alpha = (bx-ax)*(bx-ax)+(by-ay)*(by-ay)
    beta = 2*((bx-ax)*(ax-cx)+(by-ay)*(ay-cy))
    gamma = ax*ax+ay*ay+cx*cx+cy*cy-2*(ax*cx+ay*cy)-rayon*rayon
    if beta*beta-4*alpha*gamma>=0:
      u=((cx-ax)*(bx-ax)+(cy-ay)*(by-ay))/((bx-ax)*(bx-ax)+(by-ay)*(by-ay))
      return 0<=u and u<=1
    else:
      return False
    
  
      
  def ajouteBatiments(self, A, B, direction):
    i=0.0
    rayon = 0.5
    pas = 1.0/(Vec3(*B)-Vec3(*A)).length()*rayon
    Px=A[0]-5*(B[0]-A[0])
    Py=A[1]-5*(B[1]-A[1])
    prev=Vec3(Px, Py, 0.0)
    
    dx=B[0]-A[0]
    dy=B[1]-A[1]
    
    n=Vec3(direction*dy, -direction*dx, 0.0)
    n.normalize()
    
    while i<=1.0:
      i+=pas
      taille=random.random()*1.0+0.5
      Px=A[0]+i*(B[0]-A[0])+n[0]*taille
      Py=A[1]+i*(B[1]-A[1])+n[1]*taille
      if (Vec3(Px, Py, 0.0)-prev).length()>10*rayon+random.random()*rayon*20:
        noeudColl = self.collisionBatimentBatiment((Px, Py, 0.0), taille)
        if not noeudColl:
          if not self.collisionBatimentLigne((Px, Py, 0.0), taille):
            if random.random()>0.5:
              prev=Vec3(Px, Py, 0.0)
              mdl = loader.loadModel("box.egg")
              mdl.setPos(Px-0.5, Py-0.5, -0.5)
              mdl.reparentTo(render)
              mdl.setColor(random.random()/2, random.random()/2, random.random()/2)
              self.batiments.append(((Px,Py,0.0), taille, mdl))
              mdl.setScale(taille, taille, 1.0)
        else:
          sc = noeudColl.getScale()
          noeudColl.setScale(sc[0], sc[1], sc[2]*1.05)

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
      pt1, d1 = self.pointPlusProche((depx, depy, depz))
      pt2, d2 = self.pointPlusProche((arrx, arry, arrz))
      seuilMinD = 8.0
      if d1<seuilMinD:
        (depx, depy, depz) = pt1
      if d2<seuilMinD:
        (arrx, arry, arrz) = pt2
      if ((depx, depy, depz),(arrx, arry, arrz)) not in self.lignes and (Vec3(depx, depy, depz)-Vec3(arrx, arry, arrz)).length()>2.5:
        if not self.collisionLigneBatiment((depx, depy, depz), (arrx, arry, arrz)):
          if True:#(d1>seuilMinDAffiche or pt1==(depx, depy, depz)) and (d2>seuilMinDAffiche or pt2==(arrx, arry, arrz)):
            if (arrx, arry, arrz) not in self.points:
              self.points.append((arrx, arry, arrz))
            t = int((Vec3(depx, depy, depz)-Vec3(arrx, arry, arrz)).length())
            if t<8:
              return
            if t>=12:
              cp = int(math.sqrt(t-2))
              for i in range(1, cp, 11):
                i = float(i)
                if ((arrx+depx)*i/cp, (arry+depy)*i/cp, (arrz+depz)*i/cp) not in self.points:
                  self.points.append(((arrx+depx)*i/cp, (arry+depy)*i/cp, (arrz+depz)*i/cp))
              #self.points.append(((arrx+depx)/2, (arry+depy)/2, (arrz+depz)/2))
            lseg = LineSegs()
            lseg.moveTo(depx, depy, depz)
            lseg.drawTo(arrx, arry, arrz)
            if ((depx, depy, depz),(arrx, arry, arrz)) not in self.lignes:
              self.lignes.append(((depx, depy, depz),(arrx, arry, arrz)))
            else:
              print "danger !"
            render.attachNewNode(lseg.create())
          self.ajouteBatiments((depx, depy, depz), (arrx, arry, arrz), 1.0)
          self.ajouteBatiments((depx, depy, depz), (arrx, arry, arrz), -1.0)
    print "routes :", len(self.lignes)
    print "batiments :", len(self.batiments)
      
  def pointPlusProche(self, pt):
    d=800000.0
    ptProche=None
    for point in self.points:
      dist = (Vec3(*point)-Vec3(*pt)).lengthSquared()
      if dist < d:
        ptProche = point
        d = dist
    return ptProche, math.sqrt(d)
      
  def ping(self, task):
    self.ajouteRouteAlea()
    return task.cont      

ville=Ville(30)
taskMgr.add(ville.ping, 'PingVille')
run()
