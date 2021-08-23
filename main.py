# # This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import Qtrace_parser as qt
import pandas as pd
import run_parser as rp
import Automation
import create_manifest as man
import glob
import paramiko
import xml.etree.ElementTree as ET
import os
import shutil
from stat import S_ISDIR, S_ISREG
from time import sleep
from pathlib import Path
import os.path
from os import path
import re
import json_powerBI as jbi
Automation.main()
# jbi.push_to_powerbi('/var/www/html/LOG10T/FiVe/Classical/AEWB/21B/SBTS21B_ENB_0000_000785_000021/2021-08-09-copy',
  #                   '2CC_UL_TCP0')
#
#
# def main():
#     # print("connecting...")
#     client1 = Automation.connect_log_server()
#
#     # call pulltti on log server
#     Automation.call_pulltti(client1)
#
#     # rename logs in classical/cloud on log server
#     targetDirectory = \
#         input('/var/www/html/LOG10T/FiVe/Classical/AEWB/21B/SBTS21B_ENB_0000_000769_000000/2021-08-02-copy')
#
#     Automation.tar_logs(client1, targetDirectory)
#     Automation.rename_logs(client1, targetDirectory)
#
#     # get all the renamed files in subdirectories
#     global filelist
#     filelist = []
#     sftp1 = client1.open_sftp()
#     sftp1.chdir(targetDirectory)
#     print(sftp1.getcwd())
#
#     paths = Path('C:\Users\admin').glob('*/*.png')
#     for path in paths:
#         # because path is object not string
#         path_in_str = str(path)
#         # Do thing with the path
#         print(path_in_str)
#     # Automation.listdir_r(sftp1, targetDirectory, filelist)
#
#     # open connection to Windows PC
#     # client2 = Automation.connect_windows()
#     #
#     # Automation.filter_filelist()
#
#     # edit 1 xml document at a time, push xml file from machine B to machine C,
#     # push the corresponding log to machine C, run LTEPAT, and get Allevents.csv
#     # back onto machine B and then back onto A
#     # log_dict = {}
#     # for i in range(len(filelist)):
#     #     # move logs from log server to script Linux PC
#     #     Automation.get_log_from_server(client1, sftp1, filelist[i])
#     #
#     #     filename = filelist[i].split('/')[-1]
#
#         # if 'iperf' not in filename:
#         #     xml = Automation.edit_xml(filelist[i])
#         #
#         #     Automation.push_log_to_windows(client2, filelist[i], xml)
#         #
#         #     ltepat_output = Automation.run_LTEPAT(client2, xml)
#         #
#         #     # push AllEvents.csv and QTrace back onto machine B
#         #     log_dict = Automation.move_files_C_to_B(client2, filelist[i], i, xml, log_dict, ltepat_output)
#
#         # elif 'iperf' in filename:
#         #
#         #     os.chdir('/home/scpadm/LTEPAT_Results')
#         #
#         #     # make separate subdirectories for different tests
#         #     log_directory = '/' + '/'.join(filelist[i].split('/')[:-1])
#
#             # if log_dict.get(log_directory) == None:
#             #     # subdirectory is the test (ex. 1CC_UL_TCP)
#             #     subdirectory = str(log_directory.split('/')[-2]) + str(i)
#             #     os.mkdir(subdirectory)
#             #     log_dict.update({log_directory: subdirectory})
#             #
#             # os.chdir(log_dict.get(log_directory))
#
#     #         shutil.move('/home/scpadm/FiVe/' + filename, ('/home/scpadm/LTEPAT_Results/' +
#     #                                                       log_dict.get(log_directory) + '/' + filename))
#     #
#     # Automation.clear_B_and_C(client2)
#     #
#     # parser_input = Automation.create_parser_input(log_dict)
#     # print(parser_input)
#
#     # close client1 and sftp1 (connection to log server)
#     sftp1.close()
#     client1.close()
#     # client2.close()
#
#     # add Arnas stuff here
#     # man.fill_manifest(parser_input)
#
#
#
#
#
#
#     # ------------------------------------------------------
#
#     return 0
#
#
# main()
#
# # df = qt.file_reader('8CC TCP DL.hdf_QTraceMessages.xls')
# # print(df)
# # run_parser.run_big_parser()
# # run_parser.capture_output()
#
# # def print_hi(name):
# #     # Use a breakpoint in the code line below to debug your script.
# #     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
# #
# #
# # # Press the green button in the gutter to run the script.
# # if __name__ == '__main__':
# #     print_hi('PyCharm')
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/