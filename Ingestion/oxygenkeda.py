from tkinter import *
from time import sleep
from tkinter import filedialog
from misc.faLog import *
import pandas as pd
import scipy.signal as sig
import os
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as md
from datetime import datetime
import numpy as np
from scipy import interpolate
from scipy.interpolate import griddata
from scipy.interpolate import RectBivariateSpline
from matplotlib.ticker import MaxNLocator
import pylab
import cmocean


def init(ingestion_listbox):
    termistorkeda = ingestion_listbox.insert("", 0, text="Termistor Keda")
    oxygenmatarir = ingestion_listbox.insert(termistorkeda, 0, text="Oxygen mátarir")
    tempraturmatarir = ingestion_listbox.insert(termistorkeda, 0, text="Hitamálarir")
    ingestion_listbox.insert(oxygenmatarir, "end", text="Decimering")                       # ok
    ingestion_listbox.insert(oxygenmatarir, "end", text="Kalibrering")                      # ok
    ingestion_listbox.insert(oxygenmatarir, "end", text="Fyrireika Seaguard data")          # ok
    ingestion_listbox.insert(oxygenmatarir, "end", text="Rokna upploystiligheit (mg/l)")    # ok
    ingestion_listbox.insert(oxygenmatarir, "end", text='Ger strikumynd')                   # ikki enn
    ingestion_listbox.insert(oxygenmatarir, "end", text="Ger Countour plot")                # ok

    ingestion_listbox.insert(tempraturmatarir, "end", text="Fyrireika RBR fíl")             # ok
    ingestion_listbox.insert(tempraturmatarir, "end", text="Fyrireika dat fíl")             # ok
    ingestion_listbox.insert(tempraturmatarir, "end", text="Decimering")                    # ok
    ingestion_listbox.insert(tempraturmatarir, "end", text="Fyrireika Seaguard data")       # ok
    ingestion_listbox.insert(tempraturmatarir, "end", text='Ger strikumynd')                #
    ingestion_listbox.insert(tempraturmatarir, "end", text="Ger Countour plot")             # ok


def check_click(item, RightFrame, root):
    toReturn = 1
    if item == 'Decimering':
        decimering(RightFrame, root)
    elif item == 'Kalibrering':
        kalibering(RightFrame, root)
    elif item == 'Fyrireika Seaguard data':
        seaguard_data(RightFrame, root)
    elif item == 'Ger Countour plot':
        termistorkeda_contourplot(RightFrame, root)
    elif item == 'Fyrireika RBR fíl':
        rbr_fyrireking(RightFrame, root)
    elif item == 'Fyrireika dat fíl':
        dat_fyrireking(RightFrame, root)
    elif item == 'Ger strikumynd':
        strikumynd(RightFrame, root)
    else:
        toReturn = 0
    return toReturn


########################################################################################################################
#                                                                                                                      #
#                                            Termistor Keda koda byrjar her                                            #
#                                                                                                                      #
########################################################################################################################
#                                                                                                                      #
#                                                   Fyrireika dat fíl                                                  #
#                                                                                                                      #
########################################################################################################################


def dat_fyrireking(frame, root2):
    global root
    root = root2
    for widget in frame.winfo_children():
        widget.destroy()
    Label(frame, text='Termistorkeda', font='Helvetica 18 bold').pack(side=TOP)
    Label(frame, text='Fyrireika dat fíl').pack(side=TOP, anchor=W)
    menuFrame = Frame(frame)
    menuFrame.pack(side=TOP, fill=X, expand=False, anchor=N)
    Button(menuFrame, text='Vel datafílir', command=lambda: velFilir('.dat')).pack(side=LEFT)
    Button(menuFrame, text='Rokna', command=lambda: dat_rokna()).pack(side=LEFT)

    log_frame = Frame(frame, height=300)
    log_frame.pack(fill=X, expand=False, side=BOTTOM, anchor=W)
    gerlog(log_frame, root)


def dat_rokna():
    log_b()
    global filnavn
    if not os.path.isdir(str(os.path.dirname(filnavn[0]))+'/dat'):
        os.mkdir(os.path.dirname(filnavn[0])+'/dat')
    for i in range(len(filnavn)):
        print('Lesur fíl' + filnavn[i])
        data = pd.read_csv(filnavn[i], encoding='latin', skiprows=13, sep='\s+')
        print(data.columns.values)
        date = data.iloc[:, 1]
        time = data.iloc[:, 2]
        temprature = data.iloc[:, 3]
        str_timestamp = []
        str_tmp = []
        for j in range(len(date)):
            str_tmp.append(temprature[j].replace(',', '.'))
            tmp = date[j] + ' ' + time[j]
            timestamp = datetime.strptime(tmp, '%d.%m.%Y %H:%M:%S')
            str_timestamp.append(timestamp.strftime('%Y-%m-%d_%H:%M:%S.%f'))
        nyttfilnavn = filnavn[i]
        nyttfilnavn = os.path.dirname(filnavn[i]) + '/dat' + nyttfilnavn[len(os.path.dirname(filnavn[i])):len(filnavn[i])] + '_dat.csv'
        print('Goymur fíl ' + nyttfilnavn)
        filur_at_goyma = pd.DataFrame({'time': str_timestamp, 'signal': str_tmp})
        filur_at_goyma.to_csv(nyttfilnavn, index=False)
    log_e()







