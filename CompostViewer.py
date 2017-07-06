#!/usr/bin/python
'''
Created on 2015-06-11

@author: caribou
'''

import threading
import Queue
import time
from Tkinter import *
from socket import *
import pickle
from compost_data import *
import pygubu
import math


port = 50008
host = '192.168.2.33'
#host = '10.168.16.225'
#host = 'comporecycle.dyndns.org'
#host = '192.168.2.33'
#host = 'localhost'
#host_local = 'localhost'

# TCP STATE
TCP_NOT_CONNECT = 0
TCP_CONNECT = 1
TCP_CONNECTED = 2
TCP_GET_NODE_0_DATA = 3
TCP_GET_NODE_1_DATA = 4
TCP_GET_NODE_2_DATA = 5
TCP_GET_NODE_3_DATA = 6
TCP_GET_RELAY_STATE = 7
TCP_GET_LAST_RSSI = 8
TCP_PUT_RELAY_CONSIGNE = 9
TCP_GET_FAN_RELAY_CONFIG = 10
TCP_PUT_RELAIS_ETAT = 11
TCP_PUT_RELAIS_DELAIS = 12
TCP_GET_RELAIS_CFG = 13
TCP_GET_RRDGRAPH = 14
TCP_GET_GROUPE_SONDE = 15
TCP_GET_GROUPE_SONDE_CFG = 16
TCP_PUT_RELAIS_CFG = 17

# RRDGRAPH
RRD_GRAPH_RELAIS = 1
RRD_GRAPH_GATEWAY = 2
RRD_GRAPH_SONDE_1_COMPOST = 3
RRD_GRAPH_SONDE_2_COMPOST = 4
RRD_GRAPH_SONDE_3_COMPOST = 5
RRD_GRAPH_SONDE_4_COMPOST = 6

T_SURFACE_MASK = 0x01
T_PROFONDEUR_MASK = 0x02

class Application:
    def __init__(self, master):
        self.master = master

        self.rrd_png = PhotoImage(file='node_1.png')
        self.rrd_graph = CompostRRDGRAPH()
        self.rrd_graph.graph_start = "end-6h"
        self.rrd_graph.graph_end = "now"

        self.cur_groupe_sonde = 0


        # create builder
        self.builder = builder = pygubu.Builder()

        # load ui file
#        builder.add_from_file('CompostFanViewer.ui')
        builder.add_from_file('Viewer.ui')

#        img_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'img')
#        img_path = os.path.abspath(img_path)
#        builder.add_resource_path(img_path)

        # create a widget, using master as parent
