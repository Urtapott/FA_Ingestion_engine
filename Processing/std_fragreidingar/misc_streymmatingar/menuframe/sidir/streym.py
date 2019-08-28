import datetime as dt
import time

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy.interpolate import griddata

from .misc import minmaxvika


def tegnahovmuller(data, dypid, dato, mal='FO', ratning=0, nrplots=11, figwidth=6, figheight=7.1,
                   font=7, vmax=None, dest='', navn='Hovmuller.pdf', caption='caption',
                   dpi=200):
    """
    :param data:        numpy array við einari rekkju fyri hvørt dýpið og eina colonnu fyri hvørja máting
    :param dypid:       listi av hvussu djúpar allar binninar eru
    :param dato:        dato á øllum mátingunum
    :param ratning:     hvønn veg máta vit í
    :param nrplots:     hvussu nógv plott skullu á síðina (er verður gjørdur ein axi til colorbar eyka)
    :param figwidth:    breiddin á fig
    :param figheight:   hæddin á fig
    :param vmax:        longdin av ásinum, hviss hettar er None verður rokna hvat tað skal verða
    :param dest:        mappan sum filurin skal goymast sum
    :param navn:        navn á filinum sum verður goymdur
    :param caption:     caption sum sakal standa undir myndini
    :param dpi:         dpi á fig sum verður goymdur
    """

    print('byrja uppá ' + navn)
    #  TODO finn útav hvat eg geri við lang har er eitt petti í master og eitt petti her

    #  finn titil av síðini
    if ratning == 90:
        if mal == 'EN':
            section = 'Hovmüller diagrams of east/west velocities'
        else:
            section = 'Hovmüller diagram av streymferð í eystur/vestur ættina'
    elif ratning == 0:
        if mal == 'EN':
            section = 'Hovmüller diagrams of north/south velocities'
        else:
            section = 'Hovmüller diagram av streymferð í norður/suður ættina'
    else:
        if mal == 'EN':
            section = 'Hovmüller diagrams of %2.1f velocities' % ratning
        else:
            section = 'Hovmüller diagram av streymferð í %2.1f ættina' % ratning

    fig, axs = plt.subplots(ncols=1, nrows=nrplots + 1, figsize=(figwidth, figheight), dpi=dpi)
    mpl.rcParams['font.size'] = font

    datapunktir = len(data[0])

    #  finn hvat greinsan av contourplottinum skal vera

    if vmax is None:
        absdata = [abs(x) for y in data for x in y]
        absdata = np.sort(absdata)
        temp = int(.95 * len(absdata))
        vmax = 1.1 * absdata[temp]
        templog = -np.floor(np.log10(vmax)) + 1
        vmax = np.ceil(vmax * 10**templog)/(10**templog)

    # tekna plottini við at deila tað uppí nrplots forskellig plot og eitt vim colormap
    for i in range(nrplots):
        print('plot nr', i)
        # set up contour plotti
        plotstart = i * datapunktir // nrplots
        plotstop = (i + 1) * datapunktir // nrplots
        xmesh, ymesh = np.meshgrid(dato[plotstart:plotstop], dypid)
        date_fmt = mdate.DateFormatter('%d %b')
        # vigtugt at vmax er tað sama allastani
        contours = axs[i].contourf(xmesh, ymesh, data[::, plotstart:plotstop], levels=np.linspace(-vmax, vmax, 256), cmap='seismic', extend='both')
        # pynta um plotti
        axs[i].xaxis.set_major_formatter(date_fmt)
        # set 10 til 11 tiks í hvørt plot
        locint = np.ceil((dato[plotstop - 1] - dato[plotstart]) / 10)
        axs[i].xaxis.set_major_locator(mdate.DayLocator(interval=int(locint)))
        axs[i].xaxis.set_minor_locator(mdate.DayLocator(interval=1))
        axs[i].set_ylabel('Dýpi (m)')
        axs[i].tick_params(axis='x', which='major', pad=0)
    # finn hvat tiks skullu verða á color bar
    fig.colorbar(contours, cax=axs[nrplots], orientation='horizontal', ticks=np.linspace(-vmax, vmax, 9))
    mpl.rcParams['font.size'] = 7
    plt.subplots_adjust(left=0.1, bottom=0.05, right=0.95, top=0.95, wspace=0.5, hspace=0.5)
    mpl.rcParams['xtick.major.pad'] = 0
    fig.savefig(dest + 'myndir/' + navn, dpi=dpi)
    print('enda ' + navn)
    return '\n\\FloatBarrier\n\\newpage\n\\section{%s}\n\\begin{figure}[h!]\\label{Hov%2.1f}\n\\includegraphics[scale=1]{myndir/%s}' \
           '\n\\caption{%s}\n\\end{figure}\n\\newpage\n' % (section, ratning, navn, caption)


