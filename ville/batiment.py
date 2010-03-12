#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *
import random

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
