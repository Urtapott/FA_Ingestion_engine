from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib import dates as mdate
import numpy as np
import os
import pandas as pd
import datetime as dt
from Hovmuller_diagrams import tegnahovmuller
from Hovmuller_diagrams import plotrose2 as test
from Hovmuller_diagrams import get_dypid
from Hovmuller_diagrams import tekna_dist_rose
from Hovmuller_diagrams import speedbins
from Hovmuller_diagrams import progressive_vector
from Hovmuller_diagrams import frequencytabellir
from Hovmuller_diagrams import duration_speed


#  inlesData
for _ in [0]:
    os.chdir('/home/trondur/Documents/FA/data/SORD1702/WD')
    #  TODO sirg fyri at allar kolonninar kunnu brúkast
    dirdf = pd.read_csv('../ASCII/cur_con_pro_dir.txt', encoding='latin', skiprows=11, sep='\t', decimal=",")
    magdf = pd.read_csv('../ASCII/cur_con_pro_mag.txt', encoding='latin', skiprows=11, sep='\t', decimal=",")
    dato = []
    Bin_Size = 4
    firstbinrange = 6.15
    N = 31
    umaxfac = 1
    axcolor = 'k'
    axline = 0.5
    alpha = 0.5
    fultdypid = 100
    treebins = [9, 5, 1]

    font = 8
    figwidth = 6
    figheight = 9
    dpi = 200

    mpl.rcParams['font.size'] = font
    for i in magdf[['YR', 'MO', 'DA', 'HH', 'MM', 'SS']].values:
        i[0] += 2000
        dato.append(mdate.date2num(dt.datetime(*i)))
    # TODO skriva hettar ordiligt
    dirdf = dirdf[[str(i) for i in range(1, 13)]]
    magdf = magdf[[str(i) for i in range(1, 13)]]
    dirdf['dato'] = dato
    magdf['dato'] = dato
    file = open('master.tex', 'w')
    file.write(r"""\include{dokumentstilur}
\usepackage{calc}
\begin{document}""")

#  Setup Hovmuller
if False:
    hadd = 40

    #  TODO kjekka um eg fái tí røttu hæddina set tey røtto variablarnar inn her
    bins = int(np.ceil((hadd - (firstbinrange - Bin_Size / 2)) / Bin_Size))
    print(bins)
    bins = np.arange(1, bins + 1)
    #  TODO tak tann ratta max soleis vit ikki fáa ein error í data
    indexes = [str(i) for i in bins]

    yaxis = [Bin_Size * x + firstbinrange - Bin_Size / 2 for x in bins]
    colnames = indexes

    #  tekna Hovmullerf
    for ratning in [0, 90]:
        navn = 'Hovmuller%1.0f.pdf' % ratning
        data = magdf[colnames].values.T * np.cos(np.deg2rad(dirdf[colnames].values.T - ratning))
        a = tegnahovmuller(data, yaxis, dato, ratning=ratning, navn=navn)
        file.write(a)

#  tekna speedbins
if True:
    a = speedbins(treebins, dato, magdf, fultdypid, Bin_Size, firstbinrange)
    file.write(a)

#  tekna rósu
if True:
    mpl.rcParams['font.size'] = 8
    nsp5 = []
    for i in range(1, 13):
        nsp5.append(magdf[str(i)].describe(percentiles=[.975])['97.5%'])
    umax = np.median(nsp5) * umaxfac

    a = tekna_dist_rose(treebins, magdf, dirdf, N, umax, fultdypid, Bin_Size, firstbinrange, dpi=200)
    file.write(a)

#  tekna Progressive vector diagrams at selected layers
if True:
    a = progressive_vector(treebins, dato, magdf, dirdf, fultdypid, Bin_Size, firstbinrange)
    file.write(a)

#  tekna Frequens tabellir
if True:
    a = frequencytabellir(magdf, fultdypid, Bin_Size, firstbinrange)
    file.write(a)

#  tekna duration_speed
if True:
    a = duration_speed(treebins, dato, magdf, fultdypid, Bin_Size, firstbinrange)
    file.write(a)

#  enda texdocument
if True:
    file.write('\nDýpini skullu líka eftirhiggjast')
    file.write('\n\\end{document}')
    file.close()
