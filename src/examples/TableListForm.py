#coding:UTF-8
import sys
sys.path.insert(0, '../')

from ACurses import *
from ACursesEx import *
from T003TableEditUI import T003EditForm

class TableListForm(AForm):    
    def __init__(self):                        
        AForm.__init__(self, 0, 3, 69, 100)        
        t = ATable(0,0,10,30,
                   [("Id",5),("Name",6),("Gender",4),("Age",4),("Province",6)])
        t.onselectchange = self.selectchange  
        t.onitemclick = self.tableitemclick
        t.addrow(["11","Tom","M",20,"BJ"])
        t.addrow(["22","Jerry","F",30,"HeBei"])
        t.addrow(["33","Lily","M",10,"HuBei"])
        t.addrow(["44","Lucy","F",24,"ShanXi"])
        t.addrow(["55","Joan","M",13,"SD"])
        t.addrow(["66","Mike","F",28,"GuangXi"])
        t.addrow(["77","Moke","F",14,"TianJin"])
        t.addrow(["88","Json","M",33,"ShangHai"])
        t.addrow(["99","java","F",16,"DaLian"])
        t.addrow(["00","net","M",54,"GanSu"])
        self.add(t)
        self.t=t
        
        labelno = ALabel(0,11,5,"Number")
        edtno = AEdit(8,11,10)
        edtno.ongrabfocus = lambda:self.showmsg("Number Required")    
        self.add(labelno)
        self.add(edtno)
        self.edtno=edtno
        
        
        labelname = ALabel(20,11,5,"Name")
        edtname = AEdit(28,11,10)
        edtname.ongrabfocus = lambda:self.showmsg("Name Required")
        self.add(labelname)
        self.add(edtname)
        self.edtname=edtname
        
        labelsex = ALabel(40,11,5,"Gender")
        cmbsex = AComboBox(48,11,10,["Male","Female"])
        cmbsex.additem("Unkown")
        cmbsex.ongrabfocus = lambda:self.showmsg("Gender Required")
        self.add(labelsex)
        self.add(cmbsex)
        self.cmbsex=cmbsex
        
        bizcmbitems = [("01","Haidian"),("02","changyang"),("03","daxing"),
                   ("04","changping" ),("05","dongcheng")]
        bizcmb = ABizComboBox(60,11,20,[("Num",6),("Name",6)],bizcmbitems)
        self.add(bizcmb)
        self.bizcmb=bizcmb
        
        
        labelprov = ALabel(0,12,5,"Prov")
        cmbprov = AComboBox(8,12,20,["Beijing","Henan","ShanDong","Shanxi","HuBei","Hunan","LiaoNing",
                                 "Hebei"])
        cmbprov.ongrabfocus = lambda:self.showmsg("Prov required")
        self.add(labelprov)
        self.add(cmbprov)
        self.cmbprov=cmbprov
        
        btnadd = AButton(0,13,8,"Add")
        btnadd.onclick = self.addclick 
        btnsave = AButton(10,13,8,"Save")
        btnsave.onclick = self.saveclick
        btndel = AButton(20,13,8,"Delete")  
        btndel.onclick = self.delclick
        self.add(btnadd)
        self.add(btnsave)
        self.add(btndel)
        
        labelmsg = ALabel(0,15,50)
        self.add(labelmsg)
        self.labelmsg = labelmsg
        
        btnexit = AButton(40,13,10,"Exit")
        self.add(btnexit)
        btnexit.onclick = self.exittrade
    
    def addclick(self):
        r = ["","","","",""]
        self.t.addrow(r)
        self.t.setselectedrowindex(len(self.t.getrowitems())-1)
        self.t.showselectedpage()
        
    def saveclick(self):
        r = self.t.getselectedrow()
        self.savetorow(r)
    
    def savetorow(self,row):
        row[0] = self.edtno.gettext()
        row[1] = self.edtname.gettext()
        row[2] = self.cmbsex.getselecteditem()
        row[4] = self.cmbprov.getselecteditem()
        self.t.paint()
    
    def delclick(self):
        i = self.t.getselectedrowindex()
        if(i>=0):
            self.t.removerow(i)
    
    def selectchange(self,previndex,sindex):
        r = self.t.getselectedrow()
        self.edtno.settext(r[0])
        self.edtname.settext(r[1])
        self.cmbsex.setselecteditem(r[2])
        self.cmbprov.setselecteditem(r[4])    
    def tableitemclick(self,index):
        row = self.t.getrow(index)
        
        editUI = T003EditForm(row)
        editUI.show()
        editUI.destroy();
        self.t.paint()
        
    def showmsg(self,msg):
        self.labelmsg.settext(msg)
    def exittrade(self):
        self.destroy()

initapp()
try: 
    form = TableListForm()
    form.show()
    form.destroy()
finally:
    endapp()   