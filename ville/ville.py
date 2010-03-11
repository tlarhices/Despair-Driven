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
  
  def __init__(self, pointA, pointB, taille, ville=None):
    self.pointA = pointA
    self.pointB = pointB
    self.taille = taille
    self.racine = None
    self.estUnPont=False
    if self.pointA[2]<=0.0:
      self.pointA[2]=1.0
      self.estUnPont=True
    if self.pointB[2]<=0.0:
      self.pointB[2]=1.0
      self.estUnPont=True
    #self.fabrique()
    
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
      
  largeurVoie=0.1
  largeurTrottoir=0.05
  hauteurTrottoire=0.01
  largeurCaniveau=0.025
  profondeurCaniveau=0.01
  
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
    if len(routes)==2 and cptA==2 and cptB==2: #==2 car on a le segment actuel et le segment attache qui partagent ce point
      self.fabriqueSegmentDroit(routes)
    elif cptA==1 or cptB==1:
      self.fabriqueCulDeSac(routes, cptA==1)
    else:
      print "Configuration non geree :", len(routes), cptA, cptB
      return self.fabrique()
      
  def fabriqueCulDeSac(self, routes, culEnA):
    return self.fabriqueSegmentDroit(routes)

  def fabriqueSegmentDroit(self, routes):
    couleur = (0.0,0.0,0.0,1.0)
    if self.taille==3:
      couleur = (1.0,0.0,0.0,1.0)
    if self.racine!=None:
      self.supprime()

    self.racine = NodePath("00")
    self.format = GeomVertexFormat.getV3c4()
    self.vdata = GeomVertexData('TriangleVertices',self.format,Geom.UHStatic)
    self.vWriter = GeomVertexWriter(self.vdata, 'vertex')
    self.cWriter = GeomVertexWriter(self.vdata, 'color')
      
    nA,nB = self.getNormales(routes)
    nA=nA*(self.taille*self.largeurVoie)
    nB=nB*(self.taille*self.largeurVoie)
    
    def quad(a,b,c,d, geom):
      prim = GeomTriangles(Geom.UHStatic)
      prim.addVertex(a)
      prim.addVertex(b)
      prim.addVertex(c)
      prim.closePrimitive()
      geom.addPrimitive(prim)
      prim = GeomTriangles(Geom.UHStatic)
      prim.addVertex(b)
      prim.addVertex(d)
      prim.addVertex(c)
      prim.closePrimitive()
      geom.addPrimitive(prim)
      return geom

    geom = Geom(self.vdata)
    #Bitume
    self.vWriter.addData3f(self.pointA-nA)
    self.cWriter.addData4f(*couleur)
    self.vWriter.addData3f(self.pointA+nA)
    self.cWriter.addData4f(*couleur)
    self.vWriter.addData3f(self.pointB-nB)
    self.cWriter.addData4f(*couleur)
    self.vWriter.addData3f(self.pointB+nB)
    self.cWriter.addData4f(*couleur)
    
    geom=quad(0,1,2,3,geom)

    couleur = (0.2,0.2,0.2,1.0)
    #Canniveau, connexion a la route
    self.vWriter.addData3f(self.pointA-nA)
    self.cWriter.addData4f(*couleur)
    self.vWriter.addData3f(self.pointA+nA)
    self.cWriter.addData4f(*couleur)
    self.vWriter.addData3f(self.pointB-nB)
    self.cWriter.addData4f(*couleur)
    self.vWriter.addData3f(self.pointB+nB)
    self.cWriter.addData4f(*couleur)
  
    #Canniveau, points les plus bas
    nA.normalize()
    nB.normalize()
    nA=nA*(self.taille*self.largeurVoie+self.largeurCaniveau)
    nB=nB*(self.taille*self.largeurVoie+self.largeurCaniveau)
    nA[2]=self.profondeurCaniveau
    nB[2]=self.profondeurCaniveau
    self.vWriter.addData3f(self.pointA-nA)
    self.cWriter.addData4f(*couleur)
    nA[2]=-self.profondeurCaniveau
    nB[2]=-self.profondeurCaniveau
    self.vWriter.addData3f(self.pointA+nA)
    self.cWriter.addData4f(*couleur)
    nA[2]=self.profondeurCaniveau
    nB[2]=self.profondeurCaniveau
    self.vWriter.addData3f(self.pointB-nB)
    self.cWriter.addData4f(*couleur)
    nA[2]=-self.profondeurCaniveau
    nB[2]=-self.profondeurCaniveau
    self.vWriter.addData3f(self.pointB+nB)
    self.cWriter.addData4f(*couleur)

    geom=quad(8,4,10,6,geom)
    geom=quad(5,9,7,11,geom)

    #Canniveau vers trottoire
    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    self.vWriter.addData3f(self.pointA-nA)
    self.cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    self.vWriter.addData3f(self.pointA+nA)
    self.cWriter.addData4f(*couleur)
    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    self.vWriter.addData3f(self.pointB-nB)
    self.cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    self.vWriter.addData3f(self.pointB+nB)
    self.cWriter.addData4f(*couleur)
    
    geom=quad(12,8,14,10,geom)
    geom=quad(9,13,11,15,geom)


    #Surface du trottoire
    nA[2]=0.0
    nB[2]=0.0
    nA.normalize()
    nB.normalize()
    nA=nB*(self.taille*self.largeurVoie+self.largeurCaniveau+self.largeurTrottoir)
    nB=nB*(self.taille*self.largeurVoie+self.largeurCaniveau+self.largeurTrottoir)

    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    self.vWriter.addData3f(self.pointA-nA)
    self.cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    self.vWriter.addData3f(self.pointA+nA)
    self.cWriter.addData4f(*couleur)
    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    self.vWriter.addData3f(self.pointB-nB)
    self.cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    self.vWriter.addData3f(self.pointB+nB)
    self.cWriter.addData4f(*couleur)

    geom=quad(16,12,18,14,geom)
    geom=quad(13,17,15,19,geom)

    node = GeomNode('gnode')
    node.addGeom(geom)
    mdl = NodePath(node)
    mdl.reparentTo(self.racine)
    self.racine.reparentTo(render)
    
    if self.estUnPont:
      mdl=loader.loadModel("box.egg")
      mdl.setPos(self.pointA)
      mdl.lookAt(Point3(self.pointB))
      mdl.setScale(0.1,0.1,mdl.getZ())
      mdl.setPos(mdl, -0.5,-0.5,0.0)
      mdl.setZ(0.0)
      mdl.setP(0.0)
      mdl.setR(0.0)
      mdl.reparentTo(self.racine)
      mdl=loader.loadModel("box.egg")
      mdl.setPos(self.pointB)
      mdl.lookAt(Point3(self.pointA))
      mdl.setScale(0.1,0.1,mdl.getZ())
      mdl.setPos(mdl, -0.5,-0.5,0.0)
      mdl.setZ(0.0)
      mdl.setP(0.0)
      mdl.setR(0.0)
      mdl.reparentTo(self.racine)
      
    
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
    
  def setImportance(self, importance):
    self.importance = importance
    self.fabrique()
    
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
  affichei=0
  affichej=0
  racineSol = None
  
  def __init__(self, rayon=None, fichier=None, etape=0):
    if not rayon and not fichier:
      print "besoin de taille ou fichier"
      return
    if rayon!=None or etape==0:
      self.rayon = int(rayon)
      self.fabriqueSol()
    self.routes=[]
    self.batiments = []
    self.points=[]
    
    if fichier==None:
      while len(self.routes)==0:
        p1 = self.pointAlea(Vec3(0.0,0.0,0.0))
        p2 = self.pointAlea(Vec3(0.0,0.0,0.0))
        v=p2-p1
        v.normalize()
        v=v*self.longueurSegment*2
        p2=p1+v
        self.points = []
        self.ajouteRoute(p1, p2)
    else:
      self.charge(fichier)
    
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
    
  idAfficheRoute = 0
  def afficheRoutes(self):
    if self.idAfficheRoute >= len(self.routes):
      return
    route = self.routes[self.idAfficheRoute]
    print "Creation de la route %i/%i\r" %(self.idAfficheRoute,len(self.routes)),
    route.hauteQualite(self)
    self.idAfficheRoute+=1

  def affiche(self):
    if not self.afficheModele:
      self.affiche=self.finAffiche
      
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
        #self.flatten()
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
        Pz=self.getAltitude(Vec3(Px,Py,0.0))
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
    self.sol=[]
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
          if taille==1:
            taille=2
          pointA[2]=self.getAltitude(pointA)+1.1
          pointB[2]=self.getAltitude(pointB)+1.1
          if pointA not in self.points:
            self.points.append(pointA)
          if pointB not in self.points:
            self.points.append(pointB)
          self.routes.append(Route(pointA, pointB, taille, self))
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
     test = Vec3((random.random()*2-1)*delta+x, (random.random()*2-1)*delta+y, 0.0+z)
     alt = self.getAltitude(test)
     if alt>0.0:
       if alt<=autorise:
         test[2]=alt
         out = test
    return out
    
  def getAltitude(self, pt):
    x,y,z = pt
    if x+self.rayon<0 or x+self.rayon>=self.rayon*2:
      return -1000
    if y+self.rayon<0 or y+self.rayon>=self.rayon*2:
      return -1000
    return self.sol[int(x)+self.rayon][int(y)+self.rayon]
      
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
        Pz=self.getAltitude(Vec3(Px, Py, 0.0))
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
    Pz=Pz=self.getAltitude(Vec3(Px,Py,0.0))
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
      Pz=self.getAltitude(Vec3(Px,Py,0.0))
      if (Vec3(Px, Py, Pz)-prev).length()>3*rayon+dec:
        if Pz>0:#dec = random.random()*rayon*30
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
        if self.getAltitude(Vec3(Px,Py,0.0))<=0:
          Px=A[0]+prevR*(B[0]-A[0])
          Py=A[1]+prevR*(B[1]-A[1])
          return Vec3(Px, Py, self.getAltitude(Vec3(Px,Py,0.0)))
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
        
    if self.getAltitude(depart)<=0:
      return False
    if self.getAltitude(arrivee)<=0:
      return False

    if abs(depart[0])>self.rayon:
      return False
    if abs(depart[1])>self.rayon:
      return False
    if abs(arrivee[0])>self.rayon:
      return False
    if abs(arrivee[1])>self.rayon:
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
      position[2]=self.getAltitude(position)
      plus[2]=self.getAltitude(plus)

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
        
      points.append(position)
      taille = 2.0
      routes.append(Route(position, plus, taille))
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
    self.affiche()
    self.ajouteRouteAlea()
    if len(self.batiments)>500:
      self.sauvegarde("ville.out")
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
      self.sauvegarde("ville-s2.out")
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
      self.sauvegarde("ville-s3.out")
    return task.cont
    
  def pingModeleBatiments(self, task):
    self.pings+=1
    if self.pings==1:
      print "TODO : pingModeleBatiments"
    self.affiche()
    if self.pings%60==0:
      self.sauvegarde("ville-s4.out")
    return task.cont
    
  def pingModeleSol(self, task):
    self.pings+=1
    if self.pings==1:
      print "TODO : pingModeleSol"
    self.affiche()
    if self.pings%60==0:
      self.sauvegarde("ville-s5.out")
    return task.cont

  posBat = 0
  passeBat = 0
  ajoutBatPasse = 0
  def concentreBatiments(self):
    if self.posBat>=len(self.batiments):
      self.posBat = 0
      self.passeBat += 1
      self.ajoutBatPasse = 0
    print "Batiments, passe %i %i nouveaux batiments ajoutes pour un total de %i" %(self.passeBat, self.ajoutBatPasse, len(self.batiments))
    batiment = self.batiments[self.posBat]
    position = batiment.position
    orientation = batiment.orientation
    importance = batiment.importance
    taille = batiment.taille
    tailleTeste = random.random()*1.0+0.5

    nouvImportance = importance*0.95
    if nouvImportance>=1.0:
      for angle in range(0,360):
        if random.random()>=0.5:
          tailleTeste = random.random()*1.0+0.5
        direction = Vec3((taille+tailleTeste+0.005)*math.cos(float(angle)/180*math.pi), (taille+tailleTeste+0.005)*math.sin(float(angle)/180*math.pi), 0.0)
        newPos = position + direction
        newPos[2]=self.getAltitude(newPos)
        if newPos[2]>0:
          if random.random()>0.05:
            if not self.collisionBatimentBatiment(newPos, tailleTeste):
              if not self.collisionBatimentLigne(newPos, tailleTeste):
                if self.pointPlusProche(newPos)[1]<=self.longueurSegment:
                  batiment = Batiment(newPos, orientation, tailleTeste, nouvImportance)
                  self.batiments.append(batiment)
                  self.ajoutBatPasse +=1
    self.posBat+=1

#base.setBackgroundColor(40.0/255, 169.0/255, 12.0/255)

dlight = PointLight('my dlight')
dlnp = render.attachNewNode(dlight)
dlnp.setPos(0, 0, 30)
render.setLight(dlnp)
ville=Ville(rayon=None, fichier="ville-s2.out", etape=3) #ville.out
taskMgr.add(ville.ping, 'PingVille')
base.accept('a-repeat', ville.chercheQuartiers)
run()
