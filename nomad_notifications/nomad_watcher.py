###############################################################################

import os
import logging
import requests
import json
import time

import consul
import nomad

###############################################################################

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

# Loggers config
logger = logging.getLogger('jobs')
logger.setLevel(getattr(logging, LOGLEVEL))

# urllib3 errors only
logger_urllib = logging.getLogger('urllib3.connectionpool')
logger_urllib.setLevel(logging.ERROR)

def watcher(
        watch_status     = [ 'pending' ], 
        nomad_addr       = 'http://localhost:4646',
        consul_addr      = "http://localhost:8500",
        consul_kv_prefix = 'nomad_watcher'
    ):

    logger.debug("Nomad  addr: {}".format(nomad_addr))
    logger.debug("Consul addr: {}".format(consul_addr))

    # Extract hostname and port out of the uri
    nomad_server = nomad_addr.split(':')[1][2:]
    nomad_port   = nomad_addr.split(':')[2]

    consul_server = consul_addr.split(':')[1][2:]
    consul_port   = consul_addr.split(':')[2]

    nomad_c  = nomad.Nomad(nomad_server, nomad_port, timeout = 5)
    consul_c = consul.Consul(host = consul_server, port = consul_port)

    allocs = nomad_c.allocations.get_allocations()

    jobs_spotted = filter(lambda f: f['ClientStatus'] in watch_status, allocs)
    
    # Get job ids stored in consul
    job_ids_kv = consul_c.kv.get('{}'.format(consul_kv_prefix), keys = True)[1]

    job_ids = []
    if job_ids_kv is not None: 
        job_ids = map(lambda m: str(m.split('/')[1]), job_ids_kv)
        logger.debug('kv: {}'.format(job_ids))

    r = {}
    for j in jobs_spotted:

        logger.debug("job: {} - job_ids: {}".format(j['ID'], job_ids))

        # If the job id is already in KV, skip notifications
        # In a future release, this might trigger a re-alert
        if j['ID'] in job_ids:
            logger.debug('job {} is present in KV ...'.format(j['ID']))
            continue

        logger.info('alert: job:{} - status:{}'.format(j['ID'], j['ClientStatus']))

        consul_c.kv.put('{}/{}'.format(consul_kv_prefix, j['ID']), "{}".format(time.time()))

        r[j['ID']] = { 
            'Name':         j['Name'], 
            'ClientStatus': j['ClientStatus'], 
            'CreateTime':   j['CreateTime']
        }
        
        logger.info('job_name: {} - job_id: {} - job_status: {} - '.format(
                j['Name'], 
                j['ID'][:8], 
                j['ClientStatus'], 
                time.ctime(j['CreateTime']/1000000000)
            )
        )

    return r
