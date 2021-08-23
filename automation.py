import paramiko
import xml.etree.ElementTree as ET
import os
import shutil
from stat import S_ISDIR, S_ISREG
import stat
from time import sleep
import create_manifest as cm
# main method to run all functions
def main():
    client1 = connect_log_server()
    # call pulltti on log server
    call_pulltti(client1)
    # rename logs in classical/cloud on log server
    targetDirectory = input("Enter complete file path of directory on log"
                            "server to convert/parse.\n(ex: /var/www/html/LOG10T/FiVe/1CC_UL_TCP/Iteration_1)"
                            "\nPlease only include 1 Iteration of 1 Test's worth of data: ")
    info_txt_directory = input("Please also enter the file path of the 'info.txt' file for the day's data set")
    tar_logs(client1, targetDirectory)
    rename_logs(client1, targetDirectory)
    # get all the renamed files in subdirectories
    global filelist
    filelist = []
    sub_dir_ = ''
    sftp1 = client1.open_sftp()
    sftp1.chdir(targetDirectory)
    listdir_r(sftp1, targetDirectory, filelist)
    # open connection to Windows PC
    client2 = connect_windows()
    filter_filelist()
    clear_B_and_C(client2)
    # edit 1 xml document at a time, push xml file from machine B to machine C,
    # push the corresponding log to machine C, run LTEPAT, and get Allevents.csv
    # back onto machine B and then back onto A
    log_dict = {}
    for i in range(len(filelist)):
        # move logs from log server to script Linux PC
        get_log_from_server(client1, sftp1, filelist[i])
        filename = filelist[i].split('/')[-1]
        if 'iperf' not in filename:
            xml = edit_xml(filelist[i])
            push_log_to_windows(client2, filelist[i], xml)
            ltepat_output = run_LTEPAT(client2, xml)
            # push AllEvents.csv and QTrace back onto machine B
            log_dict = move_files_C_to_B(client2, filelist[i], i, xml, log_dict, ltepat_output)
        elif 'iperf' in filename:
            os.chdir('/home/scpadm/LTEPAT_Results')
            # make separate subdirectories for different tests
            log_directory = '/' + '/'.join(filelist[i].split('/')[:-1])
            if log_dict.get(log_directory) == None:
                # subdirectory is the test (ex. 1CC_UL_TCP)
                subdirectory = str(log_directory.split('/')[-2]) + str(i)
                os.mkdir(subdirectory)
                log_dict.update({log_directory: subdirectory})
            os.chdir(log_dict.get(log_directory))
            sub_dir_ = log_dict.get(log_directory)
            shutil.move('/home/scpadm/raw_data/' + filename, ('/home/scpadm/LTEPAT_Results/' +
                                                              log_dict.get(log_directory) + '/' + filename))
    clear_B_and_C(client2)
    parser_input = create_parser_input(log_dict)
    print(parser_input)
    cm.fill_manifest(parser_input, info_txt_directory, sub_dir_)
    # close client1 and sftp1 (connection to log server)
    sftp1.close()
    move_files_B_to_A(client1, parser_input, targetDirectory)
    client1.close()
    client2.close()
    # add Arnas stuff here
    # ------------------------------------------------------
    return 0
# returns client for log server
def connect_log_server():
    # host information for Linux Log server PC
    host = "10.52.203.213"
    user = "scpadm"
    password = "scpadm"
    # connect to host PC using paramiko
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=password)
    return client
# returns client for Windows PC
def connect_windows():
    # host Windows PC information
    host = "10.52.203.16"
    user = r"NOKLAB\usnap-scpadm"
    password = "Scp@dm1!"
    # connect to host PC using paramiko
    client2 = paramiko.SSHClient()
    client2.load_system_host_keys()
    client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client2.connect(hostname=host, username=user, password=password)
    return client2
# call pulltti which is a script on log server
def call_pulltti(client1):
    client1.exec_command('cd /var/www/html/LOG10T/FiVe; python PullTTI.py')
    return 0
# recursive loop to generate all files in all subdirectories of a directory
def listdir_r(sftp, remotedir, filelist):
    for entry in sftp.listdir_attr(remotedir):
        remotepath = remotedir + "/" + entry.filename
        mode = entry.st_mode
        if S_ISDIR(mode):
            listdir_r(sftp, remotepath, filelist)
        elif S_ISREG(mode):
            filelist.append(remotepath)
