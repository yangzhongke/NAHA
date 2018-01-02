#coding:UTF-8
import sys
sys.path.insert(0, '../')

from ACurses import *
from ACursesEx import *
from Menu import *

class MenuDemoForm(AForm):    
    def __init__(self):     
        AForm.__init__(self, 20, 5, 10, 35)	
        menu = AMenu(0,0,50)
        filemi = AMenuItem("File")
        filemi.additem(AMenuItem("Open",self.showinfo))
        filemi.additem(AMenuItem("Save"))
        filemi.additem(AMenuItem("Exit",self.exittrade))
        menu.additem(filemi)
        menu.additem(AMenuItem("Edit"))
        
        viewmi = AMenuItem("View")
        scalemi = AMenuItem("Test")
        scalemi.additem(AMenuItem("50%"))
        scalemi.additem(AMenuItem("100%"))
        scalemi.additem(AMenuItem("150%"))
        scalemi.additem(AMenuItem("200%"))
        viewmi.additem(scalemi)
        viewmi.additem(AMenuItem("big"))
        viewmi.additem(AMenuItem("small"))
        menu.additem(viewmi)
        menu.additem(AMenuItem("About"))
        self.add(menu)
    def showinfo(self,item):
        msgbox("rupeng.com")
    def exittrade(self,item):
        self.destroy()

initapp()
try: 
    f = MenuDemoForm();
    f.show()
    f.destroy()
finally:
    endapp()