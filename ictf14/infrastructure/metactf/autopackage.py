#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: If you are not us, consider changing the copyright and name strings :)

# TODO: Consider switching back to the standard dh_make + Makefile method.
#       (See create-debian.sh in the 2013 repository.)
#
#       Also, reconsider the "mixed" build/install, the use of Architecture: any,
#       and the use of debuild in lieu of dpkg-buildpackage or pdebuild.

import argparse
import logging
import json
import os
import re
import shutil
import subprocess
import textwrap


AUTOCONFIRM=False

player_username='ctf'


# These cannot catch everything, obviously, but should help.

def must_confirm(msg):
    if not AUTOCONFIRM:
        assert raw_input("{} Type 'yes' to continue: ".format(msg)) == 'yes'

def ask_for_confirmation_on_mentions(needle, haystack, msg=None, start_only=False):
    lines = [ l for l in haystack.splitlines() if ((l.startswith(needle)) if start_only else (needle in l)) ]
    if lines:
        print "These lines contain '{}':".format(needle)
        print '    ', '\n    '.join(lines)
        if msg:
            print(msg)
        must_confirm("Is the script OK?")


def sanity_check_sh(custom_sh, debian_dep):
    # This is tricky
    if 'randomize_va_space' in custom_sh:
        print "Do NOT disable ASLR on the whole machine. If necessary, the service should use 'setarch --addr-no-randomize' when running its stuff."
        assert 'randomize_va_space' not in custom_sh
    ask_for_confirmation_on_mentions('adduser', custom_sh, 'Apart from very special cases (multi-user services), you should not add custom users.')
    ask_for_confirmation_on_mentions('useradd', custom_sh, 'Apart from very special cases (multi-user services), you should not add custom users.')
    assert 'inetd.conf' not in custom_sh
    ask_for_confirmation_on_mentions('chown', custom_sh, "Apart from special cases, files should not have custom owners. Also, owners in /usr/ctf/... and /var/ctf/... are overridden anyway.")
    ask_for_confirmation_on_mentions('chgrp', custom_sh, "Apart from special cases, files should not have custom owners. Also, owners in /usr/ctf/... and /var/ctf/... are overridden anyway.")
    ask_for_confirmation_on_mentions('chmod', custom_sh, "Apart from special cases, files should not have custom permissions. Also, permissions in /usr/ctf/... and /var/ctf/... are overridden anyway.")
    ask_for_confirmation_on_mentions('setcap', custom_sh, "Custom capabilities open scary possibilities for code-executing exploits... avoid them, if possible.", start_only=True)
    if 'apache' in custom_sh:
        print "You seem to be using Apache. Make sure the service does _not_ change the global configuration, is compatible with other services."
        print
        print "Info at https://git.seclab.cs.ucsb.edu/gitlab/ictf/ictf-framework/issues/8"
        print
        print 'Make sure the script only affects /etc/sites-enabled.d/service_name.conf (not the global apache2.conf), and gives _no_ file-execution permissions to www-data.'
        ask_for_confirmation_on_mentions('apache', custom_sh)
        # TODO: actual (pre-)dependencies chain
        #assert not re.search(r'\Wapache2-mpm-itk', debian_dep)
        #assert 'libapache2-mpm-itk' in debian_dep
    assert 'apache2.conf' not in custom_sh

    if 'mysql' in custom_sh:
        print "You seem to be using MySQL. Make sure the service does _not_ change the global configuration, uses /etc/mysql/debian.cnf on install instead of the 'root' user, and uses only its own DB and user."
        print "Info at https://git.seclab.cs.ucsb.edu/gitlab/ictf/ictf-framework/issues/9"
        assert 'my.cnf' not in custom_sh
        ask_for_confirmation_on_mentions('mysql', custom_sh) 
        assert 'mysql' in debian_dep

    # Finally, whitelist "OK" /etc mentions and check for other /etc uses
    custom_sh = custom_sh.replace('/etc/apache2/sites-enabled.d/','{sites_enabled}')
    custom_sh = custom_sh.replace('/etc/apache2/sites-available.d/','{sites_available}')
    custom_sh = custom_sh.replace('--defaults-extra-file=/etc/mysql/debian.cnf','{uses_mysql_debian_cnf}')
    ask_for_confirmation_on_mentions('/etc', custom_sh, "Your script seem to be doing something with /etc. Make sure you do not interfere with other services or global settings.")
    ask_for_confirmation_on_mentions('/proc', custom_sh, "Your script seem to be doing something with /proc. This is quite unusual. Make sure you do not interfere with other services or global settings.")
    ask_for_confirmation_on_mentions('sysctl', custom_sh, "Your script seem to be doing something with sysctl. Make sure you do not interfere with other services or global settings.")

