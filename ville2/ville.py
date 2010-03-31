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

class Sol:
  sol = None
  eau = None
  
  def __init__(self, tailleX, tailleY):
    self.tailleX = int(tailleX+0.5)
    self.tailleY = int(tailleY+0.5)
    self.sol = []
    self.eau = []
    
  def genereSol(self):
    
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
        mdl=loader.loadModel("sphere.egg")
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

  def getAltitude(self, pt):
    x,y,z = pt
    if x<0 or x>=self.tailleX:
      return -1000
    if y<0 or y>=self.tailleY:
      return -1000
    return self.sol[int(x)][int(y)]#max(self.sol[int(x)][int(y)], self.eau([int(x)][int(y)]))


  def getMinMax(self):
    self.minAlt = self.sol[0][0]
    self.maxAlt = self.sol[0][0]
    for i in range(0, self.tailleX):
      for j in range(0, self.tailleY):
        self.minAlt = min(self.minAlt, self.sol[i][j])
        self.maxAlt = max(self.maxAlt, self.sol[i][j])
    self.altitudeMax = self.maxAlt/2
    
  afficheModele = True
  affichei = 0
  affichej = 0
  racineSol = None
  def affiche(self):
    if not self.afficheModele:
      self.affiche=self.finAffiche
      
    if self.racineSol == None:
      self.racineSol = NodePath("sol")
      self.racineSol.reparentTo(render)
    for i in range(0,self.tailleY*3):
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

    
class Route:
  parents = None
  pointA = None
  pointB = None
  taille = None
  ville = None
  type = None
  couleur = (0.0,0.0,0.0)
  limites = None
  
  influencePopulationDirection = 1.0
  influencePopulation = 30.0
  
  influenceIndustrieDirection = 1.0
  influenceIndustrie = 20.0
  
  def __init__(self, pointA, pointB, parents, ville, taille=None):
    self.type = Route
    self.transpercement = ville.transpercement
    self.limites = {Route:(0,360), Autoroute:(10,35), Nationale:(0,360)}
    
    self.parents = []
    if parents!=None:
      self.parents+=parents
      
    for route in ville.routes:
      if pointA==route.pointA or pointA==route.pointB or pointB==route.pointA or pointB==route.pointB:
        self.ajouteParent(route)
        route.ajouteParent(self)
      
    self.pointA = pointA
    self.pointB = pointB
    self.ville = ville
    if taille==None:
      self.taille = ville.tailleRoute
    else:
      self.taille=taille
    self.fabrique()
    self.ville.ajoutePop(self.pointA, self.influencePopulation, self.influencePopulationDirection)
    self.ville.ajoutePop(self.pointB, self.influencePopulation, self.influencePopulationDirection)
    self.ville.ajouteIndus(self.pointA, self.influenceIndustrie, self.influenceIndustrieDirection)
    self.ville.ajouteIndus(self.pointB, self.influenceIndustrie, self.influenceIndustrieDirection)
    
  def detruit(self):
    self.ville.supprimeRoute(self)
    self.racine.detachNode()
    self.racine.removeNode()
    self.racine = None
    
  def distanceDepuisDernierCroisement(self, cote=None):
    if cote==None:
      distance=min(self.distanceDepuisDernierCroisement(self.pointA), self.distanceDepuisDernierCroisement(self.pointB))
    else:
      distance = Vec3(self.pointB-self.pointA).length()
      
      routes = []
      for route in self.parents:
        if route.pointA == cote:
          routes.append((route, route.pointB))
        if route.pointB == cote:
          routes.append((route, route.pointA))
          
      if len(routes)==0:
        distance = 10000000.0 #La route n'est pas terminee (cul de sac)
      elif len(routes)==1: #La route continue
        distance += routes[0][0].distanceDepuisDernierCroisement(routes[0][1])
      else:
        pass #On a atteind un croisement       
    return distance
    
  def fabrique(self):
    self.racine = NodePath("00")
    ligne = LineSegs()
    dic=min(self.ville.tailleX, self.ville.tailleY)
    ligne.setColor(*self.couleur) #self.distanceDepuisDernierCroisement()/dic
    ligne.setThickness(self.taille);
    A=Point3(self.pointA)
    A[2]=self.ville.sol.getAltitude(A)
    B=Point3(self.pointB)
    B[2]=self.ville.sol.getAltitude(B)
    ligne.moveTo(A)
    ligne.drawTo(B)
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
    
  def angleCibleAleatoire(self, pA, pB):
    angleAutorise = self.ville.rayonBraquage
    angle = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)
    return angle
    
  def angleCibleGlobal(self, pA, pB):
    return self.angleCibleAleatoire(pA, pB)
    
  def split(self):
    return False
    
  def testeConditionsLocales(self, pA, angle):
    return True
    
  def doSplit(self, pA, pB, force=False):
    return

  def testeValide(self):
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
      return False
    return valides
    
  def continueRoute(self):
    configurationsValides = self.testeValide()
    if not configurationsValides:
      return
    pA, pB = random.choice(configurationsValides)
    
    if self.split():
      self.doSplit(pA, pB)
    else:
      angle = self.angleCibleGlobal(pA, pB)
      if self.testeConditionsLocales(pB, angle):
        if not self.fabriqueRoute(pB, angle):
          self.abandonneRoute()
          self.ville.invalideRoute(self)
      else:
        angle=self.tourneRoute(pB, angle)
        if self.testeConditionsLocales(pB, angle):
          if not self.fabriqueRoute(pB, angle):
            self.abandonneRoute()
            self.ville.invalideRoute(self)
        else:
          self.detruit()
    self.testeValide()
    
  def abandonneRoute(self):
    pass
    
  def ajouteParent(self, parent):
    if parent==None or parent==self or parent in self.parents:
      return
    self.parents.append(parent)
    
  def gereConditionsLocales(self, pA, pB, angle):
    #On teste l'intersection
    r, point, route = self.ville.intersectionne(pA, pB, self.limites)
    if r!=None:
      pB=point
      
      route.detruit()
      routeA=self.type(route.pointA, pB, None, self.ville)
      self.ville.ajouteRoute(routeA)
      routeB=self.type(pB, route.pointB, None, self.ville)
      self.ville.ajouteRoute(routeB)
      
      if random.random()<self.transpercement:
        self.fabriqueRoute(pB, angle)
        
    #On cherche si on est proche d'un croisement
    minPoint, minDist = pB, 1000000000
    direction = Vec3(pA-pB)
    direction.normalize()
    for route in self.ville.routes:
      v=Vec3(pB-route.pointA)
      v.normalize()
      if Vec3(route.pointA-pB).lengthSquared()<minDist and v.angleDeg(direction)<20:
        minPoint = route.pointA
        minDist = Vec3(route.pointA-pB).lengthSquared()
        
      v=Vec3(pB-route.pointB)
      v.normalize()
      if Vec3(route.pointB-pB).lengthSquared()<minDist and v.angleDeg(direction)<20:
        minPoint = route.pointB
        minDist = Vec3(route.pointB-pB).lengthSquared()
        
    if minDist<=0.2 and minPoint!=None and minPoint!=pA:
      pB=minPoint
        
    return pA, pB
    
    
  def fabriqueRoute(self, pA, angle, type=None):
    
    if type==None:
      type=self.type
    
    
    if not self.ville.testePointValide(pA):
      return None
    pA=self.ville.snap(pA)
    vecteurDirection = Vec3(math.cos(angle/180.0*math.pi), math.sin(angle/180.0*math.pi), 0.0)

    pB = self.ville.snap(pA+vecteurDirection*self.ville.tailleVecteur)
    if not self.ville.testePointValide(pB):
      return None
    
    pA, pB = self.gereConditionsLocales(pA, pB, angle)
        
    if Vec3(pB-pA).length()<self.ville.tailleGrille:
      return None
    
    nouvelleRoute=type(pA, pB, [self], self.ville)
    self.parents.append(nouvelleRoute)
    self.ville.ajouteRoute(nouvelleRoute)
    return nouvelleRoute

  def affiche(self):
    print self.pointA, self.pointB, self.getAngle()
    
    
