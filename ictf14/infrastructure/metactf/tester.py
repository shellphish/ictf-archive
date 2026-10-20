#!/usr/bin/env python2.7
import sys
sys.path.insert(0,'.')

from os.path import join, dirname, abspath, isfile, isdir
import json
import traceback
import imp
import os
import argparse
import tempfile
try:
    import IPython
except ImportError:
    pass

VERSION='1.2.3'

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

HOST = None
PORT = None

STRESSTEST_TOTAL = 50
STRESSTEST_BUCKET = 5
assert STRESSTEST_TOTAL % STRESSTEST_BUCKET == 0, 'STRESSTEST_TOTAL needs to be a multiple of STRESSTEST_BUCKET'

# FIXME you should create an (empty) python virtualenv when no deps are specified.

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--info', dest='info_json', metavar='<info_json>', default='info.json', help='Path to the info.json file. Default: "./info.json"')
    parser.add_argument('--ip', dest='remote_ip', metavar='<remote_ip>', default='localhost', help='IP address of the remote end-point. Default: localhost.')
    parser.add_argument('--services-dir', dest='services_dir', metavar='<services_dir>', default=None, help='Path to the services dir.')
    parser.add_argument('--check-json', dest='check_json_flag', action='store_true', default=False, help='Just check that the JSON is OK.')
    parser.add_argument('--once', dest='once_flag', action='store_true', default=False, help='Run the scripts only once.')
    parser.add_argument('--single-thread', dest='single_thread_flag', action='store_true', default=False, help='Run the scripts multiple times, but one at the time.')
    parser.add_argument('--total-num', dest='total_num', default=0, help='Set the total number of runs. Default: %s' % STRESSTEST_TOTAL)
    parser.add_argument('--bucket-num', dest='bucket_num', default=0, help='Set the max number of runs at the same time. Default: %s' % STRESSTEST_BUCKET)
    parser.add_argument('--virtualenv', dest='virtualenv_dir', default=None, help='Use an already-existing virtualenv. Default: it creates a new one.')
    parser.add_argument('--assume-valid-virtualenv', dest='assume_valid_virtualenv_flag', action='store_true', default=False, help='Do not create a virtualenv. This assumes you are already using one.')
    parser.add_argument('--test-all-working', dest='test_all_working_flag', action='store_true', default=False, help='Test all working services.')
    parser.add_argument('--test-all-benign', dest='test_all_benign',action="store_true", default=False,help="Check all benign scripts against a fake IP to ensure they fail")
    parser.add_argument("--inverted",dest="inverted",action="store_true",default=False,help="Invert error behavior of some actions")
    parser.add_argument('--check-all-jsons', dest='check_all_jsons_flag', action='store_true', default=False, help='Check all JSONs.')
    parser.add_argument('--list-all-debian-deps', dest='list_all_debian_deps_flag', action='store_true', default=False, help='List all debian dependences.')
    parser.add_argument('--list-all-pip-deps', dest='list_all_pip_deps_flag', action='store_true', default=False, help='List all pip dependences.')
    parser.add_argument('--list-debian-deps', dest='list_debian_deps_flag', action='store_true', default=False, help='List debian dependences for a given service.')
    parser.add_argument('--list-pip-deps', dest='list_pip_deps_flag', action='store_true', default=False, help='List pip dependences for a given service.')
    parser.add_argument('--create-global-virtualenv', dest='global_virtual_env_dir', metavar='<global_virtual_env_dir>', default=False, help='Create a (global) python virtual environment.')
    parser.add_argument('-q', '--quiet', dest='quiet_flag', action='store_true', default=False, help='Quiet mode: suppress output from the scripts.')
    parser.add_argument('--strict', dest='strict_flag', action='store_true', default=False, help='Strict mode: stop when info.json is not OK.')
    parser.add_argument('--no-exploit', dest='no_exploit_flag', action='store_true', default=False, help='Disable running exploits during the test.')
    args = parser.parse_args()

    # TODO add default for services list


    #if args.test_all_working_flag:
        #assert args.remote_ip is not None, 'You need to specify the remote IP'
        #test_all_working(args.remote_ip)
        #return 0

    if args.check_all_jsons_flag:
        assert args.services_dir is not None, 'You need to specify the services dir'
        do_check_all_jsons(args.services_dir, args.strict_flag)
        return 0

    if args.test_all_benign:
        assert args.services_dir is not None, "you need to specify the services dir"
        do_check_all_benign(args.services_dir,args.strict_flag,args.remote_ip,args.quiet_flag,args.inverted)
        return 0

    if args.list_all_debian_deps_flag:
        assert args.services_dir is not None, 'You need to specify the services dir'
        do_list_all_debian_deps(args.services_dir)
        return 0

    if args.list_all_pip_deps_flag:
        assert args.services_dir is not None, 'You need to specify the services dir'
        do_list_all_pip_deps(args.services_dir)
        return 0

    if args.list_debian_deps_flag:
        assert isfile(args.info_json), 'You need to specify a valid info json'
        do_list_debian_deps(args.info_json)
        return 0

    if args.list_pip_deps_flag:
        assert isfile(args.info_json), 'You need to specify a valid info json'
        do_list_pip_deps(args.info_json)
        return 0

    if args.global_virtual_env_dir:
        assert args.services_dir is not None, 'You need to specify the services dir'
        assert not isdir(args.global_virtual_env_dir), 'Safety check: please specify an empty directory'
        do_create_global_virtual_env_dir(args.services_dir, args.global_virtual_env_dir)
        return 0


    info_fp = abspath(args.info_json)
    remote_ip = args.remote_ip

    # this throws an exception if fails
    check_info_file(info_fp)

    if args.check_json_flag:
        # Alright, I'm done.
        print 'info.json is OK'
        return 0

    # check if I should care about python virtualenv
    info = json.load(open(info_fp))
    deps = info['scripts-virtualenv']

    if len(deps) > 0 and not args.assume_valid_virtualenv_flag:
        if args.virtualenv_dir:
            run_test_in_virtual_env(args, args.virtualenv_dir)
            return 0
        else:
            virtualenv_dir = create_new_virtualenv()
            install_pip_deps_in_virtualenv(virtualenv_dir, deps)
            run_test_in_virtual_env(args, virtualenv_dir)
            return 0

    if args.once_flag:
        total_num = 1
        bucket_num = 1
    elif args.single_thread_flag:
        total_num = 10
        bucket_num = 1
    else:
        total_num = STRESSTEST_TOTAL
        bucket_num = STRESSTEST_BUCKET

    # honor explicit switches
    if args.total_num:
        total_num = int(args.total_num)
    if args.bucket_num:
        bucket_num = int(args.bucket_num)


    assert total_num % bucket_num == 0, 'total_num needs to be a multiple of bucket_num'

    if total_num > 1:
        do_stresstest(info_fp, remote_ip, total_num, bucket_num, args.no_exploit_flag)
        return 0

    test_all_scripts(info_fp, remote_ip, args.quiet_flag, args.no_exploit_flag)

    # clean up the generated .pyc
    info = json.load(open(info_fp))
    os.chdir(dirname(info_fp))
    scripts_fp = [info['getflag'], info['setflag']]
    scripts_fp.extend(info['benign'])
    scripts_fp.extend(info['exploit'])
    for script_fp in scripts_fp:
        pyc_fp = script_fp + 'c'
        try:
            if isfile(pyc_fp):
                os.remove(pyc_fp)
        except OSError:
            # when in stresstest, there is race condition..
            pass

    print GREEN + 'Simple test: SUCCESS (version v%s)' % VERSION + ENDC
    return 0