def sanity_check_on_install_sh(debian_dep):
    with open('install.sh') as f:
        install_sh = f.read()
    if 'DESTDIR' in install_sh:
        print "OK, you have at least one DESTDIR use in install.sh"
        print "Still, make sure everything is set to install stuff in $DESTDIR/..."
    else:
        print "I don't see 'DESTDIR' mentioned in your install.sh"
        print "For instance, /usr/ctf/xxx should be installed as $DESTDIR/usr/ctf/xxx"
        assert 'DESTDIR' in install_sh
    sanity_check_sh(install_sh, debian_dep)

def sanity_check_on_postinst_sh(debian_dep):
    with open('postinst.sh') as f:
        postinst_sh = f.read()
    sanity_check_sh(postinst_sh, debian_dep)
    if 'apache' in postinst_sh:
        assert 'restart' in postinst_sh # Let's be safe here (a reload might also be fine for simple cases).
    ask_for_confirmation_on_mentions('mv', postinst_sh, "If possible, don't move files in postinst. Just put them in the correct place in install.sh.", start_only=True)
    ask_for_confirmation_on_mentions('cp', postinst_sh, "If possible, don't copy files in postinst. Just put them in the correct place in install.sh.", start_only=True)
    ask_for_confirmation_on_mentions('ln', postinst_sh, "If possible, don't link files in postinst. Just put them in the correct place in install.sh.", start_only=True)
    ask_for_confirmation_on_mentions('rm', postinst_sh, "Don't delete files in postinst! If players must not see them, they should not be in the package!", start_only=True)
    ask_for_confirmation_on_mentions('mkdir', postinst_sh, "If possible, don't create extra directories in postinst. The standard ones are automatically created, custom ones should go in the package (install.sh).", start_only=True)

def sanity_check_on_scripted_start(rw_dir, service_name):
    must_confirm("This service has custom start/stop.sh scripts. Is that intended?")
    with open('start.sh') as f:
        start_sh = f.read()
    with open('stop.sh') as f:
        stop_sh = f.read()
    scripts = start_sh + '\n' + stop_sh
    if 'start-stop-daemon' in scripts:
        print("\nThe script is using start-stop-daemon. Make sure it's using '--name some_unique_name', otherwise another service with the same executable file (e.g., 'python') will not start.")
        # XXX: process names are limited to 15 characters!
        print("This is my suggestion:\n     /sbin/start-stop-daemon -b --start --chdir /var/ctf/{} --name {} --exec ...\n".format(service_name, service_name[-15:]))
        ask_for_confirmation_on_mentions('start-stop-daemon', scripts)
    if rw_dir.endswith('/'):
        rw_dir = rw_dir[:-1]
    if rw_dir not in start_sh:
        must_confirm("I don't see {} mentioned in start.sh. Unless there is a specific reason not to, the script should chdir there.".format(rw_dir))