########################################################################################################################
#                                                                                                                      #
#                                                   Fyrireika RBR fíl                                                  #
#                                                                                                                      #
########################################################################################################################


def rbr_fyrireking(frame, root2):
    global root
    root = root2
    for widget in frame.winfo_children():
        widget.destroy()
    Label(frame, text='Termistorkeda', font='Helvetica 18 bold').pack(side=TOP)
    Label(frame, text='Fyrireika RBR fíl').pack(side=TOP, anchor=W)
    menuFrame = Frame(frame)
    menuFrame.pack(side=TOP, fill=X, expand=False, anchor=N)
    Button(menuFrame, text='Vel datafílir', command=lambda: velFilir()).pack(side=LEFT)
    Button(menuFrame, text='Rokna', command=lambda: rbr_rokna()).pack(side=LEFT)
    Button(menuFrame, text='Rokna frá zip', command=lambda: rbr_rokna()).pack(side=LEFT)
    log_frame = Frame(frame, height=300)
    log_frame.pack(fill=X, expand=False, side=BOTTOM, anchor=W)
    gerlog(log_frame, root)

def rbr_rokna():
    log_b()
    global filnavn
    if not os.path.isdir(str(os.path.dirname(filnavn[0]))+'/rbr'):
        os.mkdir(os.path.dirname(filnavn[0])+'/rbr')
    for i in range(len(filnavn)):
        print('Lesur fíl' + filnavn[i])
        data = pd.read_csv(filnavn[i], encoding='latin1')
        print(data.columns.values)
        unixtime = data['tstamp']
        temprature = data['channel02']
        str_timestamp = []
        for j in range(len(unixtime)):
            tmp = unixtime[j] / 1000
            timestamp = datetime.utcfromtimestamp(tmp)
            str_timestamp.append(timestamp.strftime('%Y-%m-%d_%H:%M:%S.%f'))
        nyttfilnavn = filnavn[i]
        nyttfilnavn = os.path.dirname(filnavn[i]) + '/rbr' + nyttfilnavn[len(os.path.dirname(filnavn[i])):len(
            filnavn[i])] + '_rbr.csv'
        print('Goymur fíl ' + nyttfilnavn)
        filur_at_goyma = pd.DataFrame({'time': str_timestamp, 'signal': temprature})
        filur_at_goyma.to_csv(nyttfilnavn, index=False)
    log_e()

########################################################################################################################
#                                                                                                                      #
#                                             Oxygen Keda koda byrjar her                                              #
#                                                                                                                      #
########################################################################################################################
#                                                                                                                      #
#                                                      Strikumynd                                                      #
#                                                                                                                      #
########################################################################################################################


