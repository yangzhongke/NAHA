#coding:UTF-8
import sys
sys.path.insert(0, '../')

from ACurses import *
from ACursesEx import *

class T003EditForm(AForm):    
    def __init__(self,row):                        
        AForm.__init__(self, 20, 5, 15,60)     
        self.row=row
        
        ALabel1=ALabel(1,1,7,text="Id")
        self.add(ALabel1)
        edtId=AEdit(10,1,10,"")
        edtId.settext("")
        self.add(edtId)
        ALabel2=ALabel(28,1,7,text="Name")
        self.add(ALabel2)
        ALabel3=ALabel(1,2,7,text="Gender")
        self.add(ALabel3)
        ALabel4=ALabel(28,2,7,text="Age")
        self.add(ALabel4)
        ALabel5=ALabel(1,3,7,text="Province")
        self.add(ALabel5)
        edtName=AEdit(38,1,10,"")
        edtName.settext("")
        self.add(edtName)
        cmbSex=AComboBox(10,2,10,items=["Male","Female","Unkown"],showcount=3)
        self.add(cmbSex)
        edtAge=AIntegerEdit(38,2,10)
        edtAge.settext("")
        self.add(edtAge)
        cmbProv=AComboBox(10,3,10,items=["BJ","HeBei","ShanXi","HeNan"],showcount=3)
        self.add(cmbProv)
        btnok=AButton(6,5,10,text="OK")
        self.add(btnok)
        btnok.onclick=self.okclick
        btncancel=AButton(30,5,10,text="Cancel")
        self.add(btncancel)
        btncancel.onclick=self.cancelclick
        
        edtId.settext(str(row[0]))
        edtName.settext(str(row[1]))
        cmbSex.setselecteditem(str(row[2]))
        edtAge.settext(str(row[3]))
        cmbProv.setselecteditem(str(row[4]))   
        
        self.edtId=edtId
        self.edtName=edtName
        self.cmbSex=cmbSex
        self.edtAge=edtAge
        self.cmbProv=cmbProv
    def okclick(self):
        self.row[0] = self.edtId.gettext()
        self.row[1] = self.edtName.gettext()
        self.row[2] = self.cmbSex.getselecteditem()
        self.row[3] = self.edtAge.gettext()
        self.row[4] = self.cmbProv.getselecteditem()
        self.destroy()    
    def cancelclick(self):
        self.destroy()
