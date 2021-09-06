import logging
import os
import re
import requests
from datetime import datetime, timedelta, tzinfo
from typing import Any

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase
from alerta.models.alert import Alert

LOG = logging.getLogger('alerta.plugins.opsgenie2')
LOG.info('Initializing')

OPSGENIE_EVENTS_CREATE_URL = 'https://api.opsgenie.com/v2/alerts'
OPSGENIE_EVENTS_CLOSE_URL = 'https://api.opsgenie.com/v2/alerts/%s/close?identifierType=alias'
OPSGENIE_EVENTS_ACK_URL = 'https://api.opsgenie.com/v2/alerts/%s/acknowledge?identifierType=alias'
OPSGENIE_EVENTS_UNACK_URL = 'https://api.opsgenie.com/v2/alerts/%s/unacknowledge?identifierType=alias'
OPSGENIE_EVENTS_SNOOZE_URL = 'https://api.opsgenie.com/v2/alerts/%s/snooze?identifierType=alias'
# OPSGENIE_EVENTS_NOTES_URL = 'https://api.opsgenie.com/v2/alerts/%s/notes?identifierType=alias'
OPSGENIE_SERVICE_KEY = os.environ.get('OPSGENIE_SERVICE_KEY') or app.config['OPSGENIE_SERVICE_KEY']
OPSGENIE_TEAMS = os.environ.get('OPSGENIE_TEAMS', '')  # comma separated list of teams
OPSGENIE_SEND_WARN = os.environ.get('OPSGENIE_SEND_WARN') or app.config.get('OPSGENIE_SEND_WARN', False)
SERVICE_KEY_MATCHERS = os.environ.get('SERVICE_KEY_MATCHERS') or app.config['SERVICE_KEY_MATCHERS']
OPSGENIE_SEND_ENVIRONMENTS = os.environ.get('OPSGENIE_SEND_ENVIRONMENTS') or \
                             app.config.get('OPSGENIE_SEND_ENVIRONMENTS', None) # set / list of envs eg. ['prod','dev']
DASHBOARD_URL = os.environ.get('DASHBOARD_URL') or app.config.get('DASHBOARD_URL', '')
LOG.info('Initialized: %s key, %s matchers' % (OPSGENIE_SERVICE_KEY, SERVICE_KEY_MATCHERS))
OPSGENIE_PROXY = os.environ.get('OPSGENIE_PROXY')
OPGENIE_SEVERITY_MAP = os.environ.get('OPSGENIE_SEVERITY_MAP', {
    'security': 'P1',
    'critical': 'P1',
    'major': 'P2',
    'minor': 'P3',
    'warning': 'P3',
    'indeterminate': 'P4',
    'info': 'P4',
    'ok': 'P5',
    'unknown': 'P5',
    'none': 'P5'
}) or app.config.get('OPGENIE_SEVERITY_MAP', None)

proxy_dict = {
    'https': OPSGENIE_PROXY,
}


class simple_utc(tzinfo):
    def tzname(self, **kwargs):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


