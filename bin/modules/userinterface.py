from menu import Menu

class UserInterface:
  def __init__(self):
    print "UserInterface()"

  def getMenu(self):
    print "- getMenu"
    return Menu()
