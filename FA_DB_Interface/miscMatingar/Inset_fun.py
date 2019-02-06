from tkinter import *
import os
import datetime as dt
import shutil
from FA_DB_Interface.miscMatingar import db_ting as db
from FA_DB_Interface.miscMatingar import init_fun as fun
from FA_DB_Interface import Matingar
from FA_DB_Interface.miscMatingar import skrivapdf
import time
from pprint import pprint

def doublelefttree(item, setup_dict):
    try:
        if item[0] == 'I':
            int(item[1::])
        else:
            int('error')
    except ValueError:
        return
    setup_dict['typa'] = setup_dict['lefttree'].parent(item)
    velinstroment(setup_dict['lefttree'].item(item, "text"), setup_dict)

def Doublefelagartree(item, setup_dict):
    #TODO make me
    try:
        int(item)
    except ValueError:
        return
    setup_dict['info']['Umbiði_av'].set(setup_dict['felagartree'].item(item, "text"))
    setup_dict['info']['Felag'].set(setup_dict['felagartree'].parent(item))
    setup_dict['info']['id'] = item

def velinstroment(Navn, setup_dict):
    frame = setup_dict['uppsetan_frame']
    for widget in frame.winfo_children():
        widget.destroy()
    setup_dict['Instroment'] = Navn
    temp = db.getuppsetanir(Navn, setup_dict)
    setup_dict['uppsetan_nøvn'] = [[x[0], x[1]] for x in temp]
    setup_dict['uppsetwid'] = dict([(x[0], x[1]) for x in temp])
    temp = dict([(x[0], x[2]) for x in temp])
    i = 0
    for x in setup_dict['uppsetwid'].keys():
        Label(frame, text=setup_dict['uppsetwid'][x]).grid(row=i)
        setup_dict['uppsetwid'][x] = Entry(frame)
        setup_dict['uppsetwid'][x].insert(END, temp[x])
        setup_dict['uppsetwid'][x].grid(row=i, column=1)
        i += 1

def update_db(setup_dict):
    if setup_dict['Instroment'] == '':
        messagebox.showerror('Einki Instroment', 'Vel eitt instroment')
        return

    fun.geruppsetan(setup_dict)
    fun.inlesdato(setup_dict)
    #TODO ger path til at vera unig í db
    #TODO tjekka um indexi er í db
    datamui = setup_dict['Utfiltdato']['Startdato'].strftime('%y%m%d')

    raw = setup_dict['Path_to_RawData'] + '/'
    destdir = setup_dict['Instroment']
    id = db.getlastid(setup_dict) + 1

    #TODO set inní DB árðin fílir vera kopyeraðir
    #TODO finn destdir ordiligt
    if datamui not in os.listdir(raw + destdir):
        os.makedirs(raw + destdir + '/' + datamui)
    else:
        i = 0
        while True:
            i += 1
            if datamui + str(i) not in os.listdir(raw + destdir):
                datamui += str(i)
                print(datamui)
                os.makedirs(raw + destdir + '/' + datamui)
                break
    #TODO tjekka um filenames er tómt
    #TODO tjekka um nakar filur eitur tað sama
    destdir += '/' + datamui
    #TODO flyt hettar til eftir at vit hava keyrt í db
    latex(setup_dict, id, 'deployment_sheet.pdf', raw + destdir)

    embargo = setup_dict['info']['embargo'][int(setup_dict['info']['id'])]
    if embargo != None:
        embargo = setup_dict['Utfiltdato']['Startdato'] + dt.timedelta(days=embargo)

    db.insetmating(setup_dict, id, destdir, embargo)

    #TODO skal man brúka copy2
    for x in setup_dict['innsettirfilir']:
        shutil.copy(x, raw + destdir)
    #TODO riggar kanska ikki í windows
    for x in setup_dict['innsettarmappir']:
        shutil.copytree(x, raw + destdir + '/' + x.split('/')[-1])
    #TODO skal sikkur koyra rudda
    Matingar.inset_matingar(setup_dict['main_frame'], setup_dict['login']['host'],
                   setup_dict['login']['user'], setup_dict['login']['password'])

def latex(setup_dict, id, navn, dir):
    fil = skrivapdf.birjan()
    fil += skrivapdf.DepID('  ' + str(id) + '   ')
    fil += skrivapdf.tveycol('typa:', setup_dict['typa'], 'Instroment', setup_dict['Instroment'])
    for x in setup_dict['uppsetan_nøvn']:
        if setup_dict['uppsetan'][x[0]] != '':
            fil += skrivapdf.eincol(x[1] + ':', setup_dict['uppsetan'][x[0]])
    fil += skrivapdf.endi()
    skrivapdf.makepdf(fil, navn, dir)
