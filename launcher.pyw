from win32clipboard import OpenClipboard, EmptyClipboard, CloseClipboard,SetClipboardText
from win32con import KEYEVENTF_KEYUP
from win32api import GetKeyState, keybd_event
import win32gui
import time
import sys
from functools import partial
import threading
from threading import Thread

import tkinter
from tkinter import *
from tkinter import font as tkFont
from tkinter import messagebox
import tkinter.ttk as ttk

import inspect
import ctypes
import csv

def _async_raise(tid, exctype):
    """引发异常，必要时执行清理"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, launcher.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """如果它返回一个大于1的数字，你就有麻烦了，
        # 你应该用exc=NULL再次调用它来恢复效果。"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

top_two_wins = [0,10]
def monitor_window():
    state_left = GetKeyState(0x01)  # Left button down = 0 or 1. 
    while True:
        a = GetKeyState(0x01)
        if a != state_left:  # Button state changed
            state_left = a
            if a < 0:
                continue
            else:
                top_win = win32gui.GetForegroundWindow()
                tktop="TkTopLevel"
                if top_win and win32gui.GetClassName(top_win) != tktop:
                    top_two_wins[1] = top_win
        time.sleep(0.001)
   
def clipboard_operate(seq=u'empty \u00f8'):
    global top_two_wins
    if win32gui.IsWindow(top_two_wins[1]) : 
        win32gui.SetForegroundWindow(top_two_wins[1])
    else :
        print("没有top_two_wins[1]")
    #add unicode to clipboard
    OpenClipboard()
    EmptyClipboard()
    SetClipboardText(seq,13)
    CloseClipboard()
    # ctrl+v
    keybd_event(0x11, 0, 0, 0)
    keybd_event(0x56, 0, 0, 0)
    keybd_event(0x56, 0, KEYEVENTF_KEYUP, 0)
    keybd_event(0x11, 0, KEYEVENTF_KEYUP, 0)

class uniKeyboard:
    def __init__(self,top, value):
        self.b = Button(top)
        self.v = value