def test_all_working(remote_ip):
    services = []
    debs_dir = join(dirname(__file__), '../testing-debs')
    for f in sorted(os.listdir(debs_dir)):
        if f.endswith('.deb'):
            service = f.split('_')[0]
            services.append(service)

    print 'Found %s services' % len(services)

    services_dir = abspath(join(dirname(__file__), 'Services'))
    for service in services:
        print 'Testing %s..' % service
        service_dir = join(services_dir, service)
        print 'DIR: %s' % service_dir
        os.chdir(service_dir)
        cmd = '../../tester.py --single-thread info.json %s' % remote_ip
        os.system(cmd)
        #raw_input("OK..")


def get_all_info_jsons(services_dir):
    info_json_fps = []
    for service_dir in os.listdir(services_dir):
        info_json_fp = join(abspath(services_dir), service_dir, 'info.json')
        if isfile(info_json_fp):
            #print 'INFOFP:', info_json_fp
            #assert isfile(info_json_fp)
            info_json_fps.append(info_json_fp)
    return info_json_fps


def do_check_all_benign(services_dir, strict_flag,remote_ip,quiet_flag,invert_flag):
    # Get all the info jsons
    json_fps = get_all_info_jsons(services_dir)
    for info_fp in json_fps:
        print 'Checking %s' % info_fp
        try:
            # Do the actual check
            info_fp = abspath(info_fp)
            info_dir = dirname(info_fp)
            info = json.load(open(info_fp))

            # FIXME: this is ugly as shit
            global HOST, PORT
            HOST = remote_ip
            PORT = info['port']

            benign_fps = map(lambda fp:join(info_dir, fp), info['benign'])

            if quiet_flag:
                suppress_out = True
                suppress_err = True
            else:
                suppress_out = False
                suppress_err = False

            with StdSuppresser(suppress_out, suppress_err):
                flag = generate_new_flag()
                for benign_fp in benign_fps:
                    test_benign(benign_fp)
            if not inverted_flag:
                print "OK: " + info_dir
            else:
                print 'ERROR:' + info_dir

        except:
            if inverted_flag:
                print "OK: " + info_dir
            else:
                print "ERROR: " + info_dir
            if not quiet_flag:
                print 'WARNING: %s' % traceback.format_exc()





