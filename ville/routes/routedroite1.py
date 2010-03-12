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

  def filtre(self, routes, cptA, cptB):
    return len(routes)==2 and cptA==2 and cptB==2
    
  def fabrique(self, route, routes, cptA, cptB):
    couleur = (0.0,0.0,0.0,1.0)
    if route.taille==3:
      couleur = (1.0,0.0,0.0,1.0)
    if route.racine!=None:
      route.supprime()

    route.racine = NodePath("00")
    route.format = GeomVertexFormat.getV3c4()
    route.vdata = GeomVertexData('TriangleVertices',route.format,Geom.UHStatic)
    route.vWriter = GeomVertexWriter(route.vdata, 'vertex')
    route.cWriter = GeomVertexWriter(route.vdata, 'color')
      
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

    geom = Geom(route.vdata)
    #Bitume
    route.vWriter.addData3f(route.pointA-nA)
    route.cWriter.addData4f(*couleur)
    route.vWriter.addData3f(route.pointA+nA)
    route.cWriter.addData4f(*couleur)
    route.vWriter.addData3f(route.pointB-nB)
    route.cWriter.addData4f(*couleur)
    route.vWriter.addData3f(route.pointB+nB)
    route.cWriter.addData4f(*couleur)
    
    geom=quad(0,1,2,3,geom)

    couleur = (0.2,0.2,0.2,1.0)
    #Canniveau, connexion a la route
    route.vWriter.addData3f(route.pointA-nA)
    route.cWriter.addData4f(*couleur)
    route.vWriter.addData3f(route.pointA+nA)
    route.cWriter.addData4f(*couleur)
    route.vWriter.addData3f(route.pointB-nB)
    route.cWriter.addData4f(*couleur)
    route.vWriter.addData3f(route.pointB+nB)
    route.cWriter.addData4f(*couleur)
  
    #Canniveau, points les plus bas
    nA.normalize()
    nB.normalize()
    nA=nA*(route.taille*self.largeurVoie+self.largeurCaniveau)
    nB=nB*(route.taille*self.largeurVoie+self.largeurCaniveau)
    nA[2]=self.profondeurCaniveau
    nB[2]=self.profondeurCaniveau
    route.vWriter.addData3f(route.pointA-nA)
    route.cWriter.addData4f(*couleur)
    nA[2]=-self.profondeurCaniveau
    nB[2]=-self.profondeurCaniveau
    route.vWriter.addData3f(route.pointA+nA)
    route.cWriter.addData4f(*couleur)
    nA[2]=self.profondeurCaniveau
    nB[2]=self.profondeurCaniveau
    route.vWriter.addData3f(route.pointB-nB)
    route.cWriter.addData4f(*couleur)
    nA[2]=-self.profondeurCaniveau
    nB[2]=-self.profondeurCaniveau
    route.vWriter.addData3f(route.pointB+nB)
    route.cWriter.addData4f(*couleur)

    geom=quad(8,4,10,6,geom)
    geom=quad(5,9,7,11,geom)

    #Canniveau vers trottoire
    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    route.vWriter.addData3f(route.pointA-nA)
    route.cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    route.vWriter.addData3f(route.pointA+nA)
    route.cWriter.addData4f(*couleur)
    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    route.vWriter.addData3f(route.pointB-nB)
    route.cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    route.vWriter.addData3f(route.pointB+nB)
    route.cWriter.addData4f(*couleur)
    
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
    route.vWriter.addData3f(route.pointA-nA)
    route.cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    route.vWriter.addData3f(route.pointA+nA)
    route.cWriter.addData4f(*couleur)
    nA[2]=-self.hauteurTrottoire
    nB[2]=-self.hauteurTrottoire
    route.vWriter.addData3f(route.pointB-nB)
    route.cWriter.addData4f(*couleur)
    nA[2]=self.hauteurTrottoire
    nB[2]=self.hauteurTrottoire
    route.vWriter.addData3f(route.pointB+nB)
    route.cWriter.addData4f(*couleur)

    geom=quad(16,12,18,14,geom)
    geom=quad(13,17,15,19,geom)

    node = GeomNode('gnode')
    node.addGeom(geom)
    mdl = NodePath(node)
    mdl.reparentTo(route.racine)
    route.racine.reparentTo(render)
    
    if route.estUnPont:
      mdl=loader.loadModel("box.egg")
      mdl.setPos(route.pointA)
      mdl.lookAt(Point3(route.pointB))
      mdl.setScale(0.1,0.1,mdl.getZ())
      mdl.setPos(mdl, -0.5,-0.5,0.0)
      mdl.setZ(0.0)
      mdl.setP(0.0)
      mdl.setR(0.0)
      mdl.reparentTo(route.racine)
      mdl=loader.loadModel("box.egg")
      mdl.setPos(route.pointB)
      mdl.lookAt(Point3(route.pointA))
      mdl.setScale(0.1,0.1,mdl.getZ())
      mdl.setPos(mdl, -0.5,-0.5,0.0)
      mdl.setZ(0.0)
      mdl.setP(0.0)
      mdl.setR(0.0)
      mdl.reparentTo(route.racine)
