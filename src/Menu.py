#coding:utf-8
import curses,ACursesIntern
from ACurses import *

#author:杨中科

class AMenuItem:
    def __init__(self,caption,event=None,data=None):  
        self.__caption__ = caption
        self.__event__ = event 
        self.__menuitems__ = []
        self.__data__ = data
    def additem(self,menuitem): 
        if(not isinstance(menuitem,AMenuItem)):
            raise "菜单项必须是AMenuItem类型"
        self.__menuitems__.append(menuitem)  
    def isleaf(self):
        return len(self.__menuitems__)<=0
    def getsubmaxwidth(self):
        #子菜单项的最大宽度
        if(self.isleaf()):
            raise "没有子菜单项"      
        mw = 0        
        for item in self.__menuitems__:
            if(item.isleaf()):
                w = len(item.getcaption())
            else:
                #要算上末尾的">"
                w = len(item.getcaption())+1
            if(w>mw):
                mw = w
        return mw        
    def getdata(self):
        #付挂的一些数据
        return self.__data__    
    def getitems(self):
        return self.__menuitems__
    def getcaption(self):
        return self.__caption__
    def fireevent(self):
        if(self.__event__!=None):
            self.__event__(self)

class AMenu(AComponent):
    def __init__(self,x,y,width):
        AComponent.__init__(self, x, y, 1, width)
        self.__topitems__ = []
        self.__focusindex__=0
    def additem(self,item):
        if(not isinstance(item,AMenuItem)):
            raise "菜单项必须是AMenuItem类型"
        self.__topitems__.append(item)
    def hasbox(self):
        return False
    def isfocusable(self):
        return True
    def __paint__(self):
        AComponent.__paint__(self)
        self.win.erase() 
        x = 0
        for i in range(0,len(self.__topitems__)):
            item = self.__topitems__[i]
            c = item.getcaption()
            if(self.__focusindex__==i):
                attr = ACursesIntern.highlight_attr
            else:
                attr = curses.A_NORMAL                
            self.__textout__(x,0,c,attr)
            x = x+len(c)
            if(i<len(self.__topitems__)-1):
                self.__textout__(x,0,"|")
                x = x+1     
    def __calcsubitembounds__(self):
        "计算当前菜单项的子菜单对话框的大小和位置"
        item = self.__topitems__[self.__focusindex__]  
        if(item.isleaf()):
            raise "当前没有子菜单"
        x = self.getabsx()
        for i in range(0,self.__focusindex__):
            pitem = self.__topitems__[i]  
            x = x+len(pitem.getcaption())+1
        
        y = self.getabsy()+1
        
        height = len(item.getitems())+2
        if(height>curses.LINES-1):
            height = curses.LINES-1
        
        width = item.getsubmaxwidth()+4
        return (x,y,height,width)
    def inputproc(self,msg):
        ch = msg.ch
        if(len(self.__topitems__)<=0):
            raise "菜单必须至少有一个顶级项"        
        if(ch==KEY_ENTER or ch==curses.KEY_DOWN):
            msg.consume()  
            item = self.__topitems__[self.__focusindex__]    
            if(item.isleaf()):
                item.fireevent()
                return    
            bound = self.__calcsubitembounds__()
            dlg = MenuDialog(bound[0],bound[1],bound[2],bound[3],
                             item.getitems())            
            dlg.show()
            dlg.destroy()            
        elif(ch==curses.KEY_LEFT):
            msg.consume()
            if(self.__focusindex__<=0):
                self.__focusindex__ = len(self.__topitems__)-1
            else:
                self.__focusindex__ = self.__focusindex__ -1
            self.paint()               
        elif(ch==curses.KEY_RIGHT):
            msg.consume()
            if(self.__focusindex__>=len(self.__topitems__)-1):
                self.__focusindex__ = 0
            else:
                self.__focusindex__ = self.__focusindex__ +1
            self.paint()
class MenuDialog(AForm):
    def __init__(self,x,y,height,width,menuitems,parentdialog=None):
        AForm.__init__(self, x, y, height, width, False)
        self.__menuitems__ = menuitems
        self.__parentdialog__ = parentdialog
        listitems = []        
        for item in menuitems:
            cap = item.getcaption()
            if(item.isleaf()==False):
                cap = cap+">"
            listitems.append(cap)
            
        self.__listbox__ = AListBox(0,0,self.height,
                                    self.width,listitems)
        self.__listbox__.onitemclick = self.__listboxitemclick__
        self.add(self.__listbox__)
    def destroytoroot(self):
        self.destroy()
        if(self.__parentdialog__!=None):
            self.__parentdialog__.destroytoroot()
        
    def __listboxitemclick__(self,index):
        item = self.__menuitems__[index]
        
        #如果是叶子菜单则触发点击事件
        if(item.isleaf()):
            item.fireevent()
            #关闭本线上的菜单
            self.destroytoroot()
        #如果是普通菜单则展开下一级菜单
        else:
            self.__showsubmenu__(item)           
    def inputproc(self,msg):
        AForm.inputproc(self, msg)
        if(msg.isconsumed()):
            return
        ch = msg.ch
        if(ch==curses.KEY_RIGHT):
            #显示子菜单
            msg.consume()
            index = self.__listbox__.getselectedindex()
            if(index<0):
                return
            item = self.__menuitems__[index]
            if(item.isleaf()):
                return
            self.__showsubmenu__(item)
        elif(ch==KEY_ESC or ch==curses.KEY_LEFT):
            #关闭本级菜单
            msg.consume()
            self.destroy()

    def __showsubmenu__(self, item):
        bound = self.__calcsubitembounds__(item)
        dlg = MenuDialog(bound[0],bound[1],bound[2],bound[3],
                         item.getitems(),self) 
        dlg.show()
        dlg.destroy()
        
    def __calcsubitembounds__(self,item):
        "计算当前菜单项的子菜单对话框的大小和位置"
        if(item.isleaf()):
            raise "当前向没有子菜单"
        x = self.getabsx()+self.getwidth()

        index = self.__menuitems__.index(item)
        y = self.getabsy()+index
        
        height = len(item.getitems())+2
        if(height>curses.LINES-1):
            height = curses.LINES-1
        
        width = item.getsubmaxwidth()+4
        return (x,y,height,width)
            
            