# recursive loop to generate all files in all subdirectories of a directory
def listdir_r2(sftp, remotedir, trashList):
    for entry in sftp.listdir_attr(remotedir):
        remotepath = remotedir + "/" + entry.filename
        mode = entry.st_mode
        if S_ISDIR(mode):
            listdir_r2(sftp, remotepath, trashList)
        elif S_ISREG(mode):
            trashList.append(remotepath)
# tar log files for safety
def tar_logs(client1, filepath):
    sftp1 = client1.open_sftp()
    sftp1.chdir(filepath)
    tarFile = None
    # check if tarfile has already been created
    fileList = sftp1.listdir(sftp1.getcwd())
    for i in range(len(fileList)):
        if '.tar.gz' in fileList[i]:
            tarFile = fileList[i]
    if tarFile == None:
        client1.exec_command('cd ' + filepath + '; tar -czvf ' + filepath.split('/')[-1] + '.tar.gz ' + filepath)
    return 0
# rename these files
# a) Iperf server log (the one with -s) .txt to .txt => iperf_1CC_TCP_uni_UL_Iter2.txt
#       or iperf_1CC_TCP_bidir_UL_Iter2.txt
# b) QXDM txt (.hdf) => qxdm_1CC_TCP_uni_UL_iter2.txt
# c) TTI (Allevents) csv => tti_1CC_TCP_uni_UL_iter2.txt
def rename_logs(client1, targetDirectory):
    sftp1 = client1.open_sftp()
    sftp1.chdir(targetDirectory)
    # list of all files in all subdirectories
    global filelist
    filelist = []
    # populates filelist
    listdir_r(sftp1, targetDirectory, filelist)
    for a in range(len(filelist)):
        splitFile = filelist[a].split('/')
        negFileLength = len(splitFile[-1]) * -1
        for b in range(len(splitFile)):
            if ('CC' in splitFile[b] and '.' not in splitFile[b]):
                # uni = False means it is a bidirectional test
                uni = True
                if 'bidirectional' in splitFile[b].lower():
                    uni = False
                # grab info
                if uni == True:
                    num_carriers = splitFile[b][0:3]
                    direction = splitFile[b][4:6]
                    dataType = splitFile[b][7:10]
                elif uni == False:
                    highCC = splitFile[b][0:3]
                    lowCC = splitFile[b][4:7]
                    dataType = splitFile[b][22:25]
            if 'iteration' in splitFile[b].lower():
                iter_num = splitFile[b][-1]
        # rename iperf logs
        if 'iperf' in splitFile[-1] and '.txt' in splitFile[-1] and '_iter' not in splitFile[-1]:
            if uni == True:
                sftp1.rename(filelist[a], filelist[a][:negFileLength] + 'iperf_' + num_carriers
                             + '_' + dataType + '_uni_' + direction + '_iter' + iter_num + '.txt')
            elif uni == False:
                if 'UL' in splitFile[-1]:
                    sftp1.rename(filelist[a], filelist[a][:negFileLength] + 'iperf_' + lowCC
                                 + '_' + dataType + '_bidir_UL_iter' + iter_num + '.txt')
                elif 'DL' in splitFile[-1]:
                    sftp1.rename(filelist[a], filelist[a][:negFileLength] + 'iperf_' + highCC
                                 + '_' + dataType + '_bidir_DL_iter' + iter_num + '.txt')
        elif '.hdf' in splitFile[-1] and '_iter' not in splitFile[-1]:
            if uni == True:
                sftp1.rename(filelist[a], filelist[a][:negFileLength] + 'qxdm_' + num_carriers
                             + '_' + dataType + '_uni_' + direction + '_iter' + iter_num + '.hdf')
            elif uni == False:
                sftp1.rename(filelist[a], filelist[a][:negFileLength] + 'qxdm_' + highCC + '_' + lowCC
                             + '_' + dataType + '_bidir_iter' + iter_num + '.hdf')
        elif '.bin' in splitFile[-1] and '_iter' not in splitFile[-1]:
            if uni == True:
                sftp1.rename(filelist[a], filelist[a][:negFileLength] + 'tti_' + num_carriers
                             + '_' + dataType + '_uni_' + direction + '_iter' + iter_num + '.bin')
            elif uni == False:
                sftp1.rename(filelist[a], filelist[a][:negFileLength] + 'tti_' + highCC + '_' + lowCC
                             + '_' + dataType + '_bidir_iter' + iter_num + '.bin')
        elif '.pcap' in splitFile[-1] and '_iter' not in splitFile[-1]:
            if uni == True:
                sftp1.rename(filelist[a], filelist[a][:negFileLength] + 'bip_' + num_carriers
                             + '_' + dataType + '_uni_' + direction + '_iter' + iter_num + '.pcap')
            elif uni == False:
                sftp1.rename(filelist[a], filelist[a][:negFileLength] + 'bip_' + highCC + '_' + lowCC
                             + '_' + dataType + '_bidir_iter' + iter_num + '.pcap')
    sftp1.close()
    return 0
