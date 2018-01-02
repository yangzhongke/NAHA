#coding:UTF-8
import sys
sys.path.insert(0, '../')

from ACurses import *
from ACursesEx import *
from sys import *

class ChangePwdForm(AForm):    
    def __init__(self):                        
        AForm.__init__(self, 20, 5, 10, 35)
       
        labeluser = ALabel(0, 0, 15)
        labeluser.settext("UserName")       
        self.edtuser = AEdit(12, 0, 20)
        self.edtuser.ongrabfocus = lambda:self.showmsg("Input UserName")
        labeluser.setlabelfor(self.edtuser)
        self.addall([labeluser, self.edtuser])
       
        labelpasswd = ALabel(0, 2, 15)
        labelpasswd.settext("Password")       
        self.edtpasswd = APasswordField(12, 2, 20)
        self.edtpasswd.ongrabfocus = lambda:self.showmsg("Input Password")
        labelpasswd.setlabelfor(self.edtpasswd)       
        self.addall([labelpasswd, self.edtpasswd])
       
        btnlogin = AButton(0, 5, 10)
        btnlogin.settext("Login")
        btnexit = AButton(20, 5, 10)
        btnexit.settext("Exit")
        self.addall([btnlogin, btnexit])
       
        btnlogin.onclick = self.login
        btnexit.onclick = lambda:exit()
       
        self.labelmsg = ALabel(0, 7, 30)
        self.add(self.labelmsg)        
    def login(self): 
        user = self.edtuser.gettext()
        passwd = self.edtpasswd.gettext()
        if(len(user)<=0):
            self.showmsg("UserName is required")
            return
        if(len(passwd)<=0):
            self.showmsg("Password is required")
            return   
        if(user=="root" and passwd=="123456"):
            self.showmsg("Login ok")    
        else:
            self.showmsg("Login Error")       
    def showmsg(self, msg):
        self.labelmsg.settext(msg) 
		
initapp()
try: 
    form = ChangePwdForm()
    form.show()
    form.destroy()
finally:
	endapp()