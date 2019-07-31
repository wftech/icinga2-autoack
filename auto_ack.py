#!/usr/bin/env python 

import os
import datetime
from pprint import pprint
import json
import logging

from icinga2api.client import Client as Icinga2Client

icinga2api = Icinga2Client(config_file='icinga2-api.ini')

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger('autoack')


def do_ack():
    logger.info("Starting")
    for event in icinga2api.events.subscribe(types=['StateChange'],
                                             queue='auto-ack'):
        event = json.loads(event)

        host_name = event['host']
        try:
            service_name = event['service']
        except KeyError:
            service_name = None
        logger.info("Got change state event {event}".format(event=event))
        if event['state'] == 0:  # the service is up now
            continue

        if not service_name:
            object_type = 'Host'
            filters = 'match(host.name,filter_host)'
            filter_vars = dict(filter_host=host_name)
        else:
            object_type = 'Service'
            filters = 'match(host.name,filter_host) && match(service.name,filter_service)',
            filter_vars = dict(filter_host=host_name,
                               filter_service=service_name)

        downtimes = icinga2api.objects.list(
            'Downtime',
            filters=filters, filter_vars=filter_vars)

        expires_at = 0
        the_downtime = None
        for d in downtimes:
            if not d['attrs']['active']:
                continue
            if not d['attrs']['fixed']:
                continue

            expires_at = max(expires_at, d['attrs']['end_time'])
            the_downtime = d

        if not the_downtime:
            logger.info("No active downtimes found")
            continue

        downtime_id = int(the_downtime['attrs']['legacy_id'])
        logger.info("Found downtime {downtime_id}, doing ACK.".format(
            downtime_id=downtime_id))
        if len(downtimes) > 0 and expires_at:
            comment = 'This is auto acknowledge. {object_type} is in downtime #{downtime_id}'.format(
                downtime_id=downtime_id, object_type=object_type,
            )
            icinga2api.actions.acknowledge_problem(
                object_type=object_type,
                filters=filters,
                filter_vars=filter_vars,
                author='AutoAck bot',
                comment=comment,
                sticky=False,
                notify=False,
                expiry=expires_at,
            )

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    do_ack()
