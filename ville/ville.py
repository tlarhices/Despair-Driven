#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *
#On coupe l'audio pour le moment
loadPrcFileData("",u"audio-library-name null")
import direct.directbase.DirectStart

from weakref import proxy

import random
import math
import time
import sys

class Route:
  pointA = None
  pointB = None
  taille = None
  racine = None
  
  def __init__(self, pointA, pointB, taille):
    self.pointA = pointA
    self.pointB = pointB
    self.taille = taille
    self.racine = None
    self.fabrique()
    
  def fabrique(self):
    if self.racine!=None:
      self.supprime()
    
    couleur = (0.1,0.1,0.1)
    if self.taille>=3:
      couleur = (1.0,0.0,0.0)
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
    
  def supprime(self):
    if self.racine!=None:
      self.racine.detachNode()
      self.racine.removeNode()
      self.racine = None
    
  def estAvenue(self):
    return self.taille >= 3.0
  def getCoord(self):
    return self.pointA, self.pointB
    
  def sauvegarde(self):
    out = "R||%s||%s||%f>" %(str(list(self.pointA)), str(list(self.pointB)), self.taille)
    return out
    
class Batiment:
  position = None
  orientation = None
  taille = None
  importance = None
  jardin = None
  batiment = None
  racine = None
  
  def __init__(self, position, orientation, taille, importance):
    self.position = position
    self.orientation = orientation
    self.taille = taille
    self.importance = importance
    self.jardin = None
    self.batiment = None
    self.racine = None
    self.fabrique()
    
  def fabrique(self):
    if self.racine!=None:
      self.supprime()
    self.racine = NodePath("")
    self.batiment = loader.loadModel("box.egg")
    Px, Py, Pz = self.position
    self.racine.setPos(Px, Py, Pz)
    self.batiment.setPos(-0.5,-0.5,-0.5)
    self.batiment.reparentTo(self.racine)
    #mdl.setColor(random.random()/2, random.random()/2, random.random()/2)
    self.batiment.setColor(0.5, 0.5, 0.5)
    self.batiment.setScale(self.taille*(random.random()/2+0.5), self.taille*(random.random()/2+0.5), self.importance)
    self.sol = loader.loadModel("box.egg")
    self.sol.setScale(self.taille, self.taille*1.5, 0.001)
    self.sol.setColor(30.0/255, 159.0/255, 02.0/255)
    self.sol.setPos(-0.5,-0.5,0.0)
    self.sol.reparentTo(self.racine)
    Cx, Cy, Cz = self.orientation
    self.racine.lookAt(Cx, Cy, Pz)
    self.racine.reparentTo(render)
    
  def sauvegarde(self):
    out = "B||%s||%s||%f||%f>" %(str(list(self.position)), str(list(self.orientation)), self.taille, self.importance)
    return out

  def supprime(self):
    self.racine.detachNode()
    self.racine.removeNode()
    self.racine = None
    self.batiment = None
    self.sol = None
    
  def getImportance(self):
    return self.importance
    
  def setImportance(self, importance):
    #print
    self.importance = importance
    self.fabrique()

