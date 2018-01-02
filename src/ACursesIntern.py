#coding:utf-8

#ACurses框架内部用包，只供框架使用，应用开发人员不要调用

import curses,ACurses

#author:杨中科

#热键字符的属性
hotkey_attr = curses.A_BOLD | curses.A_UNDERLINE

#高亮项字符的属性
highlight_attr = curses.A_BOLD|curses.A_REVERSE

#parseKey函数用的字符串与功能键的对应表，采用表驱动能提高运行速度
 
funcKeyDict = {"f1":curses.KEY_F1,"f2":curses.KEY_F2,"f3":curses.KEY_F3,"f4":curses.KEY_F4,
               "f5":curses.KEY_F5,"f6":curses.KEY_F6,"f7":curses.KEY_F7,"f8":curses.KEY_F8,
               "f9":curses.KEY_F9,"f10":curses.KEY_F10,"pageup":curses.KEY_PPAGE,
               "pagedown":curses.KEY_NPAGE}

def parseKey(key):
    #将键定义翻译为Curses内部定义的键值,比如'a'翻译成'a' F1翻译成 KEY_F1
    #返回类型为int,ord()
    
    #全部转换为小写
    key = key.lower()
    
    #如果长度为1，说明是普通字符键
    if(len(key)==1):
        return ord(key)
    
    k = funcKeyDict[key]
    if(k!=None):
        return k    
    
    raise "键定义错误:"+key

def getownerform(component):
    #得到一个控件所在的窗口   
    if(isinstance(component.parent,ACurses.AForm)):
        return component.parent
    else:
        return getownerform(component.parent)  

def getfocusablecomponents(container):
    #得到控件所有的能得到焦点的子控件，拉平树结构
    if(not isinstance(container,ACurses.AContainer)):
        raise "控件必须是AContainer类型的"
    components = []
    for comp in container.components:
        if(isinstance(comp,ACurses.AContainer)):
            components = components + getfocusablecomponents(comp)
        elif(comp.isfocusable()):
            components.append(comp)
    return   components      
def ljustandcut(str,width):
    #保证字符串str的宽度为width，如果宽度不足width则右边补足空格，
    #如果str长度超出width则截取
    newstr = str.ljust(width)
    
    #双字节字符计数器
    mchcount = 0
    for i in range(0,width):
        c = ord(newstr[i])
        if(c>=127):
            mchcount = mchcount+1
    
    #如果mchcount为奇数，说明如果从width处切割则会导致一个汉字被切分
    #所以从width-1处切割。
    #原理：连续两个都大于127的字符就说明是一个汉字的两个字节   
    if((mchcount % 2)==1): 
        #补充一个空格，否则在ATable控件中会造成行累积误差       
        return newstr[:width-1]+" "
    else:
        return newstr[:width]
def dellaststr(str):
    #将字符串最后一个字符删除，如果最后一个是中文，则删除最后这个中文
    w = len(str)
    if(ord(str[w-1])>=127 and ord(str[w-2])>=127):
        return str[:w-2]
    else:
        return str[:w-1]

def isbrokenstr(str):
    #判断一个字符串是否是破损字符，也就是含有半个汉字的破损字符串
    mchcount = 0
    for s in str:
        c = ord(s)
        if(c>=127):
            mchcount = mchcount+1
    if((mchcount % 2)==0):
        return False
    else:
        return True    

def splitstr(str,width):
    #切割字符串，将str切割为宽度为width的等宽字符串，保证中文不被切开
    ret = []   
    
    #剩余的字符串
    leftstr = str    
    while(len(leftstr)>0):
        tmpstr = leftstr[:width]
        #如果从width处切割会造成破损字符串，则向前挪一个位置
        if(isbrokenstr(tmpstr)):
            ret.append(leftstr[:width-1])
            leftstr = leftstr[width-1:]
        else:
            ret.append(tmpstr)
            leftstr = leftstr[width:]
    return ret

def clearlist(list):
#下边这种写法会造成元素不能被清空
#    for item in list:
#        list.remove(item)

#下面这种实现方式比较易懂，不过效率比较低    
#    for i in range(0,len(list)):
#        list.pop()
    #这是利用了切片的原理，list[:]就是指整个slice，效率比较高    
    list[:]=[] 

def masktore(mask):
#    将掩码字符串转换为正则表达式，掩码字符串语法:
#    # 任意数字字符  ' 转义符  U 大写字母
#    L 小写字母  A 数字或者字符（包含大小写）
#    ? 任意字母  * 任意字符
#    _ 此标识符前的元字符可又有无（也就是最多有一个）
#    TODO:效率太低，需要改进，写一个简单的词法分析器来优化，从前往后扫描翻译

    ret = mask
    #首先将mask出现的正则表达式元字符转义
    #注意防止后边的replace把前边的正确的replace结果搞乱
    ret = ret.replace("\\","\\\\")
    ret = ret.replace(".","\\.")
    ret = ret.replace("^","\\^")
    ret = ret.replace("$","\\$")    
    ret = ret.replace("+","\\+")
    ret = ret.replace("?",".")
    ret = ret.replace("{","\\{")
    ret = ret.replace("}","\\}")
    ret = ret.replace("[","\\[")
    ret = ret.replace("]","\\]")    
    ret = ret.replace("|","\\|")
    
    #将mask元字符翻译为正则表达式
    ret = ret.replace("#","\\d")
    ret = ret.replace("'","\\")
    ret = ret.replace("A","\\w")
    ret = ret.replace("U","[A-Z]")
    ret = ret.replace("L","[a-z]")    
    ret = ret.replace("*",".")
    ret = ret.replace("_","?")
    return "^"+ret+"$"

def formatdecimalstr(value):
    #将数字字符串格式化为带千分符的字符串
    #为减少内存占用，不使用re包
    parts = value.split(".")
    intpart = parts[0]
    fintpart = ""
    count = 0
    for i in range(len(intpart)-1,-1,-1):
        c = intpart[i]
        fintpart = str(c)+ fintpart
        count = count+1
        if((count % 3)==0 and count<len(intpart)):
            fintpart = ","+ fintpart
    if(len(parts)==1):
        return fintpart
    elif(len(parts)==2):
        return fintpart+"."+parts[1]
    else:
        raise "格式错误"    


    