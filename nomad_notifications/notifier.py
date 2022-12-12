###############################################################################

import os
import logging
import json
import requests

###############################################################################

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

# Loggers config
logger = logging.getLogger('notifier')
logger.setLevel(getattr(logging, LOGLEVEL))

# urllib3 errors only
logger_urllib = logging.getLogger('urllib.connectionpool')
logger_urllib.setLevel(logging.ERROR)

def slack(slack_webhook, slack_channel, jobs):

    for k,v in jobs.items():

        slack_payload = {
            "fallback": "Nomad Job: {}".format(v['Name']),
            "pretext":  "Nomad Job: {}".format(v['Name']),
            "color":    "{}".format("danger"),
            "fields": [
                {
                    "title": "Status: {}".format(v['ClientStatus']),
                    "value": "Alloc ID: {}".format(k),
                    "short": True
                }
            ]
        }

        logger.debug(json.dumps(slack_payload))

        slack_message = {
            "channel":     slack_channel,
            "attachments": [ slack_payload ]
        }

        payload_json = json.dumps(slack_message).encode('utf-8')

        r = requests.post(slack_webhook, data = payload_json)

        if r.status_code != 200:
            logger.error("status code: {} - {}".format(
                    r.status_code,
                    r.text
                )
            )
