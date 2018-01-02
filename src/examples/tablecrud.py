import sys
sys.path.insert(0, '../')

from ACurses import *
from ACursesEx import *

ADDNEW="ADDNEW"
EDIT = "EDIT"
VIEW = "VIEW"

trade = None
ALabel5=None
edtdesc=None
btnexit=None
ALabel4=None
edtamount=None
bizcmbOfficeNum=None
ALabel7=None
bizcmbaccounttype=None
edttotalcount=None
btnadd=None
AEdit2=None
ALabel9=None
edtspecaccountno=None
btndel=None
ALabel8=None
ALabel3=None
edttotalamount=None
btnedit=None
btnsave=None
ALabel1=None
ALabel10=None
AEdit1=None
edtbranchaccountno=None
ARectAngle1=None
ALabel6=None
ALabel2=None

table = None
labelmsg = None
uistate = None



def main():
    global trade, ALabel5,edtdesc,btnexit,ALabel4,edtamount,bizcmbOfficeNum,ALabel7,bizcmbaccounttype,edttotalcount,btnadd,AEdit2,ALabel9,edtspecaccountno,btndel,ALabel8,ALabel3,edttotalamount,btnedit,btnsave,ALabel1,ALabel10,AEdit1,edtbranchaccountno,ARectAngle1,ALabel6,ALabel2,labelmsg,table
    trade=AForm(0,0, 80, 80)
    ALabel1=ALabel(0,0,12,text="Number:")
    trade.add(ALabel1)
    
    officenumitems = []   
    officenumitems.append(["001","ChaoYang"]) 
    officenumitems.append(["002","DaXing"]) 
    officenumitems.append(["003","HaiDian"])
    bizcmbOfficeNum=ABizComboBox(14,0,10,[("Number",5),("Name",12)],officenumitems)
    bizcmbOfficeNum.setpanelwidth(25)
    trade.add(bizcmbOfficeNum)
    
    
    ALabel2=ALabel(27,0,8,text="TotalCount:")
    trade.add(ALabel2)
    
    edttotalcount=AIntegerEdit(38,0,10)
    edttotalcount.settext("")
    trade.add(edttotalcount)
    
    ALabel3=ALabel(51,0,10,text="TotalAmount:")
    trade.add(ALabel3)
    
    edttotalamount=ADecimalEdit(64,0,10)
    edttotalamount.settext("")
    edttotalamount.setvalidfailpolicy(GRABFOCUSANDNOCLEAR)
    edttotalamount.onvalid = edttotalamountonvalid
    edttotalamount.onfocuslost = edttotalamountonfocuslost
    trade.add(edttotalamount)    
    
    ARectAngle1=ARectAngle(0,1,6,77)
    trade.add(ARectAngle1)
    ALabel4=ALabel(1,2,8,text="BranchNumber:")
    trade.add(ALabel4)
    
    edtbranchaccountno=AEdit(14,2,21,"")
    edtbranchaccountno.settext("")
    edtbranchaccountno.ontextchange=edtbranchaccountnotextchange
    trade.add(edtbranchaccountno)
    
    ALabel5=ALabel(38,2,10,text="AccountNumber:")
    trade.add(ALabel5)
    
    edtspecaccountno=AEdit(50,2,22,"")
    edtspecaccountno.ontextchange=edtspecaccountnotextchange
    trade.add(edtspecaccountno)

    ALabel6=ALabel(1,3,10,text="CompanyName:")
    trade.add(ALabel6)
    AEdit1=AEdit(13,3,62,"")
    AEdit1.settext("")
    trade.add(AEdit1)
    ALabel7=ALabel(1,4,10,text="Name:")
    trade.add(ALabel7)
    AEdit2=AEdit(13,4,62,"")
    AEdit2.settext("")
    trade.add(AEdit2)
    ALabel8=ALabel(1,5,10,text="Loan/Credit:")
    trade.add(ALabel8)
    
    accttypeitems = []
    accttypeitems.append(["1","Loan"])
    accttypeitems.append(["2","Credit"])
    bizcmbaccounttype=ABizComboBox(12,5,10,[("Number",4),("Name",4)],accttypeitems)
    bizcmbaccounttype.setpanelwidth(20)
    trade.add(bizcmbaccounttype)    
    
    ALabel9=ALabel(24,5,6,text="Amount:")
    trade.add(ALabel9)
    edtamount=ADecimalEdit(31,5,14)
    edtamount.settext("")
    trade.add(edtamount)
    ALabel10=ALabel(46,5,6,text="Desc:")
    trade.add(ALabel10)
    edtdesc=AEdit(54,5,22,"")
    edtdesc.settext("")
    trade.add(edtdesc)
    btnadd=AButton(3,8,8,text="Add")
    trade.add(btnadd)
    btnadd.onclick=btnaddclick
    btnedit=AButton(13,8,10,text="Edit")
    trade.add(btnedit)
    btnedit.onclick=btneditclick
    btndel=AButton(26,8,10,text="Delete")
    trade.add(btndel)
    btndel.onclick=btndelclick
    btnsave=AButton(39,8,10,text="Save")
    trade.add(btnsave)
    btnsave.onclick=btnsaveclick
    btnexit=AButton(53,8,10,text="Exit")
    trade.add(btnexit)
    btnexit.onclick=btnexitclick
    
    table = ATable(0,9,6,75,[("OrderNum",4),("BranchNum",10),("CompanyName",10)
                              ,("Amount",10),("AcctNo",10)
                              ,("Name",10),("Sig",10)
                              ,("Desc",10)])
    table.onselectchange = tableselectchange
    trade.add(table)
    
    labelmsg = ALabel(0,15,50)
    trade.add(labelmsg)
    
    trade.registerkeyevent("f1",showabout)
    trade.show()