class Autoroute(Route):
  couleur = (1.0,0.0,0.0)
  influencePopulationDirection = -3.5
  influencePopulation = 20.0

  influenceIndustrieDirection = 1.5
  influenceIndustrie = 30.0

  def __init__(self, pointA, pointB, parents, ville, taille=None):
    Route.__init__(self, pointA, pointB, parents, ville, taille=taille)
    self.type = Autoroute
    self.transpercement = ville.transpercement*2
    self.limites = {None:(0,55)}

  def abandonneRoute(self):
    self.doSplit(self.pointA, self.pointB, force=True)
  
  def angleCibleAleatoire(self, pA, pB):
    angleAutorise = self.ville.rayonBraquage
    angle = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)
    return angle
    
  def getAltitude(self, pB, angle):
    vecteurDirection = Vec3(math.cos(angle/180.0*math.pi), math.sin(angle/180.0*math.pi), 0.0)

    pC = self.ville.snap(pB+vecteurDirection*self.ville.tailleVecteur)
    if not self.ville.testePointValide(pC):
      return 10000
    return self.ville.sol.getAltitude(pC)

  def affiche(self):
    print self.pointA, self.pointB, self.getAngle()
    
  def testeAngle(self, pB, angle):
    altB = self.ville.sol.getAltitude(pB)
    altC = self.getAltitude(pB, angle)
    if altC<0.5:
      return False, 800000
    return True, altB-altC
    
  def angleCibleGlobal(self, pA, pB):
    centre = self.getAngle(pA, pB)
    deb = centre-self.ville.rayonBraquage
    fin = centre+self.ville.rayonBraquage
    echantillons = 250.0
    pas = (fin-deb)/echantillons
    
    minAngle = centre
    minOK, minEcart = self.testeAngle(pB, centre)
    minEcart = abs(minEcart)
    while deb<fin:
      ok, ecart = self.testeAngle(pB, deb)
      ecart = abs(ecart)
      if ecart<minEcart:
        minAngle=deb
        minEcart=ecart
        minOK=ok
      deb+=pas
    if not ok:
      centre = self.getAngle(pA, pB)
      deb = centre-self.ville.rayonBraquage*2.5
      fin = centre+self.ville.rayonBraquage*2.5
      echantillons = 250.0
      pas = (fin-deb)/echantillons

      minAngle = centre
      maxAlt = self.getAltitude(pB, centre)
      while deb<fin:
        alt = self.getAltitude(pB, deb)
        if maxAlt<alt:
          minAngle=deb
          maxAlt=alt
        deb+=pas
      
    return minAngle
    
  def split(self):
    if random.random()>0.50:
      if self.distanceDepuisDernierCroisement()>100 and self.distanceDepuisDernierCroisement()<=10000:
        return True
    return False
    
  def testeConditionsLocales(self, pA, angle):
    return True
    
  def doSplit(self, pA, pB, force=False):
    self.fabriqueRoute(pB, self.getAngle(pA, pB))
    type=self.type
    if force or random.random()<0.98:
      type=Nationale
      
      angle = self.angleCibleAleatoire(pA, pB)+20
      if self.testeConditionsLocales(pB, angle):
        self.fabriqueRoute(pB, angle, type=type)
      angle = self.angleCibleAleatoire(pB, pA)-20
      if self.testeConditionsLocales(pA, angle):
        self.fabriqueRoute(pB, angle, type=type)

      angle = self.angleCibleAleatoire(pA, pB)-20
      if self.testeConditionsLocales(pB, angle):
        self.fabriqueRoute(pB, angle, type=type)
      angle = self.angleCibleAleatoire(pB, pA)+20
      if self.testeConditionsLocales(pA, angle):
        self.fabriqueRoute(pB, angle, type=type)
      
    else:
      if random.random()>0.952:
        angle = self.angleCibleAleatoire(pA, pB)+20
        if self.testeConditionsLocales(pB, angle):
          self.fabriqueRoute(pB, angle, type=type)
      if random.random()>0.952:
        angle = self.angleCibleAleatoire(pA, pB)-20
        if self.testeConditionsLocales(pB, angle):
          self.fabriqueRoute(pB, angle, type=type)

      if random.random()>0.952:
        angle = self.angleCibleAleatoire(pB, pA)+20
        if self.testeConditionsLocales(pA, angle):
          self.fabriqueRoute(pB, angle, type=type)
      if random.random()>0.952:
        angle = self.angleCibleAleatoire(pB, pA)-20
        if self.testeConditionsLocales(pA, angle):
          self.fabriqueRoute(pB, angle, type=type)

