#!/usr/bin/env python
# -*- coding: utf-8 -*-
import direct.directbase.DirectStart
import random
import math
from pandac.PandaModules import *
from weakref import proxy

class Joueur:
  stress = None
  touches = None
  touchesControles = None
  configClavier = None
  actions = None
  preImage = None
  
  def __init__(self, niveau):
		self.stress = 0.0
		self.niveau = niveau
		self.touches = []
		self.touchesControles = []
		self.configClavier = {}
		self.configClavier["arrow_up"]="avant"
		self.configClavier["arrow_down"]="arriere"
		self.configClavier["arrow_left"]="gauche"
		self.configClavier["arrow_right"]="droite"
		self.configClavier["+"]="haut"
		self.configClavier["-"]="bas"
		
		base.disableMouse()
		base.camera.setPos(0.5,-5.5,0.5)
		base.camera.lookAt(0.5,1.0,0.5)
		base.camLens.setNear(0.1)
		
		base.accept('wheel_up', self.presseTouche, ['wheel_up'])
		base.accept('wheel_down', self.presseTouche, ['wheel_down'])
		base.buttonThrowers[0].node().setButtonDownEvent('presseTouche')
		base.buttonThrowers[0].node().setButtonUpEvent('relacheTouche')
		base.accept('presseTouche', self.presseTouche)
		base.accept('relacheTouche', self.relacheTouche)
		self.lierActionsFonctions()
		taskMgr.add(self.ping, "Boucle IO")
		
  def ping(self, task):
    if self.preImage != None:
			deltaT = task.time - self.preImage
    else:
			deltaT = task.time
    self.preImage = task.time
    self.gereTouche(deltaT)
    return task.cont
		
  ### Gestion du clavier/souris ----------------------------------------
  def presseTouche(self, touche):
    """Une touche a ete pressee, on l'ajoute a la liste des touches"""
    self.touches.append(touche)
    if touche in ["alt", "shift", "control"]:#, "lalt", "lshift", "lcontrol", "ralt", "rshift", "rcontrol"]:
      self.touchesControles.append(touche)
    self.gereTouche(0.0)
    
  def relacheTouche(self, touche):
    """Une touche a ete relachee, on l'enleve de la liste des touches"""
    while self.touches.count(touche)>0:
      self.touches.remove(touche)
      if touche+"-off" in self.configClavier.keys():
        action = self.configClavier[touche+"-off"]
        if action not in self.actions.keys():
          #La touche a ete configuree pour faire un truc mais on sait pas ce que c'est
          print "Type d'action inconnue : ", action
        else:
          #On lance la fonction
          self.appelFonction(*self.actions[action], temps=0.0)
    while self.touchesControles.count(touche)>0:
      self.touchesControles.remove(touche)
            
  def gereTouche(self, temps):
    """Gere les touches clavier"""
    for touche in self.touches:
      #On ajoute les touches de modifications dans l'ordre alphabetique genre alt+shit-r indique que les touche alt, shift et r sont pressees en meme temps
      if self.touchesControles:
        tch=touche
        touche = "+".join(sorted(self.touchesControles))+"-"+touche
        #Si jamais la touche avec les modificateurs appliquee n'est pas dans la config, on teste sans
        if not touche in self.configClavier.keys():
          touche=tch
      #La touche est configuree
      if touche in self.configClavier.keys():
        action = self.configClavier[touche]
        if action not in self.actions.keys():
          #La touche a ete configuree pour faire un truc mais on sait pas ce que c'est
          print "Type d'action inconnue : ", action
        else:
          #On lance la fonction
          self.appelFonction(*self.actions[action], temps=temps)
      
  def lierActionsFonctions(self):
    """On donne des noms gentils a des appels de fonction moins sympas"""
    self.actions = {}
    self.actions["avant"] = (self.bouge,{"y":1.0, "temps":0.0})
    self.actions["arriere"] = (self.bouge,{"y":-1.0, "temps":0.0})
    self.actions["gauche"] = (self.bouge,{"x":-1.0, "temps":0.0})
    self.actions["droite"] = (self.bouge,{"x":1.0, "temps":0.0})
    self.actions["haut"] = (self.bouge,{"z":1.0, "temps":0.0})
    self.actions["bas"] = (self.bouge,{"z":-1.0, "temps":0.0})
    
  def bouge(self, x=0.0,y=0.0,z=0.0,temps=0.0):
    vec=Vec3(0.0,y,z)
    oldPos = base.camera.getPos()
    base.camera.setPos(base.camera, vec*temps)
    position = int(base.camera.getPos()[0]+0.5), int(base.camera.getPos()[1]+0.5), int(base.camera.getPos()[2]+0.5)
    #if position[0]>self.niveau.taille or position[0]>self.niveau.taille or abs(position[2])>self.niveau.taille
    #if self.niveau.structure[position[0]][position[1]][position[2]]>0.0:
		#	print "coll"
		#	base.camera.setPos(oldPos)
    base.camera.setH(base.camera, -x*temps*20)
		

  def appelFonction(self, fonction, parametres, temps=0.0):
    """Appel la fonction fonction en lui passant les parametres decris"""
    if parametres==None:
      fonction()
    elif isinstance(parametres, dict):
      if "temps" in parametres.keys():
        parametres["temps"]=temps
      fonction(**parametres)
    elif isinstance(parametres, list) or isinstance(parametres, tuple):
      fonction(*parametres)
    else:
      print "ERREUR : Start.appelFonction, parametres doit etre None, un tuple, une liste ou un dictionnaire"
      fonction[parametre]
  ### Fin gestion du clavier/souris ------------------------------------