#        self.mainwindow = builder.get_object('CompostFanWidget', master)
        self.mainwindow = builder.get_object('CompostFanViewer', master)


        self.relais_cfg_chk_sonde_1_surface = builder.get_variable('relais_cfg_chk_sonde_1_surface')
        self.relais_cfg_chk_sonde_1_profondeur = builder.get_variable('relais_cfg_chk_sonde_1_profondeur')
        self.relais_cfg_chk_sonde_2_surface = builder.get_variable('relais_cfg_chk_sonde_2_surface')
        self.relais_cfg_chk_sonde_2_profondeur = builder.get_variable('relais_cfg_chk_sonde_2_profondeur')
        self.relais_cfg_chk_sonde_3_surface = builder.get_variable('relais_cfg_chk_sonde_3_surface')
        self.relais_cfg_chk_sonde_3_profondeur = builder.get_variable('relais_cfg_chk_sonde_3_profondeur')
        self.relais_cfg_chk_sonde_4_surface = builder.get_variable('relais_cfg_chk_sonde_4_surface')
        self.relais_cfg_chk_sonde_4_profondeur = builder.get_variable('relais_cfg_chk_sonde_4_profondeur')


        # connect method callbacks
        builder.connect_callbacks(self)

        # getting ConnectionLabelFrame widget
        self.ConnectionLabelFrame = builder.get_object('ConnectionLabelFrame')
        self.TCP_CON_BUTTON_CONNECT = builder.get_object('TCP_CON_BUTTON_CONNECT')
        self.TCP_CON_BUTTON_DISCONNECT = builder.get_object('TCP_CON_BUTTON_DISCONNECT')
        self.TCP_CON_ENTRY_CON_INFORMATION = builder.get_object('TCP_CON_ENTRY_CON_INFORMATION')

        # getting Notebook widget
        self.Notebook = builder.get_object('Notebook')
        self.GS_TAB = builder.get_object('GS_TAB')
        self.RELAIS_CFG_TAB = builder.get_object('RELAIS_CFG_TAB')
        self.RELAIS_DATA_TAB = builder.get_object('RELAIS_DATA_TAB')
        self.SONDE_1_TAB = builder.get_object('SONDE_1_TAB')
        self.SONDE_2_TAB = builder.get_object('SONDE_2_TAB')
        self.SONDE_3_TAB = builder.get_object('SONDE_3_TAB')
        self.SONDE_4_TAB = builder.get_object('SONDE_4_TAB')
        self.SONDE_4_TAB = builder.get_object('SONDE_4_TAB')

        self.GS_FRAME = builder.get_object('GS_FRAME')
        self.GS_BUTTON_GS1 = builder.get_object('GS_BUTTON_GS1')
        self.GS_BUTTON_GS2 = builder.get_object('GS_BUTTON_GS2')
        self.GS_BUTTON_GS3 = builder.get_object('GS_BUTTON_GS3')
        self.GS_BUTTON_GS4 = builder.get_object('GS_BUTTON_GS4')

        self.RELAIS_CFG_FRAME = builder.get_object('RELAIS_CFG_FRAME')
        self.RELAIS_CFG_LABEL_FRAME_CFG_SONDE_1 = builder.get_object('RELAIS_CFG_LABEL_FRAME_CFG_SONDE_1')
        self.RELAIS_CFG_LABEL_FRAME_CFG_SONDE_2 = builder.get_object('RELAIS_CFG_LABEL_FRAME_CFG_SONDE_2')
        self.RELAIS_CFG_LABEL_FRAME_CFG_SONDE_3 = builder.get_object('RELAIS_CFG_LABEL_FRAME_CFG_SONDE_3')
        self.RELAIS_CFG_LABEL_FRAME_CFG_SONDE_4 = builder.get_object('RELAIS_CFG_LABEL_FRAME_CFG_SONDE_4')

        self.RELAIS_CFG_LABEL_SONDE_1_ID = builder.get_object('RELAIS_CFG_LABEL_SONDE_1_ID')
        self.RELAIS_CFG_LABEL_SONDE_2_ID = builder.get_object('RELAIS_CFG_LABEL_SONDE_2_ID')
        self.RELAIS_CFG_LABEL_SONDE_3_ID = builder.get_object('RELAIS_CFG_LABEL_SONDE_3_ID')
        self.RELAIS_CFG_LABEL_SONDE_4_ID = builder.get_object('RELAIS_CFG_LABEL_SONDE_4_ID')

        self.RELAIS_CFG_ENTRY_CUR_SONDE_1_ID = builder.get_object('RELAIS_CFG_ENTRY_CUR_SONDE_1_ID')
        self.RELAIS_CFG_ENTRY_CUR_SONDE_2_ID = builder.get_object('RELAIS_CFG_ENTRY_CUR_SONDE_2_ID')
        self.RELAIS_CFG_ENTRY_CUR_SONDE_3_ID = builder.get_object('RELAIS_CFG_ENTRY_CUR_SONDE_3_ID')
        self.RELAIS_CFG_ENTRY_CUR_SONDE_4_ID = builder.get_object('RELAIS_CFG_ENTRY_CUR_SONDE_4_ID')

        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_1_ID = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_SONDE_1_ID')
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_2_ID = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_SONDE_2_ID')
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_3_ID = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_SONDE_3_ID')
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_4_ID = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_SONDE_4_ID')

        self.RELAIS_CFG_LABEL_SONDE_1_ENDROIT = builder.get_object('RELAIS_CFG_LABEL_SONDE_1_ENDROIT')
        self.RELAIS_CFG_LABEL_SONDE_2_ENDROIT = builder.get_object('RELAIS_CFG_LABEL_SONDE_2_ENDROIT')
        self.RELAIS_CFG_LABEL_SONDE_3_ENDROIT = builder.get_object('RELAIS_CFG_LABEL_SONDE_3_ENDROIT')
        self.RELAIS_CFG_LABEL_SONDE_4_ENDROIT = builder.get_object('RELAIS_CFG_LABEL_SONDE_4_ENDROIT')

        self.RELAIS_CFG_ENTRY_CUR_SONDE_1_ENDROIT_TXT = builder.get_object('RELAIS_CFG_ENTRY_CUR_SONDE_1_ENDROIT_TXT')
        self.RELAIS_CFG_ENTRY_CUR_SONDE_2_ENDROIT_TXT = builder.get_object('RELAIS_CFG_ENTRY_CUR_SONDE_2_ENDROIT_TXT')
        self.RELAIS_CFG_ENTRY_CUR_SONDE_3_ENDROIT_TXT = builder.get_object('RELAIS_CFG_ENTRY_CUR_SONDE_3_ENDROIT_TXT')
        self.RELAIS_CFG_ENTRY_CUR_SONDE_4_ENDROIT_TXT = builder.get_object('RELAIS_CFG_ENTRY_CUR_SONDE_4_ENDROIT_TXT')

        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_1_ENDROIT_TXT = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_SONDE_1_ENDROIT_TXT')
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_2_ENDROIT_TXT = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_SONDE_2_ENDROIT_TXT')
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_3_ENDROIT_TXT = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_SONDE_3_ENDROIT_TXT')
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_4_ENDROIT_TXT = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_SONDE_4_ENDROIT_TXT')

        self.RELAIS_CFG_LABEL_SONDE_1_CHOIX_TEMPERATURE = builder.get_object('RELAIS_CFG_LABEL_SONDE_1_CHOIX_TEMPERATURE')
        self.RELAIS_CFG_LABEL_SONDE_2_CHOIX_TEMPERATURE = builder.get_object('RELAIS_CFG_LABEL_SONDE_2_CHOIX_TEMPERATURE')
        self.RELAIS_CFG_LABEL_SONDE_3_CHOIX_TEMPERATURE = builder.get_object('RELAIS_CFG_LABEL_SONDE_3_CHOIX_TEMPERATURE')
        self.RELAIS_CFG_LABEL_SONDE_4_CHOIX_TEMPERATURE = builder.get_object('RELAIS_CFG_LABEL_SONDE_4_CHOIX_TEMPERATURE')

        self.RELAIS_CFG_CHK_BUTTON_SONDE_1_T_SURFACE = builder.get_object('RELAIS_CFG_CHK_BUTTON_SONDE_1_T_SURFACE')
        self.RELAIS_CFG_CHK_BUTTON_SONDE_2_T_SURFACE = builder.get_object('RELAIS_CFG_CHK_BUTTON_SONDE_2_T_SURFACE')
        self.RELAIS_CFG_CHK_BUTTON_SONDE_3_T_SURFACE = builder.get_object('RELAIS_CFG_CHK_BUTTON_SONDE_3_T_SURFACE')
        self.RELAIS_CFG_CHK_BUTTON_SONDE_4_T_SURFACE = builder.get_object('RELAIS_CFG_CHK_BUTTON_SONDE_4_T_SURFACE')


        self.RELAIS_CFG_CHK_BUTTON_SONDE_1_T_PROFONDEUR = builder.get_object('RELAIS_CFG_CHK_BUTTON_SONDE_1_T_PROFONDEUR')
        self.RELAIS_CFG_CHK_BUTTON_SONDE_2_T_PROFONDEUR = builder.get_object('RELAIS_CFG_CHK_BUTTON_SONDE_2_T_PROFONDEUR')
        self.RELAIS_CFG_CHK_BUTTON_SONDE_3_T_PROFONDEUR = builder.get_object('RELAIS_CFG_CHK_BUTTON_SONDE_3_T_PROFONDEUR')
        self.RELAIS_CFG_CHK_BUTTON_SONDE_4_T_PROFONDEUR = builder.get_object('RELAIS_CFG_CHK_BUTTON_SONDE_4_T_PROFONDEUR')



        self.RELAIS_CFG_LABEL_FRAME_DELAIS_MIN = builder.get_object('RELAIS_CFG_LABEL_FRAME_DELAIS_MIN')
        self.RELAIS_CFG_LABEL_DELAIS_MIN = builder.get_object('RELAIS_CFG_LABEL_DELAIS_MIN')
        self.RELAIS_CFG_ENTRY_CUR_DELAIS_MIN = builder.get_object('RELAIS_CFG_ENTRY_CUR_DELAIS_MIN')
        self.RELAIS_CFG_ENTRY_UPDATE_DELAIS_MIN = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_DELAIS_MIN')


        self.RELAIS_CFG_LABEL_FRAME_PC = builder.get_object('RELAIS_CFG_LABEL_FRAME_PC')
        self.RELAIS_CFG_LABEL_PC1 = builder.get_object('RELAIS_CFG_LABEL_PC1')
        self.RELAIS_CFG_LABEL_PC2 = builder.get_object('RELAIS_CFG_LABEL_PC2')
        self.RELAIS_CFG_LABEL_PC3 = builder.get_object('RELAIS_CFG_LABEL_PC3')
        self.RELAIS_CFG_LABEL_PC4 = builder.get_object('RELAIS_CFG_LABEL_PC4')
        self.RELAIS_CFG_ENTRY_CUR_PC1 = builder.get_object('RELAIS_CFG_ENTRY_CUR_PC1')
        self.RELAIS_CFG_ENTRY_CUR_PC2 = builder.get_object('RELAIS_CFG_ENTRY_CUR_PC2')
        self.RELAIS_CFG_ENTRY_CUR_PC3 = builder.get_object('RELAIS_CFG_ENTRY_CUR_PC3')
        self.RELAIS_CFG_ENTRY_CUR_PC4 = builder.get_object('RELAIS_CFG_ENTRY_CUR_PC4')
        self.RELAIS_CFG_ENTRY_UPDATE_PC1 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_PC1')
        self.RELAIS_CFG_ENTRY_UPDATE_PC2 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_PC2')
        self.RELAIS_CFG_ENTRY_UPDATE_PC3 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_PC3')
        self.RELAIS_CFG_ENTRY_UPDATE_PC4 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_PC4')


        self.RELAIS_CFG_LABEL_FRAME_TV = builder.get_object('RELAIS_CFG_LABEL_FRAME_TV')
        self.RELAIS_CFG_LABEL_TV1 = builder.get_object('RELAIS_CFG_LABEL_TV1')
        self.RELAIS_CFG_LABEL_TV2 = builder.get_object('RELAIS_CFG_LABEL_TV2')
        self.RELAIS_CFG_LABEL_TV3 = builder.get_object('RELAIS_CFG_LABEL_TV3')
        self.RELAIS_CFG_LABEL_TV4 = builder.get_object('RELAIS_CFG_LABEL_TV4')
        self.RELAIS_CFG_ENTRY_CUR_TV1 = builder.get_object('RELAIS_CFG_ENTRY_CUR_TV1')
        self.RELAIS_CFG_ENTRY_CUR_TV2 = builder.get_object('RELAIS_CFG_ENTRY_CUR_TV2')
        self.RELAIS_CFG_ENTRY_CUR_TV3 = builder.get_object('RELAIS_CFG_ENTRY_CUR_TV3')
        self.RELAIS_CFG_ENTRY_CUR_TV4 = builder.get_object('RELAIS_CFG_ENTRY_CUR_TV4')
        self.RELAIS_CFG_ENTRY_UPDATE_TV1 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_TV1')
        self.RELAIS_CFG_ENTRY_UPDATE_TV2 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_TV2')
        self.RELAIS_CFG_ENTRY_UPDATE_TV3 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_TV3')
        self.RELAIS_CFG_ENTRY_UPDATE_TV4 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_TV4')

        self.RELAIS_CFG_ENTRY_CUR_TA1 = builder.get_object('RELAIS_CFG_ENTRY_CUR_TA1')
        self.RELAIS_CFG_ENTRY_CUR_TA2 = builder.get_object('RELAIS_CFG_ENTRY_CUR_TA2')
        self.RELAIS_CFG_ENTRY_CUR_TA3 = builder.get_object('RELAIS_CFG_ENTRY_CUR_TA3')
        self.RELAIS_CFG_ENTRY_CUR_TA4 = builder.get_object('RELAIS_CFG_ENTRY_CUR_TA4')

        self.RELAIS_CFG_ENTRY_UPDATE_TA1 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_TA1')
        self.RELAIS_CFG_ENTRY_UPDATE_TA2 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_TA2')
        self.RELAIS_CFG_ENTRY_UPDATE_TA3 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_TA3')
        self.RELAIS_CFG_ENTRY_UPDATE_TA4 = builder.get_object('RELAIS_CFG_ENTRY_UPDATE_TA4')



        self.RELAIS_CFG_BUTTON_UPDATE = builder.get_object('RELAIS_CFG_BUTTON_UPDATE')

        self.RELAIS_DATA_FRAME = builder.get_object('RELAIS_DATA_FRAME')
        self.RELAIS_DATA_LABEL_FRAME_DATE_HEURE_LECTURE_DATA = builder.get_object('RELAIS_DATA_LABEL_FRAME_DATE_HEURE_LECTURE_DATA')
        self.RELAIS_DATA_LABEL_DATE_HEURE = builder.get_object('RELAIS_DATA_LABEL_DATE_HEURE')
        self.RELAIS_DATA_ENTRY_CUR_DATE_HEURE = builder.get_object('RELAIS_DATA_ENTRY_CUR_DATE_HEURE')

        self.RELAIS_DATA_LABEL_FRAME_DONNEES = builder.get_object('RELAIS_DATA_LABEL_FRAME_DONNEES')
        self.RELAIS_DATA_LABEL_T_AVG = builder.get_object('RELAIS_DATA_LABEL_T_AVG')
        self.RELAIS_DATA_LABEL_PC = builder.get_object('RELAIS_DATA_LABEL_PC')
        self.RELAIS_DATA_LABEL_TV = builder.get_object('RELAIS_DATA_LABEL_TV')
        self.RELAIS_DATA_LABEL_TA = builder.get_object('RELAIS_DATA_LABEL_TA')
        self.RELAIS_DATA_LABEL_SSR_STATE = builder.get_object('RELAIS_DATA_LABEL_SSR_STATE')

        self.RELAIS_DATA_ENTRY_CUR_T_AVG = builder.get_object('RELAIS_DATA_ENTRY_CUR_T_AVG')
        self.RELAIS_DATA_ENTRY_CUR_PC = builder.get_object('RELAIS_DATA_ENTRY_CUR_PC')
        self.RELAIS_DATA_ENTRY_CUR_TV = builder.get_object('RELAIS_DATA_ENTRY_CUR_TV')
        self.RELAIS_DATA_ENTRY_CUR_TA = builder.get_object('RELAIS_DATA_ENTRY_CUR_TA')
        self.RELAIS_DATA_ENTRY_CUR_SSR_STATE = builder.get_object('RELAIS_DATA_ENTRY_CUR_SSR_STATE')

        self.SONDE_1_FRAME = builder.get_object('SONDE_1_FRAME')
        self.SONDE_2_FRAME = builder.get_object('SONDE_2_FRAME')
        self.SONDE_3_FRAME = builder.get_object('SONDE_3_FRAME')
        self.SONDE_4_FRAME = builder.get_object('SONDE_4_FRAME')

        self.SONDE_1_LABEL_FRAME_DATE_HEURE_LECTURE_DATA = builder.get_object('SONDE_1_LABEL_FRAME_DATE_HEURE_LECTURE_DATA')
        self.SONDE_2_LABEL_FRAME_DATE_HEURE_LECTURE_DATA = builder.get_object(
            'SONDE_2_LABEL_FRAME_DATE_HEURE_LECTURE_DATA')
        self.SONDE_3_LABEL_FRAME_DATE_HEURE_LECTURE_DATA = builder.get_object(
            'SONDE_3_LABEL_FRAME_DATE_HEURE_LECTURE_DATA')
        self.SONDE_4_LABEL_FRAME_DATE_HEURE_LECTURE_DATA = builder.get_object(
            'SONDE_4_LABEL_FRAME_DATE_HEURE_LECTURE_DATA')

        self.SONDE_1_LABEL_DATE_HEURE = builder.get_object('SONDE_1_LABEL_DATE_HEURE')
        self.SONDE_2_LABEL_DATE_HEURE = builder.get_object('SONDE_2_LABEL_DATE_HEURE')
        self.SONDE_3_LABEL_DATE_HEURE = builder.get_object('SONDE_3_LABEL_DATE_HEURE')
        self.SONDE_4_LABEL_DATE_HEURE = builder.get_object('SONDE_4_LABEL_DATE_HEURE')

        self.SONDE_1_ENTRY_CUR_DATE_HEURE = builder.get_object('SONDE_1_ENTRY_CUR_DATE_HEURE')
        self.SONDE_2_ENTRY_CUR_DATE_HEURE = builder.get_object('SONDE_2_ENTRY_CUR_DATE_HEURE')
        self.SONDE_3_ENTRY_CUR_DATE_HEURE = builder.get_object('SONDE_3_ENTRY_CUR_DATE_HEURE')
        self.SONDE_4_ENTRY_CUR_DATE_HEURE = builder.get_object('SONDE_4_ENTRY_CUR_DATE_HEURE')

        self.SONDE_1_LABEL_FRAME_DONNEES = builder.get_object('SONDE_1_LABEL_FRAME_DONNEES')
        self.SONDE_2_LABEL_FRAME_DONNEES = builder.get_object('SONDE_2_LABEL_FRAME_DONNEES')
        self.SONDE_3_LABEL_FRAME_DONNEES = builder.get_object('SONDE_3_LABEL_FRAME_DONNEES')
        self.SONDE_4_LABEL_FRAME_DONNEES = builder.get_object('SONDE_4_LABEL_FRAME_DONNEES')

        self.SONDE_1_LABEL_T_SURFACE = builder.get_object('SONDE_1_LABEL_T_SURFACE')
        self.SONDE_2_LABEL_T_SURFACE = builder.get_object('SONDE_2_LABEL_T_SURFACE')
        self.SONDE_3_LABEL_T_SURFACE = builder.get_object('SONDE_3_LABEL_T_SURFACE')
        self.SONDE_4_LABEL_T_SURFACE = builder.get_object('SONDE_4_LABEL_T_SURFACE')

        self.SONDE_1_ENTRY_CUR_T_SURFACE = builder.get_object('SONDE_1_ENTRY_CUR_T_SURFACE')
        self.SONDE_2_ENTRY_CUR_T_SURFACE = builder.get_object('SONDE_2_ENTRY_CUR_T_SURFACE')
        self.SONDE_3_ENTRY_CUR_T_SURFACE = builder.get_object('SONDE_3_ENTRY_CUR_T_SURFACE')
        self.SONDE_4_ENTRY_CUR_T_SURFACE = builder.get_object('SONDE_4_ENTRY_CUR_T_SURFACE')

        self.SONDE_1_LABEL_T_PROFONDEUR = builder.get_object('SONDE_1_LABEL_T_PROFONDEUR')
        self.SONDE_2_LABEL_T_PROFONDEUR = builder.get_object('SONDE_2_LABEL_T_PROFONDEUR')
        self.SONDE_3_LABEL_T_PROFONDEUR = builder.get_object('SONDE_3_LABEL_T_PROFONDEUR')
        self.SONDE_4_LABEL_T_PROFONDEUR = builder.get_object('SONDE_4_LABEL_T_PROFONDEUR')

        self.SONDE_1_ENTRY_CUR_T_PROFONDEUR = builder.get_object('SONDE_1_ENTRY_CUR_T_PROFONDEUR')
        self.SONDE_2_ENTRY_CUR_T_PROFONDEUR = builder.get_object('SONDE_2_ENTRY_CUR_T_PROFONDEUR')
        self.SONDE_3_ENTRY_CUR_T_PROFONDEUR = builder.get_object('SONDE_3_ENTRY_CUR_T_PROFONDEUR')
        self.SONDE_4_ENTRY_CUR_T_PROFONDEUR = builder.get_object('SONDE_4_ENTRY_CUR_T_PROFONDEUR')

        self.SONDE_1_LABEL_CONDUCTIVITE = builder.get_object('SONDE_1_LABEL_CONDUCTIVITE')
        self.SONDE_2_LABEL_CONDUCTIVITE = builder.get_object('SONDE_2_LABEL_CONDUCTIVITE')
        self.SONDE_3_LABEL_CONDUCTIVITE = builder.get_object('SONDE_3_LABEL_CONDUCTIVITE')
        self.SONDE_4_LABEL_CONDUCTIVITE = builder.get_object('SONDE_4_LABEL_CONDUCTIVITE')

        self.SONDE_1_ENTRY_CUR_CONDUCTIVITE = builder.get_object('SONDE_1_ENTRY_CUR_CONDUCTIVITE')
        self.SONDE_2_ENTRY_CUR_CONDUCTIVITE = builder.get_object('SONDE_2_ENTRY_CUR_CONDUCTIVITE')
        self.SONDE_3_ENTRY_CUR_CONDUCTIVITE = builder.get_object('SONDE_3_ENTRY_CUR_CONDUCTIVITE')
        self.SONDE_4_ENTRY_CUR_CONDUCTIVITE = builder.get_object('SONDE_4_ENTRY_CUR_CONDUCTIVITE')

        self.SONDE_1_LABEL_BME_TEMPERATURE = builder.get_object('SONDE_1_LABEL_BME_TEMPERATURE')
        self.SONDE_2_LABEL_BME_TEMPERATURE = builder.get_object('SONDE_2_LABEL_BME_TEMPERATURE')
        self.SONDE_3_LABEL_BME_TEMPERATURE = builder.get_object('SONDE_3_LABEL_BME_TEMPERATURE')
        self.SONDE_4_LABEL_BME_TEMPERATURE = builder.get_object('SONDE_4_LABEL_BME_TEMPERATURE')

        self.SONDE_1_ENTRY_CUR_BME_TEMPERATURE = builder.get_object('SONDE_1_ENTRY_CUR_BME_TEMPERATURE')
        self.SONDE_2_ENTRY_CUR_BME_TEMPERATURE = builder.get_object('SONDE_2_ENTRY_CUR_BME_TEMPERATURE')
        self.SONDE_3_ENTRY_CUR_BME_TEMPERATURE = builder.get_object('SONDE_3_ENTRY_CUR_BME_TEMPERATURE')
        self.SONDE_4_ENTRY_CUR_BME_TEMPERATURE = builder.get_object('SONDE_4_ENTRY_CUR_BME_TEMPERATURE')

        self.SONDE_1_LABEL_BME_HUMIDITY = builder.get_object('SONDE_1_LABEL_BME_HUMIDITY')
        self.SONDE_2_LABEL_BME_HUMIDITY = builder.get_object('SONDE_2_LABEL_BME_HUMIDITY')
        self.SONDE_3_LABEL_BME_HUMIDITY = builder.get_object('SONDE_3_LABEL_BME_HUMIDITY')
        self.SONDE_4_LABEL_BME_HUMIDITY = builder.get_object('SONDE_4_LABEL_BME_HUMIDITY')

        self.SONDE_1_ENTRY_CUR_BME_HUMIDITY = builder.get_object('SONDE_1_ENTRY_CUR_BME_HUMIDITY')
        self.SONDE_2_ENTRY_CUR_BME_HUMIDITY = builder.get_object('SONDE_2_ENTRY_CUR_BME_HUMIDITY')
        self.SONDE_3_ENTRY_CUR_BME_HUMIDITY = builder.get_object('SONDE_3_ENTRY_CUR_BME_HUMIDITY')
        self.SONDE_4_ENTRY_CUR_BME_HUMIDITY = builder.get_object('SONDE_4_ENTRY_CUR_BME_HUMIDITY')

        self.SONDE_1_LABEL_BME_PRESSION = builder.get_object('SONDE_1_LABEL_BME_PRESSION')
        self.SONDE_2_LABEL_BME_PRESSION = builder.get_object('SONDE_2_LABEL_BME_PRESSION')
        self.SONDE_3_LABEL_BME_PRESSION = builder.get_object('SONDE_3_LABEL_BME_PRESSION')
        self.SONDE_4_LABEL_BME_PRESSION = builder.get_object('SONDE_4_LABEL_BME_PRESSION')

        self.SONDE_1_ENTRY_CUR_BME_PRESSION = builder.get_object('SONDE_1_ENTRY_CUR_BME_PRESSION')
        self.SONDE_2_ENTRY_CUR_BME_PRESSION = builder.get_object('SONDE_2_ENTRY_CUR_BME_PRESSION')
        self.SONDE_3_ENTRY_CUR_BME_PRESSION = builder.get_object('SONDE_3_ENTRY_CUR_BME_PRESSION')
        self.SONDE_4_ENTRY_CUR_BME_PRESSION = builder.get_object('SONDE_4_ENTRY_CUR_BME_PRESSION')

        self.SONDE_1_LABEL_BATTERIE_VOLTAGE = builder.get_object('SONDE_1_LABEL_BATTERIE_VOLTAGE')
        self.SONDE_2_LABEL_BATTERIE_VOLTAGE = builder.get_object('SONDE_2_LABEL_BATTERIE_VOLTAGE')
        self.SONDE_3_LABEL_BATTERIE_VOLTAGE = builder.get_object('SONDE_3_LABEL_BATTERIE_VOLTAGE')
        self.SONDE_4_LABEL_BATTERIE_VOLTAGE = builder.get_object('SONDE_4_LABEL_BATTERIE_VOLTAGE')

        self.SONDE_1_ENTRY_CUR_BATTERIE_VOLTAGE = builder.get_object('SONDE_1_ENTRY_CUR_BATTERIE_VOLTAGE')
        self.SONDE_2_ENTRY_CUR_BATTERIE_VOLTAGE = builder.get_object('SONDE_2_ENTRY_CUR_BATTERIE_VOLTAGE')
        self.SONDE_3_ENTRY_CUR_BATTERIE_VOLTAGE = builder.get_object('SONDE_3_ENTRY_CUR_BATTERIE_VOLTAGE')
        self.SONDE_4_ENTRY_CUR_BATTERIE_VOLTAGE = builder.get_object('SONDE_4_ENTRY_CUR_BATTERIE_VOLTAGE')

        self.SONDE_1_LABEL_TX_POWER = builder.get_object('SONDE_1_LABEL_TX_POWER')
        self.SONDE_2_LABEL_TX_POWER = builder.get_object('SONDE_2_LABEL_TX_POWER')
        self.SONDE_3_LABEL_TX_POWER = builder.get_object('SONDE_3_LABEL_TX_POWER')
        self.SONDE_4_LABEL_TX_POWER = builder.get_object('SONDE_4_LABEL_TX_POWER')

        self.SONDE_1_ENTRY_CUR_TX_POWER = builder.get_object('SONDE_1_ENTRY_CUR_TX_POWER')
        self.SONDE_2_ENTRY_CUR_TX_POWER = builder.get_object('SONDE_2_ENTRY_CUR_TX_POWER')
        self.SONDE_3_ENTRY_CUR_TX_POWER = builder.get_object('SONDE_3_ENTRY_CUR_TX_POWER')
        self.SONDE_4_ENTRY_CUR_TX_POWER = builder.get_object('SONDE_4_ENTRY_CUR_TX_POWER')

        self.SONDE_1_LABEL_LAST_RSSI = builder.get_object('SONDE_1_LABEL_LAST_RSSI')
        self.SONDE_2_LABEL_LAST_RSSI = builder.get_object('SONDE_2_LABEL_LAST_RSSI')
        self.SONDE_3_LABEL_LAST_RSSI = builder.get_object('SONDE_3_LABEL_LAST_RSSI')
        self.SONDE_4_LABEL_LAST_RSSI = builder.get_object('SONDE_4_LABEL_LAST_RSSI')

        self.SONDE_1_ENTRY_CUR_LAST_RSSI = builder.get_object('SONDE_1_ENTRY_CUR_LAST_RSSI')
        self.SONDE_2_ENTRY_CUR_LAST_RSSI = builder.get_object('SONDE_2_ENTRY_CUR_LAST_RSSI')
        self.SONDE_3_ENTRY_CUR_LAST_RSSI = builder.get_object('SONDE_3_ENTRY_CUR_LAST_RSSI')
        self.SONDE_4_ENTRY_CUR_LAST_RSSI = builder.get_object('SONDE_4_ENTRY_CUR_LAST_RSSI')



        self.GS_BUTTON_GS1.config(state='disabled')
        self.GS_BUTTON_GS2.config(state='disabled')
        self.GS_BUTTON_GS3.config(state='disabled')
        self.GS_BUTTON_GS4.config(state='disabled')

        self.RELAIS_CFG_BUTTON_UPDATE.config(state='disabled')




        # # getting tab_relais widget
        # self.bt_relais = builder.get_object('bt_relais_update')
        # self.en_t_moyenne = builder.get_object('en_t_moyenne')
        # self.en_relais_t_consigne = builder.get_object('en_relais_t_consigne')
        # self.en_relais_update_t_consigne = builder.get_object('en_update_consigne')
        # self.en_relais_t_offset_min = builder.get_object('en_relais_t_offset_min')
        # self.en_relais_t_offset_max = builder.get_object('en_relais_t_offset_max')
        # self.en_relais_current_state = builder.get_object('en_relais_current_state')
        # self.en_relais_delais = builder.get_object('en_delay_between_read')
        # self.en_relais_update_delais = builder.get_object('en_update_delais')
        # self.l_rrd_graph = builder.get_object('l_rrd_graph')
        # # getting tab_gateway widget
        #
        # # getting notebook
        # self.notebook_node = builder.get_object('notebook_node')
        #
        # # getting tabs
        # self.tab_relais = builder.get_object('tab_relais')
        # self.tab_gateway = builder.get_object('tab_gateway')
        # self.tab_sonde_compost_1 = builder.get_object('tab_sonde_compost_1')
        # self.tab_sonde_compost_2 = builder.get_object('tab_sonde_compost_2')
        # self.tab_sonde_compost_3 = builder.get_object('tab_sonde_compost_3')
        # self.tab_sonde_compost_4 = builder.get_object('tab_sonde_compost_4')
        #
        # self.f_donnes_relais = builder.get_object('f_donnes_relais')
        # self.f_donnes_gateway = builder.get_object('f_donnes_gateway')
        # self.f_donnees_sonde_compost_1 = builder.get_object('f_donnees_sonde_compost_1')
        # self.f_donnees_sonde_compost_2 = builder.get_object('f_donnees_sonde_compost_2')
        # self.f_donnees_sonde_compost_3 = builder.get_object('f_donnees_sonde_compost_3')
        # self.f_donnees_sonde_compost_4 = builder.get_object('f_donnees_sonde_compost_4')
        #
        # # getting tab_sonde_compost_1 widget
        # self.en_node_1_t_surface = builder.get_object('en_node_1_t_surface')
        # self.en_node_1_t_profondeur = builder.get_object('en_node_1_t_profondeur')
        # self.en_node_1_t_air = builder.get_object('en_node_1_t_air')
        # self.en_node_1_h_air = builder.get_object('en_node_1_h_air')
        # self.en_node_1_batt_voltage = builder.get_object('en_node_1_batt_voltage')
        # self.en_node_1_last_rssi = builder.get_object('en_node_1_last_rssi')
        #
        # # getting tab_sonde_compost_2 widget
        # self.en_node_2_t_surface = builder.get_object('en_node_2_t_surface')
        # self.en_node_2_t_profondeur = builder.get_object('en_node_2_t_profondeur')
        # self.en_node_2_batt_voltage = builder.get_object('en_node_2_batt_voltage')
        # self.en_node_2_last_rssi = builder.get_object('en_node_2_last_rssi')
        #
        # # getting tab_sonde_compost_3 widget
        # self.en_node_3_t_surface = builder.get_object('en_node_3_t_surface')
        # self.en_node_3_t_profondeur = builder.get_object('en_node_3_t_profondeur')
        # self.en_node_3_batt_voltage = builder.get_object('en_node_3_batt_voltage')
        # self.en_node_3_last_rssi = builder.get_object('en_node_3_last_rssi')
        #
        # # getting tab_sonde_compost_4 widget
        # self.en_node_4_t_surface = builder.get_object('en_node_4_t_surface')
        # self.en_node_4_t_profondeur = builder.get_object('en_node_4_t_profondeur')
        # self.en_node_4_batt_voltage = builder.get_object('en_node_4_batt_voltage')
        # self.en_node_4_last_rssi = builder.get_object('en_node_4_last_rssi')
        #
        #
        # self.notebook_node = builder.get_object('notebook_node')
        # self.notebook_node.bind('<<NotebookTabChanged>>', self.notebook_node_tab_change)
        #
        # self.en_connection_information = builder.get_object('en_connection_information')
        # self.bt_relais_update = builder.get_object('bt_relais_update')
        # self.bt_server_connect = builder.get_object('bt_server_connect')
        # self.bt_server_disconnect = builder.get_object('bt_server_disconnect')

        self.Notebook.bind('<<NotebookTabChanged>>', self.notebook_node_tab_change)

        self.nfc = NodeFanConfig()
        self.gs_id = GroupeSondeID()
        self.c_data = CompostFanData()
        self.ndr = NodeData()

        self.all_node = AllNode()

        self.cfg_data = CompostFanConfig()
        self.dataQueue = Queue.Queue()
        self.state = TCP_NOT_CONNECT
        self.last_state = self.state
        self.after_id = None
        self.sock = 0


