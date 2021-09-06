
import datetime
import logging
import os
import requests
from typing import Any
from datetime import datetime, timedelta

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

from alerta.models.alert import Alert
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.icinga2api')

DEFAULT_ICINGA2_API_URL = 'http://icinga:5561'

ICINGA2_API_URL = os.environ.get('ICINGA2_API_URL') or app.config.get('ICINGA2_API_URL', None)
ICINGA2_USERNAME = os.environ.get('ICINGA2_USERNAME') or app.config.get('ICINGA2_USERNAME', None)
ICINGA2_PASSWORD = os.environ.get('ICINGA2_PASSWORD') or app.config.get('ICINGA2_PASSWORD', None)
ICINGA2_SILENCE_DAYS = os.environ.get('ICINGA2_SILENCE_DAYS') or app.config.get('ICINGA2_SILENCE_DAYS', 1)
ICINGA2_SILENCE_FROM_ACK = os.environ.get('ICINGA2_SILENCE_FROM_ACK') or app.config.get('ICINGA2_SILENCE_FROM_ACK', False)

ICINGA2_ACK_URL = '/v1/actions/acknowledge-problem'
ICINGA2_UNACK_URL = '/v1/actions/remove-acknowledgement'
ICINGA2_COMMENT_URL = '/v1/actions/add-comment'
ICINGA2_SNOOZE_URL = '/v1/actions/schedule-downtime'
ICINGA2_UNSNOOZE_URL = '/v1/actions/remove-downtime.'

headers = {"Accept": "application/json"}


def icinga2api_payload(alert: Alert):
    """
    return an payload for icinga2api with filters and authors etc. from API ref
    https://icinga.com/docs/icinga-2/latest/doc/12-icinga2-api
    """
    payload = {
        "type": alert.attributes.get('alertType', 'Service').title(),
        "filter": f"service.name=={alert.service[0]} && host.address=={alert.resource}",
        "author": f'ack from alerta UI',
        "comment": f'this ack was sent from Alerta UI at {datetime.utcnow()} UTC',
        "expiry": (datetime.utcnow() + timedelta(seconds=alert.timeout)).timestamp()
    }
    LOG.debug(f'Generate payload for sending to icinga2 api : {payload}')
    return payload


class TriggerEvent(PluginBase):

    def __init__(self, name=None):

        self.auth = (ICINGA2_USERNAME, ICINGA2_PASSWORD) if ICINGA2_USERNAME else None

        super(TriggerEvent, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return alert

    def take_action(self, alert: Alert, action: str, text: str, **kwargs) -> Any:
        LOG.debug(f'icinga2api: got alert into plugin {action} {alert.event_type}')
        if alert.event_type != 'Icinga2Alert':
            return alert

        if action == 'ack':

            if ICINGA2_SILENCE_FROM_ACK:
                silence_seconds = kwargs.get('timeout', alert.timeout)
            else:
                try:
                    silence_days = int(ICINGA2_SILENCE_DAYS)
                except Exception as e:
                    LOG.error(
                        "icinga2api: Could not parse 'ICINGA2_SILENCE_DAYS': %s", e)
                    raise RuntimeError(
                        "Could not parse 'ICINGA2_SILENCE_DAYS': %s" % e)
                silence_seconds = silence_days * 86400

            data = icinga2api_payload(alert)
    
            base_url = ICINGA2_API_URL or alert.attributes.get('externalUrl', DEFAULT_ICINGA2_API_URL)
            url = base_url.replace('5561', '5665') + ICINGA2_ACK_URL
            
            LOG.debug('icinga2api: Add silence for alertname=%s instance=%s timeout=%s',
                  alert.event, alert.resource, str(silence_seconds))
        

            LOG.debug('icinga2api: URL=%s', url)
            LOG.debug('icinga2api: data=%s', data)

            try:
                r = requests.post(url,  headers=headers, verify=False, json=data, auth=self.auth, timeout=2)
            except Exception as e:
                raise RuntimeError("icinga2api: ERROR - %s" % e)
            LOG.debug('icinga2api: %s - %s', r.status_code, r.text)

            # example r={"status":"success","data":{"silenceId":8}}

        elif action == 'unack':
            LOG.debug('icinga2api: Remove ack for alertname=%s instance=%s', alert.event, alert.resource)

            data = icinga2api_payload(alert)

            base_url = ICINGA2_API_URL or alert.attributes.get('externalUrl', DEFAULT_ICINGA2_API_URL)
            url = base_url.replace('5561', '5665') + ICINGA2_UNACK_URL

            LOG.debug('icinga2api: URL=%s', url)
            LOG.debug('icinga2api: data=%s', data)

            try:
                r = requests.post(url, headers=headers, verify=False, json=data, auth=self.auth, timeout=2)
            except Exception as e:
                raise RuntimeError("icinga2api: ERROR - %s" % e)
            LOG.debug('icinga2api: %s - %s', r.status_code, r.text)

        return alert
