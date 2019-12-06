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


def get_downtime(filters, filter_vars):
    """Lookup downtime by filters. Returns active downtime
       with the farthest end time"""
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
        if expires_at < d['attrs']['end_time']:
            expires_at = d['attrs']['end_time']
            the_downtime = d

    return the_downtime


def acknowledge_on_downtime(the_downtime, object_type, filters, filter_vars):
    expires_at = the_downtime['attrs']['end_time']
    downtime_id = int(the_downtime['attrs']['legacy_id'])
    logger.info("Found downtime {downtime_id}, doing ACK.".format(
        downtime_id=downtime_id))
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


def handle_stream():
    logger.info("Starting")
    for event in icinga2api.events.subscribe(
            types=['StateChange', 'DowntimeStarted', 'DowntimeTriggered'],
            queue='auto-ack'):
        if type(event) is bytes:
            event = str(event, encoding='utf-8')
        event = json.loads(event)
        pprint(event)

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
        #
        the_downtime = get_downtime(filters=filters, filter_vars=filter_vars)
        if not the_downtime:
            logger.info("No active downtimes found")
            continue

        if the_downtime:
            acknowledge_on_downtime(the_downtime=the_downtime,
                                    object_type=object_type,
                                    filters=filters, filter_vars=filter_vars)
            continue


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    handle_stream()