#        self.l_rrd_graph.image.configure(image=self.rrd_png)
#        self.l_rrd_graph.rrd_png = rrd_png
#        self.l_rrd_graph.pack()


    # define the method callback


    def on_button_server_connect_clicked(self):
#        print('++on_button_server_connect_clicked()')
        self.client_connect()
        self.consumer()
        self.get_groupe_sonde()

#        self.get_relay_state()
#        self.get_last_rssi()
#        self.get_fan_relay_config()
#        self.get_fan_compost_data()
        self.TCP_CON_BUTTON_CONNECT.config(state='disabled')
        self.TCP_CON_BUTTON_DISCONNECT.config(state='normal')
#        print('--on_button_server_connect_clicked()')

    def get_fan_relay_config(self):
        print('++--get_fan_relay_config()')

    def get_relay_state(self):
#        print('++get_relay_state()')
        self.sock.send('GET_RELAY_STATE')
        self.last_state = self.state
        self.state = TCP_GET_RELAY_STATE
        self.makethread()
        self.consumer()
        self.state = self.last_state
#        print('--get_relay_state()')

    def get_rrdgraph(self):
        #        print('++get_relay_state()')
        self.f_rrdgraph = open("rrdgraph.png", 'wb')
        self.sock.send('GET_RRDGRAPH')
        self.last_state = self.state
        self.state = TCP_GET_RRDGRAPH
        self.makethread()
        self.consumer()
        self.state = self.last_state

    #        print('--get_relay_state()')

    def get_last_rssi(self):
        print('++get_last_rssi()')
        self.sock.send('GET_LAST_RSSI')
        self.last_state = self.state
        self.state = TCP_GET_LAST_RSSI
        self.makethread()
        self.consumer()
        self.state = self.last_state
        print('--get_last_rssi()')

    def get_groupe_sonde(self):
        self.sock.send('GET_GROUPE_SONDE')
        self.state = TCP_GET_GROUPE_SONDE
        self.makethread()
        self.consumer()

    def get_groupe_sonde_cfg(self):
        self.sock.send('GET_GROUPE_SONDE_CFG_' + str(self.cur_groupe_sonde))
        self.state = TCP_GET_GROUPE_SONDE_CFG
        self.makethread()
        self.consumer()


    def get_fan_compost_data(self):
