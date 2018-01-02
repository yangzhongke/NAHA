#coding:utf-8
import curses,ACursesIntern,re,logging
#author:杨中科

#curses定义的KEY_ENTER和KEY_TAB等键是unreliable的
KEY_ENTER = 10
KEY_TAB = 9
KEY_ESC = 27
KEY_SPACE = ord(' ')

#在HPUX中后退键为8，而非curses.KEY_BACKSPACE
KEY_BACKSPACE = 8


logger = None

#curs_set是否可用
curs_setEnabled=None

def getlogger():    
    return logger

def initapp(logfile="./naha.log"):
    global logger,curs_setEnabled
    #初始化日志记录器
    logger = logging.getLogger("")  #root logger
    logger.setLevel(logging.DEBUG)
    logging.raiseExceptions = 0
    hdlr = logging.FileHandler(logfile, "a")
    fmt = logging.Formatter("\n%(asctime)s %(levelname)-5s %(message)s", "%x %X")
    hdlr.setFormatter(fmt)
    logger.addHandler(hdlr)   

    curses.initscr()
    curses.cbreak()
    curses.noecho()     
    
    #判断终端是否支持curs_set方法
    curs_setEnabled = True
    try:
        curses.curs_set(False)  
        curses.curs_set(True)
    except:
        #因为某些终端不支持curs_set，所以需要截获此异常
        getlogger().warning("not support curs_set")  
        curs_setEnabled = False 

def endapp():
    curses.echo()
    curses.nocbreak()
    curses.endwin() 

#消息队列信息类
class InputProcMsg:
    def __init__(self,ch):
        #消息字符消息
        self.ch = ch
        #消息是否继续向下传
        self.__isconsumed__ = False
    def consume(self):
        '''消费此消息'''
        if(self.__isconsumed__):
            raise "此消息已经被消费了，不能重复消费！"
        self.__isconsumed__ = True
    def isconsumed(self):
        '''消息是否已经被消费'''
        return self.__isconsumed__;  

class FocusManager:
    '''焦点管理器'''
    def __init__(self,form):
        #拉平的控件列表，也是默认的控件焦点遍历顺序
        self.form = form
        #是否在代码中修改了tab顺序
        self.__orderchange__ = False
        components = self.getfocusablecomponents()
        if(len(components)>=1):
            self.curcomponent = components[0]
        else:
            self.curcomponent = None   
    def getfocusablecomponents(self):
        return ACursesIntern.getfocusablecomponents(self.form)             
    def getcurcomponent(self):
        return self.curcomponent
    def setcurcomponent(self,comp):
        '''设置当前焦点所在的组件'''
        self.curcomponent = comp
        self.__orderchange__ = True
    def grabcurrentfocus(self):
        "聚焦在当前控件上"
        if(self.curcomponent==None):
            return 
        self.curcomponent.__grabfocus__()
    def prevfocus(self):
        '''焦点前移'''
        self.gofocus(-1)
    def nextfocus(self):
        '''焦点后移'''
        self.gofocus(1)
    def gofocus(self,step):
        #向前走step步，当step为负数的时候则后退
        
        if(self.curcomponent==None):
            return    
        
        self.__orderchange__ = False
        
        #每次都实时去取可以接收焦点的控件，这样可以处理动态添加的控件
        components = self.getfocusablecomponents()
        
        #如果curcomponent不在components中，则说明此控件已经被remove掉
        if(not (self.curcomponent in components)):
            #恢复焦点到第一个控件
            if(len(components)<=0):
                self.setcurcomponent(components[0])
                self.grabcurrentfocus()                
            return             
        
        i = components.index(self.curcomponent)
        #如果__releasefocus__返回False的话则说明控件抓住了焦点
        #比如掩码编辑框验证失败禁止用户挪走光标，这样则不光标下移
        if(self.curcomponent.__releasefocus__()==False):
            return
        if(self.curcomponent.onfocuslost!=None):            
            self.curcomponent.onfocuslost() 
        
        if(self.__orderchange__==True):
            #如果__orderchange__变成了True，说明用户
            #用component.setfocus方法改变了焦点顺序
            #所以就不焦点下移了
            self.__orderchange__= False
            return                   
        #得到下一个控件，此处使用整除的效果实现控件焦点的循环
        comp = components[(i+step)%len(components)]
        self.setcurcomponent(comp)
        comp.__grabfocus__()  
            
