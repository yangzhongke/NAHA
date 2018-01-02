#coding:UTF-8
import sys
sys.path.insert(0, '../')

from ACurses import *
from ACursesEx import *

class T002Form(AForm):
    def __init__(self):                        
        AForm.__init__(self, 0, 0, 50, 80)
        label = ALabel(0,0,10,"Demo")
        self.add(label)
        
        rbmobile = ARadioButton(0,2,15,"ChinaMobile","CM")
        rbunicom = ARadioButton(20,2,15,"ChinaUniCom","CU")        
        rbgtype = ARadioGroup([rbmobile,rbunicom])
        rbgtype.selectButton(rbmobile)
        self.addall([rbmobile,rbunicom])
        
        cbvip = ACheckBox(0,3,15,"VIP")
        self.add(cbvip)
        
        labelmonth = ALabel(18,3,15,"Month")
        self.add(labelmonth)    
                
        self.edtmonth = AIntegerEdit(35,3,8)
        self.add(self.edtmonth)
        
        labelpostcode = ALabel(45,3,10,"postcode")
        edtpostcode = AMaskEdit(55,3,10,"######")
        self.add(labelpostcode)
        self.add(edtpostcode)
        
        labelipaddr = ALabel(0,4,10,"IPAddr")
        edtipaddr = AMaskEdit(10,4,20,"#_#_#.#_#_#.#_#_#.#_#_#")
        edtipaddr.setvalidfailpolicy(ACurses.GRABFOCUSANDNOCLEAR)
        self.add(labelipaddr)
        self.add(edtipaddr)
        
        labelcardno = ALabel(30,4,10,"CardNo")
        edtcardno = AMaskEdit(40,4,20,"AAAA")
        self.add(labelcardno)
        self.add(edtcardno)
        
        btnok = AButton(0,8,8,"OK")
        self.add(btnok)
       
        btnok.onclick = self.charge
        btnexit = AButton(20,8,7,"Exit")
        self.add(btnexit)
        
        btnexit.onclick = self.exittrade
    def charge(self):
        msgbox(self.edtmonth.gettext())
        self.edtmonth.setfocus()
    def exittrade(self):
        self.destroy()          

    
initapp()
try: 
    form = T002Form()
    form.show()
    form.destroy()
finally:
    endapp()   