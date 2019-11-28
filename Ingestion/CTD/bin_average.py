from tkinter import *
from tkinter import filedialog
from misc.faLog import gerlog, log_e, log_b, log_print, log_w, log_clear
import pandas as pd
import getpass # Til at fáa brúkaranavn
import numpy as np
import os
from shutil import copyfile
import fileinput
import subprocess
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import messagebox
from misc.sha2calc import get_hash
import Ingestion.CTD.bin_average_aux.ba_gui as ba_gui
from Ingestion.CTD.bin_average_aux.quality_control import qcontrol
import Ingestion.CTD.skraset_stodir
textsize = 16


def bin_average_frame(frame, root2):
    #mappunavn = './Ingestion/CTD/Lokalt_Data/2019-09-18/75_All_ASCII_Out'
    mappunavn = './Ingestion/CTD/Lokalt_Data/2019-01-17/Processed/ASCII_ALL'
    mappunavn_dict = {'mappunavn': mappunavn}
    root = root2
    for widget in frame.winfo_children():
        widget.destroy()
    Label(frame, text='Seabird SBE 25 CTD', font='Helvetica 18 bold').pack(side=TOP)
    Label(frame, text='Bin Average').pack(side=TOP, anchor=W)
    mappunavn_dict['controlsFrame'] = Frame(frame)
    mappunavn_dict['controlsFrame'].pack(side=TOP, anchor=W)
    velMappuBtn = Button(mappunavn_dict['controlsFrame'], text='Vel Fílir', command=lambda: velFil(mappunavn_dict))
    velMappuBtn.pack(side=LEFT, anchor=W)

    processBtn = Button(mappunavn_dict['controlsFrame'], text='Les inn', command=lambda: processera(root, fig, canvas, Quality_frame, mappunavn_dict))
    processBtn.pack(side=LEFT, anchor=W)

    Right_frame = Frame(frame)
    Right_frame.pack(fill=BOTH, expand=False, side=RIGHT, anchor=N)

    fig = Figure(figsize=(12, 8), dpi=100)
    plot_frame = Frame(frame, borderwidth=1, highlightbackground="green", highlightcolor="green", highlightthickness=1)
    plot_frame.pack(fill=BOTH, expand=True, side=LEFT, anchor=N)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)

    Quality_frame = Frame(Right_frame)
    Quality_frame.pack(fill=BOTH, expand=True, side=TOP, anchor=W)
    log_frame = Frame(Right_frame, height=300, width=600, borderwidth=1, highlightbackground="green", highlightcolor="green", highlightthickness=1)
    log_frame.pack(fill=X, expand=False, side=BOTTOM, anchor=W)
    gerlog(log_frame, root)
    mappunavn_dict['filur'] = 0

    mappunavn_dict['continuebtn'] = Button(Quality_frame, text='Halt áfram', command=lambda: Ingestion.CTD.skraset_stodir(frame, root2))
    mappunavn_dict['continuebtn'].pack(side=TOP, anchor=W)

    processera(root, fig, canvas, Quality_frame, mappunavn_dict)

def velFil(mappunavn):
    mappunavn['mappunavn'] = filedialog.askdirectory(title='Vel túramappu', initialdir='./Ingestion/CTD/Lokalt_Data/')