class AComponent:
    '''组件基类'''
    def __init__(self,x,y,height,width,hasbox=False): 
        '''x组件左上角横坐标，y组件左上角纵坐标，height组件高度，width组件宽度，hasbox组件是否有边框
        这里已经处理了curses中横纵坐标与习惯不符的问题，开发人员可以按照正常的方式来使用坐标 
        '''
        self.__visible__ = True
        self.height = height
        self.width = width
        self.x = x
        self.y = y

        self.__hasbox__ = hasbox  

        self.win = None
        self.parent = None
        #焦点是否在此控件上
        self.ownfocus = False
        self.ongrabfocus = None
        self.onfocuslost = None              
        
    def getclientx(self):
        '''组件客户区（也就是除去边框）的左上角的x坐标'''
        if(self.hasbox()):
            return 2#真实开始点 X，如果画框，则为 1，否则为 0
        else:
            return 0
    def getclienty(self):
        '''组件客户区（也就是除去边框）的左上角的y坐标'''
        if(self.hasbox()):
            return 1#真实开始点 Y，如果画框，则为 1，否则为 0
        else:
            return 0
    def getabsx(self):
        '''左上角相对于屏幕的x'''
        return self.win.getbegyx()[1]
    def getabsy(self):
        '''左上角相对于屏幕的y'''
        return self.win.getbegyx()[0]
    def getclientwidth(self):
        '''客户区的宽度'''
        yx = self.win.getmaxyx()
        width = yx[1]
        if(self.hasbox()):
            return width - 4#真实宽度，(根据是否有边框而变化))
        else:
            return width
    def getclientheight(self):
        '''客户区的高度'''
        yx = self.win.getmaxyx()
        height = yx[0]
        if(self.hasbox()):
            return height - 2#真实高度，(根据是否有边框而变化)
        else:
            return height
    def getwidth(self):
        '''组件的宽度'''
        return self.width
    def getheight(self):
        '''组件的高度'''
        return self.height
    def getownerform(self):
        '''组件所在的窗口'''
        return ACursesIntern.getownerform(self)            
    def __textout__(self,x,y,text,attr=None):
        '''向客户区坐标为(x,y)的地方输出文字，无需在意是否有边框，可以通过attr参数指定文字的样式'''
        #在控件有边框的时候，curses没有正确处理坐标问题，所以此处封装了坐标的处理        
        if(self.hasbox()):
            x = x+2
            y = y+1
        if(attr==None):
            self.win.addstr(y,x,text)            
        else:
            self.win.addstr(y,x,text,attr)
    def hasbox(self):
        '''组件是否有边框'''
        return self.__hasbox__
    def isvisible(self):
        '''组件是否可视'''
        if(self.__visible__==False):
            return False
        return not self.__isparenthide__()
    def show(self):
        '''将组件显示出来'''
        self.__visible__ = True
        self.paint()  
    def getch(self):
        '''光标移动到组件上，并且得到用户的输入'''
        self.win.move(0,0)
        return self.win.getch()
    def destroy(self):
        '''销毁组件，回收组件的资源'''
        self.hide()
        self.win = None
    def hide(self):
        '''隐藏组件'''
        self.__visible__ = False
        self.paint()
        if(self.win!=None):
            #box方法不能很好的清除边框，会留下残余字符，所以使用border
            self.win.border(0,0,0,0,0,0,0,0)
            self.win.erase()    
            self.win.refresh()
    def __isparenthide__(self):
        '''父控件，包括间接父控件是否不可见'''
        p = self.parent
        while(p!=None):
            if(not p.isvisible()):
                return True
            if(p.win==None):
                return True
            p = p.parent
        return False
    def paint(self):
        '''重绘界面'''
        #和refresh方法不一样，是程序内部绘制用的
        if(not self.isvisible()):
            return
        if(self.parent==None):
            return
        self.__paint__()
        if(self.hasbox()):
            self.win.box()
                    
        if(self.win!=None):
            self.win.refresh()
    
    def __paint__(self):
        '''执行客户区的重绘，由paint来调用，子组件一般只要覆盖此方法即可，边框的处理在paint中完成'''
        #显示
        if(self.isvisible()):                      
            if(self.win==None):
                self.__createwin__()                
        #隐藏
        elif(self.win!=None):
            self.win.erase()    
    def __createwin__(self):
        '''创建组件的windowobject对象'''
        if(self.parent!=None and self.parent.hasbox()):                    
            #考虑容器（窗体）对控件坐标的影响
            y = self.y+1
            x = self.x+2
        else:
            y = self.y
            x = self.x
        self.win = self.parent.win.derwin(self.height,self.width,y,x) 
        #开启功能键
        #必须每个win都开启keypad才行，否则很多控制字符接收的都是两个
        self.win.keypad(True)
       
    def refresh(self):
        '''刷新界面，并不调用paint实现重绘，只是由curses来判断界面是否应该重绘,所以通讯量非常小'''
        if(self.win==None):
            return
        #调用touchwin可以恢复被其他窗口覆盖掉的内容
        self.win.touchwin()
        self.win.refresh()  
    def inputproc(self,msg):
        '''消息处理,子组件覆盖此方法来处理用户的按键消息'''
        pass
    def __grabfocus__(self):
        '''组件获得焦点'''
        self.ownfocus = True
        if(self.ongrabfocus!=None):
            self.ongrabfocus()
    def __releasefocus__(self):
        '''通知组件释放焦点，如果此方法返回True则可以释放焦点，如果返回False则表示组件拒绝释放焦点'''
        self.ownfocus = False
        return True
    def setfocus(self):
        '''组件获得焦点'''
        focusmgr = self.getownerform().getfocusmanager()
        focusmgr.setcurcomponent(self)  
        focusmgr.grabcurrentfocus()          
    def isfocusable(self):
        '''组件是否可以获得焦点，子组件可以覆盖此方法，比如标签组件就不能获得焦点'''
        return False
    def isownfocus(self):
        '''组件是否拥有焦点'''
        return self.ownfocus

#此控件目前只做为AForm的基类存在，暂时不能当成容器控件，应用开发人员不要使用
class AContainer(AComponent):
    '''容器组件的基类'''
    def __init__(self,x,y,height,width,hasbox=False):
        AComponent.__init__(self, x, y,height, width,hasbox)
        
        #子控件
        self.components = []
    def add(self,c):
        '''将子组件加入容器'''
        if(c in self.components):
            raise "控件已经被加入了，无需再次劳神加一次"
        self.components.append(c)
        c.parent = self
        c.paint()
    def addall(self,list):
        '''将多个子组件加入容器'''
        for c in list:
            self.add(c)
    def remove(self,c):
        '''将指定组件c从容器中移除'''
        self.components.remove(c)
        c.hide()
    def removeall(self):
        '''将所有子组件从容器中移除'''
        for i in range(0,len(list)):
            component = list.pop()
            component.hide()      
    def destroy(self):
        '''销毁组件以及所有子组件'''
        AComponent.destroy(self)
        for component in self.components:
            component.destroy()     
    def __paint__(self):
        AComponent.__paint__(self)
        for component in self.components:
            component.paint()
        
    def inputproc(self,msg):
        pass
    def refresh(self):
        #调用touchwin可以恢复被其他窗口覆盖掉的内容  
        #注意要先刷新子控件再刷新父容器 
        
        #隐藏光标，因为在牡丹终端上，当refresh某个win的时候
        #光标会在win的左上角停留一瞬间
        if(curs_setEnabled):
            curses.curs_set(False)            
                     
        for component in self.components:
            component.refresh()
        AComponent.refresh(self)
        #光标重新显示
        if(curs_setEnabled):
            curses.curs_set(True)
        
