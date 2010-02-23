#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

class PluginManager:
  plugins = None
  def __init__(self):
    print "PluginManager()"
    self.plugins = self.getPluginList()
    self.roots = self.getRoots(self.plugins)

  def getPluginList(self):
    print "-getPluginList"
    pluginList = {}
    for plugin in os.listdir(os.path.join(".","plugins")):
      if plugin.endswith(".py"):
        print "--Found plugin %s. Testing..." %plugin
        try:
          _temp = __import__(plugin[:-3], globals(), locals(), ['Plugin'], -1)
          pluginTmp = _temp.Plugin() #On appel le constructeur pour être sûr que ça marche et attraper les infos de classe
          pluginList[pluginTmp._name_]=_temp.Plugin
          print "  ... plugin OK"
        except AttributeError:
          print "Warning :: ",os.path.join(".","plugins",plugin),"is not a valid plugin"
    return pluginList

  def getRoots(self, plugins):
    print "-getRoots(%s)" %str(plugins)
    rootList = {}
    include = []
    for pluginName in plugins:
      plugin = plugins[pluginName]
      if plugin._include_:
        include += plugin._include_
    for pluginName in plugins:
      if pluginName not in include:
        rootList[pluginName]=plugins[pluginName]
      
    return rootList
