import os
import shutil

from . import master
from .gui_par import insert_gui_par

def germappu(setup_dict, siduval_dict):
    startdir = os.getcwd()
    path = setup_dict['path']

    path_to_skabilon = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'skabilon')

    if path['dest'].get() == 'path':
        os.chdir(startdir)
        Exception('dest er ikki sett')
        return

    os.chdir(path['dest'].get())
    if not 'LaTeX' in os.listdir():
        os.mkdir('LaTeX')
    os.chdir('LaTeX')
    if len(os.listdir()) > 0:
        os.chdir(startdir)
        print('mappan er ikki tóm')
        Exception('mappan er ikki tóm')
        return
    for item in os.listdir(path_to_skabilon):
        s = os.path.join(path_to_skabilon, item)
        d = os.path.join(os.getcwd(), item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
    Myndin = False
    if path['mynd'].get() != 'path':
        os.mkdir(os.path.join('myndir', 'permumynd'))
        mynd_navn = os.path.split(path['mynd'].get())[1]
        Myndin = os.path.join('myndir', 'permumynd', mynd_navn)
        shutil.copy2(path['mynd'].get(), os.path.join(os.getcwd(), 'myndir', 'permumynd', mynd_navn))

    metafil = open(os.path.join('setup', 'metadata.tex'), 'w')
    metafil.write(germetafilin(setup_dict, Myndin))
    metafil.close()
    insert_gui_par(setup_dict, setup_dict['gui_par'])


    master.skriva_doc(setup_dict, siduval_dict)
    '''
    try:
        master.skriva_doc(setup_dict, siduval_dict)
    except Exception as e:
        print(e.args)
        print()
        print(dir(e))
    '''

    os.chdir(startdir)

def germetafilin(setup_dict, mynd):
    meta = setup_dict['meta']
    out = '\\def\\falogo{myndir/setupmyndir/Fiskaaling_logo_1.jpg}\n\n'
    if mynd:
        ini = mynd.replace('\\','/')
    else:
        ini = 'myndir/setupmyndir/mynd_forsida.jpeg'
    out += '\\def\\permumynd{%s}\n\n' % ini

    for i in meta:
        if meta[i].get() == '':
            ini = 'metadata \\bslash %s' % i
        else:
            ini = meta[i].get()
        out += '\\def\\%s{%s}\n\n' % (i, ini)
    out += '\\def\\samandr{\\input{texfilir/Samandrattur.tex}}'
    return out