class AForm(AContainer):
    '''窗口基类'''
    #窗口不能指定父窗口
    def __init__(self,x,y,height,width,hasbox=True):
        AContainer.__init__(self, x, y, height, width,hasbox)
        self.__visible__ = False
        
        #窗体自身的消息列表
        self.__keyeventmap__={}
        self.win = curses.newwin(self.height,self.width,self.y,self.x)
        self.win.keypad(True)
        if(self.hasbox()):
            self.win.box()        
        self.focusmanager = None
        self.afterhide = None
    def getfocusmanager(self):
        '''得到窗口的焦点管理器'''
        if(self.focusmanager == None):
            self.focusmanager = FocusManager(self)
        return self.focusmanager
    def registerkeyevent(self,key,func):
        '''注册快捷键，当key被按下的时候func方法会被调用，key支持f1、f2、pageup等这样的明文形式'''
        ch = ACursesIntern.parseKey(key)
        self.__keyeventmap__[ch] = func 
    def show(self):    
        #考虑到实际情况为了简化，此处假定窗口中至少存在一个控件
        if(len(self.components)<=0):
            raise "窗口中必须存在至少一个控件"   
  
        self.__visible__ = True
        for component in self.components:
            component.paint()
        
        #焦点第一次落在第一个控件的时候还没有刷新所以首先刷新一下
        self.refresh()   
   
        #使得焦点落在当前控件上
        self.getfocusmanager().grabcurrentfocus()
        
        while(self.__visible__==True):            
            #每次都要刷新整个窗体，因为有可能有其他操作对窗体界面有破坏
            self.refresh()
            
            curcomponent = self.getfocusmanager().getcurcomponent()
                        
            #如果当前没有焦点控件，则设定第一个控件为当前控件
            #为了简化，系统假定必须存在焦点控件
            if(curcomponent==None):
                curcomponent = self.components[0]
            
            #这种方法太巧妙了，哈哈，刚刚悟出来QCurses为什么在控件基类中
            #增加一个getch方法了，这样就可以将焦点巧妙的放到控件上了
            #这样避免了self.win.getch()的焦点问题
            ch = curcomponent.getch()             
            msg = InputProcMsg(ch)              
            #首先将消息发给焦点控件(包括Tab键)
            curcomponent.inputproc(msg)
            
            #如果消息被消费则开始下一次循环
            if(msg.isconsumed()):
                continue
            
            self.inputproc(msg)  
            if(msg.isconsumed()):
                continue
              
            if(KEY_ENTER==ch or curses.KEY_NEXT==ch or
               KEY_TAB==ch or curses.KEY_RIGHT == ch or curses.KEY_DOWN==ch):                
                #如果是焦点跳转键，则执行焦点转移
                self.getfocusmanager().nextfocus()
            elif(curses.KEY_LEFT == ch or curses.KEY_UP==ch):                
                #如果是焦点跳转键，则执行焦点转移
                self.getfocusmanager().prevfocus()
            else:
                #否则将消息首先发给自身，然后发给其他控件
                #因为ch为int类型的，而__keyeventmap__的key也是int类型
                func = self.__keyeventmap__.get(ch)
                if(func!=None):
                    func()
                    #如果本身已经接收了这个消息，则不再进行后续处理
                    continue
                #消息轮询各个控件
                self.__sendmsgexcept__(msg, curcomponent) 
        
        #窗口关闭以后清除窗口
        self.hide()        
    def hide(self):
        AContainer.hide(self)
        if(self.afterhide!=None):
            self.afterhide()
    def __sendmsgexcept__(self,msg,curcomponent): 
        #向除了curcomponent之外的所有子控件轮训发送消息
        for component in self.components: 
            #不处理焦点控件
            if(component==curcomponent):
                continue               
            component.inputproc(msg)
            if(msg.isconsumed()):
                #如果消息被停止循环，则结束
                return              
    def paint(self):
        pass

class AButton(AComponent):
    '''按钮组件'''
    def __init__(self,x,y,width,text=""):
        '''按钮必须只能占一行，text指定按钮的文字'''
        AComponent.__init__(self, x, y, 1, width)
        self.onclick = None
        self.__text__ = text
        self.__hotkey__ = None        
    def gettext(self):
        '''得到按钮文字'''
        return self.__text__
    def settext(self,text):
        '''设定按钮文字'''
        self.__text__ = text
        self.paint()
    def sethotkey(self,hotkey):
        '''设定按钮的热键，当热键按下以后按钮达到点击的效果'''
        self.__hotkey__ = hotkey    
    def __paint__(self):
        AComponent.__paint__(self)        
        vwidth = self.getclientwidth()-1-2
        s = ACursesIntern.ljustandcut(self.__text__, vwidth) 
        self.__textout__(0,0,"["+s+"]")
    def isfocusable(self):
        return True
    def inputproc(self,msg):
        ch = msg.ch
        
        if(KEY_ENTER==ch):
            self.__click__()
            msg.consume()       
        elif(self.__hotkey__!=None and ord(self.__hotkey__)==ch):
            self.__click__()
            msg.consume()

    #相应点击事件            
    def __click__(self):
        if(self.onclick!=None):
            self.onclick()
    def __grabfocus__(self):
        AComponent.__grabfocus__(self)
        self.win.attron(ACursesIntern.highlight_attr)
        self.paint()
    def __releasefocus__(self):
        AComponent.__releasefocus__(self)
        self.win.attroff(ACursesIntern.highlight_attr)
        self.paint()
        

class ASingleLineField(AComponent):
    '''单行输入框基类,高度必须为1'''
    def __init__(self,x,y,width):
        #单行控件
        AComponent.__init__(self, x, y, 1, width)
        self.__text__ = "" 
    def gettext(self):
        '''得到用户输入的文字'''
        return self.__text__
    def isfocusable(self):
        return True
    def inputproc(self,msg):
        if(not self.ownfocus):
            return
        ch = msg.ch
        if(KEY_TAB==ch or curses.KEY_NEXT==ch or KEY_ENTER==ch
           or curses.KEY_LEFT==ch or curses.KEY_RIGHT==ch 
           or curses.KEY_UP==ch or curses.KEY_DOWN==ch):
            return
        #如果存在于功能键列表中，则不消费
        if(ch in ACursesIntern.funcKeyDict.values()):
            return
        #消费掉，即使字符不被__acceptch__，也消费，否则会造成混乱
        msg.consume()
        #如果不接受输入的字符，则忽略
        if(self.__acceptch__(ch)==False):
            curses.beep()
        else:
            self.__enterinput__(ch)
    def __enterinput__(self,ch):
        '''用户处理用户键入的字符，这里已经将非法字符、Tab、光标键等字符过滤了'''
        pass
    def __acceptch__(self,ch):
        '''是否接受输入的字符，掩码框、整数框等可以覆盖此方法来拒绝接受非法字符'''
        invalidchar = [curses.KEY_HOME,curses.KEY_F1,curses.KEY_F2,
                       curses.KEY_F3,curses.KEY_F4,curses.KEY_F5,curses.KEY_F6,
                       curses.KEY_F7,curses.KEY_F8,curses.KEY_F9,curses.KEY_F10,curses.KEY_DC,
                       curses.KEY_DC,curses.KEY_IC,curses.KEY_PPAGE,curses.KEY_NPAGE,
                       curses.KEY_END]        
        return not (ch in invalidchar)

#当AEdit数据校验失败的时候的策略
#允许失去焦点并且清空
FOCUSLOSTANDCLEAR = "ALLOWFOCUSCHANGE"
#不允许失去焦点并且清空
GRABFOCUSANDCLEAR = "GRABFOCUSANDCLEAR"
#允许失去焦点并且保持输入
GRABFOCUSANDNOCLEAR = "GRABFOCSTANDNOCLEAR"

