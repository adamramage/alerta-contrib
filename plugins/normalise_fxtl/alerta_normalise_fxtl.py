
import logging

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.normalise_fxtl')

class NormaliseAlert(PluginBase):

    def pre_receive(self, alert):

        LOG.info("Normalising alert for fxtl")

        # prepend severity to alert text
        alert.text = '%s: %s' % (alert.severity.upper(), alert.text)

        alert.severity = alert.severity.lower()
        if alert.severity in ('prd', 'prod'):
            LOG.warning(f"set alert severity to production from {alert.severity} from {alert.origin}")
            alert.severity = 'production'

        # supply different default values if missing
        # if not alert.group or alert.group == 'Misc':
        #     alert.group = 'Unknown'
        # if not alert.value or alert.value == 'n/a':
        #     alert.value = '--'

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
