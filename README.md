
# icinga2-autoack

This is script which listens to Icinga2 API and acknowledges all services
in their downtimes.

Why? Because there are some buggy notification tools which do not 
honor "in downtime" but does work with acknowledged    :facepalm:

## State

This program is in proof-of-concept state. But it is already used 
in production.

## How to start

Create `icinga2-api.ini` according to [icinga2api][icinga2api] 
module [configuration][icinga2api-config].

```ini
[api]
url = https://127.0.0.1:5665/
username = auto-ack
password = Hahghoh5Ohv0fieg   
ca_certificate = ./icinga2-ca.crt
```

Start the script (possibly in Pipfile managed virtualenv).

## License

BSD-2

[icinga2api]: https://github.com/fmnisme/python-icinga2api
[icinga2api-config]: https://github.com/fmnisme/python-icinga2api/blob/master/doc/2-authentication.md#-config-file
