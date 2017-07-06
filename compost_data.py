'''
Created on 2015-06-22

@author: caribou
'''


class NodeFanConfig:
    def __init__(self):
        self.PC1 = 0.0
        self.PC2 = 0.0
        self.PC3 = 0.0
        self.PC4 = 0.0
        self.TV1 = 0
        self.TV2 = 0
        self.TV3 = 0
        self.TV4 = 0
        self.TA1 = 0
        self.TA2 = 0
        self.TA3 = 0
        self.TA4 = 0
        self.delais_minute = 0
        self.node_compost_address_0 = 0
        self.node_compost_address_1 = 0
        self.node_compost_address_2 = 0
        self.node_compost_address_3 = 0
        self.node_compost_cfg_0 = 0
        self.node_compost_cfg_1 = 0
        self.node_compost_cfg_2 = 0
        self.node_compost_cfg_3 = 0
        self.node_compost_txt_0 = ''
        self.node_compost_txt_1 = ''
        self.node_compost_txt_2 = ''
        self.node_compost_txt_3 = ''



class CompostFanData:
    def __init__(self):
        self.timestamp = 0
        self.node_0_t_1 = 0.0
        self.node_0_t_2 = 0.0
        self.node_0_t_3 = 0.0
        self.node_0_t_4 = 0.0
        self.node_0_h_1 = 0.0
        self.node_0_bat_voltage = 0.0
        self.node_1_t_1 = 0.0
        self.node_1_t_2 = 0.0
        self.node_1_t_3 = 0.0
        self.node_1_t_4 = 0.0
        self.node_1_h_1 = 0.0
        self.node_1_bat_voltage = 0.0
        self.node_2_t_1 = 0.0
        self.node_2_t_2 = 0.0
        self.node_2_t_3 = 0.0
        self.node_2_t_4 = 0.0
        self.node_2_h_1 = 0.0
        self.node_2_bat_voltage = 0.0
        self.node_3_t_1 = 0.0
        self.node_3_t_2 = 0.0
        self.node_3_t_3 = 0.0
        self.node_3_t_4 = 0.0
        self.node_3_h_1 = 0.0
        self.node_3_bat_voltage = 0.0


class GroupeSondeID:
    def __init__(self):
        self.gp1_node_address = 0
        self.gp1_active = 0
        self.gp2_node_address = 0
        self.gp2_active = 0
        self.gp3_node_address = 0
        self.gp3_active = 0
        self.gp4_node_address = 0
        self.gp4_active = 0


class NodeData:
    def __init__(self):
        self.node_id = 0
        self.timestamp = 0
        self.t_1 = 0.0
        self.t_2 = 0.0
        self.t_3 = 0.0
        self.t_4 = 0.0
        self.h_1 = 0.0
        self.pression = 0.0
        self.conductivite = 0
        self.bat_voltage = 0.0
        self.last_rssi = 0
        self.txpower = 0
        self.data_received = 0


class AllNode:
    def __init__(self):
        self.node_0 = NodeData()
        self.node_1 = NodeData()
        self.node_2 = NodeData()
        self.node_3 = NodeData()


class CompostFanConfig:
    def __init__(self):
        self.relais_mode = 0
        self.relais_etat = 0
        self.relais_delais = 0
        self.relais_t_moyenne = 0.0
        self.relais_consigne_temperature_fan = 0.0
        self.relais_consigne_offset_min_temperature_fan = 0.0
        self.relais_consigne_offset_max_temperature_fan = 0.0


class CompostRRDGRAPH:
    def __init__(self):
        self.graph_id = 0
        self.graph_start = ""
        self.graph_end = ""