class AEdit(ASingleLineField):
    '''普通编辑框'''
    def __init__(self,x,y,width,text=""):
        #单行控件
        ASingleLineField.__init__(self, x, y, width)        
        self.__validfailpolicy = FOCUSLOSTANDCLEAR
        #用户自定义校验规则
        #自从焦点进入这段时间来，是否有合法的用户字符录入
        self.__hasinput__=False
        self.onvalid=None
        self.ontextchange=None
        self.settext(text)        
    def settext(self,text,fireevent=True):
        '''设定编辑框文字'''
        #fireevent表示是否触发ontextchange事件
        if(text==None):
            self.__text__ = ""
        else:
            self.__text__ = text  
        if(fireevent and self.ontextchange!=None):
            self.ontextchange()       
        self.paint()                  
        
    def setvalidfailpolicy(self,policy):
        '''设定当输入非法字符的处理策略，可选值FOCUSLOSTANDCLEAR、GRABFOCUSANDCLEAR、GRABFOCUSANDNOCLEAR'''
        self.__validfailpolicy = policy
    def __paint__(self):
        ASingleLineField.__paint__(self)        
        #正确的能够显示的长度
        propLen = self.getclientwidth()-1-2        
        t = ACursesIntern.ljustandcut(self.__text__, propLen)
        self.__textout__(0,0,"["+t+"]")
    def __grabfocus__(self):
        ASingleLineField.__grabfocus__(self)
        self.__hasinput__=False
    def __releasefocus__(self):        
        validateresult = self.__isvaliddata__()
        if(self.onvalid!=None  and validateresult==True):
            #如果连控件的基本校验都没通过，则不调用onvalid调用客户化校验
            #这样onvalid中就不用进行基本的校验了            
            validateresult = validateresult and self.onvalid()           
     
        if(validateresult==True):
            if(self.__hasinput__ and self.ontextchange!=None):
                self.ontextchange() 
            return ASingleLineField.__releasefocus__(self)
        
        if(self.__validfailpolicy==FOCUSLOSTANDCLEAR):
            self.settext("")
            allowlostfocus = True
        elif(self.__validfailpolicy==GRABFOCUSANDCLEAR):
            self.settext("")
            allowlostfocus = False
        elif(self.__validfailpolicy==GRABFOCUSANDNOCLEAR):
            #只有在光标离开的时候才触发ontextchange事件
            if(self.__hasinput__ and self.ontextchange!=None):
                self.ontextchange()
            allowlostfocus = False
        else:
            raise "__validfailpolicy error"

        if(self.__hasinput__ and self.ontextchange!=None):
            self.ontextchange() 
        if(allowlostfocus):
            ASingleLineField.__releasefocus__(self)    
        return allowlostfocus
        
    def __isvaliddata__(self):
        return True
    def __enterinput__(self,ch):
        text = self.__text__
        #如果按下回退键则删除
        if(ch==curses.KEY_BACKSPACE or ch==KEY_BACKSPACE):
            if(len(text)<=0):
                return
            self.settext(ACursesIntern.dellaststr(text),False)         
        else:        
            #键入其他键，则将键入的字符添加到文本框中
            newtext = text + str(chr(ch))
            self.settext(newtext,False)
        self.__hasinput__=True
    def getch(self):
        curx = len(self.gettext())+1
        if(curx>=self.getclientwidth()-2):
            curx=self.getclientwidth()-3
        #将光标移动到最后一个字符的位置，如果超长则移动到组件的最右位置
        self.win.move(0,curx)
        return self.win.getch()
            
class APasswordField(ASingleLineField):
    '''
    密码输入框，键入的时候不像普通的密码框一样回显“*”，
    这样可以防止恶意者得知密码的长度，从而减少暴力破解的时间
    '''
    def __paint__(self):
        ASingleLineField.__paint__(self)
      
        #正确的能够显示的长度
        propLen = self.getclientwidth()-1
        self.__textout__(0,0," "*propLen)
    def __grabfocus__(self):
        ASingleLineField.__grabfocus__(self)
        
        #每次聚焦都清空密码
        self.__text__ = ""
    def __enterinput__(self,ch):
        self.__text__ = self.__text__ + str(chr(ch))    

class AFormatEdit(AEdit):
    '''格式化文本框,formatre指定格式，formatre为正则表达式'''
    def __init__(self,x,y,width,formatre=r".*"):
        AEdit.__init__(self, x, y, width)
        self.pattern = re.compile(formatre)
    def __isvaliddata__(self):
        if(AEdit.__isvaliddata__(self)==False):
            return False
        return (self.pattern.match(self.gettext())!=None)

class AMaskEdit(AFormatEdit):
    '''
    简化版的格式化文本框，供不熟悉正则表达式的开发人员使用
    掩码字符串语法:
    # 任意数字字符  ' 转义符  U 大写字母
    L 小写字母  A 数字或者字符（包含大小写）
    ? 任意字母  * 任意字符
    _ 此标识符前的元字符可又有无（也就是最多有一个）
    '''
    def __init__(self,x,y,width,mask):
        #为了简化实现，目前使用简单的mask翻译为正则表达式的方式
        #以后如果有严重缺陷bug或者性能问题，
        #则再参考java的MaskFormatter实现
        self.__mask__ = mask
        regexpr = ACursesIntern.masktore(mask)
        AFormatEdit.__init__(self, x, y, width,regexpr)
    def getmask(self):
        return self.__mask__

class AIntegerEdit(AFormatEdit):
    '''整数框'''
    def __init__(self,x,y,width):
        AFormatEdit.__init__(self, x, y, width, r"-?\d+$")
    def __acceptch__(self,ch):
        if(AFormatEdit.__acceptch__(self, ch)==False):
            return False
        if(ch>=ord('0') and ch<=('9')):
            return True
        if(ch==ord('-') or ch==curses.KEY_BACKSPACE or ch==KEY_BACKSPACE):
            return True
        return False
       

class ADecimalEdit(AFormatEdit):
    '''数字框，当焦点在的时候右对齐，焦点失去以后左对齐'''
    def __init__(self,x,y,width):
        AFormatEdit.__init__(self, x, y, width, r"-{0,1}\d*\.{0,1}\d*$")
    def __acceptch__(self,ch):
        if(AFormatEdit.__acceptch__(self, ch)==False):
            return False
        if(ch>=ord('0') and ch<=('9')):
            return True
        if(ch==ord('-') or ch==curses.KEY_BACKSPACE
           or ch ==KEY_BACKSPACE or ch==ord('.')):
            return True    
        return False
    def __paint__(self):
        AFormatEdit.__paint__(self) 
        #当焦点不在的时候右对齐，并且添加千分符 
        if(not self.isownfocus()):      
            #正确的能够显示的长度
            propLen = self.getclientwidth()-1-2        
            t = ACursesIntern.formatdecimalstr(self.__text__)
            t = t.rjust(propLen)
            t = t[0:propLen]
            self.__textout__(0,0,"["+t+"]")
    def __releasefocus__(self):
        ret = AFormatEdit.__releasefocus__(self)
        self.paint()
        return ret
    def __grabfocus__(self):
        AFormatEdit.__grabfocus__(self)
        self.paint()       