def speedbins(bins, dato, df, max_bin, dypir, minmax=False, dest='', dpi=200,
              mal='FO', navn=None, section=None,
              font=7, figwidth=6, figheight=7.1):
    """
        teknar magdataði fyri 3 dypir
    :param bins: [list int] len(bins)==3 tríggjar bins, [surface layer,
                                                          Center layer,
                                                          Bottom layer]
    :param dato:    mdate fyri samplini
    :param df:      dataði sum skal plottast
    :param max_bin: tann ovasta binnin vit higgja eftir
    :param dypir:   ein lista av dypinum á øllum bins
    :param minmax:  skullu vit hava tvar subsections við til veikan og sterkan streym
    :param dest:    str sum siður hvar latex dokumenti skal skrivast
    :param dpi:     upplysningurin á figurinum
    :param navn:    navnið á figurinum
    :param section: navni á sectiónini
    :return:        ein string sum kann setast inní eitt latex document
    """
    if navn == None:
        navn = 'streymstyrkiyvirtid.pdf'
    if section == None:
        if mal =='EN':
            section = 'Timeseries of speed at selected layers'
        else:
            section = 'Streymferð á útvaldum dýpum'
    if minmax:
        return speedbins2(bins, dato, df, max_bin, dypir, mal=mal, dest=dest, dpi=dpi,
              navn=navn, section=section,
              font=font, figwidth=figwidth, figheight=figheight)
    return speedbins1(bins, dato, df, dypir, mal=mal, dest=dest, dpi=dpi,
          navn=navn, section=section,
          font=font, figwidth=figwidth, figheight=figheight)


def speedbins1(bins, dato, df, dypir, mal='FO', dest='', dpi=200,
              navn='streymstyrkiyvirtid.pdf', section='Timeseries of speed at selected layers',
              font=7, figwidth=6, figheight=7.1):
    """
        teknar magdataði fyri 3 dypir
    :param bins: [list int] len(bins)==3 tríggjar bins, [surface layer,
                                                          Center layer,
                                                          Bottom layer]
    :param dato:    mdate fyri samplini
    :param df:      dataði sum skal plottast
    :param dypir:   ein lista av dypinum á øllum bins
    :param dest:    str sum siður hvar latex dokumenti skal skrivast
    :param dpi:     upplysningurin á figurinum
    :param navn:    navnið á figurinum
    :param section: navni á sectiónini
    :return:        ein string sum kann setast inní eitt latex document
    """

    if len(bins) != 3:
        raise ValueError('bins skal hava 3 bins')
    fig, axs = plt.subplots(ncols=1, nrows=3, figsize=(figwidth, figheight), dpi=dpi)
    mpl.rcParams['font.size'] = font
    date_fmt = mdate.DateFormatter('%d %b')
    for (i, item) in enumerate(bins):
        if i == 0:
            prelabel = 'a) Surface layer'
        elif i == 1:
            prelabel = 'b) Center layer'
        else:
            prelabel = 'c) Bottom layer'
        axs[i].plot(dato, df['mag' + str(item)].values, linewidth=.5, c='k')
        axs[i].xaxis.set_major_formatter(date_fmt)
        axs[i].set_ylabel('speed [mm/t]')
        axs[i].tick_params(axis='x', which='major', pad=0)
        axs[i].set_title(prelabel)
        axs[i].set_xlim(dato[0], dato[-1])
        axs[i].set_ylim(bottom=0)

    if mal=='EN':
        caption = 'Timeseries of speed at three selected bins:' \
                'a) %2.0f m depth, b) %2.0f m depth' \
                  ' and c) %2.0f m depth.' \
                  % (-dypir[bins[0]],
                     -dypir[bins[1]],
                     -dypir[bins[2]])
    else:
        caption = 'Streymferð á trimum valdum dýpum frá øllum mátitíðarskeiðnum.' \
                'a) %2.0f m depth, b) %2.0f m depth' \
                  ' and c) %2.0f m depth.' \
                  % (-dypir[bins[0]],
                     -dypir[bins[1]],
                     -dypir[bins[2]])

    plt.subplots_adjust(left=0.1, bottom=0.05, right=0.95, top=0.95, wspace=0.0, hspace=0.2)
    fig.savefig(dest + 'myndir/%s' % navn, dpi=dpi)
    return '\n\\FloatBarrier\n\\newpage\n\\section{%s}\n\\begin{figure}[h!]\\label{speedbin}\n\\includegraphics[scale=1]{myndir/%s}' \
           '\n\\caption{%s}\n\\end{figure}\n\\newpage\n' % (section, navn, caption)