def strikumynd(frame, root2):
    global root
    root = root2
    for widget in frame.winfo_children():
        widget.destroy()
    Label(frame, text='Termistorkeda', font='Helvetica 18 bold').pack(side=TOP)
    Label(frame, text='Plotta strikumynd').pack(side=TOP, anchor=W)

    menuFrame = Frame(frame)
    menuFrame.pack(side=TOP, fill=X, expand=False, anchor=N)

    log_frame = Frame(frame, height=200)
    log_frame.pack(fill=X, expand=False, side=TOP, anchor=W)
    gerlog(log_frame, root)
    plot_frame = Frame(frame)
    plot_frame.pack(fill=BOTH, expand=True, side=BOTTOM, anchor=W)
    global fig
    global ax
    fig = Figure(figsize=(8, 12), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    fig.clf()
    ax = fig.add_subplot(111)
    global filnavn
    filnavn = ['~/Documents/HVN_Temprature_18/alt/strikumynd/spd.csv', '~/Documents/HVN_Temprature_18/alt/strikumynd/5mT.csv', '~/Documents/HVN_Temprature_18/alt/strikumynd/63mT.csv', '~/Documents/HVN_Temprature_18/alt/strikumynd/85mO.csv',
               '~/Documents/HVN_Temprature_18/alt/strikumynd/85mT.csv']

    Button(menuFrame, text='Vel datafílir', command=lambda: velFilir()).pack(side=LEFT)
    Button(menuFrame, text='Tekna', command=lambda: tekna_strikumynd(canvas, float(fra_entry.get()),
                                                                     float(til_entry.get()))).pack(side=LEFT)
    fra_entry = Entry(menuFrame, width=3)
    fra_entry.pack(side=LEFT)
    fra_entry.insert(0, '0')
    Label(menuFrame, text='til').pack(side=LEFT)
    til_entry = Entry(menuFrame, width=3)
    til_entry.pack(side=LEFT)
    til_entry.insert(0, '100')
    Button(menuFrame, text='Goym mynd', command=lambda: goymmynd(fig)).pack(side=RIGHT)
    Button(menuFrame, text='CLF', command=lambda: clear_figur(canvas)).pack(side=RIGHT)


def tekna_strikumynd(canvas, d_til, d_fra):
    log_b()
    global ax
    global fig
    global dfilnavn
    global filnavn
    signal = []
    timestamp = []
    print('Lesur datafílir')
    ax2 = ax.twinx()
    ax2.spines['right'].set_position(('axes', 1.05))
    ax3 = ax.twinx()
    leg = []  # for legend
    labels = []
    for i in range(len(filnavn)):
        print(filnavn[i])
        data = pd.read_csv(filnavn[i])
        signal = data['signal'].values
        timestamp = data['time']
        md_timestamp = []
        md_signal = []
        for j in range(len(signal)):
            tmpstr = str(signal[j])
            tmpstr = tmpstr.replace(',', '.')
            md_signal.append(float(tmpstr))
            try:
                md_timestamp.append(md.date2num(datetime.strptime(timestamp[j], '%Y-%m-%d_%H:%M:%S.%f')))  # Raw seaguard data
            except:
                try:
                    md_timestamp.append(md.date2num(datetime.strptime(timestamp[j], '%d.%m.%y_%H:%M:%S')))
                except:
                    print('Veit ikki hvat eg skal gera vit hendan timestampin ' + timestamp[j])

        label = filnavn[i]
        print(label)
        label = label[len(os.path.dirname(filnavn[i]))+1::]
        print(label)
        if 'T' in label:
            label = 'Temp ' + label[:-5]
            ax.set_ylim(3, 12)
            leg = leg + ax.plot(md_timestamp, md_signal, label=label)

        elif 'spd' in label:
            label = 'Streymferð'
            p3 = ax3.plot(md_timestamp, md_signal, c='red', alpha=0.2, linewidth=1)
            leg = leg + ax3.plot(np.convolve(md_timestamp, np.ones((64,))/64, mode='valid'), np.convolve(md_signal, np.ones((64,))/64, mode='valid'), c='darkred', label=label)
            ax3.set_ylim(0, 40)
            ax3.set_yticks(np.arange(0, 25, 5))
            ax3.yaxis.label.set_color('red')
            ax3.tick_params(axis='y', colors='red')
        else:
            # oxy
            label = 'Oxygen ' + label[:-5]
            ax2.plot(md_timestamp, md_signal, label=label, c='gray', alpha=0.2, linewidth=1)
            leg = leg + ax2.plot(np.convolve(md_timestamp, np.ones((128,)) / 128, mode='valid'), np.convolve(md_signal, np.ones((128,)) / 128, mode='valid'), c='darkgray', label=label)
            ax2.set_ylim(40, 110)
            ax2.set_yticks(np.arange(40, 110, 10))
            ax2.yaxis.label.set_color('darkgray')
            ax2.tick_params(axis='y', colors='gray')
        labels.append(label)
        print(label)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)



    #ax.xaxis.set_major_locator(MaxNLocator(10))
    ax.xaxis.set_major_locator(md.MonthLocator())
    ax.yaxis.set_major_locator(MaxNLocator(10))
    ax.grid(True)
    xt = ax.get_xticks()
    text_timestamps = []
    for i in range(len(xt)):
        tmp = md.num2date(float(xt[i]))
        text_timestamps.append(tmp.strftime("%d %b"))

    ax.set_xticklabels(text_timestamps)
    ax.set_ylabel('Hiti [C]')
    ax2.set_ylabel('Oxygen metningur [%]')
    ax3.set_ylabel('Streymferð [cm/s]')
    #ax.legend()

    print(leg)
    print(labels)

    l1 = ax.legend(leg, labels, loc='upper center', ncol=7, fancybox=True, shadow=True);
    #fig.savefig('tmp.png', figsize=(8, 12), dpi=600)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=1)
    log_e()

########################################################################################################################
#                                                                                                                      #
#                                                     Contour plot                                                     #
#                                                                                                                      #
########################################################################################################################


