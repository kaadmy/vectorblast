class View:
    def __init__(self, parent):
        self.parent=parent

    def get_rot(self):
        return self.parent.get_rot()

    def get_pos(self):
        return self.parent.get_pos()

    def get_zoom(self):
        return self.parent.get_zoom()

view=None

def set(parent):
    global view
    view=View(parent)

def get_pos():
    return view.get_pos()

def get_rot():
    return view.get_rot()

def get_zoom():
    return view.get_zoom()