class Ville:
  points = None
  rayon = None
  routes = None
  batiments = None
  longueurSegment = 4.0
  sol = None
  minAlt = None
  maxAlt = None
  afficheModele = True
  
  def __init__(self, rayon=None, fichier=None):
    if not rayon and not fichier:
      print "besoin de taille ou fichier"
      return
    if rayon!=None:
      self.rayon = int(rayon)
      self.fabriqueSol()
      self.ping = self.pingCreation
    self.routes=[]
    self.batiments = []
    self.points=[]
    
    if rayon!=None:
      while len(self.routes)==0:
        p1 = self.pointAlea((0.0,0.0,0.0))
        p2 = self.pointAlea((0.0,0.0,0.0))
        v=Vec3(*p2)-Vec3(*p1)
        v.normalize()
        v=v*self.longueurSegment*2
        p2=list(Vec3(*p1)+v)
        self.points = []
        self.ajouteRoute(p1, p2)
    else:
      self.charge(fichier)
      self.ping = self.pingCreation#pingChargement
      
      
  def fabriqueSol(self):
    
    print "Creation du sol..."
    self.sol = []
    for i in range(-self.rayon, self.rayon):
      self.sol.append([])
      for j in range(-self.rayon, self.rayon):
        self.sol[i+self.rayon].append(random.random()*40-20.0)
        
    print "Flou du sol..."
    for a in range(0,25):
      for i in range(0, self.rayon*2):
        for j in range(0, self.rayon*2):
          somme = 0.0
          cpt=0
          for k in [-1, 0, 1]:
            for l in [-1, 0, 1]:
              if i+k>=0 and i+k<self.rayon*2 and j+l>=0 and j+l<self.rayon*2:
                somme+=self.sol[i+k][j+l]
                cpt+=1
          self.sol[i][j] = somme / cpt

    print "Cherche Min/max..."
    self.minAlt = self.sol[0][0]
    self.maxAlt = self.sol[0][0]
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*2):
        self.minAlt = min(self.minAlt, self.sol[i][j])
        self.maxAlt = max(self.maxAlt, self.sol[i][j])
    print "Etendue des altitudes : ", self.minAlt, self.maxAlt

    haut = 10
    bas = -7
    print "Ramenage au bon ratio..."
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*2):
        self.sol[i][j] = (self.sol[i][j]-self.minAlt)/(self.maxAlt-self.minAlt)*(haut-bas)+bas
    self.minAlt = self.sol[0][0]
    self.maxAlt = self.sol[0][0]
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*2):
        self.minAlt = min(self.minAlt, self.sol[i][j])
        self.maxAlt = max(self.maxAlt, self.sol[i][j])
    print "Etendue des altitudes : ", self.minAlt, self.maxAlt
        
    print "Aplanissage de l'eau..."
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*2):
        if self.sol[i][j]<=0:
          self.sol[i][j]=-1
        self.minAlt = min(self.minAlt, self.sol[i][j])
        self.maxAlt = max(self.maxAlt, self.sol[i][j])
        
    print "Creation des vectrices..."
    self.format = GeomVertexFormat.getV3c4()
    self.vdata = GeomVertexData('TriangleVertices',self.format,Geom.UHStatic)
    self.vWriter = GeomVertexWriter(self.vdata, 'vertex')
    self.cWriter = GeomVertexWriter(self.vdata, 'color')
            
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*2):
        self.vWriter.addData3f(i-self.rayon, j-self.rayon, self.sol[i][j])
        c1 = (0.0,0.5,0.0,1.0)
        if self.sol[i][j]<=0:
          c1 = (0.0,0.1,0.5,1.0)
        self.cWriter.addData4f(*c1)
    
  affichei=0
  affichej=0
  racineSol = None
  def affiche(self):
    if self.racineSol == None:
      self.racineSol = NodePath("sol")
      self.racineSol.reparentTo(render)
    for i in range(0,self.rayon/2):
      #print "Construction du modele... %i/%i\r" %(i+1, self.rayon*2),
      #sys.stdout.flush()
      geom = Geom(self.vdata)
      if self.affichej>=self.rayon*2:
        self.affichej=0
        self.affichei+=1
      if self.affichei>=self.rayon*2:
        #print
        #print "Compactage du modele"
        #self.racineSol.flattenStrong()
        self.affiche=self.finAffiche
        return
      prim = GeomTriangles(Geom.UHStatic)
      if self.affichej<self.rayon*2-1 and self.affichei<self.rayon*2-1:
        prim.addVertex(self.affichej+self.affichei*(self.rayon*2))
        prim.addVertex(self.affichej+(self.affichei+1)*(self.rayon*2))
        prim.addVertex(self.affichej+self.affichei*(self.rayon*2)+1)
      prim.closePrimitive()
      geom.addPrimitive(prim)
      prim = GeomTriangles(Geom.UHStatic)
      if self.affichej<self.rayon*2-1 and self.affichei<self.rayon*2-1:
        prim.addVertex(self.affichej+(self.affichei+1)*(self.rayon*2))
        prim.addVertex(self.affichej+(self.affichei+1)*(self.rayon*2)+1)
        prim.addVertex(self.affichej+self.affichei*(self.rayon*2)+1)
      prim.closePrimitive()
      geom.addPrimitive(prim)
      node = GeomNode('gnode')
      node.addGeom(geom)
      mdl = NodePath(node)
      mdl.reparentTo(self.racineSol)
      self.affichej+=1
      
  def finAffiche(self):
    pass
    
  def charge(self, fichier):
    
    def getCoord(point):
      point = point.replace("[","(")
      point = point.replace("]",")")
      pts = point.split("(")[1].split(")")[0].split(",")
      objs = []
      for pt in pts:
        objs.append(float(pt))
      return objs
    i=0
    j=0
    self.sol=[]
    fichier = open(fichier)
    for ligne in fichier:
      elements = ligne.strip().split(">")
      for element in elements:
        type = element.split("||")[0]
        parametres = element.split("||")[1:]
        if type.lower()=="s":
          self.rayon = int(parametres[0])
        elif type.lower()=="t":
          if j==0:
            self.sol.append([])
          self.sol[-1].append(float(parametres[0]))
          
          j+=1
          if j>=self.rayon*2:
            j=0
            i+=1
        elif type.lower()=="r":
          pointA, pointB, taille = parametres
          pointA=getCoord(pointA)
          pointB=getCoord(pointB)
          taille=float(taille)
          if pointA not in self.points:
            self.points.append(pointA)
          if pointB not in self.points:
            self.points.append(pointB)
          pointA[2]=self.getAltitude(*pointA[0:2])
          pointB[2]=self.getAltitude(*pointB[0:2])
          self.routes.append(Route(pointA, pointB, taille))
        elif type.lower()=="b":
          position, orientation, taille, importance = parametres
          position = getCoord(position)
          orientation = getCoord(orientation)
          taille = float(taille)
          importance = float(importance)
          self.batiments.append(Batiment(position, orientation, taille, importance))
        elif type.lower()=="":
          pass
        else:
          print "inconnu", type, parametres
          raw_input()
          
          
    self.minAlt = self.sol[0][0]
    self.maxAlt = self.sol[0][0]
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*2):
        self.minAlt = min(self.minAlt, self.sol[i][j])
        self.maxAlt = max(self.maxAlt, self.sol[i][j])
        
    print "Creation des vectrices..."
    self.format = GeomVertexFormat.getV3c4()
    self.vdata = GeomVertexData('TriangleVertices',self.format,Geom.UHStatic)
    self.vWriter = GeomVertexWriter(self.vdata, 'vertex')
    self.cWriter = GeomVertexWriter(self.vdata, 'color')
            
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*2):
        self.vWriter.addData3f(i-self.rayon, j-self.rayon, self.sol[i][j])
        c1 = (0.0,0.5,0.0,1.0)
        if self.sol[i][j]<=0:
          c1 = (0.0,0.1,0.5,1.0)
        self.cWriter.addData4f(*c1)

          
      
  def sauvegarde(self, fichier):
    fichier = open(fichier, "w")
    fichier.write("S||%i>" %self.rayon)
    for i in range(0, self.rayon*2):
      for j in range(0, self.rayon*2):
        fichier.write("T||%f>" %self.sol[i][j])

    for route in self.routes:
      fichier.write(route.sauvegarde())
    for batiment in self.batiments:
      fichier.write(batiment.sauvegarde())
    fichier.close()
      
  def pointAlea(self, pt, delta=None):
    if delta==None:
      delta = self.rayon
    out = None
    x,y,z = pt
    autorise = min(random.random(), 0.9)*self.maxAlt

    while out==None:
     test = [(random.random()*2-1)*delta+x, (random.random()*2-1)*delta+y, 0.0+z]
     alt = self.getAltitude(test[0], test[1])
     if alt>0.0:
       if alt<=autorise:
         test[2]=alt
         out = test
    return out
    
  def getAltitude(self, x, y):
    if x+self.rayon<0 or x+self.rayon>=self.rayon*2:
      return -1000
    if y+self.rayon<0 or y+self.rayon>=self.rayon*2:
      return -1000
    return self.sol[int(x)+self.rayon][int(y)+self.rayon]
      
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
    for obj in self.routes:
      C = obj.pointA
      D = obj.pointB
      #((C,D), mdl, estAvenue) = obj
      r = self.intersection(A, B, C, D)
      if r!=None:
          
        Px=A[0]+r*(B[0]-A[0])
        Py=A[1]+r*(B[1]-A[1])
        Pz=self.getAltitude(Px,Py)
        P = Px, Py, Pz
        if force:
          self.routes.remove(obj)
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
    for batiment in self.batiments:
      pos = batiment.position[0], batiment.position[1], batiment.position[2]
      taille = batiment.taille
      if (rayon+taille)*(rayon+taille)>(position-Vec3(*pos)).lengthSquared():
        return batiment
    return False
    
  def collisionLigneBatiment(self, pointA, pointB, force=False):
    for batiment in self.batiments:
      centre = batiment.position[0], batiment.position[1], batiment.position[2]
      rayon = batiment.taille
      if self.collisionLigneCercle(pointA, pointB, centre, rayon):
        if not force:
          return True
        else:
          self.batiments.remove(batiment)
          batiment.supprime()
    return False
    
  def collisionBatimentLigne(self, position, rayon):
    for route in self.routes:
      pointA, pointB = route.getCoord()
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
    Pz=Pz=self.getAltitude(Px,Py)
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
      Pz=self.getAltitude(Px,Py)
      if (Vec3(Px, Py, Pz)-prev).length()>3*rayon+dec:
        if Pz>0:#dec = random.random()*rayon*30
          noeudColl = self.collisionBatimentBatiment((Px, Py, Pz), taille)
          if not noeudColl:
            if not self.collisionBatimentLigne((Px, Py, Pz), taille):
              if random.random()>0.4:
                cpt+=1
                batiment = Batiment((Px,Py,Pz), (Cx,Cy,Cz), taille, 1.0)
                batiments.append(batiment)
                self.batiments.append(batiment)
          else:
            facteur = min(0.2 * 600.0 / float(len(self.batiments)), 0.8)
            facteur = max(0.1, facteur)
            importance = noeudColl.getImportance()
            importance = importance + facteur
            noeudColl.setImportance(importance)
        prev=Vec3(Px, Py, Pz)
    return batiments

  def continueRoute(self, route, versFin):
    route = route.pointA, route.pointB
    vecteurRoute = Vec3(*route[1])-Vec3(*route[0])
    origine = route[1]
    if not versFin:
      vecteurRoute = -vecteurRoute
      origine = route[0]
    vecteurRoute[0] = vecteurRoute[0]+(random.random()-0.5)/2
    vecteurRoute[1] = vecteurRoute[1]+(random.random()-0.5)/2
    cible = self.pointAlea(Vec3(*origine)+vecteurRoute)
    return self.ajouteRoute(origine, cible)
    
  def intersectionEau(self, A, B, force=False):
    l=(Vec3(*B)-Vec3(*A)).length()
    if l>0:
      pas = 0.33/l
      r=0
      prevR=0
      while r<1.0:
        Px=A[0]+r*(B[0]-A[0])
        Py=A[1]+r*(B[1]-A[1])
        if self.getAltitude(Px,Py)<=0:
          Px=A[0]+prevR*(B[0]-A[0])
          Py=A[1]+prevR*(B[1]-A[1])
          return Px, Py, self.getAltitude(Px,Py)
        prevR=r
        r+=pas
    return None
    
  def ajouteRoute(self, depart, arrivee, couleur=(0.1, 0.1, 0.1), force=False, estAvenue=False, cptBatiments=True, testeDistance=True):
    depart = list(depart)
    depart[2]=0.0
    arrivee = list(arrivee)
    arrivee[2]=0.0
    coll = self.intersectionne(depart, arrivee, force=force)
    if coll:
      coll = list(coll)
      coll[2]=0.0
    if coll and depart!=coll:
      arrivee = coll
      
    coll = self.intersectionEau(depart, arrivee, force=force)
    if coll:
      coll = list(coll)
      coll[2]=0.0
      if (Vec3(*arrivee)-Vec3(*depart)).length() < self.longueurSegment*math.sqrt(len(self.batiments)):
        return False
      #else:
      #  print "trav"
        
    if self.getAltitude(*depart[:-1])<=0:
      return False
    if self.getAltitude(*arrivee[:-1])<=0:
      return False

    if abs(depart[0])>self.rayon:
      return False
    if abs(depart[1])>self.rayon:
      return False
    if abs(arrivee[0])>self.rayon:
      return False
    if abs(arrivee[1])>self.rayon:
      return False
      
    if (Vec3(*arrivee)-Vec3(*depart)).length()==0:
      return False
      
    if testeDistance and not force:
      pt1, d1 = self.pointPlusProche(depart)
      pt2, d2 = self.pointPlusProche(arrivee)
      if d1<self.longueurSegment:
        depart=pt1
      if d2<self.longueurSegment:
        arrivee=pt2
      
    longueurMin = self.longueurSegment
    if (not force) and testeDistance and (Vec3(*arrivee)-Vec3(*depart)).length()<longueurMin:
      return False
      
    if not force:
      for route in self.routes:
        lpos = route.pointA, route.pointB
        if (depart,arrivee)==lpos or (arrivee,depart)==lpos:
          return False
      
    if self.collisionLigneBatiment(depart, arrivee, force=force):
      return False
      
    position = list(depart)
    points = []
    routes = []
    batiments = []
    cptBat = 0
    position[2]=0.0
    arrivee = list(arrivee)
    arrivee[2]=0.0
    longueurMarine = 0
    postMarine=False
    drop=False
    longueurMarineMin = 20
    longueurMarineMax = 30
    
    while (Vec3(*position)-Vec3(*arrivee)).length()>0:
      direction = (Vec3(*arrivee)-Vec3(*position))
      if direction.length()<self.longueurSegment:
        plus=arrivee
      else:
        direction.normalize()*self.longueurSegment
        plus=Vec3(*position)+direction
      position[2]=self.getAltitude(position[0],position[1])
      plus[2]=self.getAltitude(plus[0],plus[1])

      if position[2]<=0:
        if postMarine:
          if longueurMarine<longueurMarineMin:
            drop = True
          if longueurMarine>longueurMarineMax:
            drop = True
          longueurMarine = 0
          postMarine=False
        estAvenue = True
        position[2]=points[-1][2]
        plus[2]=points[-1][2]
        longueurMarine+=1
      else:
        batiments += self.ajouteBatiments(position, plus, 1) + self.ajouteBatiments(position, plus, -1)
        cptBat += len(batiments)
        if longueurMarine>0:
          postMarine=True
        
      points.append(position)
      taille = 1.0
      if estAvenue:
        taille = 3.0
      estAvenue = False
      routes.append(Route(position, plus, taille))
      position[2]=0.0
      plus[2]=0.0
      position = plus
      
    points.append(arrivee)
    if (not force) and ((cptBatiments and cptBat<=0) or drop or (longueurMarine!=0 and (longueurMarine<longueurMarineMin or longueurMarine>longueurMarineMax))):
      for route in routes:
        route.supprime()
      for batiment in batiments:
        batiment.supprime()
        self.batiments.remove(batiment)
      return False
    else:
      self.points+=points
      self.routes+=routes
    return True
    
  heurePing = None
  def ajouteRouteAlea(self):
    routeOrigine = random.choice(self.routes)
    choix = random.random()
    if self.continueRoute(routeOrigine, choix>=0.5):
      for i in range(0, max(10, len(self.routes)/50)):
        route = random.choice(self.routes)
        direction = 1
        if random.random()>=0.5:
          direction=-1
        self.ajouteBatiments(route.pointA, route.pointB, direction)
    
    
    if self.heurePing == None or time.time()-self.heurePing>5:
      self.heurePing = time.time()
      self.ajouteAvenue()
      #self.connecterLesBouts()
      self.heurePing = time.time() + (time.time()-self.heurePing)
    print "Batiments : %i Routes : %i\r" %(len(self.batiments), len(self.routes)),
    sys.stdout.flush()
      
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
    return
    seuilProche = self.longueurSegment*0.5
    seuilAvenue = 125
    
    routesATester = []
    for route in self.routes:
      if not route.estAvenue():
        if random.random()>0.2:
          routesATester.append(route)
    
    for route in routesATester:
      if routesATester.index(route)%20==0:
        print "Test : %i/%i\r" %(routesATester.index(route)+1, len(routesATester)),
      if not route.estAvenue():
        pts = self.pointsProcheLigne(route.pointA, route.pointB, seuilProche)
        segments = []
        umin, umax = 0.0,1.0
        pmin, pmax = route.pointA, route.pointB
        if len(pts)>=seuilAvenue:
          for pt in pts:
            dst, u = self.distPointLigne(pt, route.pointA, route.pointB)
            if u < umin:
              umin=u
              pmin=pt
            if u > umax:
              umax=u
              pmax=pt

          for routeTest in self.routes:
            if routeTest.pointA in pts or reversed(routeTest.pointA) in pts:
              if routeTest.pointB in pts or reversed(routeTest.pointB) in pts:
                segments.append(routeTest)
                
        if len(segments)>=seuilAvenue:
          print "Creation d'une avenue", (Vec3(*pmax)-Vec3(*pmin)).length()/self.longueurSegment, float(len(segments))*0.8
          
          for elem in segments:
            while routesATester.count(elem)>0:
              routesATester.remove(elem)
          for routeTest in segments:
            self.supprimeRoute(routeTest)
              
          orphelins = self.pointsProcheLigne(route.pointA, route.pointB, seuilProche)
          set = {} 
          map(set.__setitem__, orphelins, [])
          orphelins = set.keys()
                
          self.ajouteRoute(pmin, pmax, couleur=(1.0,1.0,1.0), force=True, estAvenue=True)
            
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
    return
    route.supprime()

    while route in self.routes:
      self.routes.remove(route)
    ptABout = True
    ptBBout = True
    for rt in self.routes:
      if route.pointA in rt.getCoord():
        ptABout=False
      if route.pointB in rt.getCoord():
        ptBBout=False
    if ptABout:
      self.points.remove(route.pointA)
    if ptBBout:
      self.points.remove(route.pointB)
        
        
    
  def distPointLigne(self, point, A, B):
    x1, y1, z1= A
    x2, y2, z2 = B
    x3, y3, z3 = point
    lAB = (Vec3(*B)-Vec3(*A)).length()
    u = ((x3-x1)*(x2-x1)+(y3-y1)*(y2-y1))/(lAB*lAB)
    x = x1 + u*(x2-x1)
    y = y1 + u*(y2-y1)
    return (Vec3(x, y, z3)-Vec3(*point)).length(), u
      
  def ping(self, task):
    return task.done
      
  def pingCreation(self, task):
    self.affiche()
    self.ajouteRouteAlea()
    if len(self.batiments)>500:
      self.sauvegarde("ville.out")
    return task.cont      

  def pingChargement(self, task):
    self.affiche()
    return task.cont      

#base.setBackgroundColor(40.0/255, 169.0/255, 12.0/255)

dlight = PointLight('my dlight')
dlnp = render.attachNewNode(dlight)
dlnp.setPos(0, 0, 30)
render.setLight(dlnp)

ville=Ville(rayon=None, fichier="ville.out")
taskMgr.add(ville.ping, 'PingVille')
run()
