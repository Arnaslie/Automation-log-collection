import pymongo
import datetime
import re
import csv
import pandas as pd
import xlrd
import openpyxl
import os
import create_manifest as cm
import Automation as auto
import subprocess
from pathlib import Path
def push_to_powerbi(info_txt_path, sub_dir_):
    collection_name = "KPI_NPV_FIVE"
    pattern_date = re.compile(r'\d\d\d\d-\d\d-\d\d')
    pattern_TL = re.compile(r'Test Line Name:.*')
    pattern_release = re.compile(r'gNB Software Version:.*')
    pattern_RU = re.compile(r'RU Type:.*')
    pattern_UE = re.compile(r'UE Type and Software:.*')
    TL = ''
    release = ''
    RU = ''
    UE = ''
    dl_iperf_app_tput = 0
    dl_phy_tput = 0
    dl_ipa_tput = 0
    dl_mcs = 0
    ul_iperf_app_tput = 0
    ul_phy_tput = 0
    ul_ipa_tput = 0
    ul_mcs = 0
    l3_filtered_rsrp = 0
    pathloss = 0
    direction = cm.pass_direction_to_json()
    protocol = cm.pass_protocol_to_json()
    bidir = cm.pass_bidir_to_json()
    num_dl = cm.pass_dl_carriers_to_json()
    num_ul = cm.pass_ul_carriers_to_json()
    client3 = auto.connect_log_server()
    sftp3 = client3.open_sftp()
    sftp3.get(info_txt_path + '/info.txt', '/home/scpadm/LTEPAT_Results/' + sub_dir_ + '/Output/info.txt')
    sftp3.close()
    client3.close()
    save_cwd = os.getcwd()
    print(save_cwd)
    os.chdir('/home/scpadm/LTEPAT_Results/' + sub_dir_ + '/Output')
    file_path = '/home/scpadm/LTEPAT_Results/' + sub_dir_ + '/Output/info.txt'
    Path(file_path).touch()
    with open('info.txt') as f:
        file = f.read()
        match_date = pattern_date.findall(file)
        match_TL = pattern_TL.findall(file)
        match_release = pattern_release.findall(file)
        match_RU = pattern_RU.findall(file)
        match_UE = pattern_UE.findall(file)
    for match in match_TL:
        match = match.split(':')
        TL = match[1]
        TL = TL[1:]
    for match in match_release:
        match = match.split(':')
        release = match[1]
        release = release[3:]
    for match in match_RU:
        match = match.split(':')
        RU = match[1]
        RU = RU[18:]
    for match in match_UE:
        match = match.split(':')
        UE = match[1]
        UE = UE.split(',')
        UE = UE[0]
    f.close()
    data_ = pd.read_excel('Parser_Output.xlsx', engine='openpyxl')
    dl_iperf_app_tput = (float(data_['Total DL PHY Throughput (mbps)']))
    dl_phy_tput = (float(data_['(QTRACE) Total DL PHY Throughput (Mbps)']))
    dl_ipa_tput = (float(data_['(QTRACE) DL IPA Throughput (Mbps)']))
    dl_mcs = (float(data_['DL MCS']))
    # ul_iperf_app_tput = (float(data_['DL MCS']))
    # print(ul_iperf_app_tput)
    ul_phy_tput = (float(data_['(QTRACE) UL PHY Throughput (Mbps)']))
    ul_ipa_tput = (float(data_['(QTRACE) UL IPA Throughput (Mbps)']))
    if bidir == 1:
        ul_mcs = (float(data_['(TTI) UL MCS']))
    l3_filtered_rsrp = (float(data_['L3 Filtered RSRP (db)']))
    pathloss = (float(data_['Pathloss (db)']))
    print(os.getcwd())
    os.chdir(save_cwd)
    timestamp = datetime.datetime.utcnow()
    data = [
        {
            "TL Name": TL,  # < string >, mandatory
            "Release": release,  # < string >, mandatory
            "Date": timestamp,  # < datetime.datetime >, mandatory
            "RU HW Type": RU,  # < string >
            "UE Type": UE,  # < string >
            "Direction": direction,  # < string >
            "Protocol": protocol,  # < string >
            "NUM DL Carriers": num_dl,  # < integer >
            "NUM UL Carriers": num_ul,  # < integer >
            "DL IPERF APP TPUT": dl_iperf_app_tput,  # < float >
            "DL PHY TPUT": dl_phy_tput,  # < float >
            "DL IPA TPUT": dl_ipa_tput,  # < float >
            "DL MCS": dl_mcs,  # < float >
            "UL IPERF APP TPUT": 0.1,  # < float >
            "UL PHY TPUT": ul_phy_tput,  # < float >
            "UL IPA TPUT": ul_ipa_tput,  # < float >
            "UL MCS": ul_mcs,  # < float >
            "L3 Filtered RSRP": l3_filtered_rsrp,  # < float >
            "Pathloss": pathloss  # < float >
        }
    ]
    con = pymongo.MongoClient(
      host="PLKR-SMPC.intra.noklab.net",
      username="PowerBI_public_user",
      password="InsertOnly!")
    try:
        x = con["PowerBI_public"][collection_name].insert_many(data)
        print("Inserted: " + str(data))
    except Exception as e:
        print(str(e) + "\n")
        validation = con["PowerBI_public"].command({'listCollections': 1, 'filter': {'name': collection_name}})
        for x in validation.get("cursor", {}).get("firstBatch", []):
            mandatory = x.get("options", {}).get("validator", {}).get("$jsonSchema", {}).get("required", [])
            print("required fields: " + ", ".join(mandatory) + "\n")
            for k, v in x.get("options", {}).get("validator", {}).get("$jsonSchema", {}).get("properties", {}).items():
                print(k + ": " + str(v))
    print("JSON data sent to PowerBI")