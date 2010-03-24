#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *
#On coupe l'audio pour le moment
loadPrcFileData("",u"audio-library-name null")
loadPrcFileData("",u"sync-video #f")
import direct.directbase.DirectStart

from weakref import proxy

import random
import math
import time
import sys, os

class Route:
  parents = None
  pointA = None
  pointB = None
  taille = None
  ville = None
  
  def __init__(self, pointA, pointB, parents, ville, taille=None):
    self.parents = []
    if parents!=None:
      self.parents+=parents
      
    for route in ville.routes:
      if pointA==route.pointA or pointA==route.pointB or pointB==route.pointA or pointB==route.pointB:
        self.ajouteParent(route)
      
    self.pointA = pointA
    self.pointB = pointB
    self.ville = ville
    if taille==None:
      self.taille = ville.tailleRoute
    else:
      self.taille=taille
    self.fabrique()
    
    
  def fabrique(self):
    self.racine = NodePath("00")
    ligne = LineSegs()
    ligne.setColor(1.0,0.0,0.0)
    ligne.setThickness(self.taille);
    ligne.moveTo(self.pointA)
    ligne.drawTo(self.pointB)
    self.racine.attachNewNode(ligne.create())
    self.racine.reparentTo(render)

  def getAngle(self, pA=None, pB=None):
    if pA==None:
      pA=self.pointA
    if pB==None:
      pB=self.pointB
    
    vec = Vec3(pB-pA)
    vec.normalize()
    angle = vec.signedAngleDeg(Vec3(1.0,0.0,0.0), Vec3(0.0,0.0,-1.0))
    return angle
    
  def continueRoute(self):
    AOK, BOK = True, True
    for route in self.parents:
      if self.pointA==route.pointA or self.pointA==route.pointB:
        AOK=False
      if self.pointB==route.pointA or self.pointB==route.pointB:
        BOK=False
      
    valides = []
    if AOK:
      valides.append((self.pointB, self.pointA))
    if BOK:
      valides.append((self.pointA, self.pointB))
    
    if len(valides) == 0:
      self.ville.invalideRoute(self)
      return
      
    pA, pB = random.choice(valides)
      
    choixType = random.random()*100
    if choixType>0.50:
      angleAutorise = self.ville.rayonBraquage
      angle = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)
      if not self.fabriqueRoute(pB, angle):
        self.ville.invalideRoute(self)

    elif choixType>0.15:
      angleAutorise = self.ville.rayonBraquage * 2
      angle1 = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)+90
      angle2 = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)-90
      angle3 = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)
      r1 = self.fabriqueRoute(pB, angle1)
      r2 = self.fabriqueRoute(pB, angle2)
      r3 = self.fabriqueRoute(pB, angle3)
      if r3!=None:
        r3.ajouteParent(r1)
        r3.ajouteParent(r2)
      else:
        self.ville.invalideRoute(self)
      if r2!=None:
        r2.ajouteParent(r1)
        r2.ajouteParent(r3)
      else:
        self.ville.invalideRoute(self)
      if r1!=None:
        r1.ajouteParent(r2)
        r1.ajouteParent(r3)
      else:
        self.ville.invalideRoute(self)
    else:
      angleAutorise = self.ville.rayonBraquage*2
      direction = (random.random()*2-1.0)
      angle1 = direction*angleAutorise + self.getAngle(pA, pB)+direction*self.ville.rayonBraquage
      angle2 = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)
      r1 = self.fabriqueRoute(pB, angle1)
      r2 = self.fabriqueRoute(pB, angle2)
      if r2!=None:
        r2.ajouteParent(r1)
      else:
        self.ville.invalideRoute(self)
      if r1!=None:
        r1.ajouteParent(r2)
      else:
        self.ville.invalideRoute(self)
      
  def ajouteParent(self, parent):
    if parent==None or parent in self.parents:
      return
    self.parents.append(parent)
    
  def fabriqueRoute(self, pA, angle):
    if not self.ville.testePointValide(pA):
      return None
    pA=self.ville.snap(pA)
    vecteurDirection = Vec3(math.cos(angle/180.0*math.pi), math.sin(angle/180.0*math.pi), 0.0)

    pB = self.ville.snap(pA+vecteurDirection*self.ville.tailleVecteur)
    if not self.ville.testePointValide(pB):
      return None
    
    r, point = self.ville.intersectionne(pA, pB)
    if r!=None:
      pB=point
      if random.random()<0.6:
        self.fabriqueRoute(pB, angle)
        
    if Vec3(pB-pA).length()<self.ville.tailleGrille:
      return None
    
    nouvelleRoute=Route(pA, pB, [self], self.ville)
    self.parents.append(nouvelleRoute)
    self.ville.ajouteRoute(nouvelleRoute)
    return nouvelleRoute

  def affiche(self):
    print self.pointA, self.pointB, self.getAngle()
      