class Nationale(Route):
  couleur = (0.0,1.0,1.0)

  def __init__(self, pointA, pointB, parents, ville, taille=None):
    Route.__init__(self, pointA, pointB, parents, ville, taille=taille)
    self.type = Nationale

  def angleCibleAleatoire(self, pA, pB):
    angleAutorise = self.ville.rayonBraquage
    angle = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)
    return angle
    
  def angleCibleGlobal(self, pA, pB):
    angle = self.angleCibleAleatoire(pA, pB)
    vecteurDirection = Vec3(math.cos(angle/180.0*math.pi), math.sin(angle/180.0*math.pi), 0.0)

    pC = self.ville.snap(pB+vecteurDirection*self.ville.tailleVecteur)
    if not self.ville.testePointValide(pC):
      centre = self.getAngle(pA, pB)
      deb = centre-95
      fin = centre+95
      echantillons = 350.0
      pas = (fin-deb)/echantillons
      delta=0
      
      while centre+delta<fin:
        vecteurDirection = Vec3(math.cos((centre+delta)/180.0*math.pi), math.sin((centre+delta)/180.0*math.pi), 0.0)
        pC = self.ville.snap(pB+vecteurDirection*self.ville.tailleVecteur)
        if self.ville.testePointValide(pC):
          return centre+delta
        vecteurDirection = Vec3(math.cos((centre-delta)/180.0*math.pi), math.sin((centre-delta)/180.0*math.pi), 0.0)
        pC = self.ville.snap(pB+vecteurDirection*self.ville.tailleVecteur)
        if self.ville.testePointValide(pC):
          return centre-delta
        delta+=pas

    return angle
    
  def split(self):
    if random.random()>0.986:
      if self.distanceDepuisDernierCroisement()>25 and self.distanceDepuisDernierCroisement()<=10000:
        return True
    return False
    
  def testeConditionsLocales(self, pA, angle):
    return True
    
  def doSplit(self, pA, pB, force=False):
    self.fabriqueRoute(pB, self.getAngle(pA, pB))
    if random.random()>0.9852:
      angle = self.angleCibleAleatoire(pA, pB)+90*random.random()
      if self.testeConditionsLocales(pB, angle):
        self.fabriqueRoute(pB, angle)
    if random.random()>0.9852:
      angle = self.angleCibleAleatoire(pA, pB)-90*random.random()
      if self.testeConditionsLocales(pB, angle):
        self.fabriqueRoute(pB, angle)

    if random.random()>0.9852:
      angle = self.angleCibleAleatoire(pB, pA)+90*random.random()
      if self.testeConditionsLocales(pA, angle):
        self.fabriqueRoute(pB, angle)
    if random.random()>0.9852:
      angle = self.angleCibleAleatoire(pB, pA)-90*random.random()
      if self.testeConditionsLocales(pA, angle):
        self.fabriqueRoute(pB, angle)
        
