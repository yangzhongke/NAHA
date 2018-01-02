# NAHA
NAHA-A python console UI Library that wrapped PyCurse

 
![image](https://raw.githubusercontent.com/yangzhongke/NAHA/master/doc/simple1.png) 

![image](https://raw.githubusercontent.com/yangzhongke/NAHA/master/doc/msgbox.png)

![image](https://raw.githubusercontent.com/yangzhongke/NAHA/master/doc/confirmbox.png)

![image](https://raw.githubusercontent.com/yangzhongke/NAHA/master/doc/controls1.png)

![image](https://raw.githubusercontent.com/yangzhongke/NAHA/master/doc/controls2.png)
 
![image](https://raw.githubusercontent.com/yangzhongke/NAHA/master/doc/menu1.png)

![image](https://raw.githubusercontent.com/yangzhongke/NAHA/master/doc/table1.png) 
 
![image](https://raw.githubusercontent.com/yangzhongke/NAHA/master/doc/subdialog1.png) 
 
 
'''
#coding:UTF-8
import sys
sys.path.insert(0, '../')

from ACurses import *
from ACursesEx import *

class Form1(AForm):    
    def __init__(self):                        
        AForm.__init__(self, 20, 5, 10, 35)
        
        btn1 = AButton(0,0,10)
        btn1.settext("msgbox")
        btn1.onclick=self.btn1Click     
        self.add(btn1)
        
        btn2 = AButton(15,0,10)
        btn2.settext("confirm")
        btn2.onclick=self.btn2Click     
        self.add(btn2)
    def btn1Click(self):
        msgbox("hello")        
    def btn2Click(self):
        isOk = confirmbox("are you ok?")
        if(isOk):
            msgbox("rupeng.com")
        else:
            msgbox("github.com")
        
initapp()
try: 
    form = Form1()
    form.show()
    form.destroy()
finally:
    endapp()        

 '''


All Controls:
AForm/AButton/ASingleLineField/AEdit/APasswordField/AFormatEdit/AMaskEdit/AIntegerEdit/ADecimalEdit/ALabel/AMultiLineLabel/ACheckBox/ARadioButton/ARadioGroup/AListBox/AComboBox/ATable/ABizComboBox
 
 
# 此开发包由如鹏网杨中科老师开发，学中国最牛逼的Python课程，到[如鹏网](http://www.rupeng.com)！

Email:yzk365@qq.com
 
微信:yzk369

QQ:1393695730
