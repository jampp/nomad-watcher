import logging

from nomad_notifications.lambda_watcher import main

logger = logging.getLogger('lambda_handler')
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    main(event, context)