#        print('++get_fan_compost_data()')
        self.sock.send('GET_NODE_0_DATA')
        self.state = TCP_GET_NODE_0_DATA
        self.makethread()
        self.consumer()
#        print('--get_fan_compost_data()')

    def stop_fan_compost_data(self):
        print('++stop_fan_compost_data()')
        self.sock.send('STOP_DATA')
        self.state = 0
        print('--stop_fan_compost_data()')

    def get_fan_relay_config(self):
        print('++get_fan_relay_config()')
        self.sock.send('GET FAN_RELAY_CONFIG')
        self.state = TCP_GET_RELAIS_CFG
        self.makethread()
        self.consumer()
        print('--get_fan_relay_config()')

    def on_button_server_disconnect_clicked(self):
        print('++button_server_disconnect_clicked()')
        if self.after_id is not None:
            self.mainwindow.after_cancel(self.after_id)
            print('after_cancel')

        self.sock.close()

        self.TCP_CON_ENTRY_CON_INFORMATION.delete(0, END)
        self.TCP_CON_ENTRY_CON_INFORMATION.insert(0, 'Disconnected')

        self.GS_BUTTON_GS1.config(state='disabled')
        self.GS_BUTTON_GS2.config(state='disabled')
        self.GS_BUTTON_GS3.config(state='disabled')
        self.GS_BUTTON_GS4.config(state='disabled')

        self.clear_relais_cfg()

        self.Notebook.select(str(self.GS_FRAME))

        self.TCP_CON_BUTTON_CONNECT.config(state='normal')
        self.TCP_CON_BUTTON_DISCONNECT.config(state='disabled')
        print('--button_server_disconnect_clicked()')

    def on_button_groupe_sonde_1_clicked(self):
        print ('++on_button_groupe_sonde_1_clicked()')
        self.cur_groupe_sonde = 0
        self.get_groupe_sonde_cfg()
        self.Notebook.select(str(self.RELAIS_CFG_FRAME))
        self.update_relais_cfg()
        self.RELAIS_CFG_BUTTON_UPDATE.config(state='normal')

    def on_button_groupe_sonde_2_clicked(self):
        print ('++on_button_groupe_sonde_2_clicked()')
        self.cur_groupe_sonde = 1
        self.get_groupe_sonde_cfg()
        self.Notebook.select(str(self.RELAIS_CFG_FRAME))
        self.update_relais_cfg()
        self.RELAIS_CFG_BUTTON_UPDATE.config(state='normal')

    def on_button_groupe_sonde_3_clicked(self):
        print ('++on_button_groupe_sonde_3_clicked()')
        self.cur_groupe_sonde = 2
        self.get_groupe_sonde_cfg()
        self.Notebook.select(str(self.RELAIS_CFG_FRAME))
        self.update_relais_cfg()
        self.RELAIS_CFG_BUTTON_UPDATE.config(state='normal')


    def on_button_groupe_sonde_4_clicked(self):
        print ('++on_button_groupe_sonde_4_clicked()')
        self.cur_groupe_sonde = 3
        self.get_groupe_sonde_cfg()
        self.Notebook.select(str(self.RELAIS_CFG_FRAME))
        self.update_relais_cfg()
        self.RELAIS_CFG_BUTTON_UPDATE.config(state='normal')


    def on_chk_button_sonde_1_surface(self):
        print ('++on_chk_button_sonde_1_surface()')
        print("variable : " + self.relais_cfg_chk_sonde_1_surface.get())

        if self.relais_cfg_chk_sonde_1_surface.get() == 'yes':
            self.nfc.node_compost_cfg_0 = self.nfc.node_compost_cfg_0 | T_SURFACE_MASK
        else:
            self.nfc.node_compost_cfg_0 = self.nfc.node_compost_cfg_0 ^ T_SURFACE_MASK
        print (str(self.nfc.node_compost_cfg_0))


    def on_chk_button_sonde_1_profondeur(self):
        print ('++on_chk_button_sonde_1_profondeur()')
        print("variable : " + self.relais_cfg_chk_sonde_1_profondeur.get())

        if self.relais_cfg_chk_sonde_1_profondeur.get() == 'yes':
            self.nfc.node_compost_cfg_0 = self.nfc.node_compost_cfg_0 | T_PROFONDEUR_MASK
        else:
            self.nfc.node_compost_cfg_0 = self.nfc.node_compost_cfg_0 ^ T_PROFONDEUR_MASK
        print (str(self.nfc.node_compost_cfg_0))


    def on_chk_button_sonde_2_surface(self):
        print ('++on_chk_button_sonde_2_surface()')
        print("variable : " + self.relais_cfg_chk_sonde_2_surface.get())

        if self.relais_cfg_chk_sonde_2_surface.get() == 'yes':
            self.nfc.node_compost_cfg_1 = self.nfc.node_compost_cfg_1 | T_SURFACE_MASK
        else:
            self.nfc.node_compost_cfg_1 = self.nfc.node_compost_cfg_1 ^ T_SURFACE_MASK
        print (str(self.nfc.node_compost_cfg_1))


    def on_chk_button_sonde_2_profondeur(self):
        print ('++on_chk_button_sonde_2_profondeur()')
        print("variable : " + self.relais_cfg_chk_sonde_2_profondeur.get())

        if self.relais_cfg_chk_sonde_2_profondeur.get() == 'yes':
            self.nfc.node_compost_cfg_1 = self.nfc.node_compost_cfg_1 | T_PROFONDEUR_MASK
        else:
            self.nfc.node_compost_cfg_1 = self.nfc.node_compost_cfg_1 ^ T_PROFONDEUR_MASK
        print (str(self.nfc.node_compost_cfg_1))


    def on_chk_button_sonde_3_surface(self):
        print ('++on_chk_button_sonde_3_surface()')
        print("variable : " + self.relais_cfg_chk_sonde_3_surface.get())

        if self.relais_cfg_chk_sonde_3_surface.get() == 'yes':
            self.nfc.node_compost_cfg_2 = self.nfc.node_compost_cfg_2 | T_SURFACE_MASK
        else:
            self.nfc.node_compost_cfg_2 = self.nfc.node_compost_cfg_2 ^ T_SURFACE_MASK
        print (str(self.nfc.node_compost_cfg_2))

    def on_chk_button_sonde_3_profondeur(self):
        print ('++on_chk_button_sonde_3_profondeur()')
        print("variable : " + self.relais_cfg_chk_sonde_3_profondeur.get())

        if self.relais_cfg_chk_sonde_3_profondeur.get() == 'yes':
            self.nfc.node_compost_cfg_2 = self.nfc.node_compost_cfg_2 | T_PROFONDEUR_MASK
        else:
            self.nfc.node_compost_cfg_2 = self.nfc.node_compost_cfg_2 ^ T_PROFONDEUR_MASK
        print (str(self.nfc.node_compost_cfg_2))

    def on_chk_button_sonde_4_surface(self):
        print ('++on_chk_button_sonde_4_surface()')
        print("variable : " + self.relais_cfg_chk_sonde_4_surface.get())

        if self.relais_cfg_chk_sonde_4_surface.get() == 'yes':
            self.nfc.node_compost_cfg_3 = self.nfc.node_compost_cfg_3 | T_SURFACE_MASK
        else:
            self.nfc.node_compost_cfg_3 = self.nfc.node_compost_cfg_3 ^ T_SURFACE_MASK
        print (str(self.nfc.node_compost_cfg_3))

    def on_chk_button_sonde_4_profondeur(self):
        print ('++on_chk_button_sonde_4_profondeur()')
        print("variable : " + self.relais_cfg_chk_sonde_4_profondeur.get())

        if self.relais_cfg_chk_sonde_4_profondeur.get() == 'yes':
            self.nfc.node_compost_cfg_3 = self.nfc.node_compost_cfg_3 | T_PROFONDEUR_MASK
        else:
            self.nfc.node_compost_cfg_3 = self.nfc.node_compost_cfg_3 ^ T_PROFONDEUR_MASK
        print (str(self.nfc.node_compost_cfg_3))


    def on_button_relais_update_clicked(self):
        print ('++button_relais_update_clicked()')
