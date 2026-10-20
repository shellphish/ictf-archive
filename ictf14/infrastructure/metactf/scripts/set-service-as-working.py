#!/usr/bin/env python

# Yeah, dear Kevin, it doesn't follow PEP8 ;)

import json
import sys
from os.path import abspath, join, dirname
import IPython


service_full_names = sys.argv[1:]

for service_full_name in service_full_names:
    print 'processing %s' % service_full_name
    info_json_fp = abspath(join('..', dirname(__file__), 'Services', service_full_name, 'info.json'))
    f = open(info_json_fp)
    json_content = f.read()
    f.close()

    j = json.loads(json_content)
    j['is_working'] = 1

    new_j = json.dumps(j, sort_keys=True, indent=4, separators=(',',': '))
    f = open(info_json_fp, 'w')
    f.write(new_j)
    f.close()