def termistorkeda_contourplot(frame, root2):
    global root
    root = root2
    for widget in frame.winfo_children():
        widget.destroy()
    Label(frame, text='Termistorkeda', font='Helvetica 18 bold').pack(side=TOP)
    Label(frame, text='Plotta contour data').pack(side=TOP, anchor=W)

    menuFrame = Frame(frame)
    menuFrame.pack(side=TOP, fill=X, expand=False, anchor=N)
    Button(menuFrame, text='Vel dýpir', command=lambda: vel_dypir()).pack(side=LEFT)
    Button(menuFrame, text='Vel datafílir', command=lambda: velFilir()).pack(side=LEFT)
    Button(menuFrame, text='Tekna', command=lambda: rokna_og_tekna_contour(canvas, int(fra_entry.get()),
                                                                           int(til_entry.get()), float(lfra_entry.get()),
                                                                           float(ltil_entry.get()), clin.get(),
                                                                           int(clin_entry.get()))).pack(side=LEFT)
    Button(menuFrame, text='Goym mynd', command=lambda: goymmynd(fig)).pack(side=RIGHT)
    Button(menuFrame, text='CLF', command=lambda: clear_figur(canvas)).pack(side=RIGHT)
    Label(menuFrame, text='Dýpið frá:').pack(side=LEFT)
    fra_entry = Entry(menuFrame, width=3)
    fra_entry.pack(side=LEFT)
    fra_entry.insert(0, '0')
    Label(menuFrame, text='til').pack(side=LEFT)
    til_entry = Entry(menuFrame, width=3)
    til_entry.pack(side=LEFT)
    til_entry.insert(0, '86')

    Label(menuFrame, text='Litir frá:').pack(side=LEFT)
    lfra_entry = Entry(menuFrame, width=3)
    lfra_entry.pack(side=LEFT)
    lfra_entry.insert(0, '-1')
    Label(menuFrame, text='til').pack(side=LEFT)
    ltil_entry = Entry(menuFrame, width=3)
    ltil_entry.pack(side=LEFT)
    ltil_entry.insert(0, '-1')

    clin = IntVar()
    Checkbutton(menuFrame, text="Linjur", variable=clin).pack(side=LEFT)
    Label(menuFrame, text='Tal av linjum:').pack(side=LEFT)
    clin_entry = Entry(menuFrame, width=3)
    clin_entry.pack(side=LEFT)
    clin_entry.insert(0, '5')


    log_frame = Frame(frame, height=300)
    log_frame.pack(fill=X, expand=False, side=TOP, anchor=W)
    gerlog(log_frame, root)
    plot_frame = Frame(frame)
    plot_frame.pack(fill=BOTH, expand=True, side=BOTTOM, anchor=W)
    global fig
    global ax
    fig = Figure(figsize=(8, 12), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    fig.clf()
    ax = fig.add_subplot(111)

def clear_figur(canvas):
    print('Slettar mynd')
    global fig
    global ax
    fig.clf()
    ax = fig.add_subplot(111)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=1)
    if 'levels' in globals():
        global levels
        del levels


