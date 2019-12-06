
# icinga2-autoack

This script listens to Icinga2 API and acknowledges hosts and services
during they downtimes.  

It also acknowledges hosts and services with `autoack` variable set.

Why? Because there are some buggy notification tools which do not 
honor "in downtime" but does work with acknowledged state. 🤦


## Code maturity

This program is in proof-of-concept state. But it is already used 
in production. 🤷

## How to start

Create Icinga2 API user in `/etc/icinga2/

```
object ApiUser "autoack" {
        password = "mrznawrxbxbg"
        permissions = [
            "objects/query/Host",
            "objects/query/Service",
            "objects/query/Downtime",
            "actions/acknowledge-problem",
            "events/*",
            "status/query",
        ]
}
```

Create `icinga2-api.ini` according to [icinga2api][icinga2api] 
module [configuration][icinga2api-config].

```ini
[api]
url = https://my-icinga-hostname:5665/
username = auto-ack
password = mrznawrxbxbg
ca_certificate = ./icinga2-ca.crt
```

Copy  certificate from `/var/lib/icinga2/ca/ca.crt` to 
your directory.

Start the script (possibly in Pipfile managed virtualenv).


## License

BSD-2

[icinga2api]: https://github.com/fmnisme/python-icinga2api
[icinga2api-config]: https://github.com/fmnisme/python-icinga2api/blob/master/doc/2-authentication.md#-config-file