#        if self.after_id is not None:
#            self.mainwindow.after_cancel(self.after_id)
#            print('after_cancel')
        self.cfg_data.relais_consigne_temperature_fan = float(self.en_relais_update_t_consigne.get())
        self.last_state = self.state
        self.state = TCP_PUT_RELAY_CONSIGNE
        self.sock.send('PUT_RELAY_CONSIGNE')
        self.makethread()
        self.state = self.last_state
        print ('++button_relais_update_clicked()')

    def on_button_relais_on_clicked(self):
        print ('++button_relais_on_clicked()')
        self.cfg_data.relais_etat = 1
        self.last_state = self.state
        self.state = TCP_PUT_RELAIS_ETAT
        self.sock.send('PUT_RELAIS_ETAT')
        self.makethread()
        self.state = self.last_state
        print ('--button_relais_on_clicked()')

    def on_button_relais_off_clicked(self):
        print ('++button_relais_off_clicked()')
        self.cfg_data.relais_etat = 0
        self.last_state = self.state
        self.state = TCP_PUT_RELAIS_ETAT
        self.sock.send('PUT_RELAIS_ETAT')
        self.makethread()
        self.state = self.last_state
        print ('--button_relais_off_clicked()')

    def on_button_relais_auto_clicked(self):
        print ('++button_relais_auto_clicked()')
        self.cfg_data.relais_etat = 2
        self.last_state = self.state
        self.state = TCP_PUT_RELAIS_ETAT
        self.sock.send('PUT_RELAIS_ETAT')
        self.makethread()
        self.state = self.last_state
        print ('--button_relais_auto_clicked()')

    def on_button_relais_update_cfg_clicked(self):
        print ('++button_relais_update_delais_clicked()')
        self.nfc.PC1 = float(self.RELAIS_CFG_ENTRY_CUR_PC1.get())
        self.nfc.PC2 = float(self.RELAIS_CFG_ENTRY_CUR_PC2.get())
        self.nfc.PC3 = float(self.RELAIS_CFG_ENTRY_CUR_PC3.get())
        self.nfc.PC4 = float(self.RELAIS_CFG_ENTRY_CUR_PC4.get())

        self.nfc.TV1 = int(self.RELAIS_CFG_ENTRY_CUR_TV1.get())
        self.nfc.TV2 = int(self.RELAIS_CFG_ENTRY_CUR_TV2.get())
        self.nfc.TV3 = int(self.RELAIS_CFG_ENTRY_CUR_TV3.get())
        self.nfc.TV4 = int(self.RELAIS_CFG_ENTRY_CUR_TV4.get())

        self.nfc.TA1 = int(self.RELAIS_CFG_ENTRY_CUR_TA1.get())
        self.nfc.TA2 = int(self.RELAIS_CFG_ENTRY_CUR_TA2.get())
        self.nfc.TA3 = int(self.RELAIS_CFG_ENTRY_CUR_TA3.get())
        self.nfc.TA4 = int(self.RELAIS_CFG_ENTRY_CUR_TA4.get())

        self.nfc.delais_minute = int(self.RELAIS_CFG_ENTRY_CUR_DELAIS_MIN.get())

        self.nfc.node_compost_address_0 = int(self.RELAIS_CFG_ENTRY_CUR_SONDE_1_ID.get())
        self.nfc.node_compost_address_1 = int(self.RELAIS_CFG_ENTRY_CUR_SONDE_2_ID.get())
        self.nfc.node_compost_address_2 = int(self.RELAIS_CFG_ENTRY_CUR_SONDE_3_ID.get())
        self.nfc.node_compost_address_3 = int(self.RELAIS_CFG_ENTRY_CUR_SONDE_4_ID.get())

        self.nfc.node_compost_txt_0 = self.RELAIS_CFG_ENTRY_CUR_SONDE_1_ENDROIT_TXT.get()[0:16]
        self.nfc.node_compost_txt_1 = self.RELAIS_CFG_ENTRY_CUR_SONDE_2_ENDROIT_TXT.get()[0:16]
        self.nfc.node_compost_txt_2 = self.RELAIS_CFG_ENTRY_CUR_SONDE_3_ENDROIT_TXT.get()[0:16]
        self.nfc.node_compost_txt_3 = self.RELAIS_CFG_ENTRY_CUR_SONDE_4_ENDROIT_TXT.get()[0:16]

        self.last_state = self.state
        self.state = TCP_PUT_RELAIS_CFG
        self.sock.send('PUT_RELAIS_CFG_' + str(self.cur_groupe_sonde))
        self.makethread()

        self.clear_relais_cfg()
        self.get_groupe_sonde_cfg()
        self.update_relais_cfg()
        self.RELAIS_CFG_BUTTON_UPDATE.config(state='normal')

        print ('--button_relais_update_delais_clicked()')

    def clear_relais_cfg(self):
        self.RELAIS_CFG_BUTTON_UPDATE.config(state='disabled')

        self.RELAIS_CFG_ENTRY_CUR_SONDE_1_ID.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_2_ID.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_3_ID.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_4_ID.delete(0, END)

        self.RELAIS_CFG_ENTRY_CUR_DELAIS_MIN.delete(0, END)

        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_1_ID.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_2_ID.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_3_ID.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_4_ID.delete(0, END)

        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_1_ENDROIT_TXT.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_2_ENDROIT_TXT.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_3_ENDROIT_TXT.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_SONDE_4_ENDROIT_TXT.delete(0, END)

        self.RELAIS_CFG_ENTRY_UPDATE_DELAIS_MIN.delete(0, END)

        self.RELAIS_CFG_ENTRY_CUR_PC1.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_PC2.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_PC3.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_PC4.delete(0, END)

        self.RELAIS_CFG_ENTRY_UPDATE_PC1.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_PC2.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_PC3.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_PC4.delete(0, END)

        self.RELAIS_CFG_ENTRY_CUR_TV1.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TV2.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TV3.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TV4.delete(0, END)

        self.RELAIS_CFG_ENTRY_UPDATE_TV1.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_TV2.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_TV3.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_TV4.delete(0, END)

        self.RELAIS_CFG_ENTRY_CUR_TA1.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TA2.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TA3.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TA4.delete(0, END)

        self.RELAIS_CFG_ENTRY_UPDATE_TA1.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_TA2.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_TA3.delete(0, END)
        self.RELAIS_CFG_ENTRY_UPDATE_TA4.delete(0, END)

        self.RELAIS_CFG_ENTRY_CUR_SONDE_1_ENDROIT_TXT.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_2_ENDROIT_TXT.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_3_ENDROIT_TXT.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_4_ENDROIT_TXT.delete(0, END)

    def notebook_node_tab_change(self, event=None):
