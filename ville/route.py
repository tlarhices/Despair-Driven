#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *

class Route:
  pointA = None
  pointB = None
  taille = None
  racine = None
  filtres = None
  
  def __init__(self, pointA, pointB, taille, ville=None):
    self.pointA = Vec3(*pointA)
    self.pointB = Vec3(*pointB)
    self.taille = taille
    self.racine = None
    self.estUnPont=False
    if self.pointA[2]<=0.0:
      self.pointA[2]=1.0
      self.estUnPont=True
    if self.pointB[2]<=0.0:
      self.pointB[2]=1.0
      self.estUnPont=True
    self.getFiltres()
    
  def getFiltres(self):
    self.filtres=[]
    import sys, os
    sys.path.append(os.path.join(".","routes"))
    for fichier in os.listdir(os.path.join(".","routes")):
      if fichier.endswith(".py"):
        try:
          _temp = __import__(fichier[:-3], globals(), locals(), ['DessinRoute'], -1)
          DessinRoute = _temp.DessinRoute() #On appel le constructeur pour être sûr que ça marche et attraper les infos de classe
          self.filtres.append(_temp.DessinRoute)
        except AttributeError:
          print "Avertissement :: ",os.path.join(".","routes",fichier),"n'est pas un plugin de dessin de route valide"
    
  def fabrique(self):
    if self.racine!=None:
      self.supprime()
    
    couleur = (0.1,0.1,0.1)
    #if self.taille==3:
    #  couleur = (1.0,0.0,0.0)
    self.racine = NodePath("00")
    ligne = LineSegs()
    ligne.setColor(*couleur)
    ligne.setThickness(self.taille);
    ligne.moveTo(*self.pointA)
    ligne.drawTo(*self.pointB)
    self.racine.attachNewNode(ligne.create())
    self.racine.reparentTo(render)
    if self.taille>=3:
      self.racine.setLightOff()
  
  def getNormale(self, route):
    dx=route.pointB[0]-route.pointA[0]
    dy=route.pointB[1]-route.pointA[1]
    n=Vec3(dy, -dx, 0.0)
    n.normalize()
    return n
    
  def getNormales(self, routes):
    n = self.getNormale(self)
    nA=None
    nB=None
    for route in routes:
      if route.pointB == self.pointA:
        nA = self.getNormale(route)
      if route.pointA == self.pointA:
        nA = -self.getNormale(route)
      if route.pointA == self.pointB:
        nB = self.getNormale(route)
      if route.pointB == self.pointB:
        nB = -self.getNormale(route)
    if nA==None:
      nA=n #Survient dans le cas des culs de sac
    if nB==None:
      nB=n #Survient dans le cas des culs de sac
    nA=(n+nA)/2
    nB=(n+nB)/2
    return nA, nB
    
  def hauteQualite(self, ville):
    routes = []
    cptA=0
    cptB=0
    for route in ville.routes:
      if tuple(route.pointA)==tuple(self.pointA):
        routes.append(route)
        cptA+=1
      if tuple(route.pointB)==tuple(self.pointA):
        routes.append(route)
        cptA+=1
      if tuple(route.pointA)==tuple(self.pointB):
        routes.append(route)
        cptB+=1
      if tuple(route.pointB)==tuple(self.pointB):
        routes.append(route)
        cptB+=1
    while self in routes:
      routes.remove(self)
      
    for filtre in self.filtres:
      filtre = filtre()
      if filtre.filtre(routes, cptA, cptB):
        filtre.fabrique(self, routes, cptA, cptB)
        return
    print "Configuration non geree :", len(routes), cptA, cptB
    return self.fabrique()
      
  def supprime(self):
    if self.racine!=None:
      self.racine.detachNode()
      self.racine.removeNode()
      self.racine = None
    
  def getCoord(self):
    return self.pointA, self.pointB
    
  def sauvegarde(self):
    out = "R||%s||%s||%f>" %(str(list(self.pointA)), str(list(self.pointB)), self.taille)
    return out
