#coding:utf-8

import ACurses,curses

#author:杨中科
def msgbox(msg):
    '''显示消息框，msg为要显示的消息'''
    form = InfoForm(msg)
    form.show()
    form.destroy()

def confirmbox(msg):
    '''显示带有【是】、【否】按钮的提示框，msg为要显示的消息，返回值为true或者false'''
    form = ConfirmForm(msg)
    form.show()
    form.destroy()
    return form.isconfirm
    
class InfoForm(ACurses.AForm):
    def __init__(self,msg):
        ACurses.AForm.__init__(self, 5,5,10, 35)
        
        self.registerkeyevent(" ", lambda:self.destroy())
        
        btn = ACurses.AButton(13,7,7)
        btn.settext("确定")
        btn.onclick = lambda:self.destroy()
       
        #在牡丹终端上发现当x坐标为0 的时候会显示乱码，目前没有找到根本原因，先这么解决
        lablemsg = ACurses.AMultiLineLabel(1,0,5,30)
        lablemsg.settext(msg) 
    
        self.add(btn) 
        self.add(lablemsg) 
class ConfirmForm(ACurses.AForm):
    def __init__(self,msg):
        ACurses.AForm.__init__(self, 5,5,10, 35)
        self.isconfirm=False
  
        btnyes = ACurses.AButton(5,7,5)
        btnyes.settext("是")
        btnyes.onclick = self.confirm
        
        btnno = ACurses.AButton(15,7,5)
        btnno.settext("否")
        btnno.onclick = self.deny
       
        #在牡丹终端上发现当x坐标为0 的时候会显示乱码，目前没有找到根本原因，先这么解决
        lablemsg = ACurses.AMultiLineLabel(1,0,5,30)
        lablemsg.settext(msg) 
    
        self.add(btnyes) 
        self.add(btnno)
        self.add(lablemsg)   
    def confirm(self):
        self.isconfirm=True
        self.destroy()
    def deny(self):
        self.isconfirm=False
        self.destroy()