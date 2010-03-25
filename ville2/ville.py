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
        route.ajouteParent(self)
      
    self.pointA = pointA
    self.pointB = pointB
    self.ville = ville
    if taille==None:
      self.taille = ville.tailleRoute
    else:
      self.taille=taille
    self.fabrique()
    #self.ajouteBatiments(1)
    #self.ajouteBatiments(-1)
    
  def ajouteBatiments(self, direction):
    i=0.0
    A=self.pointA
    B=self.pointB
    rayon = 0.5
    pas = 1.0/(B-A).length()*rayon
    Px=A[0]-5*(B[0]-A[0])
    Py=A[1]-5*(B[1]-A[1])
    Pz=A[2]-5*(B[2]-A[2])
    prev=Vec3(Px, Py, Pz)
    
    dx=B[0]-A[0]
    dy=B[1]-A[1]
    
    n=Vec3(direction*dy, -direction*dx, 0.0)
    n.normalize()
    
    cpt=0
    dec = random.random()*rayon*30
    batiments = []
    while i<=1.0:
      i+=pas
      taille=random.random()*1.0+0.5
      Cx = A[0]+i*(B[0]-A[0])
      Cy = A[1]+i*(B[1]-A[1])
      Cz = 0.0
      Px=A[0]+i*(B[0]-A[0])+n[0]*taille
      Py=A[1]+i*(B[1]-A[1])+n[1]*taille
      point = Vec3(Px,Py,0.0)
      point[2]=A[2]
      
      if (point-prev).length()>3*rayon+dec:
        if True:#self.sol.pointValide(point):
            noeudColl = self.collisionBatimentBatiment(point, taille)
            if not noeudColl:
              if not self.collisionBatimentLigne(point, taille):
                if random.random()>0.4:
                  cpt+=1
                  batiment = Batiment(point, Vec3(Cx,Cy,Cz), taille, 1.0)
                  batiments.append(batiment)
                  self.batiments.append(batiment)
            else:
              facteur = min(0.2 * 6.0 / float(len(self.batiments)), 0.8)
              facteur = max(0.0, facteur)
              importance = noeudColl.importance
              importance = importance + facteur
              noeudColl.setImportance(importance)
        prev=point
    return batiments

    
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
    ligne.setColor(self.distanceDepuisDernierCroisement()/dic,0.0,0.0)
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

    distance = self.distanceDepuisDernierCroisement()
    do = distance
    if distance<100000:
      dic=min(self.ville.tailleX, self.ville.tailleY)*2
      distance = (distance/dic)/2
    else:
      distance = 0.05
      
    choixType = random.random()*100
    if choixType>self.ville.chanceSplit:#10:#1.0/(distance/dic):
      #print choixType, 1.0-distance, do
      angleAutorise = self.ville.rayonBraquage
      angle = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)
      if not self.fabriqueRoute(pB, angle):
        self.ville.invalideRoute(self)

    else:
      #print choixType, 1.0-distance, do, "split"
      angleAutorise = self.ville.rayonBraquage * 2
      angle1 = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)+90
      angle2 = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)-90
      angle3 = (random.random()*2-1.0)*angleAutorise + self.getAngle(pA, pB)
      
      r1, r2, r3 = False, False, False
      
      if random.random()>0.66:
        r1 = self.fabriqueRoute(pB, angle1)
      if random.random()>0.66:
        r2 = self.fabriqueRoute(pB, angle2)
      if random.random()>0.10:
        r3 = self.fabriqueRoute(pB, angle3)
      
      if r3!=None:
        if r3!=False:
          if r1!=False:
            r3.ajouteParent(r1)
          if r2!=False:
            r3.ajouteParent(r2)
      else:
        self.ville.invalideRoute(self)
      if r2!=None:
        if r2!=False:
          if r1!=False:
            r2.ajouteParent(r1)
          if r3!=False:
            r2.ajouteParent(r3)
      else:
        self.ville.invalideRoute(self)
      if r1!=None:
        if r1!=False:
          if r2!=False:
            r1.ajouteParent(r2)
          if r3!=False:
            r1.ajouteParent(r3)
      else:
        self.ville.invalideRoute(self)
      
  def ajouteParent(self, parent):
    if parent==None or parent==self or parent in self.parents:
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
    
    r, point, route = self.ville.intersectionne(pA, pB)
    if r!=None:
      pB=point
      
      route.detruit()
      routeA=Route(route.pointA, pB, None, self.ville)
      self.ville.ajouteRoute(routeA)
      routeB=Route(pB, route.pointB, None, self.ville)
      self.ville.ajouteRoute(routeB)
      
      if random.random()<self.ville.transpercement:
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
  tailleGrille = 0.53
  tailleVecteur = 1.0
  tailleX = -1
  tailleY = -1
  
  etape = 0
  tailleRoute = 3
  rayonBraquage = 5.0
  transpercement = 0.6
  chanceSplit = 0.4
  
  def __init__(self, tailleX, tailleY):
    self.tailleX = float(tailleX)
    self.tailleY = float(tailleY)
    base.cam.setPos(tailleX/2, tailleX*1.5+tailleY ,tailleY/2)
    base.cam.lookAt(tailleX/2, tailleY/2, 0.0)
    
    self.routes=[]
    self.valides=[]
    self.noeuds=[]
    
    self.fabriquePremiereRoute()
    self.racine = self.dessineRectangle((1.0,1.0,1.0), Point3(0.0,0.0,0.0), Point3(self.tailleX, self.tailleY, 0.0))
    self.racine.reparentTo(render)
    
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
      print "compactage de la zone %i/%i\r" %(cpt, taille),
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
    return out
        
  def getVoisins(self, zone, zones):
    voisins = [zone]
    minx = min(zone[0][0], zone[1][0])
    maxx = max(zone[0][0], zone[1][0])
    miny = min(zone[0][1], zone[1][1])
    maxy = max(zone[0][1], zone[1][1])

    if maxx-minx<=self.tailleGrille*4:
      return voisins
    if maxy-miny<=self.tailleGrille*4:
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
      
  def intersectionne(self, pointA, pointB):
    minr = 2.0
    minpoint=None
    minroute = None
    for route in self.routes:
      if True:#route.taille==self.tailleRoute:
        r, point = self.intersection(pointA, pointB, route.pointA, route.pointB)
        if r!=None and r!=0 and r!=1 and r<minr:
          minr = r
          minpoint = point
          minroute = route
          
        
    if minpoint!=None:
      return minr, minpoint, minroute
    return None, None, None

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

    pAx=random.random()*(maxx-minx)+minx
    pAy=random.random()*(maxy-miny)+miny
    pAz=0.0
    pA = self.snap(Point3(pAx, pAy, pAz))
    pBx=random.random()*(maxx-minx)+minx
    pBy=random.random()*(maxy-miny)+miny
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
        print "calcul des zones"
        zones = self.calculZones((Point3(0.0,0.0,0.0), Point3(self.tailleX, self.tailleY, 0.0)))
        print "compactage"
        polys = self.compacteZones(zones)
        print 
        print "total zones : ",len(polys)
        #for poly in polys:
        #  couleur = (random.random(), random.random(), random.random())
        #  for zone in poly:
        #    self.dessineRectangle(couleur, zone[0], zone[1], cross=True)
        self.etape+=1
        print "Passage a l'etape", self.etape
        self.tailleRoute-=1
        self.transpercement+=0.15
        self.chanceSplit += 0.25
        if self.etape==1:
          self.rayonBraquage*=1.5
        if self.tailleRoute>0:
          taille = len(zones)
          for zones in polys:
            zone = random.choice(zones)
            minx = min(zone[0][0], zone[1][0])
            maxx = max(zone[0][0], zone[1][0])
            miny = min(zone[0][1], zone[1][1])
            maxy = max(zone[0][1], zone[1][1])
            self.fabriquePremiereRoute(zone=zone)
      else:
        #route=random.choice(self.valides)
        #route.continueRoute()
        saveValide = self.valides[:10]
        self.valides = self.valides[10:]+self.valides[:10]
        print "Current elements %i   \r" %len(self.valides),
        for route in saveValide:
          route.continueRoute()
    return task.cont


ville = Ville(500,500)
taskMgr.add(ville.ping, 'PingVille', 5)

run()