class AHLine(AComponent):
    '''水平线'''
    def __init__(self,startx,endx,y):
        '''startx起始的横坐标，endx结束的横坐标，y纵坐标'''
        AComponent.__init__(self, startx, y, 1, endx-startx)
    def __paint__(self):
        AComponent.__paint__(self)        
        self.win.hline(0,0,curses.ACS_HLINE,self.width)

class AVLine(AComponent):
    '''垂直线'''
    def __init__(self,x,starty,endy):
        '''x横坐标，starty起始的纵坐标，endy结束的纵坐标'''
        AComponent.__init__(self, x, starty, endy-starty, 1)
    def __paint__(self):
        AComponent.__paint__(self)        
        self.win.vline(0,0,curses.ACS_VLINE,self.height)

class ARectAngle(AComponent):
    '''方框'''
    def __init__(self,x,y,height,width):
        AComponent.__init__(self, x, y,height, width,hasbox=True)

class ALabel(AComponent):
    '''标签'''
    def __init__(self,x,y,width,text=""):
        #单行控件
        AComponent.__init__(self, x, y, 1, width)
        self.__text__ = text
        self.labelfor = None
        self.__hotkey__ = None
    def setlabelfor(self,labelfor):
        '''设定标签的宿主组件，当标签的热键被按下的时候宿主组件将得到焦点'''
        self.labelfor = labelfor    
    def settext(self,text):
        '''设定标签组件'''
        self.__text__ = text
        self.paint()
    def sethotkey(self,hotkey):
        '''设定热键'''
        self.__hotkey__ = hotkey
    def __paint__(self):
        AComponent.__paint__(self)        
        vwidth = self.getclientwidth()-1
        s = ACursesIntern.ljustandcut(self.__text__, vwidth)     
        self.__textout__(0,0,s)
    def gettext(self):
        return self.__text__
    def inputproc(self,msg):
        if(self.__hotkey__==None):
            return
        
        ch = msg.ch
        #因为ch可能为F1等功能键，而他们是超越了chr的范围了，
        #所以不能使用self.__hotkey__==str(chr(ch))
        if(ord(self.__hotkey__)==ch):
            if(self.labelfor!=None):
                self.labelfor.setfocus()
                #如果热键被接受，onclick事件触发了，则消息不下传
                msg.consume()

class AMultiLineLabel(AComponent):
    '''多行标签'''
    def __init__(self,x,y,height,width):
        #单行控件
        AComponent.__init__(self, x, y, height, width)
        self.text = ""
    def settext(self,text):
        '''设定标签文字'''
        self.text = text
        self.paint()
    def __paint__(self):
        AComponent.__paint__(self)  
        '''将文字拆行处理'''
        list = ACursesIntern.splitstr(self.text, self.getclientwidth())
        for i in range(0,len(list)):
            if(i<self.getclientheight()):
                self.__textout__(0,i,list[i])
    def gettext(self):
        return self.text

class ACheckBox(AComponent): 
    '''复选框'''
    def __init__(self,x,y,width,text=""):
        #单行控件
        AComponent.__init__(self, x, y,  1, width)
        self.onclick = None
        self.__text__ = text
        self.checked = False
    def gettext(self):
        '''得到文字'''
        return self.__text__
    def ischecked(self):
        '''组件是否被选中'''
        return self.checked
    def __paint__(self):
        AComponent.__paint__(self)
        if(self.checked):
            t = "√"+self.__text__
        else:
            t = "[]"+self.__text__
        
        vwidth = self.getclientwidth()-1-2
        s = ACursesIntern.ljustandcut(t, vwidth)
        
        self.__textout__(0,0,s)
    def settext(self,text):
        '''组件标签文字'''
        self.__text__ = text
        self.paint()
    def setchecked(self,checked):
        '''设定组件的选中状态'''
        self.checked = checked
        self.paint()
    def inputproc(self,msg):
        ch = msg.ch
        if(self.ownfocus and ord(' ')==ch):
            self.__click__()
            msg.consume()

    def __click__(self):
        self.setchecked(not self.ischecked())
        if(self.onclick!=None):
            self.onclick()
    def isfocusable(self):
        return True

class ARadioButton(AComponent):
    '''单选按钮'''
    def __init__(self,x,y,width,text="",value=None):
        '''value为任意对象，这样每个按钮都可以关联一个对象，方便使用'''
        AComponent.__init__(self, x, y, 1, width)
        self.onclick = None
        self.selected = False
        self.__text__ = text
        self.__group__=None
        self.value = value
    def gettext(self):
        '''按钮文字'''
        return self.__text__
    def isselected(self):
        '''按钮是否被选中'''
        return self.selected
    def getvalue(self):
        '''按钮关联的值'''
        return self.value
    def __paint__(self):
        AComponent.__paint__(self)
        if(self.selected):
            t = "[x]"+self.__text__
        else:
            t = "[ ]"+self.__text__
        
        vwidth = self.getclientwidth()-1-2
        s = ACursesIntern.ljustandcut(t, vwidth)        
        self.__textout__(0,0,s)
    def settext(self,text):
        '''设定按钮文字'''
        self.__text__ = text
        self.paint()
    def setselected(self,selected):
        '''设定选中状态'''
        self.selected = selected
        self.paint()
    def setgroup(self,group):
        '''设定所属的按钮组，group必须为ARadioGroup类型'''
        self.__group__ = group
    def inputproc(self,msg):
        ch = msg.ch
        if(self.ownfocus and ord(' ')==ch):
            self.__click__()
            msg.consume()
    def isfocusable(self):
        return True

    def __click__(self):
        #通知按钮组选中自己
        self.__group__.selectButton(self)
        
        if(self.onclick!=None):
            self.onclick()

class ARadioGroup:
    '''单选按钮组，按钮组没有设计成一个容器控件，这样做能够提高灵活性，比如各个按钮可以不放在一起'''
    def __init__(self,buttons=[]):
        #buttons为所有的按钮
        self.buttons=[]
        for btn in buttons:
            self.add(btn)
        self.onselectchange=None
    def add(self,btn):
        '''将单选按钮添加到按钮组中'''
        self.buttons.append(btn)
        btn.setgroup(self)
    def selectButton(self,btn):
        '''选中某按钮'''        
        if not (btn in self.buttons):
            raise "这个按钮不属俺负责"
        if(btn.isselected()):
            return
        for b in self.buttons:
            if(b!=btn):
                b.setselected(False)
            else:
                b.setselected(True)
        if(self.onselectchange!=None):
            self.onselectchange(btn)
    def getselected(self):
        '''得到选中的按钮，如果没有任何按钮选中，则返回None'''
        for btn in self.buttons:
            if(btn.isselected()):
                return btn
        return None
    def getselectedvalue(self):
        '''得到选中的按钮对应的对象'''
        btn = self.getselected()
        if(btn!=None):
            return btn.getvalue()
   