def filter_filelist():
    # remove all irrelevant files from filelist
    i = 0
    while i < len(filelist):
        filename = filelist[i].split('/')[-1]
        if ('iperf' not in filename and 'qxdm' not in filename and
                'bin' not in filename and 'bip' not in filename):
            filelist.pop(i)
        else:
            i += 1
    return 0
# push the iperf logs (-s .txt), qxdm logs (.hdf), ttitrace (.bin), and bip logs (.pcap) to Windows PC
def get_log_from_server(client1, sftp1, filepath):
    os.chdir('/home/scpadm/raw_data')
    # place in /home/scpadm/raw_data on Airframe Linux PC (machine B)
    localPath = '/home/scpadm/raw_data/' + filepath.split('/')[-1]
    sftp1.get(filepath, localPath)
    return 0
# release number fetching is basically hardcoded based on number of files in path
# edit xml files before sending to Windows PC
def edit_xml(datalog):
    filename = datalog.split('/')[-1]
    release = datalog.split('/')[9]
    # find correct xml template to edit
    if '.pcap' in filename:
        mytree = ET.parse('/home/scpadm/LTEPATTemplates/BIPTemplate.xml')
        myroot = mytree.getroot()
        # edit the filepath
        for file in myroot.iter('files'):
            file.text = str(r'C:\five_logs' + '\\' + filename)
        # edit the release
        for attr in myroot.iter('L1L2'):
            attr.set('release', release)
        mytree.write('/home/scpadm/LTEPATTemplates/BIPTemplate.xml')
        return 'BIPTemplate.xml'
    elif 'qxdm' in filename:
        mytree = ET.parse('/home/scpadm/LTEPATTemplates/QCAT5GLatestTemplate.xml')
        myroot = mytree.getroot()
        # edit the filepath
        for file in myroot.iter('files'):
            file.text = str(r'C:/five_logs' + '\\' + filename)
        mytree.write('/home/scpadm/LTEPATTemplates/QCAT5GLatestTemplate.xml')
        return 'QCAT5GLatestTemplate.xml'
    elif 'tti' in filename:
        mytree = ET.parse('/home/scpadm/LTEPATTemplates/TTITemplate.xml')
        myroot = mytree.getroot()
        # edit the filepath
        for file in myroot.iter('files'):
            file.text = str(r'C:\five_logs' + '\\' + filename)
        # edit the release
        for attr in myroot.iter('L1L2'):
            attr.set('release', release)
        mytree.write('/home/scpadm/LTEPATTemplates/TTITemplate.xml')
        return 'TTITemplate.xml'
    return 0
# push edited xml files and logs from machine B to machine C
def push_log_to_windows(client2, filepath, xml):
    sftp2 = client2.open_sftp()
    filename = filepath.split('/')[-1]
    # push edited xml file from machine B to machine C
    sftp2.put('/home/scpadm/LTEPATTemplates/' + xml, 'C:/LTEPATTemplates/' + xml)
    # transfer log files from Linux PC (machine B) to Windows PC (machine C)
    sftp2.put('/home/scpadm/raw_data/' + filename, 'C:/five_logs/' + filename)
    sftp2.close()
    return 0