def sanity_check_on_files(destdir, info):

    ############### FIXME #################
    #
    #          Stopped working
    #
    return True


    # TODO: check for non-stripped binaries

    all_ok = True

    other_expected_files = [
            '/usr/share/doc/{}/copyright'.format(info['name']),
            '/usr/share/doc/{}/changelog.gz'.format(info['name']),
            '/etc/init.d/{}'.format(info['name']),
            '/etc/sudoers.d/sudo_for_{}'.format(info['name']),
        ]

    ro_dir = info['ro_dir']
    rw_dir = info['rw_dir']
    ro_files = []
    rw_files = []
    unusual = []

    def warn_on(why, what, mode):
        print "{}: {} (mode: {})".format(why, what, oct(mode))

    def check_dir(path, mode):
        if any(exp.startswith(path) for exp in other_expected_files):
            return True
        if ro_dir.startswith(path) or rw_dir.startswith(path):
            return True
        warn_on('Unusual dir', path, mode)
        unusual.append(path)
        return False

    def check_file(dir_on_vm, filename, mode):
        filepath = dir_on_vm + '/' + filename
        if filepath in other_expected_files:
            return True
        if ro_dir.startswith(dir_on_vm):
            ro_files.append(filepath)
            return True
        if rw_dir.startswith(dir_on_vm):
            rw_files.append(filepath)
            return True
        warn_on('Unusual file', filepath, mode)
        unusual.append(filepath)
        return False

    # Walks destdir and checks every file and directory    
    def filewalk_error(e):
        raise e
    for dirpath, _, filenames in os.walk(destdir, onerror=filewalk_error):
        onvm = '/'+os.path.relpath(dirpath, destdir)
        if onvm.startswith('/DEBIAN') or onvm == '/.':
            continue
        ok = check_dir(onvm, os.stat(dirpath).st_mode)
        all_ok = all_ok and ok
        for f in filenames:
            ok = check_file(onvm, f, os.stat(dirpath+'/'+f).st_mode) and all_ok
            all_ok = all_ok and ok

    print("\nFile permissions recap (note: I cannot check postinst.sh)")
    print("\nThe service will have read-only access to files in "+ro_dir)
    print("\n".join(ro_files))
    print("\nThe service will have write access to files in "+rw_dir)
    print("\n".join(rw_files))
    if unusual:
        print("\nYou will need to manually set permissions for these non-standard files: "+rw_dir)
        print("\n".join(rw_files))

    must_confirm("Are the files, paths, and permissions OK?")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--autoconfirm', action='store_true')
    parser.add_argument('-v', '--version', default='0.1')
    args = parser.parse_args()
    AUTOCONFIRM = args.autoconfirm
    version = args.version
    assert re.match(r'^[a-zA-Z0-9._-]+$', version)

    # Read JSON file
    with open("info.json", "r") as info_fh:
        info = json.load(info_fh)

    # Default directories
    info['ro_dir_rel'] = 'usr/ctf/{0[name]}/'.format(info)
    info['rw_dir_rel'] = 'var/ctf/{0[name]}/'.format(info)
    info['ro_dir'] = '/'+info['ro_dir_rel']
    info['rw_dir'] = '/'+info['rw_dir_rel']

    # Create debian directory
    try:
        os.makedirs("debian/source")
    except OSError:
        logging.warning("debian/ directory already exists")

    # Empty changelog
    with open("debian/changelog", "w") as changelog_fh:
        timestamp = """\
                       {0[name]} ({version}) unstable; urgency=low

                         * Initial release.

                        -- UCSB iCTF Team <ctf-admin@lists.cs.ucsb.edu> Fri, 06 Dec 2013 08:00:00 -0800
                    """
        changelog_fh.write(textwrap.dedent(timestamp.format(info, version=version)))

    with open("debian/compat", "w") as compat_fh:
        compat_fh.write("8")
    subprocess.check_call(['touch','debian/docs'])

    # Allow players to execute the service exactly as if it was auto-started
    with open("debian/sudo_for_{}".format(info['name']), "w") as f:
        f.write('{0} ALL= ({1}:{1}) NOPASSWD: ALL'.format(player_username, info['name']))
    with open("debian/install", "w") as f:
        f.write('debian/sudo_for_{} etc/sudoers.d'.format(info['name']))

    # Dependencies
    debian_dep = ", ".join(["ubuntu-minimal", "${shlibs:Depends}", "${misc:Depends}", "adduser"] +
                           info.get("debian_dependencies", []))

    build_dep = ", ".join(info.get("build_dependencies", []) + ["debhelper (>= 8)"])

    # Package information
    control = """\
                 Source: {0[name]}
                 Section: unknown
                 Priority: extra
                 Maintainer: UCSB iCTF Team <ctf-admin@lists.cs.ucsb.edu>
                 Build-Depends: {2}
                 Standards-Version: 3.9.4
                 Homepage: http://ictf.cs.ucsb.edu

                 Package: {0[name]}
                 Architecture: any
                 Depends: {1}
                 Description: {0[name]} CTF service
                  NOTE: this service is initially vulnerable - other teams can steal your flags!
                  .
                  You will need to patch it and keep it working for benign users.
              """
    with open("debian/control", "w") as control_fh:
        control_fh.write(textwrap.dedent(control.format(info, debian_dep, build_dep)))
    debian_copyright = """\
                Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
                Upstream-Name: {0[name]}
                Source: <http://ictf.cs.ucsb.edu>

                Files: *
                Copyright: 2014 The Regents of the University of California
                License: All rights reserved
            """
    with open("debian/copyright", "w") as control_fh:
        control_fh.write(textwrap.dedent(debian_copyright.format(info)))

    with open("debian/{0[name]}.dirs".format(info), "w") as dirs_fh:
        dirs_fh.write(info['ro_dir_rel'])

    with open("debian/source/format", "w") as source_format_fh:
        source_format_fh.write("3.0 (native)")

    if info["start_type"] != "none":
        init = """\
                  #!/bin/sh
                  ### BEGIN INIT INFO
                  # Provides:          {0[name]}
                  # Required-Start:    $all
                  # Required-Stop:     $remote_fs
                  # Default-Start:     2 3 4 5
                  # Default-Stop:      0 1 6
                  # Short-Description: {0[name]} iCTF service
                  # Description:       {0[name]} iCTF service
                  ### END INIT INFO

                  # Author: UCSB iCTF Team <ctf-admin@lists.cs.ucsb.edu>

                  PATH=/sbin:/usr/sbin:/bin:/usr/bin


                  do_start() {{
                    su -l --command {0[ro_dir]}/start.sh {0[name]}
                  }}

                  do_stop() {{
                    if ! su -l --command {0[ro_dir]}/stop.sh {0[name]}; then
                      echo "Could not call stop.sh. Resorting to pkill."
                      pkill -u {0[name]}
                      pkill -KILL -u {0[name]}
                      true
                    fi
                  }}

                  case "$1" in
                    start)
                      do_start
                      ;;
                    stop)
                      do_stop
                      ;;
                    restart|force-reload)
                      do_stop
                      do_start
                      ;;
                    *)
                      exit 3
                      ;;
                  esac
               """
        with open("debian/{0[name]}.init".format(info), "w") as init_fh:
            init_fh.write(textwrap.dedent(init.format(info)))

        if info["start_type"] == "binary":
            # TODO: Switch away from start-stop-daemon? It seems more confusing than everything.
            start = """\
                       #!/bin/sh
                       /sbin/start-stop-daemon \\
                           --background \\
                           --start \\
                           --chuid {0[name]} \\
                           --chdir {0[rw_dir]} \\
                           --make-pidfile \\
                           --pidfile {0[rw_dir]}/running.pid \\
                           --exec {0[ro_dir]}/{0[service_binary]}
                    """
            with open("start.sh", "w") as start_fh:
                start_fh.write(textwrap.dedent(start.format(info)))

            # :note: the prior stop script killed all processes from the user
            #        if a service was exploited and they somehow spawned a
            #        non-child process, they would kill it too.
            #        instead, we are using a pid file now.
            # :note: I disagree with this idea. The package should uninstall
            #        cleanly, stopping all service processes. Who cares if
            #        players learn that such a novel tool as pkill exists...
            stop = """\
                      #!/bin/sh
                      /sbin/start-stop-daemon \\
                          --stop \\
                          --pidfile {0[rw_dir]}/running.pid
                   """
            with open("stop.sh", "w") as stop_fh:
                stop_fh.write(textwrap.dedent(stop.format(info)))
        else:
            sanity_check_on_scripted_start(rw_dir=info['rw_dir'], service_name=info['name'])


        makefile = None
        if "service_source" in info:
            # pylint: disable=line-too-long
            makefile = """\
                          all:

                          install:
                          	gcc -o $(DESTDIR){0[ro_dir]}/{0[name]} {0[service_source]}
                          	install start.sh stop.sh $(DESTDIR){0[ro_dir]}
                       """
        elif os.path.isfile("install.sh"):
            makefile = """\
                          all:

                          install:
                          	export DESTDIR
                          	export SERVICE_USER
                          	bash -eux ./install.sh
                          	install start.sh stop.sh $(DESTDIR){0[ro_dir]}
                       """
            # pylint: enable=line-too-long

        if makefile is None:
            # :note: we are abusing the NotImplementedError, ugly, but works :)
            # pylint: disable=line-too-long
            raise NotImplementedError("No service_source field or install.sh. One of these is required.")
            # pylint: enable=line-too-long

    else:
        makefile = """\
                      all:

                      install:
                      	export DESTDIR
                      	export SERVICE_USER
                      	bash -eux ./install.sh
                   """
    with open("Makefile", "w") as makefile_fh:
        makefile_fh.write(textwrap.dedent(makefile.format(info)))
    
    postinst_sh = ""
    if os.path.isfile("postinst.sh"):
        with open("postinst.sh", "r+") as postinst_sh_fh:
            postinst_sh = postinst_sh_fh.read()
            postinst_sh = postinst_sh.replace("$SERVICE_USER", info["name"])

    # TODO: Should check $1 (see the old version)
    # NOTE: Trying to be super-safe on what could be on postinst.sh.
    #       This may break postinst scripts that really want different permissions.
    postinst = """\
                  set -e

                  if ! getent passwd {player_username} >/dev/null; then
                      echo
                      echo "*********  iCTF WARNING  *********"
                      echo
                      echo "You need a user named '{player_username}' on the machine (it's the player account)"
                      echo
                      echo "Should I create one automatically? [Type 'yes' to continue] "
                      read -r REPLY
                      if [ "$REPLY" = "yes" ]; then
                          adduser --gecos 'CTF player' --shell /bin/bash --disabled-password {player_username}
                          echo "OK, '{player_username}' user created."
                          echo "Note that for a real game you would probably want to create it beforehand, set the password or authorized_keys, ..."
                      else
                          echo "Run 'adduser {player_username}', set it up as you like, and then run 'dpkg --configure --pending'"
                          exit 1
                      fi
                  fi
                  if ! getent passwd {0[name]} >/dev/null; then
                      useradd -d {0[ro_dir]} -s /bin/bash --user-group {0[name]}
                  fi
                  adduser {player_username} {0[name]} # Add players to the service group
                  chown -R {player_username}:{0[name]} {0[ro_dir]}
                  chmod -R g-w,o-rwx {0[ro_dir]}
                  mkdir -p {0[rw_dir]}
                  chown -R {0[name]}:{0[name]} {0[rw_dir]}
                  chmod -R o-rwx {0[rw_dir]}
                  {1}
                  chown -R {player_username}:{0[name]} {0[ro_dir]}
                  chmod -R g-w,o-rwx {0[ro_dir]}
                  mkdir -p {0[rw_dir]}
                  chown -R {0[name]}:{0[name]} {0[rw_dir]}
                  chmod -R o-rwx {0[rw_dir]}
                  #DEBHELPER#
               """
    with open("debian/postinst", "w") as postinst_fh:
        postinst = textwrap.dedent(postinst).format(
                info, postinst_sh, player_username=player_username)
        postinst_fh.write(postinst)


    rules = """\
               #!/usr/bin/make -f
               %:
               	dh $@

               override_dh_auto_install:
               \tmkdir -p {ro_dir} {rw_dir}
               \t$(MAKE) DESTDIR={destdir} SERVICE_USER={0[name]} install

               override_dh_strip:
            """

    destdir = 'debian/{0[name]}'.format(info)
    with open("debian/rules", "w") as rules_fh:
        make_destdir = '$$(pwd)/{}'.format(destdir)
        make_dest_ro_dir = destdir + info['ro_dir']
        make_dest_rw_dir = destdir + info['rw_dir']
        rules_fh.write(textwrap.dedent(rules.format(
            info, destdir=make_destdir, ro_dir=make_dest_ro_dir, rw_dir=make_dest_rw_dir)))
        os.fchmod(rules_fh.fileno(), 0o755)

    # Let's build the debian package
    print('\nBuilding the package...')
    assert subprocess.call(["debuild", "-D", "-b", "-us", "-uc"]) == 0

    print('\n **** OK, the package has been built ****')

    print('\nRunning some sanity checks...')
    if os.path.isfile('install.sh'):
        sanity_check_on_install_sh(debian_dep)
        print('')
    if os.path.isfile("postinst.sh"):
        sanity_check_on_postinst_sh(debian_dep)
        print('')
    sanity_check_on_files(destdir, info)
    print('')


    # Clean up the mess that we created
    if info["start_type"] == "binary":
        # :note: we created the start and stop scripts, remove
        os.remove("start.sh")
        os.remove("stop.sh")

    # FIXME: this is currently hard-coded to amd64, it must be fixed
    deb_file = "{0[name]}_{version}_amd64.deb".format(info, version=version)
    if os.path.isfile(deb_file):
        os.remove(deb_file)
    shutil.move("../{}".format(deb_file), ".")

    # FIXME: we should not deleting files with a wildcard, this might be
    #        dangerous if service names collide
    os.system("rm -rf ../{0[name]}_* Makefile debian".format(info))

    print("Here's what is in the deb:")
    os.system("lesspipe {}".format(deb_file))


    print("I created the deb.")
    print("For bonus points, also check that the deb can be created in a minimal environment, for instance using pdebuild).")
    print
    print("You should test test the package on a minimal VM.")
    print "1. Create a minimal VM. You can use mine at http://ictf.cs.ucsb.edu/minima.tar.xz"
    print "2. Make sure a 'ctf' user is there, and that gdebi-core is installed"
    print "3. Copy the deb and install it with gdebi xxx.deb"
    print
    print "The service should automatically start. If it doesn't, it may be missing libraries. For instance, if it uses openssl, then \"libssl1.0.0\" should be a dependency."
    print
    print "IMPORTANT: start-stop-daemon hides error messages. Try running the executable / script / whatever directly."