class Rue(Route):
  couleur = (0.0,0.0,0.0)

  def __init__(self, pointA, pointB, parents, ville, taille=None):
    Route.__init__(self, pointA, pointB, parents, ville, taille=taille)
    self.type = Rue
    self.limites = {Autoroute:(-10,-1), None:(0,800)}

  def angleCibleAleatoire(self, pA, pB):
    angleAutorise = self.ville.rayonBraquage
    angle = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)
    return angle
    
  def angleCibleGlobal(self, pA, pB):
    return self.angleCibleAleatoire(pA, pB)
    
  def split(self):
    if random.random()>0.6:
      if self.distanceDepuisDernierCroisement()>3 and self.distanceDepuisDernierCroisement()<=10000:
        return True
    return False
    
  def testeConditionsLocales(self, pA, angle):
    return True
    
  def doSplit(self, pA, pB, force=False):
    self.fabriqueRoute(pB, self.getAngle(pA, pB))
    if random.random()>0.952:
      angle = self.angleCibleAleatoire(pA, pB)+90*random.random()
      if self.testeConditionsLocales(pB, angle):
        self.fabriqueRoute(pB, angle)
    if random.random()>0.952:
      angle = self.angleCibleAleatoire(pA, pB)-90*random.random()
      if self.testeConditionsLocales(pB, angle):
        self.fabriqueRoute(pB, angle)

    if random.random()>0.952:
      angle = self.angleCibleAleatoire(pB, pA)+90*random.random()
      if self.testeConditionsLocales(pA, angle):
        self.fabriqueRoute(pB, angle)
    if random.random()>0.952:
      angle = self.angleCibleAleatoire(pB, pA)-90*random.random()
      if self.testeConditionsLocales(pA, angle):
        self.fabriqueRoute(pB, angle)

    
