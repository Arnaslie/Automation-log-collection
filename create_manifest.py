# ? QXDM.txt,QTRACE.csv,TTI.csv,BIP.csv,
# IPERF_DL.txt,IPERF_UL.txt,sdx55,DIR,PROTO <- if
# qtrace parser will be run separately, and the output QTRACE.csv will be updated in the PARSE_MANIFEST.txt
from pathlib import Path
import os
import os.path
from os import path
import re
import run_parser as rp
import json_powerBI as jbi
import paramiko as pk
bidir_flag = 0
json_dir = ""
json_protocol = ""
num_dl_carriers = 0
num_ul_carriers = 0
def parse_manifest_creation(path) -> str:
    file_path = path + "/PARSE_MANIFEST.txt"
    Path(file_path).touch()
    print("manifest file has been created")
    return "PARSE_MANIFEST.txt"
def fill_manifest(f_list, info_txt_path, sub_dir_):
    QXDM_txt = "NONE"
    QXDM_pattern = re.compile(r'[qQ][xX][dD][mM].*?\.txt')
    QTRACE_xls = "NONE"
    QTRACE_pattern = re.compile(r'[qQ][xX][dD][mM].*?QTraceMessages\.xls')
    TTI_ALLevents_csv = "NONE"
    TTI_pattern = re.compile(r'[tT][tT][iI].*?\.csv')
    BIP_ALLevents_csv = "NONE"
    BIP_pattern = re.compile(r'[bB][iI][pP].*?\.csv')
    Iperf_UL = "NONE"
    iperf_UL_pattern = re.compile(r'[iI][pP][eE][rR][fF].*?UL.*?\.txt')
    Iperf_DL = "NONE"
    iperf_DL_pattern = re.compile(r'[iI][pP][eE][rR][fF].*?DL.*?\.txt')
    device = "sdx55"
    direction = "NONE"
    direction_pattern = re.compile(r'[UD]L')
    protocol = "NONE"
    protocol_pattern = re.compile(r'(UDP|TCP)')
    bidirectional_flag = 0
    template = QXDM_txt + "," + QTRACE_xls + "," + TTI_ALLevents_csv + "," + BIP_ALLevents_csv + "," + Iperf_UL + "," + Iperf_DL + "," + device + "," + direction + "," + protocol + "\n"
    for path in f_list:
        os.chdir(path)
        manifest_file = parse_manifest_creation(path)
        dir_files = os.listdir(path)
        for file in dir_files:
            match_QXDM = QXDM_pattern.findall(file)
            if (len(match_QXDM) > 0):
                QXDM_txt = match_QXDM[0]
                split_DP = QXDM_txt.split("_")
                direction = split_DP[4]
                protocol = split_DP[2]
                if (split_DP[3] == 'uni'):
                    bidirectional_flag = 0
                else:
                    bidirectional_flag = 1
                print(split_DP)
                carrier_num = split_DP[1]
                if bidirectional_flag == 0:
                    if direction == 'DL':
                        global num_dl_carriers
                        num_dl_carriers = int(carrier_num[0])
                    elif direction == 'UL':
                        global num_ul_carriers
                        num_ul_carriers = int(carrier_num[0])
            match_QTRACE = QTRACE_pattern.findall(file)
            if (len(match_QTRACE) > 0):
                QTRACE_xls = match_QTRACE[0]
            match_TTI = TTI_pattern.findall(file)
            if (len(match_TTI) > 0):
                TTI_ALLevents_csv = match_TTI[0]
            match_BIP = BIP_pattern.findall(file)
            if (len(match_BIP) > 0):
                BIP_ALLevents_csv = match_BIP[0]
            match_BIP = BIP_pattern.findall(file)
            if (len(match_BIP) > 0):
                BIP_ALLevents_csv = match_BIP[0]
            match_iperfUL = iperf_UL_pattern.findall(file)
            if (len(match_iperfUL) > 0):
                Iperf_UL = match_iperfUL[0]
            match_iperfDL = iperf_DL_pattern.findall(file)
            if (len(match_iperfDL) > 0):
                Iperf_DL = match_iperfDL[0]
                iperf_split = Iperf_DL.split('_')
                iperf_carrier = iperf_split[1]
                if bidirectional_flag == 1:
                    num_dl_carriers = int(iperf_carrier[0])
                    if num_dl_carriers == 8:
                        num_ul_carriers = 2
                    elif num_dl_carriers == 4:
                        num_ul_carriers = 1
        if (bidirectional_flag):
            direction = 'BIDIR'
        template = QXDM_txt + "," + QTRACE_xls + "," + TTI_ALLevents_csv + "," + BIP_ALLevents_csv + "," + Iperf_UL + "," + Iperf_DL + "," + device + "," + direction + "," + protocol + "\n"
        f = open(manifest_file, 'w')
        f.write(template)
        f.close()
        global bidir_flag
        bidir_flag = bidirectional_flag
        global json_dir
        json_dir = direction
        global json_protocol
        json_protocol = protocol
        rp.run_big_parser(path)
        jbi.push_to_powerbi(info_txt_path, sub_dir_)
def pass_direction_to_json():
    return json_dir
def pass_protocol_to_json():
    return json_protocol
def pass_bidir_to_json():
    return bidir_flag
def pass_dl_carriers_to_json():
    return num_dl_carriers
def pass_ul_carriers_to_json():
    return num_ul_carriers