def do_check_all_jsons(services_dir, strict_flag):
    json_fps = get_all_info_jsons(services_dir)
    for json_fp in json_fps:
        print 'Checking %s' % json_fp
        try:
            check_info_file(json_fp)
        except AssertionError:
            if strict_flag:
                raise
            print 'WARNING: %s' % traceback.format_exc()


def do_list_all_debian_deps(services_dir):
    json_fps = get_all_info_jsons(services_dir)
    all_debian_deps = set()
    for json_fp in json_fps:
        #print 'CURRENT JSON: %s' % json_fp
        with open(json_fp, 'rb') as f:
            j = json.loads(f.read())
            debian_deps = j['scripts-packages']
            all_debian_deps.update(debian_deps)
    print 'List of debian deps'
    print '-------------------'
    for debian_dep in sorted(all_debian_deps):
        print debian_dep
    print '-------------------'


def do_list_all_pip_deps(services_dir):
    json_fps = get_all_info_jsons(services_dir)
    all_pip_deps = set()
    for json_fp in json_fps:
        #print 'CURRENT JSON: %s' % json_fp
        with open(json_fp, 'rb') as f:
            j = json.loads(f.read())
            pip_deps = j['scripts-virtualenv']
            all_pip_deps.update(pip_deps)
    print 'List of pip deps'
    print '-------------------'
    for pip_dep in sorted(all_pip_deps):
        print pip_dep
    print '-------------------'


def do_list_debian_deps(json_fp):
    with open(json_fp, 'rb') as f:
        j = json.loads(f.read())
        debian_deps = j['scripts-packages']
    print 'List of debian deps'
    print '-------------------'
    for debian_dep in debian_deps:
        print debian_dep
    print '-------------------'


def do_list_pip_deps(json_fp):
    with open(json_fp, 'rb') as f:
        j = json.loads(f.read())
        pip_deps = j['scripts-virtualenv']
    print 'List of pip deps'
    print '-------------------'
    for pip_dep in pip_deps:
        print pip_dep
    print '-------------------'


def do_create_global_virtual_env_dir(services_dir, global_virtual_env_dir):
    json_fps = get_all_info_jsons(services_dir)
    all_pip_deps = set()
    for json_fp in json_fps:
        with open(json_fp, 'rb') as f:
            j = json.loads(f.read())
            pip_deps = j['scripts-virtualenv']
            all_pip_deps.update(pip_deps)
    all_pip_deps = list(all_pip_deps)

    global_virtual_env_dir = abspath(global_virtual_env_dir)
    assert not isdir(global_virtual_env_dir)
    os.makedirs(global_virtual_env_dir)

    create_new_virtualenv(global_virtual_env_dir)
    install_pip_deps_in_virtualenv(global_virtual_env_dir, all_pip_deps)


# This throws an exception if the json is NOT valid.
#EDIT EG: Return the dict, so we can use it for stuff
def check_info_file(info_fp):

    if not isfile(info_fp):
        raise Exception('%s doesn\'t exist.' % info_fp)

    info = json.load(open(info_fp))

    fields = ['name', 'authors', 'port', 'getflag', 'setflag', 'benign',
              'exploit', 'flag_id_description', 'service_description']
    for f in fields:
        if f not in info.keys():
            raise Exception('Field "%s" not found.' % f)

    assert info['name'] != '' and not info['name'].startswith('ictf-')
    assert info['origin'] != ''
    assert type(info['authors']) == list and len(info['authors']) > 0
    assert type(info['port']) == int
    assert type(info['getflag']) != list and info['getflag'] != ''
    assert type(info['setflag']) != list and info['setflag'] != ''
    assert type(info['benign']) == list and len(info['benign']) > 0
    assert type(info['exploit']) == list and len(info['exploit']) > 0
    assert info['flag_id_description'] != ''
    assert info['service_description'] != ''
    assert type(info['scripts-virtualenv']) == list
    assert type(info['scripts-packages']) == list