class Niveau:
	bruit = None
	sombre = None
	joueur = None
	structure = None
	blocs = None
	
	def __init__(self, taille):
		self.blocs=[]
		self.structure=[]
		for i in range(0, taille+2):
			self.structure.append([])
			for j in range(0, taille+2):
				self.structure[i].append([])
				for k in range(0, taille+2):
					self.structure[i][j].append(1.0)
		self.joueur = Joueur(proxy(self))
		self.niveauSombre(0.2)
		self.niveauBruit(0.05)
		self.genere(taille)
		self.affiche()
				
		taskMgr.add(self.ping, "Ping")
		
	def genere(self, taille):
		light = PointLight('soleil')
		light.setColor((0.7,0.7,0.65,1.0))
		light = render.attachNewNode(light)
		render.setLight(light)
		
		light = PointLight('soleil')
		light.setColor((0.7,0.7,0.65,1.0))
		light = render.attachNewNode(light)
		render.setLight(light)
		light.setPos(len(self.structure),len(self.structure),len(self.structure))
		
		position = Vec3(len(self.structure)/2,len(self.structure)/2,len(self.structure)/2)
		#base.camera.setPos(position + (0.5,0.5,0.5))
		self.structure[int(base.camera.getPos()[0]+0.5)][int(base.camera.getPos()[1]+0.5)][int(base.camera.getPos()[2]+0.5)]=0.0
		#position = Vec3(int(base.camera.getPos()[0]+0.5), int(base.camera.getPos()[1]+0.5), int(base.camera.getPos()[2]+0.5))
		while len(self.blocs)<taille:
			if position not in self.blocs and position.length()<30:
				self.structure[int(position[0])][int(position[1])][int(position[2])] = 0.0
				self.blocs.append(position)
			else:
				position = random.choice(self.blocs)
			type = random.randint(0,3)
			direction = random.randint(0,2)-1
			if direction==0:
				direction=-1
			
			if type==1:
				position = position + (0.0, direction, 0.0)
			elif type==2:
				position = position + (direction, 0.0, 0.0)
			elif type==3:
				position = position + (0.0, 0.0, direction)
								
	def affiche(self):
		for x in range(0, len(self.structure)):
			for y in range(0, len(self.structure[x])):
				for z in range(0, len(self.structure[x][y])):
					print x,y,z
					if self.structure[x][y][z]>=1.0:
						self.ajouteBoite(Vec3(x,y,z))
				
	def ping(self, task):
		self.niveauSombre(abs(math.sin(task.time))*self.joueur.stress/2)
		self.niveauBruit(abs(math.sin(task.time/3))*self.joueur.stress/2)
		return task.cont
				
	def ajouteBoite(self, position):
		bx = loader.loadModel("box.egg")
		bx.reparentTo(render)
		bx.clearTexture()
		#bx.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
		#bx.setColor(random.random(),random.random(),random.random(),1.0)
		bx.setColor(0.3,0.5,0.5,1.0)
		#bx.setTransparency(TransparencyAttrib.MDual)
		bx.setPos(position)
		
	def niveauBruit(self, niveau):
		if self.bruit==None:
			cm = CardMaker("bruit"); 
			cm.setFrameFullscreenQuad() 
			cm.setUvRange(loader.loadTexture("whitenoise.bmp")) 
			self.bruit = NodePath(cm.generate()) 
			self.bruit.reparentTo(render2d) 
			self.bruit.setTexture(loader.loadTexture("whitenoise.bmp")) 
			self.bruit.setTransparency(TransparencyAttrib.MDual)
		self.bruit.setColor(1.0,1.0,1.0,niveau)
		
	def niveauSombre(self, niveau):
		if self.sombre==None:
			cm = CardMaker("sombre"); 
			cm.setFrameFullscreenQuad() 
			cm.setUvRange(loader.loadTexture("noir.png")) 
			self.sombre = NodePath(cm.generate()) 
			self.sombre.reparentTo(render2d) 
			self.sombre.setTexture(loader.loadTexture("noir.png")) 
			self.sombre.setTransparency(TransparencyAttrib.MDual)
		self.sombre.setColor(1.0,1.0,1.0,niveau)
		

niveau = Niveau(10)

run()