class Ville:
  routes = None
  valides = None
  noeuds = None
  tailleGrille = 0.5
  tailleVecteur = 1.0
  tailleX = -1
  tailleY = -1
  
  etape = 0
  tailleRoute = 3
  rayonBraquage = 5.0
  
  def __init__(self, tailleX, tailleY):
    self.tailleX = float(tailleX)
    self.tailleY = float(tailleY)
    
    self.routes=[]
    self.valides=[]
    self.noeuds=[]
    
    self.fabriquePremiereRoute()
    
    self.racine = NodePath("00")
    ligne = LineSegs()
    ligne.setColor(1.0,1.0,1.0)
    ligne.setThickness(1.0);
    ligne.moveTo(0.0, 0.0, 0.0)
    ligne.drawTo(self.tailleX, 0.0, 0.0)
    ligne.drawTo(self.tailleX, self.tailleY, 0.0)
    ligne.drawTo(0.0, self.tailleY, 0.0)
    ligne.drawTo(0.0, 0.0, 0.0)
    self.racine.attachNewNode(ligne.create())
    self.racine.reparentTo(render)
    
  def intersection(self, A, B, C, D):
    Ax, Ay, Az = A
    Bx, By, Bz = B
    Cx, Cy, Cz = C
    Dx, Dy, Dz = D
    
    try:
      r=((Ay-Cy)*(Dx-Cx)-(Ax-Cx)*(Dy-Cy))/((Bx-Ax)*(Dy-Cy)-(By-Ay)*(Dx-Cx))
    except:
      return None, None
    try:
      s=((Ay-Cy)*(Bx-Ax)-(Ax-Cx)*(By-Ay))/((Bx-Ax)*(Dy-Cy)-(By-Ay)*(Dx-Cx))
    except:
      return None, None
    if 0<r and r<1 and 0<s and s<1:
      point = Point3(A[0]+r*(B[0]-A[0]), A[1]+r*(B[1]-A[1]), 0.0)
      return r, point
    else:
      return None, None
      
  def intersectionne(self, pointA, pointB):
    minr = 2.0
    minpoint=None
    for route in self.routes:
      if route.taille==self.tailleRoute:
        r, point = self.intersection(pointA, pointB, route.pointA, route.pointB)
        if r!=None and r!=0 and r!=1 and r<minr:
          minr = r
          minpoint = point
        
    if minpoint!=None:
      return minr, minpoint
    return None, None

  def snap(self, point):
    for noeud in self.noeuds:
      if Vec3(noeud-point)<=self.tailleGrille:
        return noeud
    return point
    
  def ajouteRoute(self, route):
    self.routes.append(route)
    self.valides.append(route)
    if route.pointA not in self.noeuds:
      self.noeuds.append(route.pointA)
    if route.pointB not in self.noeuds:
      self.noeuds.append(route.pointB)
    
  def invalideRoute(self, route):
    while self.valides.count(route)>0:
      self.valides.remove(route)
    
  def fabriquePremiereRoute(self):
    pAx=random.random()*self.tailleX
    pAy=random.random()*self.tailleY
    pAz=0.0
    pA = self.snap(Point3(pAx, pAy, pAz))
    pBx=random.random()*self.tailleX
    pBy=random.random()*self.tailleY
    pBz=0.0
    pB = Point3(pBx, pBy, pBz)
    vecRoute = Vec3(*(pB-pA))
    vecRoute.normalize()
    vecRoute = vecRoute*self.tailleVecteur
    pB = self.snap(pA+vecRoute)
    if not self.testePointValide(pB):
      pB = self.snap(pA-vecRoute)
      if not self.testePointValide(pB):
        print "snif"
    self.ajouteRoute(Route(pA, pB, None, proxy(self))) 
    
  def testePointValide(self, point):
    if point[0]>=0.0 and point[0]<self.tailleX:
      if point[1]>=0.0 and point[1]<self.tailleY:
        return True
    return False
    
  def affiche(self):
    print "Ville :"
    print "- Taille", self.tailleX,"x",self.tailleY
    print "- Routes (",len(self.routes),")"
    for route in self.routes:
      route.affiche()
      
  def ping(self, task):
    if self.etape in (0,1,2):
      if len(self.valides)==0:
        self.etape+=1
        print "Passage a l'etape", self.etape
        self.tailleRoute-=1
        if self.etape==1:
          self.rayonBraquage*=1.5
        if self.tailleRoute>0:
          self.fabriquePremiereRoute()
      else:
        #route=random.choice(self.valides)
        #route.continueRoute()
        pass
      saveValide = self.valides[:]
      for route in saveValide:
        route.continueRoute()
    return task.cont


ville = Ville(500,500)
taskMgr.add(ville.ping, 'PingVille', 5)

run()