def generate_new_flag():
    import string, random
    FLAG_POSSIBILITIES = string.ascii_uppercase + string.digits + string.ascii_lowercase
    new_flag = ''.join(random.choice(FLAG_POSSIBILITIES) for x in range(13))
    return "FLG" + new_flag


def test_benign(benign_fp):
    try:
        print YELLOW, 'Benign()', ENDC
        benign = imp.load_source('benign', benign_fp)
        from benign import Benign
        b = Benign()
        b.execute(HOST, PORT, '', '')
        res = b.result()
        print 'Result: %s' % str(res)
        assert res['ERROR'] == 0
    except AssertionError:
        print 'AssertionError while executing Benign'
        print traceback.format_exc()
        print '----------------------'
        print RED + 'ERROR' + ENDC
        sys.exit(2)
    except Exception:
        print 'Exception while executing Benign'
        print traceback.format_exc()
        print '----------------------'
        print RED + 'ERROR' + ENDC
        sys.exit(2)


def test_setflag(setflag_fp, flag):
    try:
        print YELLOW, 'SetFlag(flag=%s)' % flag, ENDC
        setflag = imp.load_source('setflag', setflag_fp)
        from setflag import SetFlag
        sf = SetFlag()
        sf.execute(HOST, PORT, flag)
        res = sf.result()
        print 'Result: %s' % str(res)
        flag_id = res['FLAG_ID']
        token = res['TOKEN']
        assert type(flag_id) == str and flag_id
        assert res['ERROR'] == 0
        return flag_id, token
    except AssertionError:
        print 'AssertionError while executing Setflag'
        print traceback.format_exc()
        print '----------------------'
        print RED + 'ERROR' + ENDC
        sys.exit(2)
    except Exception:
        print 'Exception while executing Setflag'
        print traceback.format_exc()
        print '----------------------'
        print RED + 'ERROR' + ENDC
        sys.exit(2)


def test_getflag(getflag_fp, flag_id, token, flag):
    try:
        print YELLOW, 'GetFlag(flag_id=%s, token=%s)' % (flag_id, token), ENDC
        getflag = imp.load_source('getflag', getflag_fp)
        from getflag import GetFlag
        cf = GetFlag()
        cf.execute(HOST, PORT, flag_id, token)
        res = cf.result()
        print 'Result: %s' % str(res)
        assert res['ERROR'] == 0
        assert res['FLAG'] == flag
    except AssertionError:
        print 'AssertionError while executing Getflag'
        print traceback.format_exc()
        print '----------------------'
        print RED + 'ERROR' + ENDC
        sys.exit(2)
    except Exception:
        print 'Exception while executing Getflag'
        print traceback.format_exc()
        print '----------------------'
        print RED + 'ERROR' + ENDC
        sys.exit(2)


def test_exploit(exploit_fp, flag_id, flag):
    try:
        print YELLOW, 'Exploit(flag_id=%s)' % (flag_id), ENDC
        exploit = imp.load_source('exploit', exploit_fp)
        from exploit import Exploit
        e = Exploit()
        e.execute(HOST, PORT, flag_id)
        res = e.result()
        print 'Result: %s' % str(res)
        assert res['ERROR'] == 0
        assert res['FLAG'] == flag
    except AssertionError:
        print 'AssertionError while executing Exploit'
        print traceback.format_exc()
        print '----------------------'
        print RED + 'ERROR' + ENDC
        sys.exit(2)
    except Exception:
        print 'Exception while executing Exploit'
        print traceback.format_exc()
        print '----------------------'
        print RED + 'ERROR' + ENDC
        sys.exit(2)


