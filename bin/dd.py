print "main"
import sys
import os
sys.path.append(os.path.join(".","modules"))
sys.path.append(os.path.join(".","plugins"))

import general

from configuration import Configuration
from pluginmanager import PluginManager
general.configuration = Configuration()
general.configuration.loadConfiguration(os.path.join(".", "configuration", "main.cfg"))
general.pluginManager = PluginManager()
if not general.pluginManager.roots:
  print "Error : No plugin found, exiting."
  sys.exit()
elif len(general.pluginManager.roots)==1:
  selectedPlugin = general.pluginManager.roots.values()[0]
else:
  print "-- Select plugin :"
  for root in general.pluginManager.roots:
    print "-- - %s" %root
  selectedPlugin = general.pluginManager.roots.values()[0]

print "Using plugin : %s" %str(selectedPlugin)
general.selectedPlugin = selectedPlugin()
general.graphicalEngine = general.selectedPlugin.getGraphicalEngine()
print "- graphicalEngine : %s" %str(general.graphicalEngine)
general.userInterface = general.selectedPlugin.getUserInterface()
print "- userInterface : %s" %str(general.userInterface)
general.scriptEngine = general.selectedPlugin.getScriptEngine()
print "- scriptEngine : %s" %str(general.scriptEngine)
general.mainLoop = general.selectedPlugin.getMainLoop()
print "- mainLoop : %s" %str(general.mainLoop)
general.mainMenu = general.userInterface.getMenu()
print "- mainMenu : %s" %str(general.mainMenu)
general.mainMenu.start()