def rokna_og_tekna_contour(canvas, d_fra, d_til, c_fra_input, c_til_input, clin, clintal):
    log_b()
    global ax
    global fig
    global dfilnavn
    global filnavn
    er_ox = False
    if 'dfilnavn' not in globals():
        dfilnavn = "/home/johannus/Documents/HVN_ox_18/alt/alt.csv"
    if dfilnavn.split('/')[-1] == 'alt.csv': # Um alt skal gerast í einum høggji
        sets = pd.read_csv(dfilnavn)
        print(sets)
        for row_index, row in sets.iterrows(): # Fyri hvørt sett
            startTime = md.date2num(datetime.strptime(row.startDate, "%Y-%m-%dT%H:%M:%SZ"))
            stopTime = md.date2num(datetime.strptime(row.stopDate, "%Y-%m-%dT%H:%M:%SZ"))
            setFiles = os.listdir(dfilnavn.split(dfilnavn.split('/')[-1])[0] + row.mappunavn + '/')
            print(setFiles)
            filnavn = []
            for file in setFiles:
                if file == 'zdyb.csv':
                    dypirfil = pd.read_csv(dfilnavn.split(dfilnavn.split('/')[-1])[0] + row.mappunavn + '/' + file)
                    print('funnið dýpið fíĺ')
                elif file == 'zkalib.csv':
                    print('funnið kalib fíl')
                else:
                    filnavn.append(dfilnavn.split(dfilnavn.split('/')[-1])[0] + row.mappunavn + '/' + file)

            signal = []
            timestamp = []
            print('Lesur datafílir')
            for i in range(len(filnavn)):
                print('Lesur:' + filnavn[i])
                if not 'zdyb' in filnavn[i]: # Fyrr var hettar : if 'kalib' in filnavn[i] or 'sg' in filnavn[i]
                    print(filnavn[i])
                    data = pd.read_csv(filnavn[i])
                    signal.append(data['signal'].values)
                    timestamp.append(data['time'])
                else:
                    print('Feilur! ikki kalib í fílnavn')

            tempSet = signal[1]
            plotAvg = []
            for value in tempSet[1:100]:
                plotAvg.append(float(value))
            if np.mean(plotAvg) > 30:
                er_ox = True
                print("Oxygen Plot")
            else:
                print("Tempratur Plot")

            print('Roknar um til datetime')
            flat_timestamp = []
            flat_signal = []
            starttid = 100000000000
            stoptid = 0
            dypir = []
            print(dypirfil)
            dypir_sernr = dypirfil['serial']
            dypir_virdir = dypirfil['d']
            stostadypid = 1
            for i in range(len(dypir_virdir)):  # Finnur størsta dýpið
                if float(dypir_virdir[i]) > stostadypid:
                    stostadypid = dypir_virdir[i]
            print(np.linspace(0, stostadypid, 10))
            ctr = 0
            for i in range(len(filnavn)): # Fyri hvønn fíl
                print('Fílur' + str(i))
                # Finn dýpi á fíli
                hettardypid = -99.9
                print(len(dypirfil))
                for j in range(len(dypirfil)):
                    if str(dypir_sernr[j]) in filnavn[i]:
                        print('funnið dypir á fíli ' + str(dypir_sernr[j]))
                        hettardypid = -dypir_virdir[j]
                flat_timestamp_tmp = []
                flat_signal_tmp = []
                dypir_tmp = []
                for j in range(len(timestamp[i])):
                    try:
                        tmpDatetime = timestamp[i][j]
                        if len(tmpDatetime) > 24:  # nasty máti at hontera millisekund við nógvur sifrum
                            tmpDatetime = tmpDatetime[:len(tmpDatetime) - 3]
                        flat_timestamp_tmp.append(md.date2num(datetime.strptime(tmpDatetime, '%Y-%m-%d_%H:%M:%S.%f')))  # Vanlig ox format
                        tmpSignal = str(signal[i][j])
                        tmpSignal = tmpSignal.replace(',', '.')
                        flat_signal_tmp.append(float(tmpSignal))
                        dypir_tmp.append(hettardypid)
                        ctr += 1
                    #except: # Lorta máti at lesa seaguard data inn, einaferð fari eg at fiksa hettar
                    except Exception as e:
                        try:
                            flat_timestamp_tmp.append(md.date2num(datetime.strptime(timestamp[i][j], '%d.%m.%y_%H:%M:%S')))  # Raw seaguard data
                            tmp = str(signal[i][j])
                            tmp = tmp.replace(',', '.')
                            flat_signal_tmp.append(float(tmp))
                            dypir_tmp.append(hettardypid)
                            ctr += 1
                        except:
                            print('Fuck: ' + str(e))
                            print('Hjálp ' + timestamp[i][j] + ' ' + tmp)
                            print(filnavn[i])
                startIndex = 0
                stopIndex = 0
                for i, ts in enumerate(flat_timestamp_tmp):
                    if ts > startTime:
                        startIndex = i
                        print('Start index er: ' + str(startIndex))
                        break
                for i, ts in enumerate(flat_timestamp_tmp):
                    stopIndex = i
                    if ts > stopTime:
                        print('Stop index er: ' + str(stopIndex))
                        break
                print(startTime)
                print(stopTime)
                flat_timestamp.extend(flat_timestamp_tmp[startIndex:stopIndex])
                flat_signal.extend(flat_signal_tmp[startIndex:stopIndex])
                dypir.extend(dypir_tmp[startIndex:stopIndex])
            tmp = pd.DataFrame(flat_timestamp)
            tmp.to_csv('farts.csv')
            print('Finnur endapunkt í tíðsaksanum')
            for j in range(len(flat_timestamp)):
                if flat_timestamp[j] > stoptid:
                    stoptid = flat_timestamp[j]
                if flat_timestamp[j] < starttid:
                    starttid = flat_timestamp[j]
            n = 2000
            # X, Y = np.meshgrid(flat_timestamp, dypir)
            # f = griddata((flat_timestamp, dypir), flat_signal, (X, Y), method='linear', rescale=False)
            # f = interpolate.interp2d((flat_timestamp, dypir), flat_signal, (X, Y), kind='linear')

            flat_signal = flat_signal[0::50]
            flat_timestamp = flat_timestamp[0::50]
            dypir = dypir[0::50]
            print('Ger meshgrid')


            X, Y = np.meshgrid(np.linspace(starttid, stoptid, n), np.linspace(d_fra, -d_til, len(flat_timestamp)))
            # X, Y = np.mgrid[starttid-10:stoptid+10:100j, -stostadypid-10:d_fra+10]
            print('Interpolerar')
            flat_signal = np.array(flat_signal)
            flat_timestamp = np.array(flat_timestamp)
            dypir = np.array(dypir)
            f = griddata((flat_timestamp, dypir), flat_signal, (X, Y), method='linear', rescale=False)
            ax.set_ylabel('Dýpi [m]')

            if er_ox:
                colormap = 'plasma'
                if c_fra_input != '-1':
                    c_fra = 60
                else:
                    c_fra = c_fra_input
                if c_til_input != '-1':
                    c_til = 130
                else:
                    c_til = c_til_input
                crange = np.arange(c_fra, c_til, 5)
            else:
                colormap = cmocean.cm.thermal
                if c_fra_input != '-1':
                    c_fra = 6
                else:
                    c_fra =c_fra_input
                if c_til_input != '-1':
                    c_til = 11
                else:
                    c_til = c_til_input
                crange = np.arange(c_fra, c_til, 0.5)
            levels_exists = False

            if 'levels' in globals():
                levels_exists = True
            global levels

            if levels_exists:
                c = ax.contourf(X, Y, f, levels=levels, cmap=colormap, extend='both')
            else:
                levels = np.linspace(c_fra, c_til, 200)
                c = ax.contourf(X, Y, f, levels=levels, cmap=colormap, extend='both')
                cbar = fig.colorbar(c, ticks=crange, pad=0.01)
                if er_ox:
                    cbar.set_label('Oxygen Metningur [%]', rotation=270)
                else:
                    cbar.set_label('Hiti [°C]', rotation=270)

            if er_ox:
                crange = [70, 90, 110]
            else:
                crange = np.arange(c_fra, c_til)
                step = 1
                while len(crange) > clintal:
                    crange = np.arange(c_fra, c_til, step)
                    step += 1
            cc = ax.contour(X, Y, f, levels=crange, colors='k')
            ax.clabel(cc, inline=1, fontsize=15, fmt='%2.0f')

            ax.set_ylim(-d_til, -d_fra)

            #ax.xaxis.set_major_locator(MaxNLocator(10))
            ax.xaxis.set_major_locator(md.MonthLocator())
            xt = ax.get_xticks()
            text_timestamps = []
            for i in range(len(xt)):
                tmp = md.num2date(float(xt[i]))
                text_timestamps.append(tmp.strftime("%d %b"))
            try:
                ax.set_xticks(text_timestamps)
            except:
                print('nooo')
            try:
                ax.set_xticklabels(text_timestamps)
            except:
                print('bapokafs')
            ax.scatter(flat_timestamp, dypir, alpha=0.2, s=.5, c='black')
            print(dypir.size)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=1)
    log_e()


