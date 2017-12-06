# vim:ts=4:sw=4:et:ft=python

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
import consul
import nomad
import requests
import json
import time

###############################################################################

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

# Loggers config
logger = logging.getLogger('jobs')
logger.setLevel(getattr(logging, LOGLEVEL))

def jobs(nomad_addr = 'http://localhost:4646', consul_addr = "http://localhost:8500"):

    logger.debug("Nomad  addr: {}".format(nomad_addr))
    logger.debug("Consul addr: {}".format(consul_addr))

    # Extract hostname and port out of the uri
    nomad_server = nomad_addr.split(':')[1][2:]
    nomad_port   = nomad_addr.split(':')[2]

    nmd = nomad.Nomad(nomad_server, nomad_port, timeout = 5)

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
      print r['Name'], r['ID'][:8], r['ClientStatus'], time.ctime(r['CreateTime']/1000000000)

  else:

    pass