def speedbins2(bins, dato, df, max_bin, dypir, mal='FO', dest='', dpi=200,
              navn='streymstyrkiyvirtid.pdf', section='Timeseries of speed at selected layers',
              font=7, figwidth=6, figheight=7.1):
    """
        teknar magdataði fyri 3 dypir
    :param bins: [list int] len(bins)==3 tríggjar bins, [surface layer,
                                                          Center layer,
                                                          Bottom layer]
    :param dato:    mdate fyri samplini
    :param df:      dataði sum skal plottast
    :param max_bin: tann ovasta binnin vit higgja eftir
    :param dypir:   ein lista av dypinum á øllum bins
    :param dest:    str sum siður hvar latex dokumenti skal skrivast
    :param dpi:     upplysningurin á figurinum
    :param navn:    navnið á figurinum
    :param section: navni á sectiónini
    :return:        ein string sum kann setast inní eitt latex document
    """
    #  TODO kanska hav miðal yvir dýpið inni í master.py

    #finn minmax
    #   finn miðalstreym
    max_v, min_v = minmaxvika(df, max_bin)


    if len(bins) != 3:
        raise ValueError('bins skal hava 3 bins')
    fig, axs = plt.subplots(ncols=1, nrows=3, figsize=(figwidth, figheight), dpi=dpi)
    fig2, axs2 = plt.subplots(ncols=1, nrows=3, figsize=(figwidth, figheight), dpi=dpi)
    fig3, axs3 = plt.subplots(ncols=1, nrows=3, figsize=(figwidth, figheight), dpi=dpi)
    mpl.rcParams['font.size'] = font
    date_fmt = mdate.DateFormatter('%d %b')
    for (i, item) in enumerate(bins):
        if i == 0:
            prelabel = 'a) Surface layer'
        elif i == 1:
            prelabel = 'b) Center layer'
        else:
            prelabel = 'c) Bottom layer'
        midaltid1 = dato[max_v]
        midaltid2 = dato[min_v]
        tid1 = [np.searchsorted(dato, midaltid1-3.5), np.searchsorted(dato, midaltid1+3.5)]
        tid2 = [np.searchsorted(dato, midaltid2-3.5), np.searchsorted(dato, midaltid2+3.5)]

        axs[i].plot(dato, df['mag' + str(item)].values, linewidth=.5, c='k')
        axs2[i].plot(dato[tid1[0]:tid1[1]], df['mag' + str(item)].values[tid1[0]:tid1[1]], linewidth=.5, c='k')
        axs3[i].plot(dato[tid2[0]:tid2[1]], df['mag' + str(item)].values[tid2[0]:tid2[1]], linewidth=.5, c='k')
        #  TODO eg skal ikki hava hattar scatter
        axs[i].scatter(dato[max_v], 1000, c='r')
        axs[i].scatter(dato[min_v], 1000, c='g')

        axs[i].xaxis.set_major_formatter(date_fmt)
        axs[i].set_ylabel('speed [mm/t]')
        axs[i].tick_params(axis='x', which='major', pad=0)
        axs[i].set_title(prelabel)
        axs[i].set_xlim(dato[0], dato[-1])
        axs[i].set_ylim(bottom=0)

        axs2[i].xaxis.set_major_formatter(date_fmt)
        axs2[i].set_ylabel('speed [mm/t]')
        axs2[i].tick_params(axis='x', which='major', pad=0)
        axs2[i].set_title(prelabel)
        axs2[i].set_xlim(dato[tid1[0]], dato[tid1[1]])
        axs2[i].set_ylim(bottom=0)

        axs3[i].xaxis.set_major_formatter(date_fmt)
        axs3[i].set_ylabel('speed [mm/t]')
        axs3[i].tick_params(axis='x', which='major', pad=0)
        axs3[i].set_title(prelabel)
        axs3[i].set_xlim(dato[tid2[0]], dato[tid2[1]])
        axs3[i].set_ylim(bottom=0)

    if mal == 'EN':
        caption = 'Timeseries of speed at three selected bins:' \
                'a) %2.0f m depth, b) %2.0f m depth' \
                  ' and c) %2.0f m depth.' \
                  % (-dypir[bins[0]],
                     -dypir[bins[1]],
                     -dypir[bins[2]])
    else:
        caption = 'Streymferð á trimum valdum dýpum frá øllum mátitíðarskeiðnum.' \
                'a) %2.0f m depth, b) %2.0f m depth' \
                  ' and c) %2.0f m depth.' \
                  % (-dypir[bins[0]],
                     -dypir[bins[1]],
                     -dypir[bins[2]])

    plt.subplots_adjust(left=0.1, bottom=0.05, right=0.95, top=0.95, wspace=0.0, hspace=0.2)
    fig.savefig(dest + 'myndir/%s' % navn, dpi=dpi)
    fig2.savefig(dest + 'myndir/%s' % 'high_' + navn, dpi=dpi)
    fig3.savefig(dest + 'myndir/%s' % 'low_' + navn, dpi=dpi)
    if mal =='EN':
        subsections = ['high current', 'low current']
    else:
        subsections = ['Høgur streymur', 'Lágur streymur']
    out = ''
    out += '\n\\FloatBarrier\n\\newpage\n\\section{%s}\n\\begin{figure}[h!]\\label{speedbin}\n\\includegraphics[scale=1]{myndir/%s}' \
            '\n\\caption{%s}\n\\end{figure}\n\\newpage\n' % (section, navn, caption)
    out += '\n\\FloatBarrier\n\\newpage\n\\subsection{%s}\n\\begin{figure}[h!]\\label{speedbin}\n\\includegraphics[scale=1]{myndir/%s}' \
            '\n\\caption{%s}\n\\end{figure}\n\\newpage\n' % (subsections[0], 'high_' + navn, caption)
    out += '\n\\FloatBarrier\n\\newpage\n\\subsection{%s}\n\\begin{figure}[h!]\\label{speedbin}\n\\includegraphics[scale=1]{myndir/%s}' \
            '\n\\caption{%s}\n\\end{figure}\n\\newpage\n' % (subsections[1], 'low_' + navn, caption)
    return out