class TyperLocater:
    def __init__(self, top=None):
        #super(TyperLocater,self).__init__()
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#b2c9f4' # Closest X11 color: 'SlateGray2'
        _ana1color = '#eaf4b2' # Closest X11 color: '{pale goldenrod}'
        _ana2color = '#f4bcb2' # Closest X11 color: 'RosyBrown2'

        self.top = top
        top.geometry("-9+100")
        top.title("英语字体键盘")
        top.configure(highlightbackground="#f5deb3")
        top.configure(highlightcolor="black")
        
        menubar = Menu(top)
        menubar.add_command(label="Serif 粗体", command=self.font1)
        menubar.add_command(label="缩小-", command=self.zoom_out)
        menubar.add_command(label="放大+", command=self.zoom_in)
        menubar.add_command(label="打开", command=self.entry_csv_file)
        self.top.config(menu=menubar)
        
        self.helv36 = tkFont.Font(family='Unifont', size=15, weight='bold')
        self.keyboard = [
                         [u'\ud835\udfd9',u'\ud835\udfda',u'\ud835\udfdb',u'\ud835\udfdc',u'\ud835\udfdd',u'\ud835\udfde',u'\ud835\udfdf',u'\ud835\udfe0',u'\ud835\udfe1',u'\ud835\udfe2',],
                         [u'\ud835\udd52',u'\ud835\udd53',u'\ud835\udd54',u'\ud835\udd55',u'\ud835\udd56',u'\ud835\udd57',u'\ud835\udd58',u'\ud835\udd59',u'\ud835\udd5a',u'',],
                         [u'\ud835\udd5b',u'\ud835\udd5c',u'\ud835\udd5d',u'\ud835\udd5e',u'\ud835\udd5f',u'\ud835\udd60',u'\ud835\udd61',u'\ud835\udd62',u'\ud835\udd63',u'',],
                         [u'\ud835\udd64',u'\ud835\udd65',u'\ud835\udd66',u'\ud835\udd67',u'\ud835\udd68',u'\ud835\udd69',u'\ud835\udd6a',u'\ud835\udd6b',u'\00a0',u'',]
        ]
        self.uni_list = [
                         [u'\ud835\udfd9',u'\ud835\udfda',u'\ud835\udfdb',u'\ud835\udfdc',u'\ud835\udfdd',u'\ud835\udfde',u'\ud835\udfdf',u'\ud835\udfe0',u'\ud835\udfe1',u'\ud835\udfe2',],
                         [u'\ud835\udd52',u'\ud835\udd53',u'\ud835\udd54',u'\ud835\udd55',u'\ud835\udd56',u'\ud835\udd57',u'\ud835\udd58',u'\ud835\udd59',u'\ud835\udd5a',u'',],
                         [u'\ud835\udd5b',u'\ud835\udd5c',u'\ud835\udd5d',u'\ud835\udd5e',u'\ud835\udd5f',u'\ud835\udd60',u'\ud835\udd61',u'\ud835\udd62',u'\ud835\udd63',u'',],
                         [u'\ud835\udd64',u'\ud835\udd65',u'\ud835\udd66',u'\ud835\udd67',u'\ud835\udd68',u'\ud835\udd69',u'\ud835\udd6a',u'\ud835\udd6b',u'\0020',u'',]
        ]
        
        self.create_keyboard()
        
    def redraw_keyboard(self):
        for uk in self.keyboard:
            uk.b.grid_forget()
        #self.uni_list = [[u'\u0045',u'\u004d',u'\u0050',u'\u0054',u'\u2122']]
        self.create_keyboard()
        
    def zoom_out(self):
        org_size = self.helv36["size"]
        if org_size>10:
            self.helv36.configure(size=org_size-1)
        
    def zoom_in(self):
        org_size = self.helv36["size"]
        if org_size<38:
            self.helv36.configure(size=org_size+1)
        
    def create_keyboard(self):
        m = len(self.uni_list)
        n = len(self.uni_list[0])
        for i in range(m):
            for j in range(n):
                uk =uniKeyboard(self.top, self.uni_list[i][j])
                self.keyboard.append(uk)
                uk.b.configure(activebackground="#d9d9d9")
                uk.b.configure(disabledforeground="#b8a786")
                uk.b.configure(highlightbackground="#f5deb3")
                uk.b.configure(text=uk.v)
                uk.b.configure(command=partial(clipboard_operate,uk.v))
                uk.b.configure(font=self.helv36)
                uk.b.grid(row=i,column=j)

    def read_unicode_csv(self,v,entry_win):
        try:
            filename = v.get()
            with open(filename,"rb") as f:
                self.uni_list = []
                for line in f.readlines():
                    s = [i for i in line.decode("utf-8").strip().split(',')]
                    self.uni_list.append(s)
                self.redraw_keyboard()
        except:
           tkinter.messagebox.showinfo('csv error','only utf-8 .csv file')
    def font1(self) :
        try:
            a == sys.argv[0]
            filename = "./font/serif_bold.csv"
            with open(filename,"rb") as f:
                self.uni_list = []
                for line in f.readlines():
                    s = [i for i in line.decode("utf-8").strip().split(',')]
                    self.uni_list.append(s)
                self.redraw_keyboard()
        except:
            tkinter.messagebox.showinfo('csv error','only utf-8 .csv file')
        
    def entry_csv_file(self):
        entry_win = Toplevel()
        entry_win.geometry("-90+10")
        entry_win.title("input a csv file")
        v1 = StringVar()
        e1=Entry(entry_win,textvariable=v1,width=50)
        e1.grid(row=1,column=0)
        Button(entry_win,text="OK",command=partial(self.read_unicode_csv,v1,entry_win)).grid(row=3,column=0)
        
root = Tk()
root.wm_attributes('-topmost',1)
top = TyperLocater (root)
monitor = threading.Thread(target=monitor_window)
monitor.start()

def stop_thread():
    _async_raise(monitor.ident, SystemExit)
    sys.exit(0)
    
root.protocol("WM_DELETE_WINDOW", stop_thread)
root.mainloop()
