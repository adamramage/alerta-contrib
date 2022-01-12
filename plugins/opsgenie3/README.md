OpsGenie-Enhanced Plugin
================

Send OpsGenie messages for new alerts.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Features
------------
proxy support - For connecting to OpsGenie API from behind a corporate FW.
Team Routing support via alert annotations
Team Routing support for multiple teams and default teams (a NOC group etc)
Configurable priority mapping from alerta -> opsgenie Px



Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/opsgenie3

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `opsgenie3` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

SERVICE_KEY_MATCHERS takes an array of dictionary objects, mapping a regular
expression to a OpsGenie API integration key.  This allows sending alerts to
multiple OpsGenie service integrations, based on 'alert.resource'.

OPSGENIE_DEFAULT_TEAM is used as a default team for 2 uses. 1, fallback team for alerting if no team is specified in 
an alert. 2, will always add this team(s) to every message payload. This means that more than 1 team will get the alert 
and can act on it. This is being used to control alerts to a central NOC desk and have on call teams also receive alerts.

OPSGENIE_SEVERITY_MAP is a dict used to map any severity level to an opsgenie level. 
eg.
{
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
}

```python
OPSGENIE_DEFAULT_TEAM = 'Team_A,TeamB'
```

```python
PLUGINS = ['opsgenie']
OPSGENIE_SERVICE_KEY = ''  # default="not set"
SERVICE_KEY_MATCHERS = []  # default="not set"
```

The `DASHBOARD_URL` setting should be configured to link pushover messages to
the Alerta console:

```python
DASHBOARD_URL = ''  # default="not set"
```

The `OPSGENIE_SEND_WARN` setting should be configured if you would like to send
informational and warning alerts onto OpsGenie.

```python
OPSGENIE_SEND_WARN = True   # default=True
```

**Example**

```python
PLUGINS = ['reject', 'opsgenie3']
OPSGENIE_SERVICE_KEY = 'XXX-YYY-BBB-ZZZ'
SERVICE_KEY_MATCHERS = [ {"regex":"proxy[\\d+]","api_key":"6b982ii3l8p834566oo13zx9477p1zxd"} ]
DASHBOARD_URL = 'https://try.alerta.io'
OPSGENIE_SEND_WARN = False
OPSGENIE_DEFAULT_TEAM = 'Team_A'
```

References
----------

  * OpsGenie Integration API: https://www.opsgenie.com/docs/web-api/alert-api


remote-ack
----------
Use the opsGenie EOM tool to via 

License
-------

Copyright (c) 2017 Kurt Westerfeld. Available under the MIT License.
