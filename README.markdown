# Client for Product Definition Center (PDC)

[![Build Status](https://travis-ci.org/product-definition-center/pdc-client.svg?branch=master)](https://travis-ci.org/product-definition-center/pdc-client)
[![Coverage Status](https://coveralls.io/repos/product-definition-center/pdc-client/badge.svg?branch=master&service=github)](https://coveralls.io/github/product-definition-center/pdc-client?branch=master)

PDC Client is command line and Python interface to PDC server.

Read [the documentation](https://pdc-client.readthedocs.io).

## Examples

### curl (Making Requests without PDC Client)

    $ curl --negotiate -u : -H "Accept: application/json" \
        https://pdc.example.com/rest_api/v1/auth/token/obtain/

    {"token":"123..."}

    $ curl -X POST \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -H "Authorization: Token 123..." \
        -d '{"email": "user@example.com", "username": "user"}' \
        https://pdc.example.com/rest_api/v1/contacts/people/

### PDC Client

    $ pdc_client -s example -x POST -r contacts/people/ \
        -d '{"email": "user@example.com", "username": "user"}'

- Handles authentication automatically.
- Data in JSON format by default.
- PDC server defined in configuration file.

See also [pdc\_client](https://pdc-client.readthedocs.io/en/latest/pdc_client.html).

### PDCClient API

```python
from pdc_client import PDCClient

try:
    client = PDCClient('example')
    client['contacts/people/']({
        'email': 'user@example.com',
        'username': 'user',
    })
except Exception as e:
    print(e.response.json())
```

- Handles request and response data natively as `dict`.
- HTTP request API is basically wrapper for
  [BeanBag](http://beanbag.readthedocs.org/en/latest/).

See also [API](https://pdc-client.readthedocs.io/en/latest/api.html).

### pdc

This is much more user friendly user high-level interface. A single invocation
can perform multiple requests depending on what subcommand you used.

See also [pdc](https://pdc-client.readthedocs.io/en/latest/pdc.html).

## Installation

Install using `yum` of `dnf`.

    sudo dnf install pdc-client

Or install from PyPI.

    pip install pdc-client

See also [Installation](https://pdc-client.readthedocs.io/en/latest/install.html).

## Configuration

Configuration file `~/.config/pdc/client_config.json` defines connections to
PDC servers with optional tokens and plugins for `pdc` utility.

    {
        "prod": {
            "host": "https://pdc.example.com/rest_api/v1/",
            "plugins": ["permission.py", "release.py"]
        }
    }

See also [Configuration](https://pdc-client.readthedocs.io/en/latest/config.html).

## Known Issues

### Kerberos

Under enterprise network, [Reverse DNS
mismatches](http://web.mit.edu/Kerberos/www/krb5-latest/doc/admin/princ_dns.html#reverse-dns-mismatches)
may cause problems authenticating with Kerberos.

If you can successfully run `kinit` but not authenticate yourself to PDC
servers, check `/etc/krb5.conf` and make sure that `rdns` is set to
false in `libdefaults` section. :

    [libdefaults]
        rdns = false

## For Developers

### Build

If you have got the code and setup your development environment,
then you could build from source and install the client.

    $ git checkout `{release-tag}`
    $ tito build --rpm --offline
    $ sudo yum install /tmp/tito/noarch/pdc-client*.noarch.rpm

See also [Release](https://pdc-client.readthedocs.io/en/latest/release.html).

### Development Configuration

You can add local development server to configuration file
(`~/.config/pdc/client_config.json`).

    {
        "local": {
            "host": "http://localhost:8000/rest_api/v1/",
            "develop": true,
            "ssl-verify": false
        }
    }
