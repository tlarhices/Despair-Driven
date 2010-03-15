#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *

import random
import math

class Sol:
  sol = None
  minAlt = None
  maxAlt = None
  afficheModele = True
  affichei=0
  affichej=0
  racineSol = None
  altitudeMax = -1000
  
  def __init__(self):
    self.sol = []
    
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

  def getAltitude(self, pt):
    x,y,z = pt
    if x+self.rayon<0 or x+self.rayon>=self.rayon*2:
      return -1000
    if y+self.rayon<0 or y+self.rayon>=self.rayon*3:
      return -1000
    return self.sol[int(x)+self.rayon][int(y)+self.rayon]

  def genereSol(self, rayon):
    self.rayon = rayon
    
    print "Creation du sol..."
    self.sol = []
    for i in range(-self.rayon, self.rayon):
      self.sol.append([])
      for j in range(-self.rayon, self.rayon*3):
        self.sol[i+self.rayon].append(random.random()-0.35)

    print "Flou du sol..."
    for a in range(0,10):
      for i in range(0, self.rayon*2):
        for j in range(0, self.rayon*3):
          somme = 0.0
          cpt=0
          for k in [-2, -1, 0, 1, 2]:
            for l in [-1, 0, 1]:
              if i+k>=0 and i+k<self.rayon*2 and j+l>=0 and j+l<self.rayon*3:
                somme+=self.sol[i+k][j+l]
                cpt+=1
          self.sol[i][j] = somme / cpt

    print "Creation du sol..."
    for i in range(-self.rayon, self.rayon):
      facteur=2.0
      r1=max(-1, (float(i)+float(self.rayon))/(self.rayon)*facteur)
      r2=max(-1, (float(i+20)+float(self.rayon))/(self.rayon)*facteur)
      r3=max(-1, (float(i+40)+float(self.rayon))/(self.rayon)*facteur)
      for j in range(-self.rayon, self.rayon*3):
        self.sol[i+self.rayon][j+self.rayon]*=(10*(r1*r2*r3)*random.random())
        self.sol[i+self.rayon][j+self.rayon]*=self.sol[i+self.rayon][j+self.rayon]

    self.getMinMax()
    for a in range(0,30):
      a=random.randint(0, int(self.rayon*1.0))+self.rayon/4
      b=random.randint(0, int(self.rayon*3))
      self.sol[a][b]+=self.maxAlt*1.5
    for a in range(0,10):
      a=random.randint(0, int(self.rayon*1.5))
      b=random.randint(0, int(self.rayon*3))
      self.sol[a][b]-=self.minAlt*1.25

    print "Flou du sol..."
    for a in range(0,5):
      for i in range(0, self.rayon*2):
        for j in range(0, self.rayon*3):
          somme = 0.0
          cpt=0
          for k in [-1, 0, 1, -2]:
            for l in [-1, 0, 1]:
              if i+k>=0 and i+k<self.rayon*2 and j+l>=0 and j+l<self.rayon*3:
                somme+=self.sol[i+k][j+l]
                cpt+=1
          self.sol[i][j] = somme / cpt

    self.getMinMax()
    print "Etendue des altitudes : ", self.minAlt, self.maxAlt

    haut = 30
    bas = -0.05
    print "Ramenage au bon ratio..."
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*3):
        self.sol[i][j] = (self.sol[i][j]-self.minAlt)/(self.maxAlt-self.minAlt)*(haut-bas)+bas

    print "Aplanissage de l'eau..."
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*3):
        if self.sol[i][j]<=0.0:#random.random()/4:
          self.sol[i][j]=0
        
    self.getMinMax()
    print "Etendue des altitudes : ", self.minAlt, self.maxAlt
    self.fabriqueVectrices()

  def fabriqueVectrices(self):
    print "Creation des vectrices..."
    self.format = GeomVertexFormat.getV3c4()
    self.vdata = GeomVertexData('TriangleVertices',self.format,Geom.UHStatic)
    self.vWriter = GeomVertexWriter(self.vdata, 'vertex')
    self.cWriter = GeomVertexWriter(self.vdata, 'color')
            
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*3):
        self.vWriter.addData3f(i-self.rayon, j-self.rayon, self.sol[i][j])
        c1 = (0.0,0.5,0.0,1.0)
        if self.sol[i][j]<=0:
          c1 = (0.0,0.1,0.5,1.0)
        self.cWriter.addData4f(*c1)
        
  def getMinMax(self):
    self.minAlt = self.sol[0][0]
    self.maxAlt = self.sol[0][0]
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*3):
        self.minAlt = min(self.minAlt, self.sol[i][j])
        self.maxAlt = max(self.maxAlt, self.sol[i][j])
    self.altitudeMax = self.maxAlt/2

    
  def affiche(self):
    if not self.afficheModele:
      self.affiche=self.finAffiche
      
    if self.racineSol == None:
      self.racineSol = NodePath("sol")
      self.racineSol.reparentTo(render)
    for i in range(0,self.rayon*2):
      #print "Construction du modele... %i/%i\r" %(i+1, self.rayon*2),
      #sys.stdout.flush()
      geom = Geom(self.vdata)
      if self.affichej>=self.rayon*3:
        self.affichej=0
        self.affichei+=1
      if self.affichei>=self.rayon*2:
        #print
        #print "Compactage du modele"
        #self.racineSol.flattenStrong()
        self.affiche=self.finAffiche
        #self.flatten()
        return
      prim = GeomTriangles(Geom.UHStatic)
      if self.affichej<self.rayon*3-1 and self.affichei<self.rayon*2-1:
        prim.addVertex(self.affichej+self.affichei*(self.rayon*3))
        prim.addVertex(self.affichej+(self.affichei+1)*(self.rayon*3))
        prim.addVertex(self.affichej+self.affichei*(self.rayon*3)+1)
      prim.closePrimitive()
      geom.addPrimitive(prim)
      prim = GeomTriangles(Geom.UHStatic)
      if self.affichej<self.rayon*3-1 and self.affichei<self.rayon*2-1:
        prim.addVertex(self.affichej+(self.affichei+1)*(self.rayon*3))
        prim.addVertex(self.affichej+(self.affichei+1)*(self.rayon*3)+1)
        prim.addVertex(self.affichej+self.affichei*(self.rayon*3)+1)
      prim.closePrimitive()
      geom.addPrimitive(prim)
      node = GeomNode('gnode')
      node.addGeom(geom)
      mdl = NodePath(node)
      mdl.reparentTo(self.racineSol)
      self.affichej+=1
      
  def finAffiche(self):
    pass