def vel_dypir():
    global dfilnavn
    dfilnavn = filedialog.askopenfile(title='Vel Dýpid fíl',
                                      filetypes=(("csv Fílir", "*.csv"), ("all files", "*.*"))).name


def goymmynd(fig):
    log_b()
    filnavn = filedialog.asksaveasfilename(parent=root, title="Goym mynd",  filetypes=(("pdf Fílur", "*.pdf"), ("png Fílur", "*.png"), ("jpg Fílur", "*.jpg")))
    print('Goymir mynd')
    fig.savefig(filnavn, dpi=600, bbox_inches='tight')
    print('Liðugt')
    log_e()

########################################################################################################################
#                                                                                                                      #
#                                                  Seaguard data                                                       #
#                                                                                                                      #
########################################################################################################################


def seaguard_data(frame, root2):
    global root
    root = root2
    for widget in frame.winfo_children():
        widget.destroy()
    Label(frame, text='Termistorkeda', font='Helvetica 18 bold').pack(side=TOP)
    Label(frame, text='Les seaguard data').pack(side=TOP, anchor=W)

    menuFrame = Frame(frame)
    menuFrame.pack(side=TOP, fill=X, expand=False, anchor=N)

    Button(menuFrame, text='Vel Seaguard fíl', command=lambda: vel_fil()).pack(side=LEFT)

    Button(menuFrame, text='Eksportera fíl', command=lambda: eksportera(v)).pack(side=LEFT)

    v = IntVar()
    temp_radBtn = Radiobutton(frame, text='Tempratur', variable=v, value=1)
    temp_radBtn.pack(side=TOP, anchor=W)
    o2metn = Radiobutton(frame, text='Oxygen metningur', variable=v, value=2)
    o2metn.pack(side=TOP, anchor=W)
    o2cong = Radiobutton(frame, text='Oxygen upploysiligheit', variable=v, value=3)
    o2cong.pack(side=TOP, anchor=W)
    absSpeed = Radiobutton(frame, text='Streyferð (ABS)', variable=v, value=4)
    absSpeed.pack(side=TOP, anchor=W)



    log_frame = Frame(frame, height=300)
    log_frame.pack(fill=X, expand=False, side=BOTTOM, anchor=W)
    gerlog(log_frame, root)


