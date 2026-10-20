# Writing MetaCTF Services

Ideas

# Required files

## info.json

Has the following fields:

    "name" : "example_service",
    "authors" : ["UCSB Seclab <ctf-admin@lists.cs.ucsb.edu>"],
    "port" : 1337,
    "benign" : ["benign.py"],
    "exploit" : ["exploit.py"],
    "flag_id_description" : "The flag_id is the flag_id.",
    "service_description" : "This is an example service that's super l337.",
    "start_type": "scripted" or "binary" or "none",
    "build_dependencies" : ["example1", "example2"]
    "debian_dependencies" : ["example1", "example2"]
    
The target machine is assumed to already have ubuntu-minimal
    
## setflag.py

This script takes a flag as a parameter, generates a token and flag_id, uses them to store the flag in your service, and returns the flag_id and token.

    class SetFlag():
        def execute(self, ip, port, flag):
            # connect to the service
            # generate a flag id and token
            # set the flag
            
            self.flag_id = flag_id
            self.token = token
            self.error = 0
            self.error_msg = ''

## getflag.py

This script takes flag_id and token as parameters, interfaces with your service and returns the flag. 

    class GetFlag():
        def execute(self, ip, port, flag_id, token):
            # log in to the service using the flag_id and token
            # retrieve the flag
    
            self.flag = flag
            self.error = 0
            self.error_msg = ''

# Semi-required files

## install.sh

This script should compile and install the service into the $DESTDIR directory. When it is run, $PWD is the directory where the service's info.json file is. The following environment variables will be provided:

    DESTDIR: where to install your service. This represents the / directory of the target system
    SERVICE_USER: the username that will be created for your service

Optionally, this script can be ommitted for simple services by providing a "service_source" entry in info.json. The service will be automatically compiled (with some default compilation settings) and deployed. This isn't very recommended.

    "service_source": "example.c"

Example:

    #!/bin/bash
    gcc -o $DESTDIR/usr/ctf/example/example example.c -fno-stack-protector

## postinst.sh

This script should do any post-install setup. It will be executed on the image *after* the install is completed. This is purely optional.

    SERVICE_USER: the username that was created for you

## start.sh

This script should start your CTF service. It will be run as your service's user (user "example" for the "example" service). This script is only needed if "start_type" is set to "scripted".

If "start_type" is set to "binary", the following field must be provided for automatic service startup:

    "service_binary": "example"

## stop.sh

This script should stop your CTF service. It will be run as your service's user (user "example" for the "example" service). This script is only needed if "start_type" is set to "scripted".

If this file is ommitted, all processes owned by the service's user will be killed.

## benign.py

This script will interact with your program just to create benign traffic. This makes it so you can't just decide which connections are not from getflag and setflag scripts and block all others.

    class Benign():
        def execute(self, ip, port, flag_id, token):
            # connect up
            # interact
            # create new fake flags, if you really want to
            
            self.flag_id = flag_id
            self.token = token
            self.error = 0
            self.error_msg = ''

## exploit.py

This script will take a flag_id as a parameter and return the flag.

    class Exploit():
        def execute(self, ip, port, flag_id):
            # hax0r shit
            # get the flag
            
            self.flag = flag
            self.error = 0
            self.error_msg = ''