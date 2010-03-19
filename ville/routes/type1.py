#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *

class DessinRoute:
  largeurVoie=0.1
  largeurTrottoir=0.05
  hauteurTrottoire=0.01
  largeurCaniveau=0.025
  profondeurCaniveau=0.01
  
  def __init__(self):
    pass

  def filtre(self, routes):
    return False
    
  def fabrique(self, routes):
    pass

  def detecteCote(self, routes):
    if tuple(routes[0].pointA) in routes[1].getCoordTuple() and tuple(routes[0].pointA) in routes[2].getCoordTuple():
      c1=0
    if tuple(routes[0].pointB) in routes[1].getCoordTuple() and tuple(routes[0].pointB) in routes[2].getCoordTuple():
      c1=1
    if tuple(routes[1].pointA) in routes[0].getCoordTuple() and tuple(routes[1].pointA) in routes[2].getCoordTuple():
      c2=0
    if tuple(routes[1].pointB) in routes[0].getCoordTuple() and tuple(routes[1].pointB) in routes[2].getCoordTuple():
      c2=1
    if tuple(routes[2].pointA) in routes[0].getCoordTuple() and tuple(routes[2].pointA) in routes[1].getCoordTuple():
      c3=0
    if tuple(routes[2].pointB) in routes[0].getCoordTuple() and tuple(routes[2].pointB) in routes[1].getCoordTuple():
      c3=1
    return c1, c2, c3
    
  def tronconDroit(self, route, routes, pointA, pointB):
    couleur = (0.0,0.0,0.0,1.0)
    if route.taille==3:
      couleur = (1.0,0.0,0.0,1.0)
    lampadaires=[]
    feuxtricolores=[]
    racine = NodePath("00")
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData('TriangleVertices',format,Geom.UHStatic)
    vWriter = GeomVertexWriter(vdata, 'vertex')
    cWriter = GeomVertexWriter(vdata, 'color')
      
    nA,nB = route.getNormales(routes)
    nA=nA*(route.taille*self.largeurVoie)
    nB=nB*(route.taille*self.largeurVoie)
    
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

    geom = Geom(vdata)
    #Bitume
    vWriter.addData3f(pointA-nA)
    cWriter.addData4f(*couleur)
    vWriter.addData3f(pointA+nA)
    cWriter.addData4f(*couleur)
    vWriter.addData3f(pointB-nB)
    cWriter.addData4f(*couleur)
    vWriter.addData3f(pointB+nB)
    cWriter.addData4f(*couleur)
    
    geom=quad(0,1,2,3,geom)

    couleur = (0.2,0.2,0.2,1.0)
    #Canniveau, connexion a la route
    vWriter.addData3f(pointA-nA)
    cWriter.addData4f(*couleur)
    vWriter.addData3f(pointA+nA)
    cWriter.addData4f(*couleur)
    vWriter.addData3f(pointB-nB)
    cWriter.addData4f(*couleur)
    vWriter.addData3f(pointB+nB)
    cWriter.addData4f(*couleur)
  
    #Canniveau, points les plus bas
    nA.normalize()
    nB.normalize()
    nA=nA*(route.taille*self.largeurVoie+self.largeurCaniveau)
    nB=nB*(route.taille*self.largeurVoie+self.largeurCaniveau)
    nA[2]=self.profondeurCaniveau
    nB[2]=self.profondeurCaniveau
    vWriter.addData3f(pointA-nA)
    cWriter.addData4f(*couleur)
    nA[2]=-self.profondeurCaniveau
    nB[2]=-self.profondeurCaniveau
    vWriter.addData3f(pointA+nA)
    cWriter.addData4f(*couleur)
    nA[2]=self.profondeurCaniveau
    nB[2]=self.profondeurCaniveau
    vWriter.addData3f(pointB-nB)
    cWriter.addData4f(*couleur)
    nA[2]=-self.profondeurCaniveau
    nB[2]=-self.profondeurCaniveau
    vWriter.addData3f(pointB+nB)
    cWriter.addData4f(*couleur)

    geom=quad(8,4,10,6,geom)
    geom=quad(5,9,7,11,geom)

    #Canniveau vers trottoire
    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    vWriter.addData3f(pointA-nA)
    cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    vWriter.addData3f(pointA+nA)
    cWriter.addData4f(*couleur)
    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    vWriter.addData3f(pointB-nB)
    cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    vWriter.addData3f(pointB+nB)
    cWriter.addData4f(*couleur)
    
    geom=quad(12,8,14,10,geom)
    geom=quad(9,13,11,15,geom)


    #Surface du trottoire
    nA[2]=0.0
    nB[2]=0.0
    nA.normalize()
    nB.normalize()
    nA=nB*(route.taille*self.largeurVoie+self.largeurCaniveau+self.largeurTrottoir)
    nB=nB*(route.taille*self.largeurVoie+self.largeurCaniveau+self.largeurTrottoir)

    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    vWriter.addData3f(pointA-nA)
    cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    vWriter.addData3f(pointA+nA)
    cWriter.addData4f(*couleur)
    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    vWriter.addData3f(pointB-nB)
    cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    vWriter.addData3f(pointB+nB)
    cWriter.addData4f(*couleur)
    
    nA.normalize()
    nA=nB*(route.taille*self.largeurVoie+self.largeurCaniveau+self.largeurTrottoir/3)
    pt=Point3(*pointA)
    pt[2]+=self.hauteurTrottoire

    geom=quad(16,12,18,14,geom)
    geom=quad(13,17,15,19,geom)

    node = GeomNode('gnode')
    node.addGeom(geom)
    mdl = NodePath(node)
    mdl.reparentTo(racine)
    
    if route.estUnPont:
      mdl=loader.loadModel("box.egg")
      mdl.setPos(pointA)
      mdl.lookAt(Point3(pointB))
      mdl.setScale(0.1,0.1,mdl.getZ())
      mdl.setPos(mdl, -0.5,-0.5,0.0)
      mdl.setZ(0.0)
      mdl.setP(0.0)
      mdl.setR(0.0)
      mdl.reparentTo(racine)
      mdl=loader.loadModel("box.egg")
      mdl.setPos(pointB)
      mdl.lookAt(Point3(pointA))
      mdl.setScale(0.1,0.1,mdl.getZ())
      mdl.setPos(mdl, -0.5,-0.5,0.0)
      mdl.setZ(0.0)
      mdl.setP(0.0)
      mdl.setR(0.0)
      mdl.reparentTo(racine)
      
    return racine, lampadaires, feuxtricolores
