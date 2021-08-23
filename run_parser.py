import os
import subprocess
import paramiko as pk
def run_big_parser(path):
    os.chdir('/home/scpadm/five/postproc')
    p1 = subprocess.run(
        ['python3', 'Parser18_five_bipcpp_qtrace_bidir.py', path])

