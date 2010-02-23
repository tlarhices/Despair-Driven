from plugininterface import PluginInterface
from graphicalengine import GraphicalEngine
from userinterface import UserInterface
from scriptengine import ScriptEngine

class Plugin(PluginInterface):
  _name_ = "main1"
  _include_ = ("slave1",)

  def getGraphicalEngine(self):
    print "- getGraphicalEngine"
    return GraphicalEngine()

  def getUserInterface(self):
    print "- getUserInterface"
    return UserInterface()

  def getScriptEngine(self):
    print "- getScriptEngine"
    return ScriptEngine()

  def getMainLoop(self):
    print "- getMainLoop"
    return self.loop

  def loop(self, temps):
    print "- loop %s" %str(temps)
    print "ping %.3f" %temps
