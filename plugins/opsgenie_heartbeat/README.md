OpsGenie HeartBeat Plugin
================

Send OpsGenie Heartbeat based on an alert generated in alerta.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/opsgenie

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `opsgenie-heartbeat` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

This plugin has been written to be as dynamic as possible. Its purpose is to create a continuous 'ping' out to opsgenies
heartbeat service that if stopped (alerta down, internet down etc) would cause alerts not to be escalated the heartbeat will 
be triggered within OpsGenie to let you know comms are down.

To ensure that alerta generates the alert (and prove that alerta is working) this plugin will intercept an alert generated in any way you want
with a type of 'opsgenieHb' and use the service name as the HB name in opsgenie. the API key (unique to every HB) is set in the alert as a tag 
called password:

it would be intended that this alert is raised via cron (or another task) the same way heartbeats are processed, to create the alert 
via the cli use
`alerta send -r heartbeat -e opsgenie_heartbeat -E production -s ok -S HBNAME -O alerta/opsgenie --type opsgenieHb --tag password:xxxx-yyyy-ddddd`

where HBNAME is the heartbeat name in opsgenie (and in the url)

in docker this would be added to the config file `supervisord.conf`
`[program:OpsgenieHb]
command=sh -c "sleep 300 && alerta send -r heartbeat -e opsgenie_heartbeat -E production -s ok -S HBNAME -O alerta/opsgenie --type opsgenieHb --tag password:xxxx-yyyy-ddddd"
autostart=true
autorestart=true
redirect_stderr=true`

PLUGINS = ['opsgenie-heartbeat']

```

References
----------

  * OpsGenie Heartbeat API: https://docs.opsgenie.com/docs/heartbeat-api#ping-heartbeat-request



