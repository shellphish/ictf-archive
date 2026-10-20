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
    createdeb --json=<json> --out_folder=<out_folder> [--only_working] [--check_existing_out] [--ignore_existing_in] 
'''

extra_packages = ["libapache2-mpm-itk","libc6-dev-i386","python-dev",
        "python-pip","python-virtualenv"]


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
            print "!","problem executing",args,shell
            print res[0]
            print res[1]
            print res[2]

    return res


def get_deb(folder,name=""):
    created_debs = [n for n in os.listdir(folder) if (n.endswith(".deb") and name in n)]
    if len(created_debs)==0:
        return None
    else:
        return created_debs[0]


def main():
    cmd_args = args = docopt.docopt(ARGS)
    #print cmd_args
    json_content = open(cmd_args["--json"]).read()
    json_data = json.loads(json_content)
    service_folder =  os.path.dirname(os.path.abspath(cmd_args["--json"]))
    print "===","START working on",json_data["name"]

    if not os.path.exists(cmd_args["--out_folder"]):
        os.makedirs(cmd_args["--out_folder"])

    if cmd_args["--check_existing_out"] and \
            get_deb(cmd_args["--out_folder"],json_data["name"])!=None:
        print json_data["name"], "already created"
        return 1

    if 'SUDO_USER' in os.environ:
        real_user = os.environ['SUDO_USER']
    else:
        print "WARNING","I may need to run with sudo to be able to install packages"
        real_user = getpass.getuser()

    #TODO check existing in

    print "installing extra_packages:",extra_packages
    args = ["apt-get","install","-y"]
    args.extend(extra_packages)
    res = exec_cmd(args)

    if cmd_args["--only_working"] and \
            ("is_working" not in json_data or not json_data["is_working"]):
        print json_data["name"], "is not flagged as working"
        return 1


    existing_deb_in_git = get_deb(service_folder)
    if existing_deb_in_git == None or cmd_args["--ignore_existing_in"]:
        delete_created = True
        if "build_dependencies" in json_data:
            print "installing build_dependencies:",json_data['build_dependencies']
            args = ["apt-get","install","-y"]
            args.extend(json_data['build_dependencies'])
            res = exec_cmd(args)

        print "running autopackage..."
        autopackage_fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), \
                "autopackage.py")
        res = exec_cmd([autopackage_fname,"-y"],cwd = service_folder)

        created_deb_fname = get_deb(service_folder)
        if created_deb_fname==None:
            print "ERROR","no .deb created","autopackage output:"
            print res[0]
            print res[1]
            print res[2]
            return 2

    else:
        print "deb already existing in git"
        delete_created = False
        created_deb_fname = existing_deb_in_git

    out_fname = os.path.join(cmd_args["--out_folder"],created_deb_fname)
    in_fname = os.path.join(service_folder,created_deb_fname)

    print "copying created deb in",out_fname
    shutil.copy2(in_fname,out_fname)
    os.chown(out_fname,getpwnam(real_user)[2],getpwnam(real_user)[3])
    if delete_created:
        os.unlink(in_fname)


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
sudo ./createdeb.py --json Services/ictf-2012-powerplan/info.json --out_folder ../outd/

find Services/ -name "info.json" | xargs -n1 -P1 -I {} sudo ./createdeb.py --json {}  --out_folder ../outd/ --only_working | tee ../out.txt
'''




