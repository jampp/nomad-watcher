# Nomad Watcher

## Configuration

  * `LOGLEVEL (default: INFO)`: self explanatory ;)
  * `LOCAL (default: false)`: Run the code locally. If set to `True` this will 
    use `KMS` to unencrypt sensitive information (`SLACK_WEBHOOK`)
  * `NOMAD_ADDR (default: http://localhost:4646)`
  * `NOMAD_WATCH_STATUS (default: pending)`: Comma separated values of job
     states to watch for
  * `CONSUL_ADDR (default: http://localhost:8500)`
  * `CONSUL_KV_PREFIX (nomad_watcher)`: Prefix where the allocation IDs will
    be stored
  * `SLACK_WEBHOOK (default: None)`: If running on AWS Lambda, this will be
    taken as an encrypted parameter, and be decrypted with `KMS`, otherwise,
    will be taken as plan text. If this is not specified, notifications to
    slack will not be sent, and will only be reported through lambda's output

## Running on AWS Lambda

FIXME

## Running locally 

FIXME
