
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase

# Map OpManager Severity codes to Alert ones
SEVERITY_MAP = {
    "Attention": "warning",
    "Trouble": "minor",
    "Critical": "major",
    "Service Down": "critical",
    "Clear": "ok",
    "critical": "critical",
    "Warning": "warning",
    "Minor": "minor",
    "Major": "major",
    "Information": "info"
}

class OpManagerWebhook(WebhookBase):

    def incoming(self, query_string, payload):
        alert = Alert(
            resource=payload['resource'],
            event=payload['event'],
            environment=payload['env'],
            severity=SEVERITY_MAP.get(payload['severity'], "warning"),
            service=[payload['service']],
            group='NetAlert',
            value=payload['value'],
            text=f'{payload["text"]}',
            tags=payload.get('tags', []),
            attributes=payload.get('attr', {}),
            origin=payload["origin"],
            raw_data=str(payload)
        )
        return alert

# Payload for opmanager
# {
# 	"env": "dev-opman",
# 	"event" : "$message",
# 	"resource" : "$DeviceField(type)",
# 	"service" : "$displayName",
# 	"severity" : "$stringseverity",
# 	"group": "$category",
# 	"tags" ["opmanager", "oxfx"]
# 	"origin": "oxfx1opmanp01.ent.foxtel.com.au"
# 	"text": "$message",
# 	"attr": {"escalate_to": "$CustomField(Escalate To)"},
# 	"value": "$lastPolledValue"
# }