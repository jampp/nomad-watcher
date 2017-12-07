# vim:ts=4:sw=4:et:ft=python

import os
import logging
import time
import json

import boto3
import distutils.util

import nomad_watcher
import notifier

###############################################################################

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

RUN_LOCAL = distutils.util.strtobool(os.environ.get('LOCAL', 'False'))

NOMAD_ADDR         = os.environ.get('NOMAD_ADDR',  'http://localhost:4646')
NOMAD_WATCH_STATUS = os.environ.get('NOMAD_WATCH_STATUS', 'pending')
CONSUL_ADDR        = os.environ.get('CONSUL_ADDR', 'http://localhost:8500')
CONSUL_KV_PREFIX   = os.environ.get('CONSUL_KV_PREFIX', 'nomad_watcher')

SLACK_WEBHOOK = None
if RUN_LOCAL:
    SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK', None)
else:
    from base64 import b64decode
    SLACK_WEBHOOK_ENC = os.environ.get('SLACK_WEBHOOK', None)

    if SLACK_WEBHOOK_ENC is not None:
        SLACK_WEBHOOK     = boto3.client('kms').decrypt(
                CiphertextBlob = b64decode(SLACK_WEBHOOK_ENC)
            )['Plaintext']

SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', None)

# Loggers config
logger = logging.getLogger()
logger.setLevel(getattr(logging, LOGLEVEL))

def main(event, context):

    logger.debug(json.dumps(event))

    nomad_watch_status = NOMAD_WATCH_STATUS.split(',')

    jobs = nomad_watcher.watcher(
        watch_status     = nomad_watch_status, 
        nomad_addr       = NOMAD_ADDR, 
        consul_addr      = CONSUL_ADDR,
        consul_kv_prefix = CONSUL_KV_PREFIX
    )

    if SLACK_WEBHOOK is not None:
        notifier.slack(SLACK_WEBHOOK, SLACK_CHANNEL, jobs)

