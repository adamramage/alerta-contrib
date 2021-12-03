
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

LOG = logging.getLogger('alerta.plugins.librenms')

DEFAULT_ICINGA2_API_URL = 'http://icinga:80'

LIBRENMS_API_KEY = os.environ.get('LIBRENMS_API_KEY') or app.config.get('LIBRENMS_API_KEY', None)
LIBRENMS_SILENCE_FROM_ACK = os.environ.get('LIBRENMS_SILENCE_FROM_ACK') or app.config.get('LIBRENMS_SILENCE_FROM_ACK', False)

LIBRENMS_ACK_URL = '/api/v0/alerts'
LIBRENMS_UNACK_URL = '/api/v0/alerts/unmute/'

headers = {"X-Auth-Token": f"{LIBRENMS_API_KEY}"}


def librenms_payload(alert: Alert):
    """
    return an payload for icinga2api with filters and authors etc. from API ref
    https://icinga.com/docs/icinga-2/latest/doc/12-icinga2-api
    """
    payload = {
        "type": alert.attributes.get('alertType', 'service').title(),
        "filter": f"{alert.attributes.get('alertType', 'service').lower()}.name==\"{alert.service[0]}\" && host.address==\"{alert.resource}\"",
        "author": f'ack from alerta UI',
        "comment": f'this ack was sent from Alerta UI at {datetime.utcnow()} UTC',
        "expiry": (datetime.utcnow() + timedelta(seconds=alert.timeout)).timestamp()
    }
    LOG.debug(f'Generate payload for sending to icinga2 api : {payload}')
    return payload


class TriggerEvent(PluginBase):

    def __init__(self, name=None):

        # self.auth = (ICINGA2_USERNAME, ICINGA2_PASSWORD) if ICINGA2_USERNAME else None

        super(TriggerEvent, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return alert

    def take_action(self, alert: Alert, action: str, text: str, **kwargs) -> Any:
        LOG.debug(f'librenms: got alert into plugin {action} {alert.event_type}')
        if alert.event_type != 'libreNMS':
            return alert

        if action == 'ack':
            base_url = alert.attributes.get('externalUrl', None)
            ext_alert_id = alert.attributes.get('alert_id', None)

            if not base_url:
                raise RuntimeError("librenms: Sending ack to libreNMS, no externalUrl present in alert.")

            #check the alert_id exists.

            if ext_alert_id:
                url = f'{base_url}{LIBRENMS_ACK_URL}/{ext_alert_id}'
                LOG.debug('librenms: send ack to librenms for %s alert_id %s',
                      alert.event, alert.attributes.get('alert_id'))
                LOG.debug('librenms: URL=%s', url)
                try:
                    r = requests.put(url,  headers=headers, verify=False, timeout=3)
                except Exception as e:
                    raise RuntimeError("librenms: ERROR - %s" % e)

                LOG.debug('librenms: %s - %s', r.status_code, r.text)
            else:
                LOG.error('librenms: Error sending ACK, no alert_id present in source alert')
                raise RuntimeError("librenms: Sending ack to libreNMS, no alert_id present.")

        elif action == 'unack':
            base_url = alert.attributes.get('externalUrl')

            # check the alert_id exists.
            ext_alert_id = alert.attributes.get('alert_id', None)

            if ext_alert_id:
                url = f'{base_url}{LIBRENMS_UNACK_URL}/{ext_alert_id}'
                LOG.debug('librenms: send unack to librenms for %s alert_id %s',
                          alert.event, alert.attributes.get('alert_id'))
                LOG.debug('librenms: URL=%s', url)
                try:
                    r = requests.put(url, headers=headers, verify=False, timeout=3)
                except Exception as e:
                    raise RuntimeError("librenms: ERROR - %s" % e)

                LOG.debug('librenms: %s - %s', r.status_code, r.text)
            else:
                LOG.error('librenms: Error sending UNACK, no alert_id present in source alert')
                raise RuntimeError("librenms: Sending unack to libreNMS, no alert_id present.")

        return alert