class Ville:
  routes = None
  valides = None
  noeuds = None
  tailleGrille = 0.53
  tailleVecteur = 1.0
  tailleX = -1
  tailleY = -1
  
  etape = 0
  tailleRoute = 3
  rayonBraquage = 5.0
  transpercement = 0.6
  chanceSplit = 0.4
  
  popMap = None
  indusMap = None
  
  testePopulation = False
  
  def __init__(self, tailleX, tailleY):
    self.tailleX = float(tailleX)
    self.tailleY = float(tailleY)
    
    self.sol=Sol(tailleX, tailleY)
    self.sol.genereSol()

    dlight = PointLight('my dlight')
    dlnp = render.attachNewNode(dlight)
    self.sol.getMinMax()
    dlnp.setPos(self.tailleX/2, self.tailleY/2, self.sol.altitudeMax*5)
    render.setLight(dlnp)

    base.cam.setPos(tailleX/2, tailleX*1.5+tailleY ,tailleY/2)
    base.cam.lookAt(tailleX/2, tailleY/2, 0.0)
    
    self.routes=[]
    self.valides=[]
    self.noeuds=[]
    
    self.popMap = []
    self.indusMap = []
    for i in range(0, int(self.tailleX+1.5)):
      self.popMap.append([])
      self.indusMap.append([])
      for j in range(0, int(self.tailleY+1.5)):
        self.popMap[i].append(0.0)
        self.indusMap[i].append(0.0)

    self.fabriquePremiereRoute()
    self.fabriquePremiereRoute()
    self.racine = self.dessineRectangle((1.0,1.0,1.0), Point3(0.0,0.0,0.0), Point3(self.tailleX, self.tailleY, 0.0))
    self.racine.reparentTo(render)
    
        
  def ajoutePop(self, point, rayon, ajoute):
    k=int(point[0]+0.5)
    l=int(point[1]+0.5)
    for i in range(int(-rayon), int(rayon+0.5)):
      for j in range(int(-rayon), int(rayon+0.5)):
        if i+k>=0 and i+k<self.tailleX and j+l>=0 and j+l<self.tailleY:
          self.popMap[i+k][j+l] += ajoute*math.sqrt(i*i+j*j)

  def ajouteIndus(self, point, rayon, ajoute):
    k=int(point[0]+0.5)
    l=int(point[1]+0.5)
    for i in range(int(-rayon), int(rayon+0.5)):
      for j in range(int(-rayon), int(rayon+0.5)):
        if i+k>=0 and i+k<self.tailleX and j+l>=0 and j+l<self.tailleY:
          self.indusMap[i+k][j+l] += ajoute*math.sqrt(i*i+j*j)
        
  def printPop(self):
    mx = 0.0
    for i in range(0, int(self.tailleX)):
      print "Print %i/%i  \r" %(i, self.tailleX),
      if i%3==0:
        for j in range(0, int(self.tailleY)):
          if j%3==0:
            if self.testePointValide(Point3(i,j,0.0)):
              if self.popMap[i][j] > 0.05:
                mdl = loader.loadModel("box.egg")
                mdl.reparentTo(render)
                mdl.setPos(i,j, self.sol.getAltitude(Point3(i,j,0.0))+0.5)
                mdl.setScale(self.popMap[i][j]/5000)
                mx = max(mx, self.popMap[i][j])
              if self.indusMap[i][j] > 0.05:
                mdl = loader.loadModel("box.egg")
                mdl.reparentTo(render)
                mdl.setPos(i+0.5,j+0.5, self.sol.getAltitude(Point3(i,j,0.0))+0.5)
                mdl.setScale(self.indusMap[i][j]/5000)
                mdl.setColor(1.0,0.0,0.0)
                mx = max(mx, self.indusMap[i][j])
              
    print
    print "max", mx
    
  def dessineRectangle(self, couleur, pointA, pointB, cross=False):
    racine = NodePath("00")
    ligne = LineSegs()
    ligne.setColor(*couleur)
    ligne.setThickness(1.0);
    ligne.moveTo(pointA)
    ligne.drawTo(pointB[0], pointA[1], pointA[2])
    ligne.drawTo(pointB)
    ligne.drawTo(pointA[0], pointB[1], pointA[2])
    ligne.drawTo(pointA)
    if cross:
      ligne.drawTo(pointB)
      ligne.moveTo(pointB[0], pointA[1], pointA[2])
      ligne.drawTo(pointA[0], pointB[1], pointA[2])
      
    racine.attachNewNode(ligne.create())
    racine.reparentTo(render)
    return racine
    
  def calculZones(self, rectangle):
    zones = []
    pa, pb = rectangle
    cx = (pa[0]+pb[0])/2.0
    cy = (pa[1]+pb[1])/2.0
    cz = (pa[2]+pb[2])/2.0
    c = Point3(cx, cy, cz)
    r1 = (pa, c)
    r2 = (Point3(c[0], pa[1], c[2]), Point3(pb[0], c[1], c[2]))
    r3 = (Point3(pa[0], c[1], c[2]), Point3(c[0], pb[1], c[2]))
    r4 = (c, pb)
    
    r=self.rectangleVide(r1)
    if r==1:
      zones.append(r1)
    elif r==0:
      zones+=self.calculZones(r1)
    else:
      #coul = (random.random(), random.random(), random.random())
      #self.dessineRectangle(coul, r1[0], r1[1], cross=True)
      pass

    r=self.rectangleVide(r2)
    if r==1:
      zones.append(r2)
    elif r==0:
      zones+=self.calculZones(r2)
    else:
      #coul = (random.random(), random.random(), random.random())
      #self.dessineRectangle(coul, r2[0], r2[1], cross=True)
      pass
    
    r=self.rectangleVide(r3)
    if r==1:
      zones.append(r3)
    elif r==0:
      zones+=self.calculZones(r3)
    else:
      #coul = (random.random(), random.random(), random.random())
      #self.dessineRectangle(coul, r3[0], r3[1], cross=True)
      pass

    r=self.rectangleVide(r4)
    if r==1:
      zones.append(r4)
    elif r==0:
      zones+=self.calculZones(r4)
    else:
      #coul = (random.random(), random.random(), random.random())
      #self.dessineRectangle(coul, r4[0], r4[1], cross=True)
      pass
    return zones

  def compacteZones(self, zones):
    out = []
    cpt=0
    taille=len(zones)
    for zone in zones:
      cpt+=1
      print "Compactage de la zone %i/%i - %i \r" %(cpt, taille, len(zones)),
      zones.remove(zone)
      out.append([])
      voisins = self.getVoisins(zone, zones)
      for voisin in voisins:
        while zones.count(voisin)>0:
          zones.remove(voisin)
        if voisin not in out[-1]:
          out[-1].append(voisin)
      if len(out[-1])<20:
        out=out[:-1]
    print
    return out
        
  def getVoisins(self, zone, zones):
    voisins = [zone]
    minx = min(zone[0][0], zone[1][0])
    maxx = max(zone[0][0], zone[1][0])
    miny = min(zone[0][1], zone[1][1])
    maxy = max(zone[0][1], zone[1][1])

    if maxx-minx<=self.tailleGrille*2:
      return voisins
    if maxy-miny<=self.tailleGrille*2:
      return voisins

      
    delta = self.tailleGrille/20
    pa = Point3(minx - delta, (miny+maxy)/2, 0.0)
    pb = Point3((minx+maxx)/2, miny - delta, 0.0)
    pc = Point3(maxx + delta, (miny+maxy)/2, 0.0)
    pd = Point3((minx+maxx)/2, maxy + delta, 0.0)
      
    for zonetest in zones:
      if self.pointDansZone(zonetest, pa) or\
         self.pointDansZone(zonetest, pb) or\
         self.pointDansZone(zonetest, pc) or\
         self.pointDansZone(zonetest, pd):
        zones.remove(zonetest)
        voisins+=self.getVoisins(zonetest, zones)
    return voisins
    
  def pointDansZone(self, zone, point):
    minx = min(zone[0][0], zone[1][0])
    maxx = max(zone[0][0], zone[1][0])
    miny = min(zone[0][1], zone[1][1])
    maxy = max(zone[0][1], zone[1][1])

    if point[0]>=minx and point[0]<=maxx:
      if point[1]>=miny and point[1]<=maxy:
        return True
    return False
    
      
  def rectangleVide(self, rectangle):
    pa, pb = rectangle
    minx = min(pa[0],pb[0])
    maxx = max(pa[0],pb[0])
    miny = min(pa[1],pb[1])
    maxy = max(pa[1],pb[1])
    
    if maxx-minx<=self.tailleGrille:
      return -1
    if maxy-miny<=self.tailleGrille:
      return -1
      
    for route in self.routes:
      if route.pointA[0]>=minx and route.pointA[0]<=maxx:
        if route.pointA[1]>=miny and route.pointA[1]<=maxy:
          return 0
      if route.pointB[0]>=minx and route.pointB[0]<=maxx:
        if route.pointB[1]>=miny and route.pointB[1]<=maxy:
          return 0
    
    return 1

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
      
  def angleOK(self, angle, minAngle, maxAngle):
    if angle<0:
      angle = -angle
    if angle>180:
      angle = angle -180
    if angle<0:
      angle = -angle
      
    return (angle>=minAngle and angle<=maxAngle) or (180-angle>=minAngle and 180-angle<=maxAngle)
      
  def intersectionne(self, pointA, pointB, limites):
    #
    # limites : tableau de la forme {route: (minAngle, maxAngle), ..., None] (minAngle, maxAngle)]
    #
    minr = 2.0
    minpoint=None
    minroute = None
    for route in self.routes:
      if route.type in limites.keys():
        minAngle, maxAngle = limites[route.type]
      else:
        minAngle, maxAngle = limites[None]
        
      r, point = self.intersection(pointA, pointB, route.pointA, route.pointB)
      if r!=None and r!=0 and r!=1 and r<minr:
        if self.angleOK(Vec3(pointB-pointA).angleDeg(Vec3(route.pointB-route.pointA)), minAngle, maxAngle):
          minr = r
          minpoint = point
          minroute = route
        
    if minpoint!=None:
      return minr, minpoint, minroute
    return None, None, None

  def snap(self, point, rayon=None):
    if rayon==None:
      rayon=self.tailleGrille
    for noeud in self.noeuds:
      if Vec3(noeud-point)<=rayon:
        return noeud
    return point
    
  def ajouteRoute(self, route):
    self.routes.append(route)
    self.valides.append(route)
    if route.pointA not in self.noeuds:
      self.noeuds.append(route.pointA)
    if route.pointB not in self.noeuds:
      self.noeuds.append(route.pointB)
      
  def supprimeRoute(self, route):
    self.invalideRoute(route)
    while self.routes.count(route)>0:
      self.routes.remove(route)
    
  def invalideRoute(self, route):
    while self.valides.count(route)>0:
      self.valides.remove(route)
    
  def fabriquePremiereRoute(self, zone=None):
    if zone==None:
      zone=(Point3(0.0,0.0,0.0), Point3(self.tailleX, self.tailleY, 0.0))
    minx = min(zone[0][0], zone[1][0])
    maxx = max(zone[0][0], zone[1][0])
    miny = min(zone[0][1], zone[1][1])
    maxy = max(zone[0][1], zone[1][1])

    pAx = -1000
    pAy = -1000
    pAz = -1000
    pA=Point3(pAx, pAy, pAz)
    while not self.testePointValide(pA):
      pAx=random.random()*(maxx-minx)+minx
      pAy=random.random()*(maxy-miny)+miny
      pAz=0.0
      pA=Point3(pAx, pAy, pAz)
      pA = self.snap(pA)
    
    pBx = -1000
    pBy = -1000
    pBz = -1000
    pB=Point3(pBx, pBy, pBz)
    while not self.testePointValide(pB):
      pBx=random.random()*(maxx-minx)+minx
      pBy=random.random()*(maxy-miny)+miny
      pBz=0.0
      pB = Point3(pBx, pBy, pBz)
      pB = self.snap(pB)

    vecRoute = Vec3(*(pB-pA))
    vecRoute.normalize()
    vecRoute = vecRoute*self.tailleVecteur
    pB = self.snap(pA+vecRoute)
    if not self.testePointValide(pB):
      pB = self.snap(pA-vecRoute)
      if not self.testePointValide(pB):
        print "snif"
    self.ajouteRoute(Autoroute(pA, pB, None, proxy(self))) 
    self.routes[-1].doSplit(self.routes[-1].pointA, self.routes[-1].pointB)
    
  def testePointValide(self, point, minAlt=0.0):
    if point[0]>=0.0 and point[0]<self.tailleX:
      if point[1]>=0.0 and point[1]<self.tailleY:
        if self.sol.getAltitude(point)>minAlt:
          if not self.testePopulation:
            return True
          else:
            return self.popMap[int(point[0])][int(point[1])]>0.0 or self.indusMap[int(point[0])][int(point[1])]>0.0
    return False
    
  def affiche(self):
    print "Ville :"
    print "- Taille", self.tailleX,"x",self.tailleY
    print "- Routes (",len(self.routes),")"
    for route in self.routes:
      route.affiche()
      
  def dessineZones(self, zones, couleur, tailleMin, tailleMax):
    for zone in zones:
      minx = min(zone[0][0], zone[1][0])
      maxx = max(zone[0][0], zone[1][0])
      miny = min(zone[0][1], zone[1][1])
      maxy = max(zone[0][1], zone[1][1])
      if maxx-minx>tailleMin and maxx-minx<tailleMax:
        if maxy-miny>tailleMin and maxy-miny<tailleMax:
          self.dessineRectangle(couleur, zone[0], zone[1], cross=True)
      
  def ping(self, task):
    self.sol.affiche()
    return self.pingVrai(task)
    
  def pingVrai(self, task):
    print "Creation des autoroutes..."
    self.pingVrai = self.pingAutoroutes
    return task.cont
    
  def getZones(self):
    print "Calcul des zones..."
    zones = self.compacteZones(self.calculZones((Point3(0.0,0.0,0.0), Point3(self.tailleX, self.tailleY, 0.0))))
    print "Total zones : ",len(zones)
    return zones

  def pingAutoroutes(self, task):
    if len(self.valides)==0:
      print "Creation des quartiers"
      #self.quartiers = self.getZones()
      #print "crea"
      #for zone in self.quartiers:
      #  couleur = (1.0,1.0,1.0)#(random.random(), random.random(), random.random())
      #  self.dessineZones(zone, couleur, self.tailleGrille*2, self.tailleGrille*40)
      #print "print"
      #self.printPop()
      print "OK"
      self.fabriqueGrilleRues()
      self.testePopulation = True
      self.pingVrai = self.pingRoutes
    else:
      self.continueRoutes()
    return task.cont
    
  def pingRoutes(self, task):
    if len(self.valides)==0:
      self.pingVrai = self.pingQuartiers
    else:
      self.continueRoutes()
    return task.cont

  def pingQuartiers(self, task):
    return task.done
    

  def fabriqueGrilleRues(self):
    for route in self.routes:
      if isinstance(route, Nationale):
        choix = random.random()
        if choix>0.8:
          angle = route.getAngle(route.pointA, route.pointB)
          angle = angle+90
          vecteurDirection = Vec3(math.cos(angle/180.0*math.pi), math.sin(angle/180.0*math.pi), 0.0)
          self.ajouteRoute(Rue(route.pointA, route.pointA+vecteurDirection, None, proxy(self))) 

          angle = route.getAngle(route.pointA, route.pointB)
          angle = angle+90
          vecteurDirection = Vec3(math.cos(angle/180.0*math.pi), math.sin(angle/180.0*math.pi), 0.0)
          self.ajouteRoute(Rue(route.pointB, route.pointB+vecteurDirection, None, proxy(self))) 

          angle = route.getAngle(route.pointA, route.pointB)
          angle = angle-90
          vecteurDirection = Vec3(math.cos(angle/180.0*math.pi), math.sin(angle/180.0*math.pi), 0.0)
          self.ajouteRoute(Rue(route.pointA, route.pointA+vecteurDirection, None, proxy(self))) 

          angle = route.getAngle(route.pointA, route.pointB)
          angle = angle-90
          vecteurDirection = Vec3(math.cos(angle/180.0*math.pi), math.sin(angle/180.0*math.pi), 0.0)
          self.ajouteRoute(Rue(route.pointB, route.pointB+vecteurDirection, None, proxy(self)))         

  def continueRoutes(self):
    saveValide = self.valides[:10]
    self.valides = self.valides[10:]+self.valides[:10]
    print "Nombre d'elements %i   \r" %len(self.valides),
    for route in saveValide:
      route.continueRoute()

ville = Ville(500,500)
taskMgr.add(ville.ping, 'PingVille', 5)

run()