# Convert QXDM .hdf to .txt & Qtrace using LTEPAT.exe
def run_LTEPAT(client2, xml):
    sftp2 = client2.open_sftp()
    # run LTEPAT.exe on the .hdf file to convert to .txt file
    client2.exec_command('C:\LTEPAT\LTEPAT.exe C:\LTEPATTemplates\\' + xml)
    # will be of size 3 if processing QXDM, otherwise will be of size 1
    ltepat_output = []
    if xml == 'QCAT5GLatestTemplate.xml':
        print("LTEPAT processing QXDM logs...")
        qtraceFileName = None
        qxdmtxtFileName = None
        qxdmxlsxFileName = None
        # wait for LTEPAT to process logs
        while qtraceFileName == None or qxdmtxtFileName == None or qxdmxlsxFileName == None:
            # get QTrace from LTEPAT_Results and put them on machine B
            curr_dir = sftp2.listdir('C:/five_logs')
            for a in range(len(curr_dir)):
                if 'qtrace' in curr_dir[a].lower():
                    qtraceFileName = curr_dir[a]
                if '.hdf_NR.txt' in curr_dir[a]:
                    qxdmtxtFileName = curr_dir[a]
                if '.hdf_NR.xlsx' in curr_dir[a]:
                    qxdmxlsxFileName = curr_dir[a]
            sleep(4)
        print("Writing Data to Files...")
        # wait for all QXDM logs to finish processing
        curr_dir2 = sftp2.listdir('C:/five_logs')
        qxdmCount = len(curr_dir2)
        while qxdmCount > 6:
            qxdmCount = 0
            curr_dir2 = sftp2.listdir('C:/five_logs')
            for b in range(len(curr_dir2)):
                if 'qxdm' in curr_dir2[b]:
                    qxdmCount += 1
            sleep(4)
        sleep(3)
        ltepat_output.append(qtraceFileName)
        ltepat_output.append(qxdmtxtFileName)
        ltepat_output.append(qxdmxlsxFileName)
    elif xml == 'TTITemplate.xml':
        print("LTEPAT processing TTITrace...")
        # wait for LTEPAT to process logs
        resultsFolderFound = False
        fileFound = False
        while resultsFolderFound == False:
            curr_dir = sftp2.listdir('C:/five_logs')
            for a in range(len(curr_dir)):
                if curr_dir[a] == 'LTEPAT_Results':
                    resultsFolderFound = True
            sleep(2)
        while fileFound == False:
            curr_dir2 = sftp2.listdir('C:/five_logs/LTEPAT_Results')
            for b in range(len(curr_dir2)):
                if curr_dir2[b] == 'AllEvents.csv':
                    fileFound = True
            sleep(2)
        # hard code set time for TTI trace to finish
        print("Sleeping for 420 seconds for TTI to finish")
        sleep(420)
    elif xml == 'BIPTemplate.xml':
        print("LTEPAT processing BIP logs...")
        # wait for LTEPAT to process logs
        resultsFolderFound = False
        fileFound = False
        while resultsFolderFound == False:
            curr_dir = sftp2.listdir('C:/five_logs')
            for a in range(len(curr_dir)):
                if curr_dir[a] == 'LTEPAT_Results':
                    resultsFolderFound = True
            sleep(2)
        while fileFound == False:
            curr_dir2 = sftp2.listdir('C:/five_logs/LTEPAT_Results')
            for b in range(len(curr_dir2)):
                if 'AllEvents.csv' in curr_dir2[b]:
                    fileFound = True
            sleep(2)
        print("Sleeping for 180 seconds for BIP to finish")
        sleep(180)
    sftp2.close()
    return ltepat_output