def showabout():
    msgbox("NAHA Demo")

def showinfo(msg):
    labelmsg.settext(msg)
def edtbranchaccountnotextchange():
    no = edtbranchaccountno.gettext()
    if(no!=None and no.startswith("hjd")):
        AEdit1.settext("HJD")
    else:
        AEdit1.settext("WangJing")
        
def edtspecaccountnotextchange():
    no = edtspecaccountno.gettext()    
    if(no!=None and no.startswith("jwc")):
        AEdit2.settext("HouQin")
    else:
        AEdit2.settext("caiwu")
    if(uistate==ADDNEW or uistate==EDIT):
        bizcmbaccounttype.setfocus()
    
def edttotalamountonvalid():
    txt = edttotalamount.gettext()
    if(txt==None or len(txt)==0):
        showinfo("Amount is required")
        return False
    dvalue = float(txt)
    if(dvalue<=0.00):
        showinfo("Amount must >0")
        return False
    return True    
def edttotalamountonfocuslost():
    btnadd.setfocus()       
def tableselectchange(previndex,curindex):
    global uistate
    uistate = VIEW
    row = table.getrow(curindex)
    edtbranchaccountno.settext(row[1])
    AEdit1.settext(row[2])
    edtamount.settext(row[3])
    edtspecaccountno.settext(row[4])
    AEdit2.settext(row[5])    
    bizcmbaccounttype.setselectedkey(row[6].getvalue())
    edtdesc.settext(row[7])
def btnaddclick():
    global uistate
    uistate = ADDNEW
    i = len(table.getrowitems())    
    table.addrow([i,"","","","","",ACellWrapper("",""),""])
    edtbranchaccountno.setfocus()
def btneditclick():
    global uistate
    uistate = EDIT
    edtbranchaccountno.setfocus()
def btndelclick():
    i = table.getselectedrowindex()
    if(i>=0):
        table.removerow(i)
def btnsaveclick():
    row = table.getrow(table.getselectedrowindex())
    row[1] = edtbranchaccountno.gettext()
    row[2] = AEdit1.gettext()
    row[3] = edtamount.gettext()
    row[4] = edtspecaccountno.gettext()
    row[5] = AEdit2.gettext()
    cell = ACellWrapper(bizcmbaccounttype.getselectedkey(),
                        bizcmbaccounttype.getselectedvalue())
    row[6] = cell   
    row[7] = edtdesc.gettext()
    table.paint()
def btnexitclick():
    trade.destroy()
 
initapp()
try:  
	main();
finally:
	endapp()	