class AListBox(AComponent):
    '''列表框'''
    def __init__(self,x, y, height, width,items=[]):
        '''items表示列表框中要显示的项'''
        AComponent.__init__(self, x, y, height, width)
        self.items = items        
        self.selectedindex = -1
        self.onitemclick = None
        self.onselectchange = None
        
        self.setitems(items)
    def hasbox(self):
        return True
    def isfocusable(self):
        return True
    def __paint__(self):
        AComponent.__paint__(self)
        self.win.erase()
        w = self.getclientwidth()
        startindex = self.topindex
        endindex = self.topindex+self.getclientheight()
        for i in range(startindex,endindex):
            if(i==self.selectedindex):
                #对选中项高亮显示
                attr = ACursesIntern.highlight_attr
            else:
                attr = curses.A_NORMAL            
            
            cury = i-self.topindex
            
            if(i<len(self.items)):
                s = str(self.items[i]) 
                text = ACursesIntern.ljustandcut(s,w)    
                self.__textout__(0, cury,text,attr)               
                
    def inputproc(self,msg):
        ch = msg.ch
        #向上键焦点上移
        if(ch==curses.KEY_UP):
            si = self.getselectedindex()
            if(si>0):
                self.setselectedindex(si-1)
            self.showselectedpage()
            msg.consume()
        #向下键焦点下移
        elif(ch==curses.KEY_DOWN):
            si = self.getselectedindex()
            if(si<len(self.items)-1):
                self.setselectedindex(si+1)
            self.showselectedpage()
            msg.consume()
        #按下回车键触发“项被点击onitemclick”事件
        elif(ch==KEY_ENTER):
            msg.consume()
            if(self.onitemclick!=None):
                self.onitemclick(self.getselectedindex())
    def __pageup__(self,pagecount=1):
        '''上翻页，pagecount翻的页数'''
        #可视区域上方的条数
        i = self.topindex
        if(i<=0):
            return        
        self.topindex = self.topindex- self.getclientheight()*pagecount
        self.paint()
    def __pagedown__(self,pagecount=1):
        '''下翻页，pagecount翻的页数'''
        #可视区域下方的条数
        i = len(self.items)-self.topindex-self.getclientheight()*pagecount
        if(i<=0):
            return
        
        self.topindex = self.topindex + self.getclientheight()*pagecount 
        self.paint() 
    def showselectedpage(self):  
        '''将选中的项所在的页显示出来''' 
        si = self.getselectedindex()
        #如果已经在可视范围内则返回
        if(si>=self.topindex and si<self.topindex+self.getclientheight()):
            return
        if(si>=self.topindex+self.getclientheight()):
            pagecount = (si-self.topindex)/self.getclientheight()
            self.__pagedown__(pagecount)
            return
        if(si<self.topindex):
            pagecount = (self.topindex-si)/self.getclientheight()+1
            self.__pageup__(pagecount)
            return
        raise "不可能状态"
    
    def setselectedindex(self,index):
        '''设定选中的项的索引号'''
        previndex = self.getselectedindex()
        self.selectedindex = index
        self.paint()
        if(self.onselectchange!=None):
            self.onselectchange(previndex,index)
    def getselectedindex(self):
        '''得到选中的项的索引号'''
        return self.selectedindex
    def getitem(self,index):
        '''得到第index项'''
        return self.items[index]
    def getitems(self):
        '''得到所有的项'''
        return self.items
    def setitems(self,items):
        '''设定列表的项'''
        if(len(items)>0):
            #显示区域内的第一行的索引
            self.topindex=0
            self.setselectedindex(0)
        else:
            self.topindex=0
            self.setselectedindex(-1)
        self.paint()
    def setselecteditem(self,item):
        '''设定选中的项'''
        if(not (item in self.items)):
            return
        i = self.items.index(item)
        self.setselectedindex(i)
    def getselecteditem(self):
        '''得到选中项'''
        i = self.getselectedindex()
        if(i>=0):
            return self.items[i]
        else:
            return None    
    def additem(self,item):
        '''向列表中添加单项'''
        self.items.append(item) 
        self.paint()
    def additems(self,items):
        '''向列表中添加多项'''
        self.items = self.items + items
        self.paint()
    def insertitem(self,index,item):
        '''向列表的第index位置后添加项item'''
        self.items.insert(index,item)
        self.paint()
    def removeitem(self,item):
        '''将项item从列表中移除'''
        self.items.remove(item)
        self.paint()
    def removeallitem(self):
        '''移除所有项'''
        ACursesIntern.clearlist(self.items)
        self.paint()

class AComboBox(AComponent):
    '''普通的下拉列表框'''
    def __init__(self,x,y,width,items=[],showcount=3):
        #showcount:下拉显示的条数
        AComponent.__init__(self, x, y, 1, width)
        self.setitems(items)
        self.__selectedindex__ = -1
        self.setshowcount(showcount)  
        #弹出窗格的宽度，默认等于控件宽度
        self.__panelwidth__ = width
    def isfocusable(self):
        return True     
    def setpanelwidth(self,w):
        '''设定下拉面板的宽度，默认为列表框的宽度'''
        self.__panelwidth__ = w
    def __createwin__(self):
        AComponent.__createwin__(self)
        self.__initdialog__() 
    def __initdialog__(self):
        '''创建显示下拉内容的对话框'''
        self.dlg = AForm(self.getabsx(),self.getabsy()+1
                    ,self.__showcount__+2,self.__panelwidth__,hasbox=False)
    
        self.listbox = AListBox(0,0,self.__showcount__+2
                                ,self.dlg.getclientwidth(),self.__items__)
        self.listbox.onitemclick = self.__itemclick__
        self.dlg.add(self.listbox)
    def destroy(self):
        AComponent.destroy(self)
        self.dlg.destroy()
    def __itemclick__(self,index):
        #隐藏对话框
        self.dlg.hide()
        
    def __paint__(self):
        AComponent.__paint__(self)       
        
        obj = self.getselecteditem()
        if(obj==None):
            text = ""
        else:
            text = str(obj)
        
        vwidth = self.getclientwidth()-1-2
        s = ACursesIntern.ljustandcut(text, vwidth)
        
        self.__textout__(0, 0, "<"+s+">")    
    def inputproc(self,msg):
        ch = msg.ch
        if(ch==curses.KEY_DOWN):
            msg.consume()
            self.listbox.setselectedindex(self.__selectedindex__)
            self.dlg.show()
            self.__selectedindex__ = self.listbox.getselectedindex()
            self.paint()
            
    def getselectedindex(self):
        '''得到选中项的索引'''
        return self.__selectedindex__
    def getitem(self,index):
        '''得到索引为index的项'''
        return self.__items__[index]
    def getselecteditem(self):
        '''得到选中项'''
        i = self.__selectedindex__
        if(i<0):
            return None
        else:
            return self.__items__[i]
    def setitems(self,items):
        '''设定列表项'''
        self.__items__ = items
        self.paint()
    def setselecteditem(self,item):
        '''设定选中项'''
        if(not(item in self.__items__)):
            return
        self.__selectedindex__ = self.__items__.index(item)   
        self.paint()
    def setselectedindex(self,index):
        '''设定索引号为index项为选中项'''
        self.__selectedindex__ = index
    def setshowcount(self,showcount):
        '''设定下拉框中显示的项的数目，默认为3项'''
        self.__showcount__ = showcount;
    def additem(self,item):
        '''添加项'''
        self.__items__.append(item)
        self.paint()
    def additems(self,items):
        '''添加多项'''
        self.__items__ = self.__items__ + items
        self.paint()
    def insertitem(self,index,item):
        '''向index位置中插入项item'''
        self.__items__.insert(index,item)
        self.paint()
    def removeitem(self,item):
        '''将项item从列表中移除'''
        sself.__items__.remove(item)
        self.paint()

