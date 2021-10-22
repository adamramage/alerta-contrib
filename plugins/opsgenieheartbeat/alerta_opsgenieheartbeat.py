import logging
import os
import requests

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase
from alerta.models.alert import Alert

LOG = logging.getLogger('alerta.plugins.opsgenieheartbeat')
LOG.info('Initializing OpsGenie Heartbeat')

OPSGENIE_HEARTBEAT_BASE_URL = "https://api.opsgenie.com/v2/heartbeats/"

# alerta send -r heartbeat -e opsgenie_heartbeat -E production -s ok -S  -O alerta/opsgenie --type opsgenieHb

# service name will be picked up and sent as heartbeat name
# password will be set in the alert via a tag called password:

# curl -X GET 'https://api.opsgenie.com/v2/heartbeats/HeartbeatName/ping'
#     --header 'Authorization: GenieKey eb243592-faa2-4ba2-a551q-1afdf565c889'

OPSGENIE_PROXY = os.environ.get('OPSGENIE_PROXY')

proxy_dict = {
    'https': OPSGENIE_PROXY,
}


class TriggerHeartBeat(PluginBase, ABC):
    def pre_receive(self, alert: 'Alert', **kwargs):
        return alert

    def post_receive(self, alert: 'Alert', **kwargs):
        LOG.debug('Alert receive %s: %s' % (alert.id, alert.get_body(history=False)))
        body = alert.get_body(history=False)

        if alert.event_type == "opsgenieHb":
            password = alert.tags['password']
            hbname = alert.service
            url = f"{OPSGENIE_HEARTBEAT_BASE_URL}{hbname}/ping"
            headers = {
                "Authorization": 'GenieKey ' + password
            }

            try:
                r = requests.post(url, headers=headers, timeout=2, proxies=proxy_dict)
                LOG.debug('OpsGenie HB response to %s: %s - %s' % (url, r.status_code, r.text))
                if r.status_code != 200:
                    alert.severity = "major"
                    alert.text = "Heatbeat is Failing to send outbound to OpsGenie, has Alerta lost comms to OpsGenie/" \
                                 "the internet"
                    return alert
            except Exception as e:
                # alert.severity = "major"
                # alert.text = "Heatbeat is Failing to send outbound to OpsGenie, has Alerta lost comms to OpsGenie/" \
                #              "the internet"
                # return alert
                raise RuntimeError("OpsGenie connection error: %s" % e)

    def status_change(self, alert, status, text):
        return alert