def plotrose(ax, N, umax, lv, Es, Ns, eind='mm/s', axline=.5, axcolor='k', alpha=.5):
    '''
    teknar eina rósu har eg fari at reina at gera tað møguligt at tekna tað í bins
    og í confidens interval

    :param ax:      axin sum rósan skal plottast á
    :param N:       hvussu nógvar bins dataði skal sorterast í av fyrstan tíð
    :param umax:    hvar greinsunar á ásunum skullu verða
    :param lv:      hvar levels á contour plottinum skullu verða
    :param Es:      u data   Haldi eg  í hvussu er data Est
    :param Ns:      v data   Haldi eg  í hvussu er data North
    :param eind:    eindin á Es og Ns sum skal verða tað sama
    :param axline:  tjúktin á linjunum
    :param axcolor: farvan á linjunum
    :param alpha:   alpha á linjunum
    :return:        figurin út aftur við øllum breitingunum
                    (veit ikki um tað er neyðut at returna hann)
    '''
    #  variablin har eg samli dataði í
    F = np.zeros(shape=(N, N))

    #  her filli eg inn í bins
    for k in range(len(Ns)):
        #  hvat fyri bin skal hendan mátingin inní
        Ebin = int(np.floor(((N-1)*((Es[k])+umax)) / (2 * umax) + .5))
        Nbin = int(np.floor(((N-1)*((Ns[k])+umax)) / (2 * umax) + .5))
        if 0 <= Ebin < N and 0 <= Nbin < N:
            F[Nbin][Ebin] += 1

    antal_pertiklar = len(Ns)
    arial_av_kassa = (2 * umax / (N-1))**2
    F /= antal_pertiklar * arial_av_kassa

    #  hvat er index á binnunum
    x = np.linspace(-umax, umax, N)
    X, Y = np.meshgrid(x, x)
    #  ger eitt interpolering uppá eitt størri data sett eftir hvat er í F
    #til at gera eitt stórt contour til confidens

    con = ax.contourf(X, Y, F, levels=lv, cmap=cm.jet)
    cb = plt.colorbar(con, ax=ax)
    cb.set_ticks([])

    #  tekna allar aksarnir vannratt loddratt diagonalt og ein sirkul á [0,0] radius 100
    ax.plot([0, 0], [-umax, umax], c=axcolor, linewidth=axline, alpha=alpha)
    ax.plot([-umax, umax], [0, 0], c=axcolor, linewidth=axline, alpha=alpha)
    ax.plot([-umax, umax], [umax, -umax], c=axcolor, linewidth=axline / 2, alpha=alpha)
    ax.plot([-umax, umax], [-umax, umax], c=axcolor, linewidth=axline / 2, alpha=alpha)
    p = mpatches.Circle((0, 0), 100, fill=False, color=axcolor, linewidth=axline / 2, alpha=alpha)
    ax.add_patch(p)

    ax.set_aspect(1)
    ax.set_xlabel('E (' + eind + ')')
    ax.set_ylabel('N (' + eind + ')')


def tekna_dist_rose(bins, data, N, umax, dypir, mal='FO', dest='LaTeX/', dpi=200,
                    navn='Rosa.pdf', section=None,
                    axcolor='k', axline=0.5, alpha=0.5, font=8, figwidth=6,
                    figheight=7.1):
    '''
    Ger eina síðu við rósuplottum á trimun forskelligum dýpum

    :param bins:        [list int] len(bins)==3 tríggjar bins, [surface layer,
                                                                Center layer,
                                                                Bottom layer]
    :param data:        Dataði sum skal til at tekna rósurnar
    :param N:           Hvussu nógvar bins dataði skal sorterast í av fyrstan tíð
    :param umax:        Hvar greinsunar á ásunum skullu verða
    :param dypir        Ein listi av øllum dýpinum har dýpi er dypir(bin+1)
    :param dest:        Hvat fyri mappu skullu plottini í (undirmappu)
    :param dpi:         Upplysningurin á figurinum
    :param navn:        Navnið á figurinum
    :param section:     Navni á sectiónini
    :param axcolor:     Farvan á axanum (matplotlib)
    :param axline:      Tjúktin á axanum
    :param alpha:       alpha á axanum
    :param font:        Støddin á tekstinum
    :param figwidth:    Breiddin á fig
    :param figheight:   Hæddin á fig

    :return:        ein string sum kann setast inní eitt latex document
    '''

    if section == None:
        if mal == 'EN':
            section = 'Rose diagrams at selected layers'
        else:
            section = 'Rósu diagram á ymsum dýpum'
    if len(bins) != 3:
        print(bins)
        raise ValueError('bins skal hava 3 bins')
    fig, axs = plt.subplots(ncols=2, nrows=3, figsize=(figwidth, figheight), dpi=dpi)
    mpl.rcParams['font.size'] = font
    for (i, item) in enumerate(bins):
        if i == 0:
            prelabel = 'a) Surface layer'
        elif i == 1:
            prelabel = 'b) Center layer'
        else:
            prelabel = 'c) Bottom layer'
        Es = data['u' + str(item)].dropna().values
        Ns = data['v' + str(item)].dropna().values

        umax2 = []
        for x in Es:
            umax2.append(abs(x))
        for x in Ns:
            umax2.append(abs(x))
        umax2.sort()
        umax2 = umax2[int(0.95 * len(umax2))]

        plotrose(axs[i, 0], N, umax2, lv=10, Es=Es, Ns=Ns,
             axcolor=axcolor, axline=axline, alpha=alpha)
        axs[i, 0].set_ylabel(prelabel + '\n' + axs[i, 0].get_ylabel())
        plotrose(axs[i, 1], N, umax, lv=10, Es=Es, Ns=Ns,
             axcolor=axcolor, axline=axline, alpha=alpha)
        axs[i, 1].set_ylabel('')
    if mal == 'EN':
        caption = 'Distribution of velocity vectors: ' \
                  'a)~%2.0f~m~depth, b)~%2.0f~m~depth, and~c)~%2.0f~m~depth.' \
                  % (-dypir[bins[0]],
                     -dypir[bins[1]],
                     -dypir[bins[2]])
    else:
        caption = 'Títtleiki av streymferð í rætning á: ' \
                  'a)~%2.0f~m~dýpið, b)~%2.0f~m~dýpið, og~c)~%2.0f~m~dýpið.' \
                  % (-dypir[bins[0]],
                     -dypir[bins[1]],
                     -dypir[bins[2]])

    plt.gca().set_aspect('equal', adjustable='box')
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.0, hspace=0.5)
    fig.savefig(dest + 'myndir/' + navn)
    return '\n\\FloatBarrier\n\\newpage\n\\section{%s}\n\\begin{figure}[h!]\\label{rose}\n\\includegraphics[scale=1]{myndir/%s}' \
           '\n\\caption{%s}\n\\end{figure}\n\\newpage\n' % (section, navn, caption)


