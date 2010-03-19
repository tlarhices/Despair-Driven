#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandac.PandaModules import *
import random
import general

class Route:
  pointA = None
  pointB = None
  taille = None
  racine = None
  filtres = None
  lampadaires=None
  feuxtricolores=None
  
  def __init__(self, pointA, pointB, taille, ville=None):
    self.pointA = Vec3(*pointA)
    self.pointB = Vec3(*pointB)
    self.taille = taille
    self.racine = None
    self.estUnPont=False
    self.lampadaires=[]
    self.feuxtricolores=[]

    if self.pointA[2]<=0.0:
      self.pointA[2]=2.1
      self.estUnPont=True
    if self.pointB[2]<=0.0:
      self.pointB[2]=2.1
      self.estUnPont=True
    self.getFiltres()
    
  def getFiltres(self):
    if general.filtresRoute!=None:
      self.filtres = general.filtresRoute[:]
      return
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
    general.filtresRoute = self.filtres[:]
    
  def fabrique(self):
    if self.racine!=None:
      self.supprime()
    
    self.lampadaires=[]
    self.feuxtricolores=[]
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
    
    routesA = []
    routesB = []
    for route in ville.routes:
      if tuple(self.pointA) in route.getCoordTuple():
        routesA.append(route)
      if tuple(self.pointB) in route.getCoordTuple():
        routesB.append(route)

    self.getFiltres()
    filtresValidesA = []
    filtresValidesB = []
    for filtre in self.filtres:
      filtre=filtre()
      if filtre.filtre(routesA):
        filtresValidesA.append(filtre)
      if filtre.filtre(routesB):
        filtresValidesB.append(filtre)
    if len(filtresValidesA)==0:
      print "Configuration non geree :", len(routesA)

      import os
      fichPlug = open(os.path.join(".","routes","%i.py" %(len(routesA))), "w")
      fichPlug.write(self.textePluginVide(routesA))
      fichPlug.close()
      self.fabrique()
    else:
      filtre=random.choice(filtresValidesA)
      filtre.fabrique(routesA)
    if len(filtresValidesB)==0:
      print "Configuration non geree :", len(routesB)

      import os
      fichPlug = open(os.path.join(".","routes","%i.py" %(len(routesB))), "w")
      fichPlug.write(self.textePluginVide(routesB))
      fichPlug.close()
      self.fabrique()
    else:
      filtre=random.choice(filtresValidesB)
      filtre.fabrique(routesB)
    self.ajouteLampadaires()
    self.racine.setPos(self.racine, 0.0,0.0,1.1)
    
  def ajouteLampadaires(self):
    for lampadaire in self.lampadaires:
      mdl = loader.loadModel("modeles/sphere.egg")
      #mdl.setPos(-0.5,-0.5,0.0)
      mdl.setScale(0.005,0.005,0.2)
      mdl.reparentTo(lampadaire)
      
  def supprime(self):
    if self.racine!=None:
      self.racine.detachNode()
      self.racine.removeNode()
      self.racine = None
      for lampadaire in self.lampadaires:
        lampadaire.detachNode()
        lampadaire.removeNode()
      for feuxtricolore in self.feuxtricolores:
        feuxtricolore.detachNode()
        feuxtricolore.removeNode()
    
  def getCoord(self):
    return self.pointA, self.pointB
    
  def getCoordTuple(self):
    return tuple(self.pointA), tuple(self.pointB)
    
  def pointCentre(self):
    return (self.pointA+self.pointB)/2

  def sauvegarde(self):
    out = "R||%s||%s||%f>" %(str(list(self.pointA)), str(list(self.pointB)), self.taille)
    return out

  def textePluginVide(self, routes):
    #Force le reparcours des dossier de plugins
    general.filtresRoute = None
    #Cree un plugin vide
    texte  = "#!/usr/bin/env python\n"
    texte += "# -*- coding: utf-8 -*-\n"
    texte += "from pandac.PandaModules import *\n"
    texte += "from type1 import DessinRoute as Type1\n"
    texte += "\n"
    texte += "class DessinRoute(Type1):\n"
    texte += "  def __init__(self):\n"
    texte += "    Type1.__init__(self)\n"
    texte += "\n"
    texte += "  def filtre(self, routes):\n"
    texte += "    return len(routes)==%i\n" %(len(routes))
    texte += "\n"
    texte += "  def fabrique(self, routes):\n"
    texte += "    for route in routes:\n"
    texte += "      route.fabrique()\n"
    return texte