class ACellWrapper:
    '''表格内容包装器，用来包装值与显示不一致的情况'''
    def __init__(self,value,display):
        self.__value__ = value
        self.__display__ = display
    def getvalue(self):
        '''真实值'''
        return self.__value__
    def getdisplay(self):
        '''显示值'''
        return self.__display__
    def __str__(self):
        return self.getdisplay()
        
class ATable(AComponent):
    '''表格'''
    def __init__(self,x,y,height,width,header=[]):
        '''header是标题定义,每个元素是一个元组，元组的第一个元素是标题，
        第二个是宽度'''
        AComponent.__init__(self, x, y,height, width)
        self.__header__=header
        if(len(header)>0):
            #可显示区域最左端的列索引，指的是表格的列，而不是坐标列
            self.leftcolindex = 0
        else:
            self.leftcolindex = -1
        
        #焦点下移的键
        self.__nextkeys__ = [KEY_ENTER,'>','.']
        #选中当前行的键
        self.__clickkeys__ = [KEY_SPACE]
        
        self.onitemclick = None
        self.onselectchange = None       
       
        #可显示区域最顶端的行索引
        self.toprowindex = -1
        self.selectedrowindex = -1
        self.setrowitems([])
    def setnextkeys(self,keys):
        '''表示焦点下移的键,默认为>和.'''
        self.__nextkeys__ = keys
    def setclickkeys(self,keys):
        '''触发项被点击的键,默认为空格'''
        self.__clickkeys__ = keys
    def hasbox(self):
        return True
    def isfocusable(self):
        return True
    def __getvisibleitemcount__(self):
        #与listbox不同，由于有表头，所以要另外再减2
        return self.getclientheight()-2
    def __paint__(self):
        AComponent.__paint__(self)
        
        self.win.erase()
        
        if(self.leftcolindex<0):
            return
        
        #画表头
        title = ""
        for i in range(self.leftcolindex,len(self.__header__)):
            headerdef = self.__header__[i]
            htitle = headerdef[0]
            hwidth = headerdef[1]            
            #如果宽度方向已经无法再画标题，则停止画
            if(len(title)+hwidth>self.getclientwidth()):
                break
            htitle = ACursesIntern.ljustandcut(htitle, hwidth)
            title = title+htitle+"|"
        self.__textout__(0, 0, title)
        
        #画线
        self.win.hline(2,0,curses.ACS_HLINE,self.width)
        
        if(self.toprowindex<0):
            return
        y = 2
        for r in range(self.toprowindex,self.toprowindex+self.__getvisibleitemcount__()):
            if(r>=len(self.rowitems)):
                return            
            if(r==self.selectedrowindex):
                #对选中项高亮显示
                attr = ACursesIntern.highlight_attr
            else:
                attr = curses.A_NORMAL            
            rowstr = ""
            rowitem = self.rowitems[r]
            for c in range(self.leftcolindex,len(self.__header__)):
                headerdef = self.__header__[c]
                hwidth = headerdef[1]
                #如果宽度方向已经无法再画，则停止画
                if(len(rowstr)+hwidth>self.getclientwidth()):
                    break
                cellvalue = ACursesIntern.ljustandcut(str(rowitem[c]), hwidth)
                rowstr = rowstr + cellvalue+"|"        
            
            self.__textout__(0, y, rowstr, attr)
            y = y+1
    def __pageup__(self,pagecount=1):
        '''上翻pagecount页'''
        i = self.toprowindex
        if(i<=0):
            return        
        self.toprowindex = self.toprowindex- self.__getvisibleitemcount__()*pagecount
        self.paint()
    def __pagedown__(self,pagecount=1):
        '''下翻pagecount页'''
        i = len(self.rowitems)-self.toprowindex-self.__getvisibleitemcount__()*pagecount
        if(i<=0):
            return        
        self.toprowindex = self.toprowindex + self.__getvisibleitemcount__()*pagecount 
        self.paint() 
    def __pageleft__(self):
        '''左翻页'''
        if(self.leftcolindex<=0):
            return 
        self.leftcolindex = self.leftcolindex -1
        self.paint()    
    def __pageright__(self):
        '''右翻页'''
        if(self.leftcolindex+1>=len(self.__header__)):
            return
        self.leftcolindex = self.leftcolindex + 1
        self.paint()        
    def inputproc(self,msg):
        ch = msg.ch
        if(ch in self.__nextkeys__):
            self.getownerform().getfocusmanager().nextfocus()
            msg.consume()
        elif(ch==ord('<') or ch==ord(',')):
            self.getownerform().getfocusmanager().prevfocus()
            msg.consume()
        elif(ch==curses.KEY_UP):
            si = self.getselectedrowindex()
            if(si>0):
                self.setselectedrowindex(si-1)
            self.showselectedpage()
            msg.consume()
        elif(ch==curses.KEY_DOWN):
            si = self.getselectedrowindex()
            if(si<len(self.rowitems)-1):
                self.setselectedrowindex(si+1)
            self.showselectedpage()
            msg.consume()
        elif(ch==curses.KEY_LEFT):
            self.__pageleft__()
            msg.consume()
        elif(ch==curses.KEY_RIGHT):
            self.__pageright__()            
            msg.consume()
        elif(ch in self.__clickkeys__):
            msg.consume()
            if(self.onitemclick!=None):
                self.onitemclick(self.getselectedrowindex())
    def addrow(self,row):
        '''添加行'''
        self.rowitems.append(row)
        self.__rowcountchange__()
        self.paint()
    def addrows(self,rows):
        '''添加多行'''
        self.rowitems = self.rowitems+rows
        self.__rowcountchange__()
        self.paint()
    def removerow(self,index):
        '''移除第index行'''
        self.rowitems.remove(self.rowitems[index])
        self.__rowcountchange__()
        self.paint()
    def removeallrow(self):
        '''移除所有行'''
        ACursesIntern.clearlist(self.rowitems)
        self.__rowcountchange__()
        self.paint()
    def __rowcountchange__(self):        
        if(len(self.rowitems)>0):
            self.toprowindex = 0            
        else:
            self.toprowindex = -1
            self.selectedrowindex = -1
    def getrowitems(self):
        '''得到所有行'''
        return self.rowitems
    def setrowitems(self,rowitems):
        '''设定所有行'''
        self.rowitems = rowitems
        self.__rowcountchange__()
        self.paint()
    def getrow(self,index):
        '''得到第index行'''
        return self.rowitems[index]
    def getcellvalue(self,rowindex,colindex):
        '''得到第rowindex行第colindex列的值'''
        r = self.getrow(rowindex)
        return r[colindex]
    def getselectedrowindex(self):
        '''得到选中行的索引'''
        return self.selectedrowindex
    def setselectedrowindex(self,rowindex):
        '''设置选中行的索引'''
        prevrowindex = self.getselectedrowindex()
        self.selectedrowindex = rowindex
        self.paint()
        if(self.onselectchange!=None):
            self.onselectchange(prevrowindex,rowindex)
    def showselectedpage(self):  
        '''将选中的项所在的页显示出来''' 
        sri = self.getselectedrowindex()
        #如果已经在可视范围内则返回
        if(sri>=self.toprowindex and sri<self.toprowindex+self.__getvisibleitemcount__()):
            return
        if(sri>=self.toprowindex+self.__getvisibleitemcount__()):
            pagecount = (sri-self.toprowindex)/self.__getvisibleitemcount__()
            self.__pagedown__(pagecount)
            return
        if(sri<self.toprowindex):            
            pagecount = (self.toprowindex-sri)/self.__getvisibleitemcount__()+1
            self.__pageup__(pagecount)
            return
        raise "不可能状态"
    def getselectedrow(self):
        '''得到选中行'''
        i = self.getselectedrowindex()
        if(i<0):
            return None
        return self.getrow(i)
    