def progressive_vector(bins, dato, uvdf, dypir, mal='FO', dest='LaTeX/', dpi=200,
                       navn='progressive_vector.pdf',
                       section='Progressive vector diagrams at selected layers',
                       font=7, figwidth=6, figheight=7.1):
    '''
    Teknar eitt Progresiv vector plot í trimum forskelligum dýpum
    :param bins:        [list int] len(bins)==3 tríggjar bins, [surface layer,
                                                                Center layer,
                                                                Bottom layer]
    :param dato:        dato á øllum mátingunum
    :param dato:        dato í mdate
    :param uvdf:        uv data í [mm/s]
    :param dest:        Hvat fyri mappu skullu plottini í (undirmappu)
    :param dpi:         Upplysningurin á figurinum
    :param navn:        Navnið á figurinum
    :param section:     Navni á sectiónini
    :param font:        Støddin á tekstinum
    :param figwidth:    Breiddin á fig
    :param figheight:   Hæddin á fig

    :return:        ein string sum kann setast inní eitt latex document
    '''
    if mal == 'EN':
        section = 'Progressive vector diagrams at selected layers'
    else:
        section = 'Progressive vector diagrams á ymskum dýpum'
    if len(bins) != 3:
        raise ValueError('bins skal hava 3 bins')
    fig, axs = plt.subplots(ncols=1, nrows=1, figsize=(figwidth, figheight), dpi=dpi)
    mpl.rcParams['font.size'] = font
    date_fmt = mdate.DateFormatter('%d %b')

    # ein funktión til at finna tað fyrsta og sísta elementi
    # og formatera alt
    def fmt(n):
        def fun(x, pos):
            if pos in [0, n-1]:
                return mdate.num2date(x).strftime('%d %b-%y\n   %H:%M')
            return mdate.num2date(x).strftime('%B')
        return fun

    #  finn bounds--------------------
    interval = [mdate.num2date(dato[0]), mdate.num2date(dato[-1])]
    interval = [[x.year, x.month, 1] for x in interval]
    interval[0][1] += 1
    iterativ = interval[0]
    bounds = []
    while 12*iterativ[0] + iterativ[1] <= 12 *  interval[1][0] + interval[1][1]:
        bounds.append(mdate.date2num(dt.datetime(*iterativ)))
        if iterativ[1] == 12:
            iterativ[0] += 1
            iterativ[1] = 1
        else:
            iterativ[1] += 1
    #  kanna um vit eru ov tatt við
    if abs(bounds[0] - dato[0]) < 5:
        bounds = bounds[1:]
    if abs(bounds[-1] - dato[-1]) <5:
        bounds = bounds[:-1]

    bounds = [dato[0]] + bounds + [dato[-1]]
    # end finn bounds--------------------

    glxmax = -np.inf
    glymax = -np.inf
    glxmin = np.inf
    glymin = np.inf

    #  plots er ein listi av plottum sum verður filtur í tí fyrsta loopinum
    plots = []
    for (i, item) in enumerate(bins):
        #  kanska dropna
        #  skal man convertera til km

        # [km/dag]/[mm/s]
        kmdmms = (60*60*24)/1e6
        xs = uvdf['u' + str(item)] * kmdmms
        ys = uvdf['v' + str(item)] * kmdmms
        # [x, y, dato] eg loggi dato tí at hvissi eg renni meg í NaN
        punktir = [[0], [0], [dato[0]]]
        process_dato = dato[0]
        for k in range(len(xs) - 1):
            #  rokna er við konstantari ferð (xs[k], ys[k])
            #  frá tíð process_dato(sísta ikki nan ella fyrsta)
            #  til dato[k+1]
            x = xs[k]
            y = ys[k]
            if any(np.isnan([x, y])):
                continue
            punktir[0].append(punktir[0][-1] + xs[k] * (dato[k+1] - process_dato))
            punktir[1].append(punktir[1][-1] + ys[k] * (dato[k+1] - process_dato))
            process_dato = dato[k+1]
            punktir[2].append(process_dato)
        plots.append(punktir)

    for i in range(len(plots)):
        if i == 0:
            prelabel = 'Surface layer'
        elif i == 1:
            prelabel = 'Center layer'
        else:
            prelabel = 'Bottom layer'
        punktir = plots[i]
        xmin = np.min(punktir[0])
        xmax = np.max(punktir[0])
        ymin = np.min(punktir[1])
        ymax = np.max(punktir[1])

        axs.plot(plots[i][0], plots[i][1], linewidth=2.5, alpha=.05, color='k')

        tempdato = np.array(punktir[2])
        punktir = np.array([np.array(punktir[0]), np.array(punktir[1])]).T.reshape(-1, 1, 2)
        segments = np.concatenate([punktir[:-1], punktir[1:]], axis=1)

        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)
        lc = LineCollection(segments, cmap='jet', norm=norm)
        lc.set_array(tempdato)
        lc.set_linewidth(2)
        line = axs.add_collection(lc)

        axs.scatter(plots[i][0][-1], plots[i][1][-1], label=prelabel)
        glxmax = max(xmax, glxmax)
        glymax = max(ymax, glymax)
        glxmin = max(xmin, glxmin)
        glymin = max(ymin, glymin)

    cb = fig.colorbar(line, ax=axs, format=mpl.ticker.FuncFormatter(fmt(len(bounds))))
    axs.legend()
    axs.set_xlim(xmin, xmax)
    axs.set_ylim(ymin, ymax)
    plt.subplots_adjust(left=0.1, bottom=0.075, right=0.95, top=0.95, wspace=0.0, hspace=0.2)
    axs.set_xlabel('Distance [Km]')
    axs.set_ylabel('Distance [Km]')
    plt.axis('equal')
    fig.savefig(dest + 'myndir/%s' % navn, dpi=dpi)

    if mal == 'EN':
        caption = 'Progressive vector diagrams at three selected layers: Surface (%2.0f m depth),' \
                  ' center (%2.0f m depth) and bottom layer (%2.0f m depth).' \
                  % (-dypir[bins[0]],
                     -dypir[bins[1]],
                     -dypir[bins[2]])
    else:
        caption = 'PVD-plott av mátingunum, sum vísir hvussu ein lutur hevði rikið,' \
                'um rákið var eins og á mátistaðnum í øllum økinum.' \
                'Hvør litur umboðar ein mánað sum víst á litstiganum:'\
                'Surface (%2.0f m depth), center (%2.0f m depth) and bottom layer (%2.0f m depth).' \
                  % (-dypir[bins[0]],
                     -dypir[bins[1]],
                     -dypir[bins[2]])

    return '\n\\FloatBarrier\n\\newpage\n\\section{%s}\n\\begin{figure}[h!]\\label{PVD}\n\\includegraphics[scale=1]{myndir/%s}' \
           '\n\\caption{%s}\n\\end{figure}\n\\newpage\n' % (section, navn, caption)


