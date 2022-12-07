#!/usr/bin/env python3
"""
Usage:
  main.py [options]
  main.py jobs [options]
  main.py watch [options]

  General Options:

    -a,--address NOMAD_ADDR       Nomad cluster address

    -l,--loglevel LOG_LEVEL       Loglevel [default: INFO]

  Options for Job listing:

"""

###############################################################################

import os
import logging
import nomad
import requests
import json
import time

from docopt import docopt

###############################################################################

LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
LOG_LEVEL  = 'INFO'

WATCH_FOR_STATUS = [ 'pending' ]

WEBHOOK_URL = 'https://hooks.slack.com/services/put/your/webhook/here'

if __name__ == '__main__':

  opts = docopt(__doc__)

  logging.basicConfig(
    format = LOG_FORMAT,
    level  = getattr(logging, opts.get('--loglevel', LOG_LEVEL))
  )
  logger = logging.getLogger('nomad')

  logger.debug(opts)

  nomad_server = opts.get('--address', os.environ.get('NOMAD_ADDR', '127.0.0.0'))
  nomad_port   = opts.get('--port',    os.environ.get('NOMAD_PORT', 4646))

  nmd = nomad.Nomad(nomad_server, nomad_port, timeout=5)

  if opts['jobs']:
    for j in nmd.jobs.get_jobs():
      logger.info("Name: {0} - Status: {1}".format(j['Name'], j['Status']))
  
  if opts['watch']:
    
    allocs = nmd.allocations.get_allocations()

    report = filter(lambda f: f['ClientStatus'] in WATCH_FOR_STATUS, allocs)
    
    for r in report:
      payload = {
        "attachments": [
          {
            "color":"#D00000",
            "fields": [
              {
                "title": "Job: {0}".format(r['Name']),
                "value": "Nomad Status: {0}".format(r['ClientStatus']),
                "short": False
              },
              {
                "title": "Allocation ID: {0}".format(r['ID'][:8]),
                "short": True
              }
            ]
          }
        ]
      }
      requests.post(WEBHOOK_URL, data = json.dumps(payload))
      print(r['Name'], r['ID'][:8], r['ClientStatus'], time.ctime(r['CreateTime']/1000000000))

  else:
    pass
