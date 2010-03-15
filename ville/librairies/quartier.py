#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *

class Quartier:
  bords=False
  densite=False
  def __init__(self, bords, densite):
    self.bords = bords
    self.densite = densite
    
  def verifieOK(self):
    points={}
    for route in self.bords:
      points[tuple(route.pointA)]=points.get(tuple(route.pointA), 0)+1
      points[tuple(route.pointB)]=points.get(tuple(route.pointB), 0)+1
    OK=True
    for point in points:
      if points[point]!=2:
        OK=False
    return OK
    
  def rendOK(self, ville):
    if self.verifieOK():
      print "Quartier OK"
      return
      
    print "Quartier pas OK"
    mieux = True
    while not self.verifieOK() and mieux:
      mieux = self.light(ville)
      if not self.verifieOK():
        mieux = self.heavy(ville) or mieux
      
    self.affiche()
    
  def light(self, ville):
    mieux=False
    points={}
    for route in self.bords:
      points[tuple(route.pointA)]=points.get(tuple(route.pointA), 0)+1
      points[tuple(route.pointB)]=points.get(tuple(route.pointB), 0)+1
      
    pointsPasOK = []
    for point in points:
      if points[point]!=2:
        pointsPasOK.append(point)
        
    for route in ville.routes:
      if tuple(route.pointA) in pointsPasOK and tuple(route.pointB) in pointsPasOK:
        if self.bords.count(route)>0:
          pass
        else:
          self.bords.append(route)
          mieux=True
    if mieux:
      print "light a servit a un truc !"
    return mieux
    
    
  def heavy(self, ville):
    bary = self.barycentre()
    contours = []
    points = ville.cherchePointAutour(bary, ville.longueurSegment*2)
    for point in points:
      print "test %i/%i\r" %(ville.points.index(point), len(ville.points)),
      i = ville.intersectionne(bary, point)
      if i==None:
        contours.append(point)
        
    mieux=False
    for route in ville.routes:
      if (route.pointA in contours and route.pointB in contours):
        if route not in self.bords:
          self.bords.append(route)
          mieux=True
    print "Etait pas bien, nouveau status :",self.verifieOK(),"a fait un truc :", mieux
    return mieux

  racine=None
  def affiche(self):
    if self.racine!=None:
      self.supprime()
    self.racine = NodePath("quartier")
    self.racine.reparentTo(render)
    col = random.random(), random.random(), random.random()
    for route in self.bords:
      ligne = LineSegs()
      ligne.setColor(*col)
      ligne.setThickness(2.0);
      a = route.pointA
      a[2]=0.0
      b = route.pointB
      b[2]=0.0
      ligne.moveTo(*a)
      ligne.drawTo(*b)
      mdl=self.racine.attachNewNode(ligne.create())
      mdl.setLightOff()
      
  def supprime(self):
    if self.racine!=None:
      self.racine.detachNode()
      self.racine.removeNode()
      self.racine=None
      
  def barycentre(self):
    cx,cy,cz = 0.0,0.0,0.0
    for route in self.bords:
      px,py,pz = route.pointA
      cx+=px
      cy+=py
      cz+=pz
      px,py,pz = route.pointB
      cx+=px
      cy+=py
      cz+=pz
    cx=cx/(len(self.bords)*2)
    cy=cy/(len(self.bords)*2)
    cz=cz/(len(self.bords)*2)
    return Vec3(cx,cy,cz)