def frequencytabellir(datadf, dypir, mal='FO', dest='LaTeX/',
              navn='Frqtabel.tex', sections=None):
    '''
    skrivar tvær frequens tabellir eina við høgum streymi og hina við lágum
    :param datadf:  Ein dataframe við mag av streyminum
    :param dypir:   ein listi sum vísur hvussu djúpt tað er í binninum
    :param dest:        Hvat fyri mappu skullu plottini í (undirmappu)
    :param navn:        Navnið á figurinum
    :param section:     Navni á sectiónini

    :return:        ein string sum kann setast inní eitt latex document
    '''
    if sections == None:
        if mal == 'EN':
            sections = ['Frequency of high speeds', 'Frequency of low speeds']
        else:
            sections = ['Frekvenstalva', 'Frekvenstalva']
    #  Freequency of high speeds
    inforows = ['no.', 'm']
    infospeed = [str(x) for x in [50, 100, 150, 200, 250, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1500]]
    inforows += infospeed
    #  gera klárt til tabellina
    highstr = '\\begin{tabular}{|' + len(inforows)*'r|' + '}\n\\hline\n Bin&\tDepth&\t' \
                                                          '\multicolumn{%s}{c|}{Speed [mm/s]}\\\\\\hline\n'\
              % (len(inforows)-2,)
    highstr += inforows[0].rjust(4)
    for x in inforows[1::]:
        highstr += '&\t' + x.rjust(4)
    lowstr = highstr
    #  kanska skal man hava eitt ting sum sigur hvatt fyri bins hettar er
    loopvar = list(enumerate(dypir))
    loopvar.reverse()
    for i, Depth in loopvar:
        data = datadf['mag' + str(i + 1)].values
        sortboxir = [int(x) for x in infospeed] + [np.inf]
        tally = [0 for _ in sortboxir]

        for x in data:
            for (k, y) in enumerate(sortboxir):
                if x < y:
                    tally[k] += 1
                    break
        # tally er hvussu nógv data er minni enn tað samsvarandi virði í sortboxir
        #print(len(data) - sum(tally))
        tally = [1000*x/sum(tally) for x in tally]
        lowspeedtabel = tally
        #  rokna tey ordiligu tølini sum skullu til lowspeed
        for k in range(1, len(tally)):
            lowspeedtabel[k] = lowspeedtabel[k-1] + tally[k]


        #  rokna tey ordiligu tølini sum skullu til highspeed
        tally = [0 for _ in sortboxir]

        for x in data:
            for (k, y) in enumerate(sortboxir):
                if x <= y:
                    tally[k] += 1
                    break
        #--------------------------------------------------
        tally = [1000*x/sum(tally) for x in tally]
        templow = tally
        #  rokna tey ordiligu tølini sum skullu til lowspeed
        for k in range(1, len(tally)):
            templow[k] = templow[k-1] + tally[k]
        #--------------------------------------------------
        highspeedtabel = [1000 - x for x in templow]
        highspeedtabelround = highspeedtabel
        #  finn tølini sum skullu í high speed tabellina
        for (k, x) in enumerate(highspeedtabelround):
            if 0.005 < x < 1:
                highspeedtabelround[k] = np.round(x, 2)
            else:
                highspeedtabelround[k] = int(np.round(x, 0))
        #  skriva eina reglu til highspeed tabellina
        key = str(i + 1)
        if i == loopvar[0][0]:
            highstr += '\\\\\n\\hline\n'
        else:
            highstr += '\\\\\n'
        highstr += key.rjust(4) + '&\t' + str(-int(Depth)).rjust(4)
        for x in highspeedtabelround[0:-1]:
            highstr += '&\t' + str(x).rjust(4)
        #  finn tølini sum skullu í lowspeed tabellina
        lowspeedtabelround = lowspeedtabel
        for (k, x) in enumerate(lowspeedtabelround):
            if 0.005 < x < 1:
                lowspeedtabelround[k] = np.round(x, 2)
            else:
                lowspeedtabelround[k] = int(np.round(x, 0))
        #  skriva tølini sum skullu í lowspeed tabellina
        #  if fyri at seta eina linju yvir eina rekkju
        if i == loopvar[0][0]:
            lowstr += '\\\\\n\\hline\n'
        else:
            lowstr += '\\\\\n'
        lowstr += key.rjust(4) + '&\t' + str(-int(Depth)).rjust(4)
        for x in lowspeedtabelround[0:-1]:
            lowstr += '&\t' + str(x).rjust(4)
    highstr += '\\\\\\hline\n\\end{tabular}'
    lowstr += '\\\\\\hline\n\\end{tabular}'
    file = open(dest + 'Talvur/high_' + navn, 'w')
    file.write(highstr)
    file.close()
    file = open(dest + 'Talvur/low_' + navn, 'w')
    file.write(lowstr)
    file.close()

    if len(dypir) > 15:
        newpage = '\\newpage\n'
    else:
        newpage = ''
    if mal == 'EN':
        caption = ['Frequency (in parts per thousand) of speeds equal to or exeeding speified values.',
                   'Frequency (in parts per thousand) of speeds less than speified values.']
    else:
        caption = ['Frekvenstalva (í promillu), sum vísur part av mátingum hægri enn eina givna ferð.',
                   'Frekvenstalva (í promillu), sum vísur part av mátingum spakari enn eina givna ferð.']

    return '\n\\FloatBarrier\n\\newpage' \
           '\n\\section{%s}' \
           '\n\\begin{table}[h!]\\label{high_spd}' \
           '\n\\resizebox{\\textwidth}{!}{' \
           '\n\\input{Talvur/high_%s}' \
           '\n}' \
           '\n\\caption{%s}' \
           '\n\\end{table}' \
           '\n%s' \
           '\n\\section{%s}' \
           '\n\\begin{table}[h!]\\label{low_spd}' \
           '\n\\resizebox{\\textwidth}{!}{' \
           '\n\\input{Talvur/low_%s}' \
           '\n}' \
           '\n\\caption{%s}' \
           '\n\\end{table}' \
           '\n\\newpage\n' % (sections[0], navn, caption[0], newpage, sections[1], navn, caption[1])