def move_files_C_to_B(client2, filepath, i, xml, log_dict, ltepat_output):
    sftp2 = client2.open_sftp()
    os.chdir('/home/scpadm/LTEPAT_Results')
    # make separate subdirectories for different tests
    # ex. /var/www/html/LOG10T/FiVe/Classical/AEWB/Trunk/SBTS00_ENB_9999_210714_000007/2021-07-16-backup/1CC_UL_UDP/Iteration_1
    log_directory = '/' + '/'.join(filepath.split('/')[:-1])
    if log_dict.get(log_directory) == None:
        # subdirectory is the test (ex. 1CC_UL_TCP0)
        subdirectory = str(log_directory.split('/')[-2]) + str(i)
        os.mkdir(subdirectory)
        log_dict.update({log_directory: subdirectory})
    os.chdir(log_dict.get(log_directory))
    if xml == 'TTITemplate.xml':
        binFile = None
        curr_dir3 = sftp2.listdir('C:/five_logs')
        for c in range(len(curr_dir3)):
            if '.bin' in curr_dir3[c]:
                binFile = curr_dir3[c]
        # get AllEvents.csv from LTEPAT_Results and put them on machine B
        alleventsLocalPath = str(os.getcwd()) + '/' + binFile.split('.')[0] + '.csv'
        sftp2.get('C:/five_logs/LTEPAT_Results/AllEvents.csv', alleventsLocalPath)
    elif xml == 'QCAT5GLatestTemplate.xml':
        qtraceFileName = ltepat_output[0]
        qxdmtxtFileName = ltepat_output[1]
        qxdmxlsxFileName = ltepat_output[2]
        qtraceLocalPath = str(os.getcwd()) + '/' + qtraceFileName
        qxdmtxtLocalPath = str(os.getcwd()) + '/' + qxdmtxtFileName
        qxdmxlsxLocalPath = str(os.getcwd()) + '/' + qxdmxlsxFileName
        sftp2.get('C:/five_logs/' + qtraceFileName, qtraceLocalPath)
        sftp2.get('C:/five_logs/' + qxdmtxtFileName, qxdmtxtLocalPath)
        sftp2.get('C:/five_logs/' + qxdmxlsxFileName, qxdmxlsxLocalPath)
    elif xml == 'BIPTemplate.xml':
        bipFile = None
        curr_dir3 = sftp2.listdir('C:/five_logs')
        for d in range(len(curr_dir3)):
            if '.pcap' in curr_dir3[d]:
                bipFile = curr_dir3[d]
        # get AllEvents.csv from LTEPAT_Results and put them on machine B
        alleventsLocalPath = str(os.getcwd()) + '/' + bipFile.split('.')[0] + '.csv'
        sftp2.get('C:/five_logs/LTEPAT_Results/' + bipFile + '_AllEvents.csv', alleventsLocalPath)
    sftp2.close()
    return log_dict
# remove unnecessary files from B and C
# clears /home/scpadm/raw_data on B and C:/five_logs on C
def clear_B_and_C(client2):
    sftp2 = client2.open_sftp()
    global trashList
    trashList = []
    listdir_r2(sftp2, 'C:/five_logs', trashList)
    for i in range(len(trashList)):
        sftp2.remove(trashList[i])
    if 'LTEPAT_Results' in sftp2.listdir('C:/five_logs'):
        sftp2.chdir('C:/five_logs')
        sftp2.rmdir('LTEPAT_Results')
    # clear /home/scpadm/raw_data on B
    fileList2 = os.listdir('/home/scpadm/raw_data')
    for j in range(len(fileList2)):
        os.remove('/home/scpadm/raw_data/' + fileList2[j])
    sftp2.close()
    return 0
def create_parser_input(log_dict):
    parser_input = []
    keyList = list(log_dict.keys())
    for i in range(len(keyList)):
        machineBLocation = '/home/scpadm/LTEPAT_Results/' + log_dict.get(keyList[i])
        parser_input.append(machineBLocation)
    return parser_input
def move_files_B_to_A(client1, parser_input, targetDirectory):
    sftp1 = client1.open_sftp()
    # parser_input should be an array with only 1 filepath in it
    filepath = parser_input[0]
    # safety feature: check if Parser_Output.xlsx is already in log server directory
    if 'Parser_Output.xlsx' in sftp1.listdir(targetDirectory):
        print("Parser_Output is already in log server directory. Exiting...")
        return 0
    if 'parser_input.tar.gz' in sftp1.listdir(targetDirectory):
        print("parser_input.tar.gz is already in log server directory. Exiting...")
        return 0
    sftp1.put(filepath + '/Output/Parser_Output.xlsx', targetDirectory + '/Parser_Output.xlsx')
    # additional files to be transferred
    dirList = os.listdir(filepath)
    transferList = []
    filenameList = []
    # filter transferList
    for i in range(len(dirList)):
        if dirList[i] != 'PARSE_MANIFEST.txt' and '.swp' not in dirList[i] and dirList[i] != 'Output':
            transferList.append(filepath + '/' + dirList[i])
            filenameList.append(dirList[i])
    # create directory to tar (tar all files in this directory)
    sftp1.chdir(targetDirectory)
    sftp1.mkdir('parser_input')
    for j in range(len(transferList)):
        sftp1.put(transferList[j], targetDirectory + '/parser_input/' + filenameList[j])
    # tar the files
    client1.exec_command(
        'cd ' + targetDirectory + '; tar -czvf parser_input.tar.gz ' + targetDirectory + '/parser_input')
    # remove untarred parser_input directory
    client1.exec_command('rm ' + targetDirectory + '/parser_input/*')
    sftp1.chdir(targetDirectory)
    sftp1.rmdir('parser_input')
    sftp1.close()
    return 0