def test_all_scripts(info_fp, remote_ip, quiet_flag, no_exploit_flag):
    info_fp = abspath(info_fp)
    info_dir = dirname(info_fp)
    info = json.load(open(info_fp))

    # FIXME: this is ugly as shit
    global HOST, PORT
    HOST = remote_ip
    PORT = info['port']

    benign_fps = map(lambda fp:join(info_dir, fp), info['benign'])
    if no_exploit_flag:
        exploit_fps = []
    else:
        exploit_fps = map(lambda fp:join(info_dir, fp), info['exploit'])
    getflag_fp = join(info_dir, info['getflag'])
    setflag_fp = join(info_dir, info['setflag'])

    if quiet_flag:
        suppress_out = True
        suppress_err = True
    else:
        suppress_out = False
        suppress_err = False

    with StdSuppresser(suppress_out, suppress_err):
        flag = generate_new_flag()
        for benign_fp in benign_fps:
            test_benign(benign_fp)
        flag_id, token = test_setflag(setflag_fp, flag)
        test_getflag(getflag_fp, flag_id, token, flag)
        test_getflag(getflag_fp, flag_id, token, flag)
        for exploit_fp in exploit_fps:
            test_exploit(exploit_fp, flag_id, flag)

        flag2 = generate_new_flag()
        flag_id2, token2 = test_setflag(setflag_fp, flag2)
        for benign_fp in benign_fps:
            test_benign(benign_fp)
        for exploit_fp in exploit_fps:
            test_exploit(exploit_fp, flag_id2, flag2)
        for benign_fp in benign_fps:
            test_benign(benign_fp)
        test_getflag(getflag_fp, flag_id2, token2, flag2)
        test_getflag(getflag_fp, flag_id2, token2, flag2)

        for exploit_fp in exploit_fps:
            test_exploit(exploit_fp, flag_id, flag)
        for exploit_fp in exploit_fps:
            test_exploit(exploit_fp, flag_id2, flag2)

        # NOTE: We set fake flags, getflag must still work
        test_getflag(getflag_fp, flag_id, token, flag)
        test_getflag(getflag_fp, flag_id, token, flag)


def do_stresstest(info_json, remote_ip, total_num, bucket_num, no_exploit_flag):
    print 'Running tester.py %d times (%d at a time)' % (total_num, bucket_num)
    for idx in range(total_num/bucket_num):
        print 'Round #%d..' % (idx+1),
        stresstest_fp = join(dirname(__file__), 'stresstest.sh')
        cmd = '%s %s %s %d %s' % (stresstest_fp, info_json, remote_ip, bucket_num, '--no-exploit' if no_exploit_flag else '')
        output = os.popen(cmd).read()
        success_num = int(output)
        assert success_num == bucket_num, RED + 'ERROR: Round #%d succeeded only %d/%d' % (idx+1, success_num, bucket_num) + ENDC
        print 'OK'
    print GREEN + 'Stress test SUCCEEDED! (version: v%s)' % VERSION + ENDC


def create_new_virtualenv(venv_dir=None):
    if venv_dir is None:
        venv_dir = tempfile.mkdtemp()
    cmd = 'virtualenv -p /usr/bin/python %s' % venv_dir
    print 'CMD: %s' % cmd
    os.system(cmd)
    return venv_dir


def install_pip_deps_in_virtualenv(virtualenv_dir, deps):
    # NOTE: install deps one at the time because sometimes pip fucks it up.
    for dep in deps:
        cmd = 'bash -c "source %s/bin/activate; pip install %s"' % (
            virtualenv_dir, dep)
        print 'CMD: %s' % cmd
        os.system(cmd)


def run_test_in_virtual_env(args, virtualenv_dir):
    cmd_switches = ''
    cmd_switches += '--once ' if args.once_flag else ''
    cmd_switches += '--single-thread ' if args.single_thread_flag else ''
    cmd_switches += '--total-num ' if args.total_num else ''
    cmd_switches += '--bucket-num ' if args.bucket_num else ''
    cmd_switches += '--no-exploit ' if args.no_exploit_flag else ''
    cmd = 'bash -c "source %s/bin/activate; %s %s --assume-valid-virtualenv --info %s --ip %s"' % (
        virtualenv_dir,
        abspath(__file__),
        cmd_switches,
        args.info_json,
        args.remote_ip,
    )
    print 'CMD: %s' % cmd
    os.system(cmd)


class StdSuppresser():
    def __init__(self, suppress_out=True, suppress_err=True):
        self.suppress_out = suppress_out
        self.suppress_err = suppress_err

    def __enter__(self):
        self.devnull_f = open('/dev/null', 'w')
        if self.suppress_out:
            self.orig_stdout = sys.stdout
            sys.stdout = self.devnull_f
        if self.suppress_err:
            self.orig_stderr = sys.stderr
            sys.stderr = self.devnull_f
        return self

    def __exit__(self, type, value, traceback):
        if self.suppress_out:
            sys.stdout = self.orig_stdout
        if self.suppress_err:
            sys.stderr = self.orig_stderr
        self.devnull_f.close()


if __name__ == '__main__':
    sys.exit(main())