def eksportera(v):
    log_b()
    global filnavn
    data = pd.read_csv(filnavn, sep='\t', skiprows=1)
    print(data.columns.values)
    timestamp = data['Time tag (Gmt)'].values
    print(timestamp[0])
    for i in range(len(timestamp)):
        timestamp[i] = timestamp[i].replace(' ', '_')
    print(timestamp[0])
    print(v.get())
    if v.get()==2:
        try:
            o2 = data['AirSaturation(%)']
        except:
            o2 = data['AirSaturation']
    elif v.get()==1:
        o2 = data['Temperature(Deg.C)']
    elif v.get()==4:
        try:
            o2 = data['Abs Speed(cm/s)']
        except:
            o2 = data['Abs Speed']
    savefilnavn = filedialog.asksaveasfilename(title='Goym fíl', filetypes=(("csv Fílir", "*.csv"), ("all files", "*.*")))
    data_tosave = pd.DataFrame({'time': timestamp, 'signal': o2})
    data_tosave.to_csv(savefilnavn, index=False)
    log_e()


def vel_fil():
    global filnavn
    filnavn = filedialog.askopenfile(title='Vel Seaguard fíl', filetypes=(("txt Fílir", "*.txt"), ("csv Fílir", "*.csv"),
                                                                 ("all files", "*.*"))).name

########################################################################################################################
#                                                                                                                      #
#                                                   Kalibrering                                                        #
#                                                                                                                      #
########################################################################################################################