#        print self.Notebook.select()

#        print str(self.f_donnes_relais)


#         if str(self.f_donnes_relais) == self.notebook_node.select():
#             print ("Tab relais")
#             self.rrd_graph.graph_id = RRD_GRAPH_RELAIS
#
#         elif str(self.f_donnes_gateway) == self.notebook_node.select():
#             print('Tab Gateway')
#             self.rrd_graph.graph_id = RRD_GRAPH_GATEWAY
#
#         elif str(self.f_donnees_sonde_compost_1) == self.notebook_node.select():
#             print('Tab Compost 1')
#             self.rrd_graph.graph_id = RRD_GRAPH_SONDE_1_COMPOST
#
#         elif str(self.f_donnees_sonde_compost_2) == self.notebook_node.select():
#             print('Tab Compost 2')
#             self.rrd_graph.graph_id = RRD_GRAPH_SONDE_2_COMPOST
#
#         elif str(self.f_donnees_sonde_compost_3) == self.notebook_node.select():
#             print('Tab Compost 3')
#             self.rrd_graph.graph_id = RRD_GRAPH_SONDE_3_COMPOST
#
#         elif str(self.f_donnees_sonde_compost_4) == self.notebook_node.select():
#             print('Tab Compost 4')
#             self.rrd_graph.graph_id = RRD_GRAPH_SONDE_4_COMPOST

        print ('++--notebook_tab_changed()')

    def update_relay_state(self):
