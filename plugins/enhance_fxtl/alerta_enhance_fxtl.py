
import logging
import os
import requests
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.enhance_fxtl')

RUNBOOK_URL = os.environ.get('RUNBOOK_URL', 'https://foxsportsau.atlassian.net/wiki/search?text=')

ALERTA_EXTENDA_URL = os.environ.get('ALERTA_EXTENDA_URL', 'http://localhost:8082')
ALERTA_EXTENDA_TIMEOUT = os.environ.get('ALERTA_EXTENDA_TIMEOUT', 2)
ENABLE_EXTENDA = bool(os.environ.get('ENABLE_EXTENDA', 'False'))
ALERTA_EXTENDA_PROXY = os.environ.get('ALERTA_EXTENDA_PROXY')

proxy_dict = {
    'https': ALERTA_EXTENDA_PROXY,
    'http': ALERTA_EXTENDA_PROXY
}


class EnhanceAlert(PluginBase):

    def pre_receive(self, alert):

        if ENABLE_EXTENDA and not ALERTA_EXTENDA_URL:
            if not alert.repeat:
                # Anything inside here should be deduped

                headers = {}
                payload = alert
                try:
                    r = requests.post(ALERTA_EXTENDA_URL, data=payload, headers=headers, timeout=ALERTA_EXTENDA_TIMEOUT, proxies=proxy_dict)
                    alert = await r.json()

                #     TODO: change the process above to send the bare minimum then upsert the response into the alerta model.
                #     TODO: Need to make sure too that the response above doesnt get munched and we lose data.

                except Exception as e:
                    raise RuntimeError("Alerta-Extenda Error: %s" % e)

        LOG.info("Enhancing alert foxtel")

        # Set "isOutOfHours" flag for later use by notification plugins
        # dayOfWeek = alert.create_time.strftime('%a')
        # hourOfDay = alert.create_time.hour
        # if dayOfWeek in ['Sat', 'Sun'] or 8 > hourOfDay > 18:
        #     alert.attributes['isOutOfHours'] = True
        # else:
        #     alert.attributes['isOutOfHours'] = False

        # Add link to Run Book based on event name
        alert.attributes['runBookUrl'] = '%s%s' % (RUNBOOK_URL, alert.event.replace(' ', '-'))
        alert.attributes['conflenceLink'] = f'<html><a href="{RUNBOOK_URL}{alert.event.replace(" ", "-")}" target' \
                                            f'="_blank"><b>Alert Troubleshooting Procedure Guidelines - More ' \
                                            f'info.</b></a></html> '

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