class TriggerEvent(PluginBase):
    def opsgenie_service_key(self, resource):
        if not SERVICE_KEY_MATCHERS:
            LOG.debug('No matchers defined! Default service key: %s' % (OPSGENIE_SERVICE_KEY))
            return OPSGENIE_SERVICE_KEY

        for mapping in SERVICE_KEY_MATCHERS:
            if re.match(mapping['regex'], resource):
                LOG.debug('Matched regex: %s, service key: %s' % (mapping['regex'], mapping['api_key']))
                return mapping['api_key']

        LOG.debug('No regex match! Default service key: %s' % (OPSGENIE_SERVICE_KEY))
        return OPSGENIE_SERVICE_KEY

    def opsgenie_environment(self, environment):
        if not OPSGENIE_SEND_ENVIRONMENTS:
            LOG.debug('No Match for environment will send to all environments')
            return True

        for env in OPSGENIE_SEND_ENVIRONMENTS:
            if environment == env:
                LOG.debug(f'environment {environment} enable for alerting to opsgenie.')
                return True

        LOG.debug(f'environment {environment} is not enabled for alerting to opsgenie')
        return False

    def opsgenie_close_alert(self, alert, why):

        headers = {
            "Authorization": 'GenieKey ' + self.opsgenie_service_key(alert.resource)
        }

        closeUrl = OPSGENIE_EVENTS_CLOSE_URL % alert.id
        LOG.debug('OpsGenie close %s: %s %s' % (why, alert.id, closeUrl))

        try:
            r = requests.post(closeUrl, json={}, headers=headers, timeout=2, proxies=proxy_dict)
        except Exception as e:
            raise RuntimeError("OpsGenie connection error: %s" % e)
        return r

    def opsgenie_ack_alert(self, alert, why):

        headers = {
            "Authorization": 'GenieKey ' + self.opsgenie_service_key(alert.resource)
        }

        ackUrl = OPSGENIE_EVENTS_ACK_URL % alert.id
        LOG.debug('OpsGenie ack %s: %s %s' % (why, alert.id, ackUrl))

        try:
            r = requests.post(ackUrl, json={}, headers=headers, timeout=2, proxies=proxy_dict)
        except Exception as e:
            raise RuntimeError("OpsGenie connection error: %s" % e)
        return r

    def opsgenie_unack_alert(self, alert, why):

        headers = {
            "Authorization": 'GenieKey ' + self.opsgenie_service_key(alert.resource)
        }

        ackUrl = OPSGENIE_EVENTS_UNACK_URL % alert.id
        LOG.debug('OpsGenie ack %s: %s %s' % (why, alert.id, ackUrl))

        try:
            r = requests.post(ackUrl, json={}, headers=headers, timeout=2, proxies=proxy_dict)
        except Exception as e:
            raise RuntimeError("OpsGenie connection error: %s" % e)
        return r

    def opsgenie_snooze_alert(self, alert, why):

        headers = {
            "Authorization": 'GenieKey ' + self.opsgenie_service_key(alert.resource)
        }
        body = alert.get_body(history=False)
        ackUrl = OPSGENIE_EVENTS_SNOOZE_URL % alert.id
        LOG.debug('OpsGenie ack %s: %s %s' % (why, alert.id, ackUrl))

        try:
            endtime = (datetime.utcnow().replace(tzinfo=simple_utc()) + timedelta(seconds=int(body['timeout']))
                       ).isoformat()
            payload = {
                "endTime": endtime,
                "user": "Alerta API",
                "source": alert.resource,
                "note": "Action executed via Alert API"
            }
            r = requests.post(ackUrl, json=payload, headers=headers, timeout=2, proxies=proxy_dict)
        except Exception as e:
            raise RuntimeError("OpsGenie connection error: %s" % e)
        return r

    def pre_receive(self, alert: 'Alert', **kwargs):
        return alert

    def post_receive(self, alert: 'Alert', **kwargs):
        LOG.debug('Alert receive %s: %s' % (alert.id, alert.get_body(history=False)))
        body = alert.get_body(history=False)
        # print(f'{alert} body:{body} {alert.serialize}')
        if alert.repeat:
            LOG.debug('Alert repeating; ignored')
            return

        # If alerta has cleared or status is closed, send the close to opsgenie
        if (alert.severity in ['cleared', 'normal', 'ok']) or (alert.status == 'closed'):
            r = self.opsgenie_close_alert(alert, 'CREATE-CLOSE')
        elif (alert.severity not in ['major', 'critical', 'security']) and not OPSGENIE_SEND_WARN:
            LOG.info('Just informational or warning not sending to OpsGenie')
        else:
            headers = {
                "Authorization": 'GenieKey ' + self.opsgenie_service_key(alert.resource)
            }

            # Send all alert data as details to opsgenie
            body = alert.get_body(history=False)
            details = {}
            details['web_url'] = '%s/#/alert/%s' % (DASHBOARD_URL, alert.id)
            details['service'] = alert.service[0]
            details['origin'] = body['origin']
            details['event'] = body['event']
            details['group'] = body['group']
            details['trendIndication'] = body['trendIndication']
            details['severity'] = alert.severity
            details['previousSeverity'] = alert.severity
            details['duplicateCount'] = body['duplicateCount']
            payload = {
                "alias": alert.id,
                "message": "[ %s ]: %s: %s" % (alert.environment, alert.severity, alert.text),
                "entity": alert.environment,
                "responders": self.get_opsgenie_teams(),
                "tags": [alert.environment, alert.resource, alert.service[0], alert.event],
                "details": details,
                "description": alert.text,
                "priority": OPGENIE_SEVERITY_MAP.get(body['severity'].lower()) or 'P3'
            }

            LOG.debug('OpsGenie CREATE payload: %s' % payload)

            try:
                r = requests.post(OPSGENIE_EVENTS_CREATE_URL, json=payload, headers=headers, timeout=2, proxies=proxy_dict)
                LOG.debug('OpsGenie response: %s - %s' % (r.status_code, r.text))
            except Exception as e:
                raise RuntimeError("OpsGenie connection error: %s" % e)

    # generate list of responders from OPSGENIE_TEAMS env var
    def get_opsgenie_teams(self):
        teams = OPSGENIE_TEAMS.replace(' ', '')  # remove whitespace
        if len(teams) == 0:
            return []  # no teams specified
        teams = teams.split(',')
        return [{"name": team, "type": "team"} for team in teams]

    def status_change(self, alert: 'Alert', status: str, text: str, **kwargs):
        # LOG.debug('Alert change %s to %s: %s' % (alert.id, status, alert.get_body(history=False)))
        # if status not in ['ack', 'assign', 'closed', 'shelved', 'open']:
        #     LOG.debug('Not sending status change to opsgenie: %s to %s' % (alert.id, status))
        #     return
        return

    # moved actions from status_change to take_action as it seems the correct place to do these things.
    def take_action(self, alert: Alert, action: str, text: str, **kwargs) -> Any:
        if action == 'ack':
            r = self.opsgenie_ack_alert(alert, 'STATUS-ACK')
            LOG.debug('OpsGenie response: %s - %s' % (r.status_code, r.text))
        elif action == 'unack':
            r = self.opsgenie_unack_alert(alert, 'STATUS-UNACK')
            LOG.debug('OpsGenie response: %s - %s' % (r.status_code, r.text))
        elif action == 'close':
            r = self.opsgenie_close_alert(alert, 'STATUS-CLOSE')
            LOG.debug('OpsGenie response: %s - %s' % (r.status_code, r.text))
        elif action == 'shelve':
            r = self.opsgenie_snooze_alert(alert, 'STATUS-SHELVED')
            LOG.debug('OpsGenie response: %s - %s' % (r.status_code, r.text))
        elif action == 'unshelve':
            # There is no un-snooze in opsgenie, but an ack/unack seems to have the desired result.
            r = self.opsgenie_ack_alert(alert, 'STATUS-ACK')
            LOG.debug('OpsGenie response: %s - %s' % (r.status_code, r.text))
            r = self.opsgenie_unack_alert(alert, 'STATUS-UNACK')
            LOG.debug('OpsGenie response: %s - %s' % (r.status_code, r.text))

        return alert

    # added an opsGenie close alert if the event is deleted in Alerta to prevent ongoing alarms
    def delete(self, alert: 'Alert', **kwargs) -> bool:
        r = self.opsgenie_close_alert(alert, 'STATUS-CLOSE')
        LOG.debug('OpsGenie response: %s - %s' % (r.status_code, r.text))
        return True
