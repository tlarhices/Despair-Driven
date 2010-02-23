class PluginInterface:
  _name_ = "not a plugin"
  _include_ = None

  def __init__(self):
    pass
 
  def getGraphicalEngine(self):
    pass
  def getUserInterface(self):
    pass
  def getScriptEngine(self):
    pass
  def getMainLoop(self):
    pass

