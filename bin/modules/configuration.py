#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Planet - A game
#Copyright (C) 2009 Clerc Mathias
#See the license file in the docs folder for more details

import general

import os
import sys

class Configuration:
  """Gère le fichier de configuration"""
  configuration = None #Le dictionnaire qui contient la configuration actuelle
  configurationFile = None #Le fichier que l'on a chargé
  
  def __init__(self):
    self.configuration = {}
    
  def loadConfiguration(self, configurationFile, errorIfNotExist=True):
    """Charge un fichier de configuration"""
    section = None
    subsection = None
    
    if not os.path.exists(configurationFile):
      if errorIfNotExist:
        raw_input("CONFIGURATION :: ERROR : The configuration file '%s' does not exists." %configurationFile)
      return
    
    self.configurationFile = configurationFile
    configurationFile = open(configurationFile, "r")
    for line in configurationFile:
      line = line.strip().lower() #Everythong in lower case
      if line and line[0]!="#": #We don't look at lines starting by "#" or empty lines
        if line.startswith("[[") and line.endswith("]]"): #If line is like [[****]] this is a section
          section = line[2:-2].strip()
          subsection = None
        elif line.endswith(":"): #If line ends with : this is a subsection
          subsection = line[:-1].strip()
        else: #Otherwise this is content
          if section == None:
            print "Configuration content without section : ",line
          else:
            a,b = line.split("=")
            a = a.strip()
            b = b.strip()
            if not section in self.configuration.keys():
              self.configuration[section]={}
            if not subsection in self.configuration[section].keys():
              self.configuration[section][subsection]={}
            self.configuration[section][subsection][a]=b
    
  def sauve(self, fichier):
    """Sauvegarde un fichier de configuration (ne garde pas les commentaires)"""
    #Formatte les valeurs pour un sotckage vers le fichier
    def versStr(valeur):
      if isinstance(valeur, bool):
        return str(valeur)[0] #Transforme True en 'T' et False en 'F'
      return str(valeur)
      
    fichier = open(fichier, "w")
    for section in sorted(self.configuration.keys()): #Sauve les sections
      fichier.write("[["+str(section)+"]]\r\n")
      for soussection in sorted(self.configuration[section].keys()): #Sauve les sous-sections
        fichier.write(str(soussection)+":\r\n")
        for element in sorted(self.configuration[section][soussection].keys()): #Sauve les clefs
          fichier.write(str(element)+" = "+versStr(self.configuration[section][soussection][element])+"\r\n")
        fichier.write("\r\n")
    fichier.write("\r\n")
    
  def getConfigurationClavier(self):
    """Retourne la configuration du clavier"""
    out = {}
    if "commandes" not in self.configuration.keys():
      print "ERREUR:getConfigurationClavier :: pas de touches configurées"
      return {}
    for clef in self.configuration["commandes"]["clavier"]:
      out[clef]=self.configuration["commandes"]["clavier"][clef]
    for clef in self.configuration["commandes"]["souris"]:
      out[clef]=self.configuration["commandes"]["souris"][clef]
    return out
    
  def setConfiguration(self, section, soussection, champ, valeur):
    """Change une valeur de la configuration courante"""
    section=str(section).lower()
    soussection=str(soussection).lower()
    champ=str(champ).lower()
    
    if not section in self.configuration.keys():
      self.configuration[section]={}
    if not soussection in self.configuration[section].keys():
      self.configuration[section][soussection]={}
    self.configuration[section][soussection][champ]=valeur
    
  def versType(self, valeur, defaut, type):
    """
    Effectue un transtypage sécurisé
    Effectue type(valeur), si une erreur survient un message est affiché et type(defaut) est renvoyé
    Effectue un transtypage intelligent des booléens
    Si type(defaut) retourne une erreur, le programme se bloque
    """
    try:
      if type==bool:
        if isinstance(valeur, bool):
          return valeur
        elif isinstance(valeur, (int, float)):
          return valeur!=0
        return valeur.lower().strip()=="t"
      return type(valeur)
    except Exception, ex:
      print "configuration::transtypage::Erreur ::",valeur,"n'est pas typpable en",str(type)
      if defaut==valeur:
        raise ex
      return self.versType(defaut, defaut, type)
    
    
  def getConfiguration(self, section, soussection, champ, defaut, type=None):
    """Retourne une valeur de configuration"""
    
    if type==None:
      frame = sys._getframe(1)
      texte=str(frame.f_code.co_filename)+"::"+"??"+"::"+str(frame.f_code.co_name)+u" > Avertissement :: getConfiguration sans type est déprécié, pensez à mettre à jour"
      print texte
      type=str
    
    section=str(section).lower()
    soussection=str(soussection).lower()
    champ=str(champ).lower()
    
    if section not in self.configuration.keys():
      print self.configuration.keys()
      print "getConfiguration::section pas dans le fichier de configuration ::",section
      #raw_input("pause_configuration")
      self.configuration[section]={}
      self.configuration[section][soussection]={}
      self.configuration[section][soussection][champ]=self.versType(defaut, defaut, type)
      return self.versType(defaut, defaut, type)
    if soussection not in self.configuration[section].keys():
      print self.configuration.keys()
      print "getConfiguration::sous-section pas dans le fichier de configuration ::",section, soussection
      #raw_input("pause_configuration")
      self.configuration[section][soussection]={}
      self.configuration[section][soussection][champ]=self.versType(defaut, defaut, type)
      return self.versType(defaut, defaut, type)
    if champ not in self.configuration[section][soussection].keys():
      print "getConfiguration::champ pas dans le fichier de configuration ::",section, soussection, champ
      #raw_input("pause_configuration")
      self.configuration[section][soussection][champ]=self.versType(defaut, defaut, type)
      return self.versType(defaut, defaut, type)
      
    return self.versType(self.configuration[section][soussection][champ], defaut, type)