class ABizComboBox(AComponent):
    '''
    复杂的下拉列表框，可以支持输入，每一行包含key和value，当输入key的时候自动选中value
    这里规定第一列为key列，第二列为要显示的Label列
    header为表头，为一个含有两个元素的列表，每个列表元素为一个二元组（不选用map，因为有可能key重复）
    items为含有二元组的列表
    '''
    def __init__(self,x,y,width,header=[],items=[],showcount=3):
        #showcount:下拉显示的条数
        AComponent.__init__(self, x, y, 1, width)
        self.__items__ = items
        self.__header__ = header
        self.__showcount__ = showcount  
        self.__selectrowindex__ = -1
        #用户输入的key值
        self.__key__ = ""
        #弹出窗格的宽度，默认等于控件宽度
        self.__panelwidth__ = width
    def isfocusable(self):
        return True     
    def setpanelwidth(self,w):
        '''设定下拉面板宽度'''
        self.__panelwidth__ = w
    def __createwin__(self):
        AComponent.__createwin__(self)
        self.__initdialog__() 
    def __initdialog__(self):
        self.dlg = AForm(self.getabsx(),self.getabsy()+1
                    ,self.__showcount__+2+2,self.__panelwidth__,hasbox=False)
        self.table = ATable(0,0,self.__showcount__+2+2
                                ,self.dlg.getclientwidth(),self.__header__)
        self.table.setclickkeys([KEY_ENTER])
        self.table.setnextkeys(['>','.'])
        #在窗口初始化的时候就要将元素赋值进去，这样elif(ch>=33 and ch<=126):的时候才会起作用
        self.table.addrows(self.__items__)
        self.table.onitemclick = self.__itemclick__
        self.dlg.add(self.table)
    def destroy(self):
        AComponent.destroy(self)
        self.dlg.destroy()
    def __grabfocus__(self):
        AComponent.__grabfocus__(self)
        #清空
        self.__key__ = ""
    def __releasefocus__(self):
        
        ret = AComponent.__releasefocus__(self)
        #清空
        self.__key__ = ""
        self.paint()
        return ret
    def __itemclick__(self,index):
        self.dlg.hide()
        
    def __paint__(self):
        AComponent.__paint__(self)       
        
        if(self.getselectedindex()<0):
            text = self.__key__
            label = ""
        else:
            text = self.getselectedkey()
            label = self.getselectedvalue()
        
        t = "<"+text+">"+label
        s = ACursesIntern.ljustandcut(t, self.getclientwidth()-1)
        self.__textout__(0, 0, s)    
    def inputproc(self,msg):
        ch = msg.ch
        if(ch==curses.KEY_DOWN):
            msg.consume()
            self.table.removeallrow()
            self.table.addrows(self.__items__)
            self.table.setselectedrowindex(self.__selectrowindex__)
            
            self.dlg.show()
            self.__selectrowindex__ = self.table.getselectedrowindex()
            self.paint()
            
        elif(ch>=33 and ch<=126):
            msg.consume()
            self.table.setselectedrowindex(-1)
            self.setselectedindex(-1)  
            self.__key__ = self.__key__ + str(chr(ch))
            rowitems = self.table.getrowitems()
            i = 0
            for row in rowitems:                
                if(row[0]==self.__key__):
                    self.__key__ = ""
                    self.table.setselectedrowindex(i)
                    self.setselectedindex(i)                    
                i = i+1
            self.paint()
        #按后退键清空以前的输入
        elif(ch==curses.KEY_BACKSPACE or ch==KEY_BACKSPACE):
            msg.consume()
            self.table.setselectedrowindex(-1)
            self.setselectedindex(-1)
            self.__key__ = ""    
            self.paint()        
        
    def addrow(self,key,row=[]):
        '''添加行'''
        r = []
        r.append(key)
        r = r+row
        self.__items__.append(r)       
    def getselectedindex(self):
        '''得到选中列序号'''
        return self.__selectrowindex__
    def getselectedkey(self):
        '''得到选中列的key'''
        i = self.getselectedindex()
        if(i<0):
            return None
        else:
            row = self.__items__[i]
            return row[0]
    def setselectedindex(self,index):
        '''得到选中列的索引'''
        self.__selectrowindex__ = index
        self.paint()
    def setselectedkey(self,key):
        '''设定选中列的key'''
        i=0
        for r in self.__items__:
            if(r[0]==key):
                self.setselectedindex(i)
            i = i+1
    def getselectedvalue(self):
        '''得到选中的值'''
        i = self.getselectedindex()
        if(i<0):
            return None
        else:
            row = self.__items__[i]
            return row[1]
    