#        print ('++update_relay_state()')
        self.en_t_moyenne.delete(0, END)
        self.en_t_moyenne.insert(0, str(self.cfg_data.relais_t_moyenne) + ' deg C')

        self.en_relais_t_consigne.delete(0, END)
        self.en_relais_t_consigne.insert(0, str(self.cfg_data.relais_consigne_temperature_fan) + ' deg C')

        self.en_relais_t_offset_min.delete(0, END)
        self.en_relais_t_offset_min.insert(0, str(self.cfg_data.relais_consigne_offset_min_temperature_fan) + ' deg C')

        self.en_relais_t_offset_max.delete(0, END)
        self.en_relais_t_offset_max.insert(0, str(self.cfg_data.relais_consigne_offset_max_temperature_fan) + ' deg C')

        self.en_relais_current_state.delete(0, END)
        relais_etat = self.cfg_data.relais_etat
        if relais_etat == 0:
            self.en_relais_current_state.insert(0, 'OFF')
        elif relais_etat == 1:
            self.en_relais_current_state.insert(0, 'ON')
        elif relais_etat == 2:
            self.en_relais_current_state.insert(0, 'AUTO')

        self.en_relais_delais.delete(0, END)
        self.en_relais_delais.insert(0, str(self.cfg_data.relais_delais))

#        print ('--update_relay_state()')

    def update_last_rssi_state(self):
        print ('++--update_last_rssi_state()')

    def update_relais_cfg(self):

        self.RELAIS_CFG_CHK_BUTTON_SONDE_1_T_SURFACE.config(state='normal')
        self.RELAIS_CFG_CHK_BUTTON_SONDE_1_T_PROFONDEUR.config(state='normal')

        if self.nfc.node_compost_cfg_0 & T_SURFACE_MASK:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_1_T_SURFACE.select()
        else:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_1_T_SURFACE.deselect()

        if self.nfc.node_compost_cfg_0 & T_PROFONDEUR_MASK:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_1_T_PROFONDEUR.select()
        else:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_1_T_PROFONDEUR.deselect()

        if self.nfc.node_compost_cfg_1 & T_SURFACE_MASK:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_2_T_SURFACE.select()
        else:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_2_T_SURFACE.deselect()

        if self.nfc.node_compost_cfg_1 & T_PROFONDEUR_MASK:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_2_T_PROFONDEUR.select()
        else:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_2_T_PROFONDEUR.deselect()

        if self.nfc.node_compost_cfg_2 & T_SURFACE_MASK:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_3_T_SURFACE.select()
        else:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_3_T_SURFACE.deselect()

        if self.nfc.node_compost_cfg_2 & T_PROFONDEUR_MASK:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_3_T_PROFONDEUR.select()
        else:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_3_T_PROFONDEUR.deselect()

        if self.nfc.node_compost_cfg_3 & T_SURFACE_MASK:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_4_T_SURFACE.select()
        else:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_4_T_SURFACE.deselect()

        if self.nfc.node_compost_cfg_3 & T_PROFONDEUR_MASK:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_4_T_PROFONDEUR.select()
        else:
            self.RELAIS_CFG_CHK_BUTTON_SONDE_4_T_PROFONDEUR.deselect()



        self.RELAIS_CFG_ENTRY_CUR_DELAIS_MIN.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_DELAIS_MIN.insert(0, str(self.nfc.delais_minute))

        self.RELAIS_CFG_ENTRY_CUR_PC1.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_PC1.insert(0, str(self.nfc.PC1))
        self.RELAIS_CFG_ENTRY_CUR_PC2.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_PC2.insert(0, str(self.nfc.PC2))
        self.RELAIS_CFG_ENTRY_CUR_PC3.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_PC3.insert(0, str(self.nfc.PC3))
        self.RELAIS_CFG_ENTRY_CUR_PC4.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_PC4.insert(0, str(self.nfc.PC4))

        self.RELAIS_CFG_ENTRY_CUR_TV1.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TV1.insert(0, str(self.nfc.TV1))
        self.RELAIS_CFG_ENTRY_CUR_TV2.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TV2.insert(0, str(self.nfc.TV2))
        self.RELAIS_CFG_ENTRY_CUR_TV3.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TV3.insert(0, str(self.nfc.TV3))
        self.RELAIS_CFG_ENTRY_CUR_TV4.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TV4.insert(0, str(self.nfc.TV4))

        self.RELAIS_CFG_ENTRY_CUR_TA1.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TA1.insert(0, str(self.nfc.TA1))
        self.RELAIS_CFG_ENTRY_CUR_TA2.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TA2.insert(0, str(self.nfc.TA2))
        self.RELAIS_CFG_ENTRY_CUR_TA3.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TA3.insert(0, str(self.nfc.TA3))
        self.RELAIS_CFG_ENTRY_CUR_TA4.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_TA4.insert(0, str(self.nfc.TA4))

        self.RELAIS_CFG_ENTRY_CUR_SONDE_1_ID.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_1_ID.insert(0, str(self.nfc.node_compost_address_0))
        self.RELAIS_CFG_ENTRY_CUR_SONDE_2_ID.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_2_ID.insert(0, str(self.nfc.node_compost_address_1))
        self.RELAIS_CFG_ENTRY_CUR_SONDE_3_ID.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_3_ID.insert(0, str(self.nfc.node_compost_address_2))
        self.RELAIS_CFG_ENTRY_CUR_SONDE_4_ID.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_4_ID.insert(0, str(self.nfc.node_compost_address_3))

        self.RELAIS_CFG_ENTRY_CUR_SONDE_1_ENDROIT_TXT.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_1_ENDROIT_TXT.insert(0, self.nfc.node_compost_txt_0)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_2_ENDROIT_TXT.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_2_ENDROIT_TXT.insert(0, self.nfc.node_compost_txt_1)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_3_ENDROIT_TXT.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_3_ENDROIT_TXT.insert(0, self.nfc.node_compost_txt_2)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_4_ENDROIT_TXT.delete(0, END)
        self.RELAIS_CFG_ENTRY_CUR_SONDE_4_ENDROIT_TXT.insert(0, self.nfc.node_compost_txt_3)

    def update_form(self):
#        print('++update_form()')

        self.en_node_1_t_surface.delete(0, END)
        self.en_node_1_t_surface.insert(0, str(self.all_node.node_0.t_1))
        self.en_node_1_t_profondeur.delete(0, END)
        self.en_node_1_t_profondeur.insert(0, str(self.all_node.node_0.t_2))
        self.en_node_1_t_air.delete(0, END)
        self.en_node_1_t_air.insert(0, str(self.all_node.node_0.t_3))
        self.en_node_1_h_air.delete(0, END)
        self.en_node_1_h_air.insert(0, str(self.all_node.node_0.h_1))
        self.en_node_1_batt_voltage.delete(0, END)
        self.en_node_1_batt_voltage.insert(0, str(self.all_node.node_0.bat_voltage))
        self.en_node_1_last_rssi.delete(0, END)
        self.en_node_1_last_rssi.insert(0, str(self.all_node.node_0.last_rssi))

#        print('Node 1 temperature de surface: ' + str(self.all_node.node_0.t_1) + ' deg C')
#        print('Node 1 temperature de profondeur: ' + str(self.all_node.node_0.t_2) + ' deg C')

        self.en_node_2_t_surface.delete(0, END)
        self.en_node_2_t_surface.insert(0, str(self.all_node.node_1.t_1))
        self.en_node_2_t_profondeur.delete(0, END)
        self.en_node_2_t_profondeur.insert(0, str(self.all_node.node_1.t_2))
        self.en_node_2_batt_voltage.delete(0, END)
        self.en_node_2_batt_voltage.insert(0, str(self.all_node.node_1.bat_voltage))
        self.en_node_2_last_rssi.delete(0, END)
        self.en_node_2_last_rssi.insert(0, str(self.all_node.node_1.last_rssi))

#        print('Node 2 temperature de surface: ' + str(self.all_node.node_1.t_1) + ' deg C')
#        print('Node 2 temperature de profondeur: ' + str(self.all_node.node_1.t_2) + ' deg C')

        self.en_node_3_t_surface.delete(0, END)
        self.en_node_3_t_surface.insert(0, str(self.all_node.node_2.t_1))
        self.en_node_3_t_profondeur.delete(0, END)
        self.en_node_3_t_profondeur.insert(0, str(self.all_node.node_2.t_2))
        self.en_node_3_batt_voltage.delete(0, END)
        self.en_node_3_batt_voltage.insert(0, str(self.all_node.node_2.bat_voltage))
        self.en_node_3_last_rssi.delete(0, END)
        self.en_node_3_last_rssi.insert(0, str(self.all_node.node_2.last_rssi))

#        print('Node 3 temperature de surface: ' + str(self.all_node.node_2.t_1) + ' deg C')
#        print('Node 3 temperature de profondeur: ' + str(self.all_node.node_2.t_2) + ' deg C')

        self.en_node_4_t_surface.delete(0, END)
        self.en_node_4_t_surface.insert(0, str(self.all_node.node_3.t_1))
        self.en_node_4_t_profondeur.delete(0, END)
        self.en_node_4_t_profondeur.insert(0, str(self.all_node.node_3.t_2))
        self.en_node_4_batt_voltage.delete(0, END)
        self.en_node_4_batt_voltage.insert(0, str(self.all_node.node_3.bat_voltage))
        self.en_node_4_last_rssi.delete(0, END)
        self.en_node_4_last_rssi.insert(0, str(self.all_node.node_3.last_rssi))




    #        print('Node 4 temperature de surface: ' + str(self.all_node.node_3.t_1) + ' deg C')
#        print('Node 4 temperature de profondeur: ' + str(self.all_node.node_3.t_2) + ' deg C')