def kalibering(frame, root2):
    global root
    global filnavn
    filnavn = '/home/johannus/Documents/FA_Ingestion_engine/Kort_Data/Syðradalur.txt'
    root = root2
    for widget in frame.winfo_children():
        widget.destroy()
    Label(frame, text='Termistorkeda', font='Helvetica 18 bold').pack(side=TOP)
    Label(frame, text='Liner Kalibrering (y=ax+b)').pack(side=TOP, anchor=W)
    menuFrame = Frame(frame)
    menuFrame.pack(side=TOP, fill=X, expand=False, anchor=N)

    velMappuBtn = Button(menuFrame, text='Les inn kaliberingskofficientar', command=lambda: les_kalib_kofficientar(kalib_tree))
    velMappuBtn.pack(side=LEFT)

    velfilir_Btn = Button(menuFrame, text='Vel fílir at kalibrera', command=lambda: velFilir())
    velfilir_Btn.pack(side=LEFT)

    rokna_btn = Button(menuFrame, text='Rokna', command=lambda: rokna_kalib(kalib_tree))
    rokna_btn.pack(side=LEFT)

    log_frame = Frame(frame, height=300)
    log_frame.pack(fill=X, expand=False, side=BOTTOM, anchor=W)
    gerlog(log_frame, root)

    treeView_frame = Frame(frame)
    treeView_frame.pack(fill=Y, expand=False, side=RIGHT, anchor=N)
    kalib_tree = ttk.Treeview(treeView_frame)
    kalib_tree["columns"] = ("a", "b")
    kalib_tree.column("#0", width=100)
    kalib_tree.column("#1", width=100)
    kalib_tree.column("#2", width=100)
    scrollbar = Scrollbar(treeView_frame, orient=VERTICAL)
    scrollbar.config(command=kalib_tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    kalib_tree.heading("a", text="a")
    kalib_tree.heading("b", text="b")
    kalib_tree.pack(fill=BOTH, expand=True, side=TOP, anchor=W)


def rokna_kalib(kalib_tree):
    global filnavn
    kalib_tree_ting = kalib_tree.get_children()
    a = []
    b = []
    text = []
    if not os.path.isdir(str(os.path.dirname(filnavn[0]))+'/kalib'):
        os.mkdir(os.path.dirname(filnavn[0])+'/kalib')
    for i in range(len(kalib_tree_ting)):
        tmp = kalib_tree.item(kalib_tree_ting[i])["values"]
        a.append(float(tmp[0]))
        b.append(float(tmp[1]))
        text.append(kalib_tree.item(kalib_tree_ting[i])["text"])

    for i in range(len(filnavn)):
        print('Lesur ' + filnavn[i])
        data = pd.read_csv(filnavn[i])
        kalibrera_data = a[i] * data['signal'] + b[i]
        nyttfilnavn = filnavn[i]
        nyttfilnavn = os.path.dirname(filnavn[i]) + '/kalib/' + nyttfilnavn[len(os.path.dirname(filnavn[i])):len(filnavn[i])] + '_kalib.csv'
        print('Goymur fíl ' + nyttfilnavn)
        filur_at_goyma = pd.DataFrame({'time': data['time'], 'signal': kalibrera_data})
        filur_at_goyma.to_csv(nyttfilnavn, index=False)


    print('TODO')

########################################################################################################################
#                                                                                                                      #
#                                                    Decimering                                                        #
#                                                                                                                      #
########################################################################################################################


def decimering(frame, root2):
    global root
    global filnavn
    filnavn = '/home/johannus/Documents/FA_Ingestion_engine/Kort_Data/Syðradalur.txt'
    root = root2
    for widget in frame.winfo_children():
        widget.destroy()
    Label(frame, text='Termistorkeda', font='Helvetica 18 bold').pack(side=TOP)
    Label(frame, text='Decimering').pack(side=TOP, anchor=W)

    menuFrame = Frame(frame)
    menuFrame.pack(side=TOP, fill=X, expand=False, anchor=N)

    velMappuBtn = Button(menuFrame, text='Vel Fíl', command=lambda: velFilir())
    velMappuBtn.pack(side=LEFT)

    rokna_btn = Button(menuFrame, text='Rokna', command=lambda: rokna(int(n_entry.get())))
    rokna_btn.pack(side=LEFT)

    Label(menuFrame, text='Decimeringskofficientur:').pack(side=LEFT)

    n_entry = Entry(menuFrame, width=2)
    n_entry.pack(side=LEFT)
    n_entry.insert("end", '2')

    log_frame = Frame(frame, height=300)
    log_frame.pack(fill=X, expand=False, side=BOTTOM, anchor=W)
    gerlog(log_frame, root)


def velFilir(typa='std'):
    global filnavn
    print('Vel fíl ' + typa)
    if typa == 'std':
        filnavn = filedialog.askopenfilenames(title='Vel fílir', filetypes=(("csv Fílir", "*.csv"),
                                                                            ("all files", "*.*")))
    else:
        filnavn = filedialog.askopenfilenames(title='Vel ' + typa + ' fílir', filetypes=((typa + " Fílir", "*" + typa),
                                                                                                ("all files", "*.*")))

def les_kalib_kofficientar(kalib_tree):
    global kalib_filnavn
    kalib_filnavn = filedialog.askopenfile(title='Vel fíl', filetypes=(("csv Fílir", "*.csv"), ("txt Fílir", "*.txt"),
                                                                 ("all files", "*.*"))).name
    print(kalib_filnavn)
    kalib_tree.delete(*kalib_tree.get_children())
    data = pd.read_csv(kalib_filnavn)
    a_data = data['a'].values
    b_data = data['b'].values
    legends = data['serial'].values
    print(legends)
    for i in range(len(data)):
        kalib_tree.insert("", 0, text=legends[len(data)-i-1], values=(a_data[len(data) - i - 1], b_data[len(data) - i - 1]))


def rokna(q):
    log_b()
    global filnavn
    if not os.path.isdir(str(os.path.dirname(filnavn[0]))+'/'+str(q)):
        os.mkdir(os.path.dirname(filnavn[0])+'/'+str(q))
    for fil_index in range(len(filnavn)):
        print('Lesur fíl ' + filnavn[fil_index])
        decimated_time = []
        if 'd' in filnavn[fil_index]:
            fil_data = pd.read_csv(filnavn[fil_index])
            raw_data = fil_data['signal']
            date = fil_data['time']
            print('Decimerar tíð')
            for i in range(len(fil_data)):

                if i % q == 0:
                    decimated_time.append(date[i])
        else:
            fil_data = pd.read_csv(filnavn[fil_index], encoding='latin', skiprows=22, sep='\s+')
            print(fil_data.columns.values)
            raw_data = fil_data['Time']
            date = fil_data['Date']
            time = fil_data['&']
            print('Decimerar tíð')
            for i in range(len(fil_data)):
                if i % q == 0:
                    decimated_time.append(date[i] + '_' + time[i])

        print('Decimerar data')
        decimated_data = sig.decimate(raw_data, q, 3, ftype='fir')

        nyttfilnavn = filnavn[fil_index]
        nyttfilnavn = os.path.dirname(filnavn[fil_index]) + '/' + str(q) + '/' + nyttfilnavn[len(os.path.dirname(filnavn[fil_index]))+1:len(filnavn[fil_index])] + 'd' + str(q) + '.csv'
        print('Goymur fíl ' + nyttfilnavn)
        filur_at_goyma = pd.DataFrame({'time': decimated_time, 'signal': decimated_data})
        filur_at_goyma.to_csv(nyttfilnavn, index=False)

    log_e()