icinga2api Plugin
=================

installation
------------

This is a plugin to allow 2 way comms from libreNMS. Alerta is built in by default to libreNMS however a few mods
need to be made to the config to allow seamless 2 way comms. details below.
Once you have the librenms congigured, you can enable this plugin by:

git clone (repo)
pip3 install plugin-dir/.
add librenms to the list of alerta plugins. (ensure you are in the same venv as alerta)


Configuration
------------
the following settings are availbale:

    LIBRENMS_API_KEY > the api key to talk to the LibreNMS host. 


Issues:
config at other libreNMS end could get lost with an update
if you have 2 libreNMS servers we need more than 1 key available to talk back to the API's
http support only currently
no proxy support


Changes to Alerta.php
.attributes + 'alertid' => $obj['alert_id'],
.type = 'libreNMS' - used to filter events for callback plugin to know where they came from. was no useful info in it
.attributes. + 'externalUrl' => 'http://10.108.106.80',
.attributes +  'return_api_key' => 'xxxx', - this is used to send the api key back to alerta so you can use multiple librenms's. if this doesn't exist then we'll use the env-var above



 