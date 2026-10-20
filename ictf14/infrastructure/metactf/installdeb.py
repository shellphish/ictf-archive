#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import os
import subprocess
import json
import getpass
from pwd import getpwnam  
import shutil


ARGS = '''
Usage:
    install_deb --ip=<ip> --deb=<deb> 
'''

extra_packages = ["libapache2-mpm-itk"]


def get_debs(folder):
    debs = [os.path.join(folder,n) for n in os.listdir(folder) if (n.endswith(".deb"))]
    return debs


def exec_cmd(args,cwd=None,shell=False,auto_error=True,debug=False):
    #debug = True
    if debug:
        print "EXECUTING:",repr(args),cwd,shell

    pipe = subprocess.PIPE
    p = subprocess.Popen(args,cwd=cwd,shell=shell,stdout=pipe,stderr=pipe)
    std = p.communicate()
    res = (std[0],std[1],p.returncode)
    
    if debug:
        print "RESULT:",repr(res)

    if auto_error:
        if res[2] != 0:
            print "ERROR","problem executing",args,shell,"-->",res[2]
            print res[0]
            print res[1]

    return res


def install_remote(fname,ip):
    pfname = os.path.basename(fname)
    service_name = pfname.split("_")[0]
    exec_cmd(["scp",fname,"root@"+ip+":"+os.path.join("/tmp",pfname)])
    print "deb copied"

    print "- installing (gdebi 1)..."
    res = exec_cmd(["ssh","root@"+ip,"--","gdebi","-n",os.path.join("/tmp",pfname)],auto_error=False)
    if res[2] != 0:
        print "ERROR","problem installing",pfname,"-->",res[2]
        print res[0]
        print res[1]
        return
    else:
        print pfname,"installed 1!"

    print "- uninstalling..."
    res = exec_cmd(["ssh","root@"+ip,"--","apt-get","remove","-y",service_name],auto_error=False)
    if res[2] != 0:
        print "ERROR","problem installing",pfname,"-->",res[2]
        print res[0]
        print res[1]
        return
    else:
        print pfname,"uninstalled!"

    print "- installing (gdebi 2)..."
    res = exec_cmd(["ssh","root@"+ip,"--","gdebi","-n",os.path.join("/tmp",pfname)],auto_error=False)
    if res[2] != 0:
        print "ERROR","problem installing",pfname,"-->",res[2]
        print res[0]
        print res[1]
        return
    else:
        print pfname,"installed 2!"

    print "- installing (gdebi 3)..."
    res = exec_cmd(["ssh","root@"+ip,"--","gdebi","-n",os.path.join("/tmp",pfname)],auto_error=False)
    if res[2] != 0:
        print "ERROR","problem installing",pfname,"-->",res[2]
        print res[0]
        print res[1]
        return
    else:
        print pfname,"installed 3!"


def main():
    cmd_args = docopt.docopt(ARGS)
    if os.path.isdir(cmd_args["--deb"]):
        flist = get_debs(cmd_args["--deb"])
    else:
        flist = [cmd_args["--deb"]]


    print "disable ASLR"
    disable_aslr = "\"echo 0 > /proc/sys/kernel/randomize_va_space\""
    exec_cmd(["ssh","root@"+cmd_args["--ip"],"--","bash","-c",disable_aslr])

    print "installing extra packages:",extra_packages
    exec_cmd(["ssh","root@"+cmd_args["--ip"],"--","apt-get","install","-y"]+extra_packages)
    print "creating ctf user"
    cmd_list = "adduser --gecos 'CTF player' --shell /bin/bash --disabled-password ctf".split()
    exec_cmd(["ssh","root@"+cmd_args["--ip"],"--"]+cmd_list,auto_error=False)

    print "setting mysql"    
    sql1 = "debconf-set-selections <<< 'mysql-server mysql-server/root_password password your_password'"
    sql2 = "debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password your_password'"
    exec_cmd(["ssh","root@"+cmd_args["--ip"],"--","bash","-c"]+[sql1],auto_error=False)
    exec_cmd(["ssh","root@"+cmd_args["--ip"],"--","bash","-c"]+[sql2],auto_error=False)

    print "===","START working on list:",flist
    for fname in flist:
        print "=","START working on:",fname
        install_remote(fname,cmd_args["--ip"])


if __name__ == "__main__":
    try:
        import docopt
    except:
        print "installing pip and docopt..."
        exec_cmd(["sudo","apt-get","install","-y","python-pip"])
        exec_cmd(["sudo","pip","install","docopt"])
        import docopt

    #IPython.embed()
    sys.exit(main())



'''
./installdeb.py --ip 192.168.48.153 --deb ../outd/

SER="mathconsole";cd /home/antoniob/metactf;  SER_J=`find . -name "info.json" | grep $SER`; SER_DIR=$(dirname $SER_J); SER_D="../outd/"$SER"_0.1_amd64.deb"; ./createdeb.py --json  $SER_J --out_folder ../outd/; ./installdeb.py --ip 192.168.48.153 --deb $SER_D; cd $SER_DIR; ../../tester.py info.json 192.168.48.153; cd /home/antoniob/metactf;

SER="passwordverify";SER_J=`find . -name "info.json" | grep $SER`; ./tester.py --simple $SER_J 192.168.48.153
'''




