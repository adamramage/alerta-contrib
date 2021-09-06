icinga2api Plugin
=================

installation
------------

This is a plugin to allow 2 way comms from the icinga2alerta icinga2 notification plugin.
Once you have the icinga2 app installed and congigured, you can enable this plugin by:

git clone (repo)
pip3 install plugin-dir/.
add icinga2api to the list of alerta plugins. (ensure you are in the same venv as alerta)


Configuration
------------
the following settings are availbale:

    ICINGA2_API_URL > not really required, uses the externalUrl attribute configured in icinga2alerta
    ICINGA2_USERNAME > your api username as set in /etc/icinga2/conf.d/api-users.conf
    ICINGA2_PASSWORD > your api password as set in /etc/icinga2/conf.d/api-users.conf
    ICINGA2_SILENCE_DAYS > used to configure how long acks at set for in icinga, uses alert.timeout or def 1 
    ICINGA2_SILENCE_FROM_ACK > not tested, no idea. def False
    

 