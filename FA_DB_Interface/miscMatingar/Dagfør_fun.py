from tkinter import *
from tkinter import messagebox
import os
import shutil
import datetime as dt
from pprint import pprint
from FA_DB_Interface.miscMatingar import db_ting as db
from FA_DB_Interface.miscMatingar import init_fun as fun
from FA_DB_Interface import Matingar

def doublelefttree(id, setup_dict):
    setup_dict['id'] = id
    setup_dict['inniliggjandimappir'] = []
    setup_dict['inniliggjandifilir'] = []
    righttree = setup_dict['righttree']
    righttree.delete(*righttree.get_children())
    temp = db.getdatepath(id, setup_dict)
    setup_dict['destdir'] = temp[1]
    uppdateraDate(temp, setup_dict)
    uppdaterarighttree(righttree, temp, setup_dict)
    uppdateraupp(id, setup_dict)

def uppdateraDate(temp, setup_dict):
    Date = setup_dict['dato']['Startdato']
    for x in Date.values():
        x.config(state=NORMAL)
    Date['Ár'].delete(0, END)
    Date['Ár'].insert(0, temp[0].year)
    Date['M'].delete(0, END)
    Date['M'].insert(0, temp[0].month)
    Date['D'].delete(0, END)
    Date['D'].insert(0, temp[0].day)
    for x in Date.values():
        x.config(state=DISABLED)

def uppdaterarighttree(righttree, temp, setup_dict):
    path = setup_dict['Path_to_RawData'] + '/' + temp[1]
    temp = os.listdir(path)
    for x in temp:
        try:
            files = os.listdir(path + '/' + x)
            righttree.insert('', 0, x, text=x, tags=('inniliggjandi'))
            for y in files:
                righttree.insert(x, 'end', text=y, tags=('inniliggjandi'))
            setup_dict['inniliggjandimappir'].append(x)
        except NotADirectoryError:
            righttree.insert('', 'end', text=x, tags=('inniliggjandi'))
            setup_dict['inniliggjandifilir'].append(x)
    righttree.tag_configure('inniliggjandi', background='green')

def uppdateraupp(id, setup_dict):
    Møguligarupp, upp = db.Dagførupp(id, setup_dict)
    frame = setup_dict['uppsetan_frame']
    for widget in frame.winfo_children():
        widget.destroy()
    setup_dict['uppsetwid'] = {}
    i = 0
    for x in Møguligarupp:
        Label(frame, text=x[1]).grid(row=i)
        setup_dict['uppsetwid'][x[0]] = Entry(frame)
        setup_dict['uppsetwid'][x[0]].insert(END, x[2])
        setup_dict['uppsetwid'][x[0]].grid(row=i, column=1)
        i += 1
    for x in upp:
        setup_dict['uppsetwid'][x[0]].delete(0, END)
        setup_dict['uppsetwid'][x[0]].insert(END, x[1])

def update_db(setup_dict):
    print('hey')
    fun.geruppsetan(setup_dict)
    fun.inlesdato(setup_dict)
    pprint(setup_dict)
    db.uppdatedb(setup_dict)
    raw = setup_dict['Path_to_RawData'] + '/'
    destdir = setup_dict['destdir']
    del setup_dict['id']
    # TODO skal man brúka copy2
    for x in setup_dict['innsettirfilir']:
        shutil.copy(x, raw + destdir)
    # TODO riggar kanska ikki í windows
    for x in setup_dict['innsettarmappir']:
        shutil.copytree(x, raw + destdir + '/' + x.split('/')[-1])
    messagebox.showinfo('Uppdatera', 'Uppdatera')
    # TODO skal sikkur koyra rudda
    Matingar.inset_matingar(setup_dict['main_frame'], setup_dict['login']['host'],
                            setup_dict['login']['user'], setup_dict['login']['password'])