def processera(root, fig, canvas, Quality_frame, mappunavn_dict):
    mappunavn = mappunavn_dict['mappunavn']
    log_b()
    midlingstid = 2 # sek
    fig.clf()
    ax = fig.subplots()
    if os.path.exists(mappunavn):
        filnavn = os.listdir(mappunavn)
    else:
        messagebox.showerror("Feilur", "Mappan er ikki til")
        return
    filnavn.sort()
    mappunavn_dict['toggle_temp'] = 0
    mappunavn_dict['toggle_FlECO'] = 0
    mappunavn_dict['toggle_Sbeox0PS'] = 0
    mappunavn_dict['toggle_Sal00'] = 0
    mappunavn_dict['toggle_par'] = 0
    mappunavn_dict['toggle_C0mS'] = 0
    data = pd.read_csv(mappunavn + '/' + filnavn[mappunavn_dict['filur']], encoding='latin-1') # Les fíl

    list_of_casts = os.listdir(mappunavn)
    list_of_casts.sort()
    parent_folder = os.path.dirname(os.path.dirname(mappunavn))

    # Um mappurnar ikki eru til, ger tær
    if not os.path.exists(parent_folder + '/Processed/7_Bin_Average/'):
        os.mkdir(parent_folder + '/Processed/7_Bin_Average/')
    if not os.path.exists(parent_folder + '/ASCII/'):
        os.mkdir(parent_folder + '/ASCII/')
        os.mkdir(parent_folder + '/ASCII/ASCII_Downcast')
    if not os.path.isdir(parent_folder + '/Processed/ASCII_Upcast'):
        os.mkdir(parent_folder + '/Processed/ASCII_Upcast')
    # Kanna um metadatamappan er til
    if not os.path.isdir(parent_folder + '/ASCII/ASCII_Downcast/metadata'):
        os.makedirs(parent_folder + '/ASCII/ASCII_Downcast/metadata')  # Um ikki, ger hana

    metadata, finished_processing = ba_gui.refresh_qframe(Quality_frame, list_of_casts, parent_folder, filnavn, mappunavn_dict)
    log_print('Finished_processing?: ' + str(finished_processing))
    if finished_processing:
        pass
    #        mappunavn_dict['continuebtn'].lift()
    Label(Quality_frame, text=('―'*20), font=("Courier", textsize)).pack(side=TOP, anchor=W)
    quality_subframe = Frame(Quality_frame)
    quality_subframe.pack(fill=BOTH, expand=True, side=TOP, anchor=W)

    depth = data[data.columns[0]]
    time_fulllength = data['TimeS']
    log_print(time_fulllength)
    maxd = max(depth)
    start_index = 0
    for time in data.TimeS:
        start_index +=1
        if time > 0:
            break
    timeAx = data.TimeS[start_index:]
    ax.plot(timeAx, depth[start_index:])
    ax.set_ylim(-1, maxd+1)
    ax.set_xlabel('Tíð [s]')
    ax.set_ylabel('Dýpið [m]', color='k')
    myvar = []
    n_midlingspunktir = int(np.ceil(midlingstid / (max(data.TimeS) / len(data))))
    dypid = data[data.columns[0]]
    for i in range(len(data[data.columns[0]])-2):
        myvar.append(np.var(dypid[i:i+n_midlingspunktir]))

    # Rokna ferð á CTD
    diff_d = []
    for i in range(1, len(depth)):
        diff_d.append((depth[i-1]-depth[i])/(time_fulllength.iloc[i-1]-time_fulllength.iloc[i]))
    states = ["PreSoak", "soak_start", "soak_stop", "downcast_start", "downcast_stop", "upcast_start", "upcast_stop"]
    current_stat = states[0]
    log_print(current_stat)

    soaktime = -1
    soak_depth = -1

    if not metadata:
        soak_start = -1
        soak_stop = -1
        downcast_start = -1
        downcast_stop = -1
        upcast_stop = -1
        for i, d in enumerate(depth):  # Hettar er kodan ið finnur nær tey ymsku tingini henda
            if current_stat == "PreSoak":  # Bíða 5 sek áðrenn byrja verður at leita eftir hvar soak byrjar
                log_print(time_fulllength[i])
                if time_fulllength[i] > 5:
                    current_stat = "soak_start"
            if current_stat == "soak_start":
                if d < 5:
                    continue
                else:
                    if np.var(dypid[i:i + n_midlingspunktir]) < 0.01:
                        soak_start = i
                        current_stat = "soak_stop"
                    #    log_print('Farts '+ str(i))
            elif current_stat == "soak_stop":
                if np.var(dypid[i:i + n_midlingspunktir]) > 0.01:
                    soak_stop = i + n_midlingspunktir
                    soaktime = time_fulllength[soak_stop] - time_fulllength[soak_start]
                    soak_depth = np.round(np.mean(dypid[soak_start:soak_stop]), 3)
                    current_stat = "downcast_prepare"
            elif current_stat == "downcast_prepare":
                if d > 5:
                    continue
                else:
                    if d < 2 and np.var(dypid[i:i + n_midlingspunktir]) < 0.01:
                        current_stat = "downcast_start"
            elif current_stat == "downcast_start":
                if np.var(dypid[i:i + n_midlingspunktir]) > 0.01:
                    downcast_start = i + n_midlingspunktir
                    current_stat = "downcast_stop"
            elif current_stat == "downcast_stop":
                # if np.var(dypid[i:i+n_midlingspunktir]) < 0.01 and d > 5:
                #    downcast_stop = i
                #    current_stat = "upcast_start"
                if d == maxd:
                    downcast_stop = i
                    current_stat = "upcast_stop"
            elif current_stat == "upcast_stop":
                if np.var(dypid[i:i + n_midlingspunktir]) > 0.01:
                    upcast_stop = i
            else:
                pass
    else:
        log_print('Lesur goymd event virðir')
        soak_start = int(metadata['soak_start'])
        soak_stop = int(metadata['soak_stop'])
        downcast_start = int(metadata['downcast_start'])
        downcast_stop = int(metadata['downcast_stop'])
        upcast_stop = int(metadata['upcast_stop'])

    if os.path.isdir(parent_folder + '/RAW/'):
        # TODO: vit eru komin hertil
        raw_filar = os.listdir(parent_folder + '/RAW/')
        print(raw_filar)
        raw_filnavn = '-1'
        hesin_filur = filnavn[mappunavn_dict['filur']].upper()[:]
        for raw_file in raw_filar: # Hettar finnur rætta xml fílin
            log_print(raw_file)
            log_print(hesin_filur)
            if raw_file[0:7].upper() == hesin_filur[0:7]:
                print('Alright')
                raw_filnavn = raw_file
        if raw_filnavn == '-1':
            log_w('Eingin raw fílur funnin')
            return
        #raw_filnavn = raw_filar[filur]
        print('Lesur raw fíl: ' + raw_filnavn)
        with open(parent_folder + '/RAW/' + raw_filnavn, 'r') as raw_file:
            raw_data = raw_file.read()
        raw_data = raw_data.split('*END*')
        raw_data = raw_data[1].split('\n')
        pump_on = -1
        pump_off = -1
        lastLine = 0
        for i, line in enumerate(raw_data):
            if line:
                if line[0] == '1' and lastLine == '0':
                    pump_on = i
                elif line[0] == '0' and lastLine == '1':
                    pump_off = i
                lastLine = line[0]
        log_print('Pump ' + str(pump_on))
        if pump_on != -1:
            ax.plot([pump_on/16, pump_on/16], [-100, 100], ':')
            log_print('Pumpan tendraði aftaná: ' + str(pump_on/16) + ' sek')

        if pump_off != -1:
            log_print('Pumpan sløknaði aftaná: ' + str(pump_off/16) + ' sek')
            ax.plot([pump_off/16, pump_off/16], [-100, 100], ':')
        bin_stodd = 1 # [m]
    if downcast_start != -1:
        downcast_start_d = dypid[downcast_start]
    if downcast_stop != -1:
        downcast_stop_d = dypid[downcast_stop]

    event_dict = {'time_fulllength': time_fulllength, 'soak_start': soak_start, 'soak_stop': soak_stop, 'downcast_start': downcast_start, 'downcast_stop': downcast_stop, 'upcast_stop': upcast_stop}

    ba_gui.kanna_events(event_dict, log_w)

    soak_line_dict = {'soak_start_line': ax.plot([time_fulllength[event_dict['soak_start']], time_fulllength[event_dict['soak_start']]], [-100, 100], 'k'), 'soak_stop_line': ax.plot([time_fulllength[event_dict['soak_stop']], time_fulllength[event_dict['soak_stop']]], [-100, 100], 'k'),
                      'downcast_start_line': ax.plot([time_fulllength[event_dict['downcast_start']], time_fulllength[event_dict['downcast_start']]], [-100, 100], 'k'),
                      'downcast_stop_line': ax.plot([time_fulllength[event_dict['downcast_stop']], time_fulllength[event_dict['downcast_stop']]], [-100, 100], 'k'),
                      'upcast_stop_line': ax.plot([time_fulllength[event_dict['upcast_stop']], time_fulllength[event_dict['upcast_stop']]], [-100, 100], 'k')}

    event_dict['selected_event'] = 0
    zoomed_in_dict = {'zoomed_in':  False, 'onlyDowncast': False}
    if soak_start != -1:
        soak_line_dict['annotation'] = ax.annotate('Soak Start',
                                                   xy=(time_fulllength[soak_start], maxd + 1),
                                                   xytext=(time_fulllength[soak_start], maxd + 2),
                                                   xycoords='data',
                                                   textcoords='data',
                                                   ha='center',
                                                   arrowprops=dict(arrowstyle="->"))

    if True: # Um flaggi ikki er 0, markera mátingina reyða
        fra = 0
        til = 1
        lastflag = 0
        for i, flag in enumerate(data.Flag):
            if lastflag == 0 and flag != 0:
                fra = i
                til = 1
            if lastflag != 0 and flag == 0:
                til = i
                farvaHer = np.zeros((len(data), 1))
                farts = []
                for i in range(len(data)):
                    fra = int(fra)
                    til = int(til)
                    if (i > fra) and (i < til):
                        farvaHer[i] = 1
                        farts.append(True)
                    else:
                        farts.append(False)
                ax.fill_between(data.TimeS, -100, 0, where=farts, facecolor='red', alpha=0.2)

            lastflag = flag

        log_print('markeraokid')
        log_print(fra)
        log_print(til)

    for column in data.columns.values:
        button1 = Button(mappunavn_dict['controlsFrame'], text=column, relief=SUNKEN)
        button1.pack(side=LEFT)

    qcontrol(quality_subframe, depth, event_dict, pump_on, filnavn[mappunavn_dict['filur']])

    def key(event):
        update_annotations = False
        update_qframe = False
        if zoomed_in_dict['zoomed_in']:
            move_amount = 1
        else:
            move_amount = 8
        log_print(event.keysym)

        if event.keysym == 'w':
            if mappunavn_dict['filur'] < len(filnavn)-1:
                mappunavn_dict['filur'] += 1
                update_qframe = True
        elif event.keysym == 'q':
            if mappunavn_dict['filur'] != 0:
                mappunavn_dict['filur'] -= 1
                update_qframe = True
        elif event.keysym == 'e':
            if zoomed_in_dict['onlyDowncast']:
                zoomed_in_dict['onlyDowncast'] = False
                ax.set_xlim(0, time_fulllength[len(time_fulllength) - 1])
                log_print('Downcast')
            else:
                zoomed_in_dict['onlyDowncast'] = True
                log_print('All')
                ax.set_xlim(time_fulllength[event_dict['downcast_start']], time_fulllength[event_dict['downcast_stop']])
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        elif event.keysym == '1':
            if mappunavn_dict['toggle_temp'] == 0:
                mappunavn_dict['toggle_temp'] = 1
                mappunavn_dict['ax2'] = ax.twinx()
                mappunavn_dict['yplt2'] = mappunavn_dict['ax2'].plot(timeAx, data.T068C[start_index:], color='red')
                mappunavn_dict['ax2'].set_ylabel('T068C', color='k')
                mappunavn_dict['ax2'].set_ylim(min(data.T068C[event_dict['soak_stop']:])-0.1, max(data.T068C) + 0.1)
            else:
                mappunavn_dict['toggle_temp'] = 0
                mappunavn_dict['yplt2'].pop(0).remove()
                mappunavn_dict['ax2'].axis('off')
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        elif event.keysym == '2':
            if mappunavn_dict['toggle_FlECO'] == 0:
                mappunavn_dict['toggle_FlECO'] = 1
                mappunavn_dict['ax3'] = ax.twinx()
                mappunavn_dict['yplt3'] = mappunavn_dict['ax3'].plot(timeAx, data['FlECO-AFL'][start_index:], color='green')
                mappunavn_dict['ax3'].set_ylabel('FlECO - AFL', color='k')
                mappunavn_dict['ax3'].set_ylim(min(data['FlECO-AFL'][event_dict['soak_stop']:]) - 0.1, max(data['FlECO-AFL'][event_dict['soak_stop']:event_dict['upcast_stop']]) + 0.1)
            else:
                mappunavn_dict['toggle_FlECO'] = 0
                mappunavn_dict['yplt3'].pop(0).remove()
                mappunavn_dict['ax3'].axis('off')
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        elif event.keysym == '3':
            if mappunavn_dict['toggle_Sbeox0PS'] == 0:
                mappunavn_dict['toggle_Sbeox0PS'] = 1
                mappunavn_dict['ax4'] = ax.twinx()
                mappunavn_dict['yplt4'] = mappunavn_dict['ax4'].plot(timeAx, data['Sbeox0PS'][start_index:], color='lightblue')
                mappunavn_dict['ax4'].set_ylabel('Sbeox0PS', color='k')
                mappunavn_dict['ax4'].set_ylim(min(data['Sbeox0PS'][event_dict['soak_stop']:]) - 0.1, max(data['Sbeox0PS'][event_dict['soak_stop']:]) + 0.1)
            else:
                mappunavn_dict['toggle_Sbeox0PS'] = 0
                mappunavn_dict['yplt4'].pop(0).remove()
                mappunavn_dict['ax4'].axis('off')
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        elif event.keysym == '4':
            if mappunavn_dict['toggle_par'] == 0:
                mappunavn_dict['toggle_par'] = 1
                mappunavn_dict['ax5'] = ax.twinx()
                mappunavn_dict['yplt5'] = mappunavn_dict['ax5'].plot(timeAx, data['Par/sat/log'][start_index:], color='peru')
                mappunavn_dict['ax5'].set_ylabel('Par/sat/log', color='k')
                mappunavn_dict['ax5'].set_ylim(min(data['Par/sat/log'][event_dict['soak_stop']:event_dict['upcast_stop']]) - 0.1, max(data['Par/sat/log'][event_dict['soak_stop']:event_dict['upcast_stop']]) + 0.1)
            else:
                mappunavn_dict['toggle_par'] = 0
                mappunavn_dict['yplt5'].pop(0).remove()
                mappunavn_dict['ax5'].axis('off')
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        elif event.keysym == '5':
            if mappunavn_dict['toggle_Sal00'] == 0:
                mappunavn_dict['toggle_Sal00'] = 1
                mappunavn_dict['ax6'] = ax.twinx()
                mappunavn_dict['yplt6'] = mappunavn_dict['ax6'].plot(timeAx, data['Sal00'][start_index:], color='lightgreen')
                mappunavn_dict['ax6'].set_ylabel('Sal00', color='k')
                mappunavn_dict['ax6'].set_ylim(min(data['Sal00'][event_dict['soak_stop']:event_dict['upcast_stop']]) - 0.1, max(data['Sal00'][event_dict['soak_stop']:event_dict['upcast_stop']]) + 0.1)
            else:
                mappunavn_dict['toggle_Sal00'] = 0
                mappunavn_dict['yplt6'].pop(0).remove()
                mappunavn_dict['ax6'].axis('off')
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        elif event.keysym == '6':
            if mappunavn_dict['toggle_C0mS'] == 0:
                mappunavn_dict['toggle_C0mS'] = 1
                mappunavn_dict['ax7'] = ax.twinx()
                mappunavn_dict['yplt7'] = mappunavn_dict['ax7'].plot(timeAx, data['C0mS/cm'][start_index:], color='gold')
                mappunavn_dict['ax7'].set_ylabel('C0mS/cm', color='k')
                mappunavn_dict['ax7'].set_ylim(min(data['C0mS/cm'][event_dict['soak_stop']:event_dict['upcast_stop']]) - 0.1, max(data['C0mS/cm'][event_dict['soak_stop']:event_dict['upcast_stop']]) + 0.1)
            else:
                mappunavn_dict['toggle_C0mS'] = 0
                mappunavn_dict['yplt7'].pop(0).remove()
                mappunavn_dict['ax7'].axis('off')
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=1)

            #C0mS/cm
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=1)

            #Sbeox0PS
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=1)


        elif event.keysym == 'Return':
            log_b()
            log_print('Calculating')
            log_print(data.columns.values)

            downcast_Data = pd.DataFrame({'DepSM': np.round(data.DepSM.iloc[event_dict['downcast_start']:event_dict['downcast_stop']], 7)})
            upcast_Data = pd.DataFrame({'DepSM': np.round(data.DepSM.iloc[event_dict['downcast_stop']:event_dict['upcast_stop']], 7)})

            for column in data.columns.values:
                if column != "DepSM":
                    downcast_Data = downcast_Data.join(pd.DataFrame({column: np.round(data[column].iloc[event_dict['downcast_start']:event_dict['downcast_stop']], 7)}))
                    upcast_Data = upcast_Data.join(pd.DataFrame({column: np.round(data[column].iloc[event_dict['downcast_stop']:event_dict['upcast_stop']], 7)}))
            # Og goym dataði í mappunum
            downcast_Data.to_csv(parent_folder + '/ASCII/ASCII_Downcast/' + filnavn[mappunavn_dict['filur']], index=False)
            upcast_Data.to_csv(parent_folder + '/Processed/ASCII_Upcast/' + filnavn[mappunavn_dict['filur']], index=False)
            # Roknar kvalitet
            log_print('Assesing quality')
            summary = qcontrol(quality_subframe, depth, event_dict, pump_on, filnavn[mappunavn_dict['filur']])
            confirmation = False
            if summary['downcast_quality'] < 0:
                if messagebox.askyesno('Vátta', 'Ávaring!\nKvaliteturin á kastinum er undir 0\n Vátta at allir parametrar eru rættir'):
                    confirmation = True
            else:
                confirmation = True
            if confirmation:
                # Hettar ger metadatafílin
                metadatafile = 'key,value\n'
                metadatafile += 'Data_File_Name,' + filnavn[mappunavn_dict['filur']] + '\n'
                sha256_hash = get_hash(parent_folder + '/ASCII/ASCII_Downcast/' + filnavn[mappunavn_dict['filur']])
                metadatafile += 'sha256_hash,' + sha256_hash + '\n'
                metadatafile += 'processed_by,' + getpass.getuser() + '\n'
                for key, value in summary.items():
                    metadatafile += key + ',' + str(value) + '\n'
                metadatafile += 'soak_start,' + str(event_dict['soak_start']) + '\n'
                metadatafile += 'soak_stop,' + str(event_dict['soak_stop']) + '\n'
                metadatafile += 'downcast_start,' + str(event_dict['downcast_start']) + '\n'
                metadatafile += 'downcast_stop,' + str(event_dict['downcast_stop']) + '\n'
                metadatafile += 'upcast_stop,' + str(event_dict['upcast_stop']) + '\n'
                log_print(metadatafile)
                # Og her verður metadata fílurin goymdur
                text_file = open(parent_folder + '/ASCII/ASCII_Downcast/metadata/' + filnavn[mappunavn_dict['filur']].split('.')[0] + '_metadata.csv', "w")
                text_file.write(metadatafile)
                text_file.close()
                update_qframe = True



                with fileinput.FileInput('/home/johannus/.wine/drive_c/Program Files (x86)/Sea-Bird/SBEDataProcessing-Win32/Settings/BinAvg(1mcustomstart).psa', inplace=True, backup='.bak') as file:
                    for line in file:
                        print(line.replace('-77', str(data.iloc[event_dict['downcast_start'], 1])), end='')

                turdato = os.path.dirname(os.path.dirname(mappunavn)).split('/')[-1]
                subprocess.call(['wine', 'C:/Program Files (x86)/Sea-Bird/SBEDataProcessing-Win32/SBEBatch.exe',
                                 "C:/Program Files (x86)/Sea-Bird/SBEDataProcessing-Win32/Settings/8_Bin_Average(1m-customstart).txt",
                                 str('Z:' + os.getcwd() + '/Ingestion/CTD/Lokalt_Data/' + turdato + '/Processed/6_Window_Filter/' + filnavn[mappunavn_dict['filur']].split('.')[0]),
                                 str('Z:' + os.getcwd() + '/Ingestion/CTD/Lokalt_Data/' + turdato + '/Processed/7_Bin_Average'), '#m'])
                subprocess.call(['wine', 'C:/Program Files (x86)/Sea-Bird/SBEDataProcessing-Win32/SBEBatch.exe',
                                 "C:/Program Files (x86)/Sea-Bird/SBEDataProcessing-Win32/Settings/9_ASCII_Out.txt",
                                 str('Z:' + os.getcwd() + '/Ingestion/CTD/Lokalt_Data/' + turdato + '/Processed/7_Bin_Average/' + filnavn[mappunavn_dict['filur']].split('.')[0]),
                                 str('Z:' + os.getcwd() + '/Ingestion/CTD/Lokalt_Data/' + turdato + '/ASCII'), '#m'])

                log_print('Done exporting')
            log_e()
        elif event.keysym == 'l':
            if not zoomed_in_dict['zoomed_in']:
                event_dict['selected_event'] += 1
                update_annotations = True
        elif event.keysym == 'h':
            if not zoomed_in_dict['zoomed_in']:
                event_dict['selected_event'] -= 1
                update_annotations = True
        elif event.keysym == 'j':
            if event_dict['selected_event'] == 0:
                event_dict['soak_start'] -= move_amount
            elif event_dict['selected_event'] == 1:
                event_dict['soak_stop'] -= move_amount
            elif event_dict['selected_event'] == 2:
                event_dict['downcast_start'] -= move_amount
            elif event_dict['selected_event'] == 3:
                event_dict['downcast_stop'] -= move_amount
            elif event_dict['selected_event'] == 4:
                event_dict['upcast_stop'] -= move_amount
        elif event.keysym == 'k':
            if event_dict['selected_event'] == 0:
                event_dict['soak_start'] += move_amount
            elif event_dict['selected_event'] == 1:
                event_dict['soak_stop'] += move_amount
            elif event_dict['selected_event'] == 2:
                event_dict['downcast_start'] += move_amount
            elif event_dict['selected_event'] == 3:
                event_dict['downcast_stop'] += move_amount
            elif event_dict['selected_event'] == 4:
                event_dict['upcast_stop'] += move_amount
        elif event.keysym == 'i':
            if not zoomed_in_dict['zoomed_in']:
                zoomed_in_dict['zoomed_in'] = True
                ba_gui.zoom_in(event_dict['selected_event'], ax, event_dict, depth)
                canvas.draw()
        elif event.keysym == 'o':
            ax.set_xlim(0, time_fulllength[len(time_fulllength)-1])
            ax.set_ylim(-1, maxd + 1)
            zoomed_in_dict['zoomed_in'] = False
            canvas.draw()
        elif event.keysym == 'space':
            log_clear()
            processera(root, fig, canvas, Quality_frame, mappunavn_dict)
        elif event.keysym == 'onehalf':
            qcontrol(quality_subframe, depth, event_dict, pump_on, filnavn[mappunavn_dict['filur']])
        elif event.keysym == 'Delete':
            if os.path.exists(parent_folder + '/ASCII/ASCII_Downcast/metadata/' + filnavn[mappunavn_dict['filur']].split('.')[0] + '_do_not_use_.csv'):
                if messagebox.askyesno('Vátta', 'Strika at casti ikki skal brúkast?'):
                    os.remove(parent_folder + '/ASCII/ASCII_Downcast/metadata/' + filnavn[mappunavn_dict['filur']].split('.')[0] + '_do_not_use_.csv')
            else:
                if messagebox.askyesno('Vátta', 'Markera hettar casti sum tað ikki skal brúkast?'):
                    text_file = open(parent_folder + '/ASCII/ASCII_Downcast/metadata/' + filnavn[mappunavn_dict['filur']].split('.')[0] + '_do_not_use_.csv', "w")
                    text_file.write('Hesin fílurin er brúktur til at markera at hettar casti ikki skal brúkast')
                    text_file.close()

        if event_dict['selected_event'] == -1: # Fyri at ikki kunna velja eina linju ið ikki er til
            event_dict['selected_event'] = 0
        elif event_dict['selected_event'] == 5:
            event_dict['selected_event'] = 4

        if event.keysym == 'j' or event.keysym == 'k':
            if event_dict['selected_event'] == 0:
                soak_line_dict['soak_start_line'][0].set_data([time_fulllength[event_dict['soak_start']], time_fulllength[event_dict['soak_start']]], [-100, 100])
            if event_dict['selected_event'] == 1:
                soak_line_dict['soak_stop_line'][0].set_data([time_fulllength[event_dict['soak_stop']], time_fulllength[event_dict['soak_stop']]], [-100, 100])
            if event_dict['selected_event'] == 2:
                soak_line_dict['downcast_start_line'][0].set_data([time_fulllength[event_dict['downcast_start']], time_fulllength[event_dict['downcast_start']]], [-100, 100])
            if event_dict['selected_event'] == 3:
                soak_line_dict['downcast_stop_line'][0].set_data([time_fulllength[event_dict['downcast_stop']], time_fulllength[event_dict['downcast_stop']]], [-100, 100])
            if event_dict['selected_event'] == 4:
                soak_line_dict['upcast_stop_line'][0].set_data([time_fulllength[event_dict['upcast_stop']], time_fulllength[event_dict['upcast_stop']]], [-100, 100])
            #update_annotations = True
            canvas.draw()
        if update_annotations:
            soak_line_dict['annotation'].remove()
            soak_line_dict['annotation'] = ba_gui.update_annotations(event_dict['selected_event'], ax, event_dict, maxd)

            canvas.draw()
        if update_qframe:
            ba_gui.refresh_qframe(Quality_frame, list_of_casts, parent_folder, filnavn, mappunavn_dict)

    root.bind('<Key>', key)

    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=1)
    log_e()
