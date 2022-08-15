
import logging

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.normalise_fxtl')
SEVERITY_MAP = [
    'critical',
    'major',
    'minor',
    'warning',
    'indeterminate',
    'info',
    'ok',
    'unknown',
    'none'
]


class NormaliseAlert(PluginBase):

    def pre_receive(self, alert):

        LOG.info("Normalising alert for fxtl")

        # prepend severity to alert text
        alert.text = '%s: %s' % (alert.severity.upper(), alert.text)

        alert.severity = alert.severity.lower()
        # normalize alert severity for unknowns.
        if alert.severity not in SEVERITY_MAP:
            old_severity = alert.severity
            alert.severity = 'unknown'
            alert.text = f"PROBLEM: incorrect Severity inbound: {old_severity} = {alert.text}"

        if alert.environment is not None or alert.environment is not "":
            alert.environment = alert.environment.lower()
            LOG.info(f"fxtl : {alert}")

            if alert.environment in ('prd', 'prod'):
                LOG.warning(f"set alert environment to production from {alert.environment} from {alert.origin}")
                alert.environment = 'production'
        else:
            alert.environment = "unknown"
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
