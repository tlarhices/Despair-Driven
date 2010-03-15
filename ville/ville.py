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

sys.path.append(os.path.join(".","librairies"))

from batiment import Batiment
from route import Route
from quartier import Quartier
from sol import Sol

class Ville:
  points = None
  rayon = None
  routes = None
  batiments = None
  longueurSegment = 4.0
  afficheModele = True
  fichierIn = None
  fichierOut = None
  
  def __init__(self, rayon=None, fichierIn=None, fichierOut=None, etape=0):
    if not rayon and not fichierIn:
      print "besoin de taille ou fichier"
      return
      
    self.fichierIn=fichierIn
    self.fichierOut=fichierOut
      
    self.routes=[]
    self.batiments = []
    self.points=[]
    
    self.sol=Sol()
    if fichierIn==None:
      self.sol.genereSol(rayon)
      while len(self.routes)==0:
        p1 = self.pointAlea(Vec3(0.0,25.0,0.0))
        p2 = self.pointAlea(Vec3(0.0,25.0,0.0))
        v=p2-p1
        v.normalize()
        v=v*self.longueurSegment*2
        p2=p1+v
        self.points = []
        self.ajouteRoute(p1, p2)
    else:
      self.charge(fichierIn)

    if etape==0 or etape==1:
      self.ping = self.pingCreation
    elif etape==2:
      self.ping = self.pingChargement
    elif etape==3:
      self.ping = self.pingModeleRoutes
    elif etape==4:
      self.ping = self.pingModeleBatiments
    elif etape==5:
      self.ping = self.pingModeleSol
    else:
      print "etape inconue", etape
      
      
  idAfficheRoute = 0
  def afficheRoutes(self):
    if self.idAfficheRoute >= len(self.routes):
      return
    route = self.routes[self.idAfficheRoute]
    print "Creation de la route %i/%i\r" %(self.idAfficheRoute,len(self.routes)),
    route.hauteQualite(self)
    self.idAfficheRoute+=1

  def flatten(self):
    import time
    deb = time.time()
    gr = SceneGraphReducer() 
    print "Apply attribs"
    gr.applyAttribs(self.racineSol.node()) 
    print time.time()-deb
    deb = time.time()
    print "Combine Radius"
    #gr.setCombineRadius(10.0) 
    print time.time()-deb
    deb = time.time()
    print "Flatenning"
    gr.flatten(self.racineSol.node(), ~gr.CSOther) 
    print time.time()-deb
    deb = time.time()
    print "Make compatible"
    gr.makeCompatibleState(self.racineSol.node()) 
    print time.time()-deb
    deb = time.time()
    print "Collect"
    gr.collectVertexData(self.racineSol.node(), ~(gr.CVDFormat|gr.CVDName|gr.CVDAnimationType)) 
    print time.time()-deb
    deb = time.time()
    #print "Unify"
    #gr.unify(self.racineSol.node(), False)
    print time.time()-deb

  def chercheQuartiers(self, route=None):
    if route == None:
      route = random.choice(self.routes)
    A,B = route.getCoord()
    dx=B[0]-A[0]
    dy=B[1]-A[1]
    
    n=Vec3(dy, -dx, 0.0)
    n.normalize()
    p1=(A+B)/2+n
    p2=(A+B)/2-n

    d_1 = (p1-p2).lengthSquared()
    d_2 = (p1-p2).lengthSquared()
    deb = p1
    fin = p2

    coll1 = None
    coll2 = None
    for obj in self.routes:
      C = obj.pointA
      D = obj.pointB
      r = self.intersection(p1, p2, C, D)
      if r!=None and obj!=route:
        Px=p1[0]+r*(p2[0]-p1[0])
        Py=p1[1]+r*(p2[1]-p1[1])
        Pz=self.sol.getAltitude(Vec3(Px,Py,0.0))
        P = Px, Py, Pz
        d1 = (p1-P).lengthSquared()
        d2 = (p2-P).lengthSquared()
        if (coll1==None or d1<d_1) and d1<=d2:
          coll1=P
          d_1=d1
        if (coll2==None or d2<d_2) and d2<d1:
          coll2=P
          d_2=d2
          
    C=(A+B)/2
    if coll1!=None and coll2!=None and coll1!=p1 and coll1!=p2 and coll2!=p1 and coll2!=p2 and coll1!=coll2 and coll1!=C and coll2!=C:
      p1=(C+coll1)/2
      p2=(C+coll2)/2
      p1[2]=0.0
      p2[2]=0.0
      
      print "test"
      contours1 = []
      contours2 = []
      points = self.cherchePointAutour(p1, self.longueurSegment)+self.cherchePointAutour(p2, self.longueurSegment)
      for point in points:
        print "test %i/%i\r" %(points.index(point), len(points)),
        i1 = self.intersectionne(p1, point)
        i2 = self.intersectionne(p2, point)
        if i1==None:
          contours1.append(point)
        if i2==None:
          contours2.append(point)
          
      q1=[]
      q2=[]
      for route in self.routes:
        if (route.pointA in contours1 and route.pointB in contours1):
          q1.append(route)
        if (route.pointA in contours2 and route.pointB in contours2):
          q2.append(route)
          
      if len(q1)>2:
        q1=Quartier(q1, 1.0)
        q1.rendOK(self)
        q1.affiche()
      if len(q2)>2:
        q2=Quartier(q2, 1.0)
        q2.rendOK(self)
        q2.affiche()
        
  def cherchePointAutour(self, point, dist):
    print "creation de la liste"
    points = []
    dist=dist*dist
    for pt in self.points:
      if (pt-point).lengthSquared()<=dist:
        points.append(pt)
    print "fini"
    return points
    
  def charge(self, fichier):
    def getCoord(point):
      point = point.replace("[","(")
      point = point.replace("]",")")
      pts = point.split("(")[1].split(")")[0].split(",")
      objs = []
      for pt in pts:
        objs.append(float(pt))
      return Vec3(*objs)
      
    i=0
    j=0
    self.sol=Sol()
    fichier = open(fichier)
    for ligne in fichier:
      elements = ligne.strip().split(">")
      cptElements=0
      for element in elements:
        cptElements+=1
        if cptElements%100==0:
          print "Chargement %i/%i\r" %(cptElements, len(elements)),
        type = element.split("||")[0]
        parametres = element.split("||")[1:]
        if type.lower()=="s":
          self.sol.rayon = int(parametres[0])
        elif type.lower()=="t":
          if j==0:
            self.sol.sol.append([])
          self.sol.sol[-1].append(float(parametres[0]))
          
          j+=1
          if j>=self.sol.rayon*3:
            j=0
            i+=1
            print self.sol.sol[-1]
        elif type.lower()=="r":
          pointA, pointB, taille = parametres
          pointA=getCoord(pointA)
          pointB=getCoord(pointB)
          taille=float(taille)
          if taille==1:
            taille=2
          pointA[2]=self.sol.getAltitude(pointA)+1.1
          pointB[2]=self.sol.getAltitude(pointB)+1.1
          if pointA not in self.points:
            self.points.append(pointA)
          if pointB not in self.points:
            self.points.append(pointB)
          self.routes.append(Route(pointA, pointB, taille, self))
          self.routes[-1].fabrique()
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
    self.sol.fabriqueVectrices()
          
  def sauvegarde(self):
    fichier = open(self.fichierOut, "w")
    fichier.write("S||%i>" %self.sol.rayon)
    for i in range(0, self.sol.rayon*2):
      for j in range(0, self.sol.rayon*3):
        fichier.write("T||%f>" %self.sol.sol[i][j])

    for route in self.routes:
      fichier.write(route.sauvegarde())
    for batiment in self.batiments:
      fichier.write(batiment.sauvegarde())
    fichier.close()
      
  def pointAlea(self, pt, delta=None):
    if delta==None:
      delta = self.sol.rayon*2
    out = None
    x,y,z = pt
    autorise = self.sol.altitudeMax

    while out==None:
     test = Vec3((random.random()*2-1)*delta+x, (random.random()*2-1)*delta+y, 0.0+z)
     alt = self.sol.getAltitude(test)
     if alt>0.0:
       if alt<autorise:
         test[2]=alt
         out = test
    return out
    
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
    d = (A-B).lengthSquared()
    deb = A
    fin = B

    coll = None
    for obj in self.routes:
      C = obj.pointA
      D = obj.pointB
      r = self.intersection(A, B, C, D)
      if r!=None:
          
        Px=A[0]+r*(B[0]-A[0])
        Py=A[1]+r*(B[1]-A[1])
        Pz=self.sol.getAltitude(Vec3(Px, Py, 0.0))
        P = Vec3(Px, Py, Pz)
        d2 = (A-P).lengthSquared()
        if coll==None or d2<d:
          coll=P
          d=d2
    if coll==A:
      return None
    if coll==B:
      return None
    return coll
    
  def collisionBatimentBatiment(self, position, rayon):
    for batiment in self.batiments:
      pos = Vec3(batiment.position[0], batiment.position[1], batiment.position[2])
      taille = batiment.taille
      if (rayon+taille)*(rayon+taille)>(position-pos).lengthSquared():
        return batiment
    return False
    
  def collisionLigneBatiment(self, pointA, pointB):
    for batiment in self.batiments:
      centre = batiment.position[0], batiment.position[1], batiment.position[2]
      rayon = batiment.taille
      if self.collisionLigneCercle(pointA, pointB, centre, rayon):
        return True
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
    pas = 1.0/(B-A).length()*rayon
    Px=A[0]-5*(B[0]-A[0])
    Py=A[1]-5*(B[1]-A[1])
    Pz=self.sol.getAltitude(Vec3(Px,Py,0.0))
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
      Pz=self.sol.getAltitude(Vec3(Px,Py,0.0))
      if (Vec3(Px, Py, Pz)-prev).length()>3*rayon+dec:
        if Pz>0:#dec = random.random()*rayon*30
          if Pz<self.sol.altitudeMax:
            noeudColl = self.collisionBatimentBatiment(Vec3(Px, Py, Pz), taille)
            if not noeudColl:
              if not self.collisionBatimentLigne(Vec3(Px, Py, Pz), taille):
                if random.random()>0.4:
                  cpt+=1
                  batiment = Batiment(Vec3(Px,Py,Pz), Vec3(Cx,Cy,Cz), taille, 1.0)
                  batiments.append(batiment)
                  self.batiments.append(batiment)
            else:
              facteur = min(0.2 * 600.0 / float(len(self.batiments)), 0.8)
              facteur = max(0.1, facteur)
              importance = noeudColl.importance
              importance = importance + facteur
              noeudColl.setImportance(importance)
        prev=Vec3(Px, Py, Pz)
    return batiments

  def continueRoute(self, route, versFin):
    route = route.pointA, route.pointB
    vecteurRoute = route[1]-route[0]
    origine = route[1]
    if not versFin:
      vecteurRoute = -vecteurRoute
      origine = route[0]
    vecteurRoute[0] = vecteurRoute[0]+(random.random()-0.5)/2
    vecteurRoute[1] = vecteurRoute[1]+(random.random()-0.5)/2
    cible = self.pointAlea(origine+vecteurRoute)
    return self.ajouteRoute(origine, cible)
    
  def intersectionEau(self, A, B):
    l=(B-A).length()
    if l>0:
      pas = 0.33/l
      r=0
      prevR=0
      while r<1.0:
        Px=A[0]+r*(B[0]-A[0])
        Py=A[1]+r*(B[1]-A[1])
        if self.sol.getAltitude(Vec3(Px,Py,0.0))<=0:
          Px=A[0]+prevR*(B[0]-A[0])
          Py=A[1]+prevR*(B[1]-A[1])
          return Vec3(Px, Py, self.sol.getAltitude(Vec3(Px,Py,0.0)))
        prevR=r
        r+=pas
    return None
    
  def ajouteRoute(self, depart, arrivee, couleur=(0.1, 0.1, 0.1), cptBatiments=True):
    depart[2]=0.0
    arrivee[2]=0.0
    coll = self.intersectionne(depart, arrivee)
    if coll:
      coll[2]=0.0
    if coll and depart!=coll:
      arrivee = coll
      
    coll = self.intersectionEau(depart, arrivee)
    if coll:
      coll[2]=0.0
      if (arrivee-depart).length() < self.longueurSegment*math.sqrt(len(self.batiments)):
        return False
      #else:
      #  print "trav"
        
    if self.sol.getAltitude(depart)<=0:
      return False
    if self.sol.getAltitude(arrivee)<=0:
      return False

    if abs(depart[0])>self.sol.rayon:
      return False
    if depart[1]>self.sol.rayon*2 or depart[1]<-self.sol.rayon:
      return False
    if abs(arrivee[0])>self.sol.rayon:
      return False
    if arrivee[1]>self.sol.rayon*2 or arrivee[1]<-self.sol.rayon:
      return False
      
    if (arrivee-depart).length()==0:
      return False
      
    pt1, d1 = self.pointPlusProche(depart)
    pt2, d2 = self.pointPlusProche(arrivee)
    if d1<self.longueurSegment:
      depart=pt1
    if d2<self.longueurSegment:
      arrivee=pt2
      
    longueurMin = self.longueurSegment
    if (arrivee-depart).length()<longueurMin:
      return False
      
    for route in self.routes:
      lpos = route.pointA, route.pointB
      if (depart,arrivee)==lpos or (arrivee,depart)==lpos:
        return False
      
    if self.collisionLigneBatiment(depart, arrivee):
      return False
      
    position = depart
    points = []
    routes = []
    batiments = []
    cptBat = 0
    position[2]=0.0
    arrivee[2]=0.0
    longueurMarine = 0
    postMarine=False
    drop=False
    longueurMarineMin = 20
    longueurMarineMax = 30
    
    while (position-arrivee).length()>0:
      direction = (arrivee-position)
      if direction.length()<self.longueurSegment:
        plus=arrivee
      else:
        direction.normalize()*self.longueurSegment
        plus=position+direction
      position[2]=self.sol.getAltitude(position)
      plus[2]=self.sol.getAltitude(plus)

      if position[2]<self.sol.altitudeMax:
        if position[2]<=0:
          if postMarine:
            if longueurMarine<longueurMarineMin:
              drop = True
            if longueurMarine>longueurMarineMax:
              drop = True
            longueurMarine = 0
            postMarine=False
          position[2]=points[-1][2]
          plus[2]=points[-1][2]
          longueurMarine+=1
        else:
          batiments += self.ajouteBatiments(position, plus, 1) + self.ajouteBatiments(position, plus, -1)
          cptBat += len(batiments)
          if longueurMarine>0:
            postMarine=True
          
        points.append(Vec3(*position))
        taille = 2.0
        routes.append(Route(Vec3(*position), Vec3(*plus), taille))
      position[2]=0.0
      plus[2]=0.0
      position = plus
      
    points.append(arrivee)
    if ((cptBatiments and cptBat<=0) or drop or (longueurMarine!=0 and (longueurMarine<longueurMarineMin or longueurMarine>longueurMarineMax))):
      for route in routes:
        route.supprime()
      for batiment in batiments:
        batiment.supprime()
        self.batiments.remove(batiment)
      return False
    else:
      self.points+=points
      self.routes+=routes
      for route in routes:
        route.fabrique()
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
      self.heurePing = time.time() + (time.time()-self.heurePing)
    print "Batiments : %i Routes : %i\r" %(len(self.batiments), len(self.routes)),
    sys.stdout.flush()
      
  def pointPlusProche(self, pt, egalOK=True):
    d=800000.0
    ptProche=None
    for point in self.points:
      if egalOK or (point!=pt):
        dist = (point-pt).lengthSquared()
        if dist < d:
          ptProche = point
          d = dist
    return ptProche, math.sqrt(d)
    
  def distPointLigne(self, point, A, B):
    x1, y1, z1= A
    x2, y2, z2 = B
    x3, y3, z3 = point
    lAB = (B-A).length()
    u = ((x3-x1)*(x2-x1)+(y3-y1)*(y2-y1))/(lAB*lAB)
    x = x1 + u*(x2-x1)
    y = y1 + u*(y2-y1)
    return (Vec3(x, y, z3)-point).length(), u
      
  pings=0
      
  def ping(self, task):
    return task.done
      
  def pingCreation(self, task):
    self.pings+=1
    self.sol.affiche()
    self.ajouteRouteAlea()
    if len(self.batiments)>500:
      self.sauvegarde()
    return task.cont      

  lastPing = None
  def pingChargement(self, task):
    self.pings+=1
    self.affiche()
    if self.lastPing==None:
      self.lastPing=time.time()
    if time.time()>self.lastPing:
      deb=time.time()
      self.concentreBatiments()
      self.lastPing=time.time()+(time.time()-deb)
    if self.pings%60==0:
      self.sauvegarde()
    #self.chercheQuartiers(random.choice(self.routes))
    return task.cont      
    
  def pingModeleRoutes(self, task):
    self.pings+=1
    if self.pings==1:
      print "TODO : pingModeleRoutes"
    self.affiche()
    self.afficheRoutes()
    random.choice(self.routes).hauteQualite(self)
    if self.pings%60==0:
      self.sauvegarde()
    return task.cont
    
  def pingModeleBatiments(self, task):
    self.pings+=1
    if self.pings==1:
      print "TODO : pingModeleBatiments"
    self.affiche()
    if self.pings%60==0:
      self.sauvegarde()
    return task.cont
    
  def pingModeleSol(self, task):
    self.pings+=1
    if self.pings==1:
      print "TODO : pingModeleSol"
    self.affiche()
    if self.pings%60==0:
      self.sauvegarde()
    return task.cont

  posBat = 0
  passeBat = 0
  ajoutBatPasse = 0
  def concentreBatiments(self):
    if self.posBat>=len(self.batiments):
      self.posBat = 0
      self.passeBat += 1
      self.ajoutBatPasse = 0
    print "[%i-%i] Batiments, %i nouveaux batiments ajoutes pour un total de %i\r" %(self.passeBat, self.posBat+1, self.ajoutBatPasse, len(self.batiments)),
    batiment = self.batiments[self.posBat]
    position = batiment.position
    orientation = batiment.orientation
    importance = batiment.importance
    taille = batiment.taille
    tailleTeste = random.random()*1.0+0.5

    nouvImportance = importance*0.95
    if nouvImportance>=1.0:
      for angle in range(0,360):
        if random.random()>=0.33:
          tailleTeste = random.random()*1.0+0.5
        direction = 1.0
        if random.random()>=0.5:
          direction = -1.0
        direction = direction * Vec3((taille+tailleTeste+0.005)*math.cos(float(angle)/180*math.pi), (taille+tailleTeste+0.005)*math.sin(float(angle)/180*math.pi), 0.0)
        newPos = position + direction
        newPos[2]=self.sol.getAltitude(newPos)
        if newPos[2]>0:
          if random.random()>0.90:
            if not self.collisionBatimentBatiment(newPos, tailleTeste):
              if not self.collisionBatimentLigne(newPos, tailleTeste):
                if self.pointPlusProche(newPos)[1]<=self.longueurSegment:
                  batiment = Batiment(newPos, orientation, tailleTeste, nouvImportance)
                  self.batiments.append(batiment)
                  self.ajoutBatPasse +=1
    self.posBat+=1

#base.setBackgroundColor(40.0/255, 169.0/255, 12.0/255)

if len(sys.argv) != 4:
  print "Parametres invalides, essayez :"
  print "ville.py 0 rayon fichierOut"
  print "ou"
  print "ville.py num_etape fichierIn fichierOut"
  print "Etapes possibles :"
  print "0 - creation du sol (le second parametre represent le rayon de la ville)"
  print "1 - creation de la structure de la ville"
  print "2 - augmentation de la densite des batiments"
  print "3 - modelisation des routes"
  print "4 (todo) - modelisation des batiments"
  print "5 (todo) - modelisation du sol"
  sys.exit()
dlight = PointLight('my dlight')
dlnp = render.attachNewNode(dlight)
dlnp.setPos(0, 0, 30)
render.setLight(dlnp)
etape = int(sys.argv[1])
if etape==0:
  rayon=int(sys.argv[2])
  fichierIn=None
else:
  rayon=None
  fichierIn=sys.argv[2]

fichierOut=sys.argv[3]
  
ville=Ville(rayon=rayon, fichierIn=fichierIn, fichierOut=fichierOut, etape=etape)
taskMgr.add(ville.ping, 'PingVille')
base.accept('a-repeat', ville.chercheQuartiers)
run()
