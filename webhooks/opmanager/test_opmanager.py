import json
import unittest

from alerta.app import create_app, custom_webhooks

import alerta_opmanager


class OpManagerWebhookTestCase(unittest.TestCase):

    def setUp(self):
        test_config = {
            'TESTING': True,
            'AUTH_REQUIRED': False
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

    def test_opmanager_webhook(self):
        custom_webhooks.webhooks['opmanager'] = alerta_opmanager.OpManagerWebhook()

        payload = r"""
            {
            "env": "Production",
            "event": "$message",
            "resource" : "testresoursexx",
            "service" : "$displayNamez",
            "severity" : "Service Down",
            "group": "$category",
            "tags": ["opmanager", "oxfx"],
            "origin": "test_origin",
            "text": "$message",
            "attr": {"test":"attra"},
            "value": "$lastPolledValue"
            }"""

        response = self.client.post('/webhooks/opmanager', data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['resource'], 'testresoursexx')
        self.assertEqual(data['alert']['event'], '$message')
        self.assertEqual(data['alert']['environment'], 'Production')
        self.assertEqual(data['alert']['value'], '$lastPolledValue')
        self.assertEqual(data['alert']['text'], '$message')
        self.assertEqual(data['alert']['tags'], ['opmanager', 'oxfx'])
        self.assertEqual(data['alert']['attributes'], {"test": "attra"})