def duration_speed(bins, dato, magdf, dypir, mal='FO', dest='LaTeX/',
              navn='Duration_high.tex', section=None):
    '''
    skrivar tríggjar tabellir eina fyri hvørt dýpið í bins
    :param bins:        [list int] len(bins)==3 tríggjar bins, [surface layer,
                                                                Center layer,
                                                                Bottom layer]
    :param dato:        dato á øllum mátingunum
    :param magdf:  Ein dataframe við mag av streyminum
    :param dypir:   ein listi sum vísur hvussu djúpt tað er í binninum
    :param dest:        Hvat fyri mappu skullu plottini í (undirmappu)
    :param navn:        Navnið á figurinum
    :param section:     Navni á sectiónini

    :return:        ein string sum kann setast inní eitt latex document
    '''
    if section == None:
        if mal == 'EN':
            section = 'Duration of high speed periods'
        else:
            section = 'Tíð av samanhangandi høgari ferð'
    if len(bins) != 3:
        raise ValueError('bins skal hava 3 bins')
    duration = list(range(60, 1020 + 60, 60))
    #  kanska set speed inn sum ein variabel
    speed = [50, 100, 150, 200, 300, 400, 500, 600, 800, 1000]
    filnovn = []
    caption = []
    label = []
    for (rekkja_i_bin, item) in enumerate(bins):
        data = magdf['mag' + str(item)].values
        total = 0
        tabell = np.zeros((len(speed), len(duration)))
        #  heldur eyða við hvussu langt síðan tað var at vit vóru undir forskelligum speeds
        durationspeeds = [0 for _ in speed]
        #  okkurt til at telja ikki NaN
        i = 0
        while i < len(data):
            if ~np.isnan(data[i]):
                break
            i += 1
        dato0 = dato[i]
        for (i, magnetude) in enumerate(data):
            if np.isnan(magnetude):
                continue
            total += 1
            delta_tid = (dato[i] - dato0) * (24 * 60)       #  min
            dato0 = dato[i]
            #  uppdatera durationspeeds
            for k in range(len(speed)):
                if speed[k] <= magnetude:
                    durationspeeds[k] += delta_tid
                else:
                    durationspeeds[k] = 0
            for d in range(len(duration)):
                for s in range(len(speed)):
                    if durationspeeds[s] >= duration[d]:
                        tabell[s][d] += 1
        #  skriva tex tabell
        texstr = '\\begin{tabular}{|' + (1 + len(duration))*'r|' + '}\n'
        texstr += '\\hline\nSpeed&\t\\multicolumn{%s}{c|}{Duration (minutes)}\\\\\\hline\n' % (len(duration),)
        texstr += 'mm/s'
        for x in duration:
            texstr += '&\t' + str(x).rjust(4)
        texstr += '\\\\\\hline\n'
        for s in range(len(speed)):
            texstr += str(speed[s]).rjust(4)
            for d in range(len(duration)):
                #  temp er tað nasta talið sum skal inní tabellina
                #  tað er ok at sama total verður brúkt til alt tí tað er sama data
                temp = 1000 * tabell[s][d] / total
                if 0.005 < temp < 1:
                    temp = np.round(temp, 2)
                else:
                    temp = int(np.round(temp, 0))
                texstr += '&\t' + str(temp).rjust(4)
            texstr += '\\\\\n'
        texstr += '\\hline'
        texstr += '\n\\end{tabular}'

        if rekkja_i_bin == 0:
            prelabel = 'Surface layer'
        elif rekkja_i_bin == 1:
            prelabel = 'Center layer'
        else:
            prelabel = 'Bottom layer'
        filnovn.append(prelabel.replace(' ', '_') + '_' + navn)
        texfil = open(dest + 'Talvur/' + filnovn[-1], 'w')
        texfil.write(texstr)
        texfil.close()
        if mal == 'EN':
            caption.append('%s, at %2.0fm Depth'
                           % (prelabel, -dypir[item - 1]))
        else:
            caption.append('%s, á %2.0fm Dýpið'
                           % (prelabel, -dypir[item - 1]))
        label.append('\\label{Dur_%s}' % (item,))

    if mal == 'EN':
        forklarandi_tekstur = 'Occurrence (in parts per thousand) of contiguous periods longer than or equal to ' \
           'specified duration with speeds equal to or exceeding specified threshold values (Speed). ' \
           'Flagged ensembles are ignored.'
    else:
        forklarandi_tekstur = 'Partur av samanhangandi mátingum (í promillu),' \
                'ið hava verði longri enn givna tíðarskeiði við hægri enn givnu streymferð.'
    return '\n\\FloatBarrier\n\\newpage' \
           '\n\\section{%s}' \
           '\n%s' \
           '\n\\begin{table}[h!]' \
           '\n\\centering' \
           '\n\\resizebox{\\textwidth}{!}{' \
           '\n\\input{Talvur/%s}' \
           '\n}' \
           '\n\\caption{%s}' \
           '\n\\end{table}' \
           '\n' \
           '\n\\begin{table}[h!]' \
           '\n\\centering' \
           '\n\\resizebox{\\textwidth}{!}{' \
           '\n\\input{Talvur/%s}' \
           '\n}' \
           '\n\\caption{%s}' \
           '\n\\end{table}' \
           '\n' \
           '\n\\begin{table}[h!]' \
           '\n\\centering' \
           '\n\\resizebox{\\textwidth}{!}{' \
           '\n\\input{Talvur/%s}' \
           '\n}' \
           '\n\\caption{%s}' \
           '\n\\end{table}' \
           '\n\\newpage\n' % (section, forklarandi_tekstur, filnovn[0], caption[0], filnovn[1], caption[1], filnovn[2], caption[2])