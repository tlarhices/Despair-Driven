#!/usr/bin/env python
# -*- coding: utf-8 -*-
import direct.directbase.DirectStart
from pandac.PandaModules import *

from weakref import proxy

import random
import math
import time

class Ville:
  points = None
  rayon = None
  lignes = None
  batiments = None
  longueurSegment = 4.0
  
  def __init__(self, rayon):
    self.rayon = rayon
    self.points = [self.pointAlea((0.0,0.0,0.0)), self.pointAlea((0.0,0.0,0.0))]
    self.lignes = [[(self.points[0], self.points[1]), None, False]]
    self.batiments = []
    self.ajouteRouteAlea()
      
  def pointAlea(self, pt, delta=None):
    if delta==None:
      delta = self.rayon
    
    x,y,z = pt
    return ((random.random()*2-1)*delta+x, (random.random()*2-1)*delta+y, 0.0+z)
      
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
      
      
  def intersectionne(self, A, B, force=False):
    d = (Vec3(*A)-Vec3(*B)).lengthSquared()
    deb = A
    fin = B

    coll = None
    for obj in self.lignes:
      ((C,D), mdl, estAvenue) = obj
      r = self.intersection(A, B, C, D)
      if r!=None:
          
        Px=A[0]+r*(B[0]-A[0])
        Py=A[1]+r*(B[1]-A[1])
        P = Px, Py, 0.0
        if force:
          self.lignes.remove(obj)
          self.ajouteRoute(C, P, cptBatiments=False)
          self.ajouteRoute(P, D, cptBatiments=False)
        d2 = (Vec3(*A)-Vec3(*P)).lengthSquared()
        if coll==None or d2<d:
          coll=P
          d=d2
    if force:
      return None
    if coll==A:
      return None
    if coll==B:
      return None
    return coll
    
  def collisionBatimentBatiment(self, position, rayon):
    position = Vec3(*position)
    for pos, taille, noeud in self.batiments:
      if (rayon+taille)*(rayon+taille)>(position-Vec3(*pos)).lengthSquared():
        return noeud
    return False
    
  def collisionLigneBatiment(self, pointA, pointB, force=False):
    for centre, rayon, noeud in self.batiments:
      if self.collisionLigneCercle(pointA, pointB, centre, rayon):
        if not force:
          return True
        else:
          self.batiments.remove((centre,rayon,noeud))
          noeud.detachNode()
          noeud.removeNode()
    return False
    
  def collisionBatimentLigne(self, position, rayon):
    for (pointA, pointB), mdl, estAvenue in self.lignes:
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
    
    cpt=0
    dec = random.random()*rayon*30
    while i<=1.0:
      i+=pas
      taille=random.random()*1.0+0.5
      Cx = A[0]+i*(B[0]-A[0])
      Cy = A[1]+i*(B[1]-A[1])
      Px=A[0]+i*(B[0]-A[0])+n[0]*taille
      Py=A[1]+i*(B[1]-A[1])+n[1]*taille
      if (Vec3(Px, Py, 0.0)-prev).length()>3*rayon+dec:
        dec = random.random()*rayon*30
        noeudColl = self.collisionBatimentBatiment((Px, Py, 0.0), taille)
        if not noeudColl:
          if not self.collisionBatimentLigne((Px, Py, 0.0), taille):
            if random.random()>0.3:
              cpt+=1
              prev=Vec3(Px, Py, 0.0)
              top = NodePath("")
              mdl = loader.loadModel("box.egg")
              top.setPos(Px, Py, 0.0)
              mdl.setPos(-0.5,-0.5,0.0)
              mdl.reparentTo(top)
              #mdl.setColor(random.random()/2, random.random()/2, random.random()/2)
              mdl.setColor(0.5, 0.5, 0.5)
              self.batiments.append(((Px,Py,0.0), taille, mdl))
              mdl.setScale(taille*(random.random()/2+0.5), taille*(random.random()/2+0.5), 1.0)
              sol = loader.loadModel("box.egg")
              sol.setScale(taille, taille*1.5, 0.001)
              sol.setColor(30.0/255, 159.0/255, 02.0/255)
              sol.setPos(-0.5,-0.5,0.0)
              sol.reparentTo(top)
              top.lookAt(Cx, Cy, 0.0)
              top.reparentTo(render)
        else:
          sc = noeudColl.getScale()
          noeudColl.setScale(sc[0], sc[1], sc[2]*1.05)
    return cpt

  def continueRoute(self, route, versFin):
    route = route[0]
    vecteurRoute = Vec3(*route[1])-Vec3(*route[0])
    origine = route[1]
    if not versFin:
      vecteurRoute = -vecteurRoute
      origine = route[0]
    vecteurRoute[0] = vecteurRoute[0]+(random.random()-0.5)/2
    vecteurRoute[1] = vecteurRoute[1]+(random.random()-0.5)/2
    cible = self.pointAlea(Vec3(*origine)+vecteurRoute)
    self.ajouteRoute(origine, cible)
    
  def ajouteRoute(self, depart, arrivee, couleur=(0.1, 0.1, 0.1), force=False, estAvenue=False, cptBatiments=True, testeDistance=True):
    coll = self.intersectionne(depart, arrivee, force=force)
    if coll:
      arrivee = coll

    if Vec3(*depart).length()>self.rayon:
      return
    if Vec3(*arrivee).length()>self.rayon:
      return
      
    if testeDistance and not force:
      d1, pt1 = self.pointPlusProche(depart)
      d2, pt2 = self.pointPlusProche(arrivee)
      if d1<self.longueurSegment:
        print depart,"=>",pt1
        depart=pt1
      if d2<self.longueurSegment:
        print arrivee,"=>",pt2
        arrivee=pt2
      
    longueurMin = self.longueurSegment
    if (not force) and testeDistance and (Vec3(*arrivee)-Vec3(*depart)).length()<longueurMin:
      return
      
    if not force:
      for lpos, mdl, estAvenue in self.lignes:
        if (depart,arrivee)==lpos or (arrivee,depart)==lpos:
          return
      
    if self.collisionLigneBatiment(depart, arrivee, force=force):
      return    
      
    position = depart
    racine = NodePath("00")
    points = []
    lignes = []
    cptBat = 0
    while (Vec3(*position)-Vec3(*arrivee)).length()>0:
      direction = (Vec3(*arrivee)-Vec3(*position))
      if direction.length()<self.longueurSegment:
        plus=arrivee
      else:
        direction.normalize()*self.longueurSegment
        plus=Vec3(*position)+direction
      cptBat += self.ajouteBatiments(position, plus, 1) + self.ajouteBatiments(position, plus, -1)

      points.append(position)
      ligne = LineSegs()
      ligne.setColor(*couleur)
      ligne.moveTo(*position)
      ligne.drawTo(*plus)
      rt = racine.attachNewNode(ligne.create())
      lignes.append([(position,plus), rt, estAvenue])
      position = plus
      
    if (not force) and cptBatiments and cptBat==0:
      racine.detachNode()
      racine.removeNode()
    else:
      racine.reparentTo(render)
      self.points+=points
      self.lignes+=lignes
    self.points.append(arrivee)
    return racine
    
  heurePing = None
  def ajouteRouteAlea(self):
    routeOrigine = random.choice(self.lignes)
    choix = random.random()
    self.continueRoute(routeOrigine, choix>=0.5)
    if self.heurePing == None or time.time()-self.heurePing>5:
      if self.heurePing!=None:
        print time.time()-self.heurePing, "Go !"
      self.heurePing = time.time()
      self.ajouteAvenue()
      print "moukiz"
      #self.connecterLesBouts()
      self.heurePing = time.time() + (time.time()-self.heurePing)
    print "Batiments : %i\r" %len(self.batiments),
      
  def pointPlusProche(self, pt, egalOK=True):
    d=800000.0
    ptProche=None
    for point in self.points:
      if egalOK or (point!=pt):
        dist = (Vec3(*point)-Vec3(*pt)).lengthSquared()
        if dist < d:
          ptProche = point
          d = dist
    return ptProche, math.sqrt(d)
    
  def pointsProcheLigne(self, A, B, seuil):
    points = []
    for point in self.points:
      if self.distPointLigne(point, A, B)[0] <= seuil:
        points.append(point)
    return points
    
  def connecterLesBouts(self):
    distanceConnecte = self.longueurSegment*0.9
    for route1 in self.lignes:
      print "Attachage des routes %i/%i \r" %(self.lignes.index(route1), len(self.lignes)),
      A, B = route1[0]
      AestBout = True
      BestBout = True
      for route2 in self.lignes:
        if route1 != route2:
          if A in route2[0]:
            AestBout = False
          if B in route2[0]:
            BestBout = False
      if AestBout:
        pt, dist = self.pointPlusProche(A, egalOK=False)
        cont = True
        for route in self.lignes:
          if route[0] in [(A, pt),(pt,A)]:
            cont = False
        if cont:
          if dist<distanceConnecte and dist>0:
            self.ajouteRoute(A, pt, cptBatiments=False, testeDistance=False)
      if BestBout:
        pt, dist = self.pointPlusProche(B, egalOK=False)
        cont = True
        for route in self.lignes:
          if route[0] in [(A, pt),(pt,A)]:
            cont = False
        if cont:
          if dist<distanceConnecte and dist>0:
            self.ajouteRoute(B, pt, cptBatiments=False, testeDistance=False)
    print
    print "moukiz"
    
  def ajouteAvenue(self):
    seuilProche = self.longueurSegment*0.5
    seuilAvenue = 125
    
    routesATester = []
    for route in self.lignes:
      if not route[2]:
        if random.random()>0.2:
          routesATester.append(route)
    
    for route in routesATester:
      if routesATester.index(route)%20==0:
        print "Test : %i/%i\r" %(routesATester.index(route)+1, len(routesATester)),
      if not route[2]:
        pts = self.pointsProcheLigne(route[0][0], route[0][1], seuilProche)
        segments = []
        umin, umax = 0.0,1.0
        pmin, pmax = route[0][0], route[0][1]
        if len(pts)>=seuilAvenue:
          for pt in pts:
            dst, u = self.distPointLigne(pt, route[0][0], route[0][1])
            if u < umin:
              umin=u
              pmin=pt
            if u > umax:
              umax=u
              pmax=pt

          for routeTest in self.lignes:
            if routeTest[0][0] in pts or reversed(routeTest[0][0]) in pts:
              if routeTest[0][1] in pts or reversed(routeTest[0][1]) in pts:
                segments.append(routeTest)
                
        if len(segments)>=seuilAvenue:
          print "Creation d'une avenue", (Vec3(*pmax)-Vec3(*pmin)).length()/self.longueurSegment, float(len(segments))*0.8
          
          for routeTest in segments:
            self.supprimeRoute(routeTest)
              
          orphelins = self.pointsProcheLigne(route[0][0], route[0][1], seuilProche)
                
          rd=self.ajouteRoute(pmin, pmax, couleur=(1.0,1.0,1.0), force=True, estAvenue=True)
          if rd!=None:
            rd.setLightOff()
            
          #orphelins = self.chercheOrphelins()
          for orphelin in orphelins:
            print "Gestion de l'orphelin %i/%i\r" %(orphelins.index(orphelin)+1, len(orphelins)),
            pt, dist = self.pointPlusProche(orphelin, egalOK=False)
            self.ajouteRoute(orphelin, pt, cptBatiments=False, testeDistance=False)
          print

  def chercheOrphelins(self):
    orphelins = []
    for point in self.points:
      orph = True
      for route in self.lignes:
        if point in route[0]:
          orph = False
      if orph:
        self.points.remove(point)
    return []

          
  def supprimeRoute(self, route):
    if route[1]!=None:
      route[1].detachNode()
      route[1].removeNode()
      route[1]=None
      route[2]=True
    while route in self.lignes:
      self.lignes.remove(route)
    ptABout = True
    ptBBout = True
    for rt in self.lignes:
      if route[0][0] in rt[0]:
        ptABout=False
      if route[0][1] in rt[0]:
        ptBBout=False
    if ptABout:
      self.points.remove(route[0][0])
    if ptBBout:
      self.points.remove(route[0][1])
        
        
    
  def distPointLigne(self, point, A, B):
    x1, y1, z1= A
    x2, y2, z2 = B
    x3, y3, z3 = point
    lAB = (Vec3(*B)-Vec3(*A)).length()
    u = ((x3-x1)*(x2-x1)+(y3-y1)*(y2-y1))/(lAB*lAB)
    x = x1 + u*(x2-x1)
    y = y1 + u*(y2-y1)
    return (Vec3(x, y, 0.0)-Vec3(*point)).length(), u
      
  def ping(self, task):
    self.ajouteRouteAlea()
    return task.cont      

base.setBackgroundColor(40.0/255, 169.0/255, 12.0/255)

dlight = PointLight('my dlight')
dlnp = render.attachNewNode(dlight)
dlnp.setPos(-75, -30, 20)
render.setLight(dlnp)

ville=Ville(75)
taskMgr.add(ville.ping, 'PingVille')
run()