#        print('Consigne : ' + str(self.cfg_data.relais_consigne_temperature_fan) + " deg C")
#        print('--update_form()')

    def client_connect(self):
        print('++client_connect()')
        self.state = TCP_CONNECT
        self.sock = socket(AF_INET, SOCK_STREAM)
        try:
            self.sock.connect((host, port))
        except Exception, errorcode:
            print "Caught exception socket.error: %s" % errorcode 
        else:
            print('Sending Ready...')
            self.sock.send('Ready')
            self.makethread()
#        print('--client_connect()')

    def client_close(self):
        print('++client_close()')
        self.sock.close()
        print('++client_close()')

    def producer(self):
#        print('++producer()')
#        print ('Producer current state = %d' % self.state)

        if self.state == TCP_CONNECT:
            print('Producer state == TCP_CONNECT')
            reply = self.sock.recv(1024)
            self.dataQueue.put('client got: [%s]' % reply)
            self.state = TCP_CONNECTED

        elif self.state == TCP_GET_GROUPE_SONDE_CFG:
            print('Producer state == TCP_GET_GROUPE_SONDE_CFG')
            reply = self.sock.recv(1024)
            self.sock.send("OK")
            self.dataQueue.put(reply)

        elif self.state == TCP_GET_GROUPE_SONDE:
            print('Producer state == TCP_GET_GROUPE_SONDE')
            reply = self.sock.recv(1024)
            self.sock.send("OK")
            self.dataQueue.put(reply)
        elif self.state == TCP_GET_NODE_0_DATA:
            print('Producer state == TCP_GET_NODE_0_DATA')
            reply = self.sock.recv(1024)
            self.sock.send("OK")
            self.dataQueue.put(reply)

        elif self.state == TCP_GET_NODE_1_DATA:
            print('Producer state == TCP_GET_NODE_1_DATA')
            reply = self.sock.recv(1024)
            self.sock.send("OK")
            self.dataQueue.put(reply)

        elif self.state == TCP_GET_NODE_2_DATA:
            print('Producer state == TCP_GET_NODE_2_DATA')
            reply = self.sock.recv(1024)
            self.sock.send("OK")
            self.dataQueue.put(reply)

        elif self.state == TCP_GET_NODE_3_DATA:
            print('Producer state == TCP_GET_NODE_3_DATA')
            reply = self.sock.recv(1024)
            self.sock.send("OK")
            self.dataQueue.put(reply)

        elif self.state == TCP_GET_RELAY_STATE:
            print('Producer state == TCP_GET_RELAY_STATE')
            reply = self.sock.recv(1024)
            self.sock.send("OK")
            self.dataQueue.put(reply)

        elif self.state == TCP_GET_LAST_RSSI:
            print('Producer state == TCP_GET_LAST_RSSI')
            reply = self.sock.recv(1024)
            self.sock.send("OK")
            self.dataQueue.put(reply)

        elif self.state == TCP_GET_RELAIS_CFG:
            print('Producer state == TCP_GET_RELAIS_CFG')
            reply = self.sock.recv(1024)
            self.sock.send("OK")
            self.dataQueue.put(reply)

        elif self.state == TCP_PUT_RELAY_CONSIGNE:
            print('Producer state == TCP_PUT_RELAY_CONSIGNE')
            reply = self.sock.recv(1024)
            print('Client receive : ' + reply)
            reply_string = pickle.dumps(self.cfg_data)
            self.sock.send(reply_string)

        elif self.state == TCP_PUT_RELAIS_ETAT:
            print('Producer state == TCP_PUT_RELAIS_ETAT')
            reply = self.sock.recv(1024)
            print('Client receive : ' + reply)
            reply_string = pickle.dumps(self.cfg_data)
            self.sock.send(reply_string)

        elif self.state == TCP_PUT_RELAIS_DELAIS:
            print('Producer state == TCP_PUT_RELAIS_DELAIS')
            reply = self.sock.recv(1024)
            print('Client receive : ' + reply)
            reply_string = pickle.dumps(self.cfg_data)
            self.sock.send(reply_string)
        elif self.state == TCP_PUT_RELAIS_CFG:
            print('Producer state == TCP_PUT_RELAIS_CFG')
            reply = self.sock.recv(1024)
            # print('Client receive : ' + reply)
            reply_string = pickle.dumps(self.nfc)
            self.sock.send(reply_string)

        elif self.state == TCP_GET_RRDGRAPH:
            print('Producer state == TCP_GET_RRDGRAPH')
            reply = self.sock.recv(1024)
            if reply == "Get ready":
                # print('Client receive : ' + reply)
                reply_string = pickle.dumps(self.rrd_graph)
                self.sock.send(reply_string)
                reply = self.sock.recv(1024)
                self.sock.send("OK")

                b = int(reply)
                print b
                ff = float(b)
                bb = ff/1024
                aa = math.ceil(bb)

                print aa

                ii = 1
                print ("receiving : " + str(ii))
                reply = self.sock.recv(1024)
                self.f_rrdgraph.write(reply)
                self.sock.send("OK")

                ii += 1
                aa -= 1

                while aa:
                    print ("receiving : " + str(ii))
                    reply = self.sock.recv(1024)
                    self.f_rrdgraph.write(reply)
                    print ("send ok")
                    self.sock.send("OK")
                    ii += 1
                    aa -= 1
                self.f_rrdgraph.close()
                self.rrd_png = PhotoImage(file='rrdgraph.png')
                self.l_rrd_graph.config(image=self.rrd_png)
                self.after_id = self.mainwindow.after(15000, self.get_fan_compost_data)



    #        elif self.state == 7:
#            print('Producer state == 6')
#            reply = self.sock.recv(1024)
#            self.dataQueue.put(reply)

#        print('--producer()')

    def consumer(self):
#        print('++consumer()')
        try:
            data = self.dataQueue.get(block=False)
        except Queue.Empty:
            print('Queue empty...')
            pass
        else:
            if self.state == TCP_CONNECTED:
                print('Consumer state == TCP_CONNECTED')
#                print('Client got: [%s]' % data)
                self.TCP_CON_ENTRY_CON_INFORMATION.delete(0, END)
                self.TCP_CON_ENTRY_CON_INFORMATION.insert(0, data)
#                self.state = TCP_GET_NODE_0_DATA

            elif self.state == TCP_GET_GROUPE_SONDE:
                print('Consumer state == TCP_GET_GROUPE_SONDE')
                print(data)
                self.gs_id = pickle.loads(data)

                if self.gs_id.gp1_active == 1:
                    self.GS_BUTTON_GS1.config(state='normal')
                if self.gs_id.gp2_active == 1:
                    self.GS_BUTTON_GS2.config(state='normal')
                if self.gs_id.gp3_active == 1:
                    self.GS_BUTTON_GS3.config(state='normal')
                if self.gs_id.gp4_active == 1:
                    self.GS_BUTTON_GS4.config(state='normal')
            elif self.state == TCP_GET_GROUPE_SONDE_CFG:
                print('Consumer state == TCP_GET_GROUPE_SONDE_CFG')
                print (data)
                self.nfc = pickle.loads(data)
                self.update_relais_cfg()

            elif self.state == TCP_GET_NODE_0_DATA:
                print('Consumer state == TCP_GET_NODE_0_DATA')
                self.all_node.node_0 = pickle.loads(data)
                self.sock.send('GET_NODE_1_DATA')
#                print(self.all_node.node_0.node_id)
                self.state = TCP_GET_NODE_1_DATA
                self.makethread()
                self.consumer()

            elif self.state == TCP_GET_NODE_1_DATA:
                print('Consumer state == TCP_GET_NODE_1_DATA')
                self.all_node.node_1 = pickle.loads(data)
                self.sock.send('GET_NODE_2_DATA')
#                print(self.all_node.node_1.node_id)
                self.state = TCP_GET_NODE_2_DATA
                self.makethread()
                self.consumer()

            elif self.state == TCP_GET_NODE_2_DATA:
                print('Consumer state == TCP_GET_NODE_2_DATA')
                self.all_node.node_2 = pickle.loads(data)
                self.sock.send('GET_NODE_3_DATA')
#                print(self.all_node.node_2.node_id)
                self.state = TCP_GET_NODE_3_DATA
                self.makethread()
                self.consumer()

            elif self.state == TCP_GET_NODE_3_DATA:
                print('Consumer state == TCP_GET_NODE_3_DATA')
                self.all_node.node_3 = pickle.loads(data)
                self.update_form()
                self.get_relay_state()

            elif self.state == TCP_GET_RELAIS_CFG:
                print ('Consumer state == TCP_GET_RELAIS_CFG')
                self.cfg_data = pickle.loads(data)
                self.update_relay_state()

            elif self.state == TCP_GET_RELAY_STATE:
                print ('Consumer state == TCP_GET_RELAY_STATE')
                self.cfg_data = pickle.loads(data)
                self.update_relay_state()
                self.get_rrdgraph()

#                self.state = TCP_CONNECTED

            elif self.state == TCP_GET_LAST_RSSI:
                self.cfg_data = pickle.loads(data)
                self.update_last_rssi_state()

            elif self.state == TCP_GET_RRDGRAPH:
                print ('Consumer state == TCP_GET_RRDGRAPH')
                self.after_id = self.mainwindow.after(15000, self.get_fan_compost_data)
#                self.after_id = self.mainwindow.after(15000, self.get_fan_compost_data)

 #               self.state = TCP_CONNECTED


#            print('--consumer()')


    def makethread(self):
#        print('++makethread()')
        threading.Thread(target=self.producer())
#        print('--makethread()')

if __name__ == '__main__':
    root = Tk()
    app = Application(root)

    root.mainloop()
