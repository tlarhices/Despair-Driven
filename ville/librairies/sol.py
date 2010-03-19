#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *

import random
import math

class Sol:
  sol = None
  eau = None
  minAlt = None
  maxAlt = None
  afficheModele = True
  affichei=0
  affichej=0
  racineSol = None
  altitudeMax = -1000
  tailleX, tailleY = None, None
  
  def __init__(self):
    self.sol = []
    self.eau = []
    
  def ajouteGraine(self):
    while len(self.routes)==0:
      p1 = self.pointAlea(Vec3(0.0,0.0,0.0))
      p2 = self.pointAlea(Vec3(0.0,0.0,0.0))
      v=p2-p1
      v.normalize()
      v=v*self.longueurSegment*2
      p2=p1+v
      self.points = []
      self.ajouteRoute(p1, p2)
      
  def pointValide(self, point, testeEau=True):
    if point[0]<0:
      return False
    if point[0]>=self.tailleX:
      return False
    if point[1]<0:
      return False
    if point[1]>=self.tailleY:
      return False

    alt=self.getAltitude(point)
    if not testeEau or not self.estEau(point):
      if alt<self.altitudeMax:
        return True
      else:
        return False
    else:
      return False
    
  def estEau(self, point):
    if self.getAltitude(point)<=0:
      return True
    if self.eau[int(point[0])][int(point[1])]!=0.0:
      return True
    return False

  def getAltitude(self, pt):
    x,y,z = pt
    if x<0 or x>=self.tailleX:
      return -1000
    if y<0 or y>=self.tailleY:
      return -1000
    return self.sol[int(x)][int(y)]#max(self.sol[int(x)][int(y)], self.eau([int(x)][int(y)]))

  def genereSol(self, tailleX, tailleY):
    self.tailleX, self.tailleY = tailleX, tailleY
    
    print "Creation du sol..."
    self.sol = []
    self.eau = []
    for i in range(0, self.tailleX):
      self.sol.append([])
      self.eau.append([])
      for j in range(0, self.tailleY):
        self.sol[i].append(random.random()-0.35)
        self.eau[i].append(0.0)

    print "Flou du sol..."
    for a in range(0,8):
      for i in range(0, self.tailleX):
        for j in range(0, self.tailleY):
          somme = 0.0
          cpt=0
          for k in [-2, -1, 0, 1, 2]:
            for l in [-1, 0, 1]:
              if i+k>=0 and i+k<self.tailleX and j+l>=0 and j+l<self.tailleY:
                somme+=self.sol[i+k][j+l]
                cpt+=1
          self.sol[i][j] = somme / cpt

    self.getMinMax()
    for a in range(0,30):
      a=random.randint(0, int(self.tailleX/2-1))+self.tailleX/4
      b=random.randint(0, int(self.tailleY-1))
      self.sol[a][b]+=self.maxAlt*2
    for a in range(0,10):
      a=random.randint(0, int(self.tailleX*0.75))
      b=random.randint(0, int(self.tailleY-1))
      self.sol[a][b]-=self.minAlt*1.25

    print "Creation du sol..."
    for i in range(0, self.tailleX):
      facteur=1.0
      r1=max(-1, float(i+self.tailleX/2)/(self.tailleX)*facteur)
      r2=r1#max(-1, float(i+self.tailleX/2+self.tailleX/4)/(self.tailleX)*facteur)
      r3=r1#max(-1, float(i+self.tailleX/2+self.tailleX/8)/(self.tailleX)*facteur)
      for j in range(0, self.tailleY):
        self.sol[i][j]*=(10*(r1*r2*r3)*random.random())
        self.sol[i][j]*=self.sol[i][j]

    print "Flou du sol..."
    for a in range(0,5):
      for i in range(0, self.tailleX):
        for j in range(0, self.tailleY):
          somme = 0.0
          cpt=0
          for k in [-1, 0, 1, -2]:
            for l in [-1, 0, 1]:
              if i+k>=0 and i+k<self.tailleX and j+l>=0 and j+l<self.tailleY:
                somme+=self.sol[i+k][j+l]
                cpt+=1
          self.sol[i][j] = somme / cpt

    self.getMinMax()
    print "Etendue des altitudes : ", self.minAlt, self.maxAlt

    haut = 35
    bas = -1
    print "Ramenage au bon ratio..."
    for i in range(0, self.tailleX):
      for j in range(0, self.tailleY):
        self.sol[i][j] = (self.sol[i][j]-self.minAlt)/(self.maxAlt-self.minAlt)*(haut-bas)+bas

    """print "Aplanissage de l'eau..."
    for i in range(0, self.tailleX):
      for j in range(0, self.tailleY):
        if self.sol[i][j]<=0.0:#random.random()/4:
          self.sol[i][j]=0"""
        
    self.getMinMax()
    print "Etendue des altitudes : ", self.minAlt, self.maxAlt
    self.calculEau()
    self.fabriqueVectrices()

  def calculEau(self):
    self.getMinMax()
    
    altEau = 0.075
    minima={}
    for i in range(1, self.tailleY-1):
      if self.sol[-1][i-1]>self.sol[-1][i] and self.sol[-1][i+1]>self.sol[-1][i]:
        mdl=loader.loadModel("modeles/sphere.egg")
        mdl.reparentTo(render)
        mdl.setPos(self.tailleX, i, self.sol[-1][i])
        minima[self.sol[-1][i]]=mdl, (self.tailleX-1, i)
    for clef in sorted(minima.keys())[3:]:
      minima[clef][0].detachNode()
      minima[clef][0].removeNode()
      del minima[clef]
    minima[9999999]=NodePath("empty"), (self.tailleX-3, self.tailleY/2)
    for mdl,pt in minima.values():
      self.eau[pt[0]][pt[1]]=self.sol[pt[0]][pt[1]]+altEau
      
    change=True
    while change:
      change=False
      for i in range(0, self.tailleX):
        for j in range(0, self.tailleY):
          if self.eau[i][j]!=0.0:
            if i-1>=0:
              if self.eau[i-1][j]==0.0:
                if self.sol[i-1][j]<=self.eau[i][j] and self.sol[i-1][j]>0.0:
                  change=True
                  self.eau[i-1][j]=self.sol[i-1][j]+altEau
            if i+1<self.tailleX:
              if self.eau[i+1][j]==0.0:
                if self.sol[i+1][j]<=self.eau[i][j] and self.sol[i+1][j]>0.0:
                  change=True
                  self.eau[i+1][j]=self.sol[i+1][j]+altEau
                
            if j-1>=0:
              if self.eau[i][j-1]==0.0:
                if self.sol[i][j-1]<=self.eau[i][j] and self.sol[i][j-1]>0.0:
                  change=True
                  self.eau[i][j-1]=self.sol[i][j-1]+altEau
            if j+1<self.tailleY:
              if self.eau[i][j+1]==0.0:
                if self.sol[i][j+1]<=self.eau[i][j] and self.sol[i][j+1]>0.0:
                  change=True
                  self.eau[i][j+1]=self.sol[i][j+1]+altEau


  def fabriqueVectrices(self):
    self.format = GeomVertexFormat.getV3c4()
    self.vdata = GeomVertexData('TriangleVertices',self.format,Geom.UHStatic)
    self.vWriter = GeomVertexWriter(self.vdata, 'vertex')
    self.cWriter = GeomVertexWriter(self.vdata, 'color')
            
    for i in range(0, self.tailleX):
      print "Creation des vectrices... %i/%i \r" %(i+1, self.tailleX),
      for j in range(0, self.tailleY):
        self.vWriter.addData3f(i, j, max(self.eau[i][j], self.sol[i][j]))
        c1 = (0.0,0.5,0.0,1.0)
        if self.sol[i][j]<= self.eau[i][j]:
          c1 = (0.0,0.1,0.5,1.0)
        self.cWriter.addData4f(*c1)
        
  def getMinMax(self):
    self.minAlt = self.sol[0][0]
    self.maxAlt = self.sol[0][0]
    for i in range(0, self.tailleX):
      for j in range(0, self.tailleY):
        self.minAlt = min(self.minAlt, self.sol[i][j])
        self.maxAlt = max(self.maxAlt, self.sol[i][j])
    self.altitudeMax = self.maxAlt/2

    
  def affiche(self):
    if not self.afficheModele:
      self.affiche=self.finAffiche
      
    if self.racineSol == None:
      self.racineSol = NodePath("sol")
      self.racineSol.reparentTo(render)
    for i in range(0,self.tailleY):
      geom = Geom(self.vdata)
      if self.affichej>=self.tailleY:
        self.affichej=0
        self.affichei+=1
      if self.affichei>=self.tailleX:
        self.affiche=self.finAffiche
        return
      prim = GeomTriangles(Geom.UHStatic)
      if self.affichej<self.tailleY-1 and self.affichei<self.tailleX-1:
        prim.addVertex(self.affichej+self.affichei*(self.tailleY))
        prim.addVertex(self.affichej+(self.affichei+1)*(self.tailleY))
        prim.addVertex(self.affichej+self.affichei*(self.tailleY)+1)
      prim.closePrimitive()
      geom.addPrimitive(prim)
      prim = GeomTriangles(Geom.UHStatic)
      if self.affichej<self.tailleY-1 and self.affichei<self.tailleX-1:
        prim.addVertex(self.affichej+(self.affichei+1)*(self.tailleY))
        prim.addVertex(self.affichej+(self.affichei+1)*(self.tailleY)+1)
        prim.addVertex(self.affichej+self.affichei*(self.tailleY)+1)
      prim.closePrimitive()
      geom.addPrimitive(prim)
      node = GeomNode('gnode')
      node.addGeom(geom)
      mdl = NodePath(node)
      mdl.reparentTo(self.racineSol)
      self.affichej+=1
      
  def finAffiche(self):
    pass
