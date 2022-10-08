#!/usr/bin/env python3
#
# Copyright (C) 2018-2022 VyOS maintainers and contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 or later as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from sys import exit

from vyos.config import Config
from vyos.configdict import dict_merge
from vyos.template import render
from vyos.util import call
from vyos.xml import defaults
from vyos import ConfigError
from vyos import airbag
airbag.enable()

config_file = r'/run/crowdsec/crowdsec-firewall-boucner.yaml'

def get_config(config=None):
    if config:
        conf = config
    else:
        conf = Config()
    base = ['service', 'ips', 'crowdsec']
    if not conf.exists(base):
        return None

    crowdsec = conf.get_config_dict(base, key_mangling=('-', '_'), get_first_key=True)
    # We have gathered the dict representation of the CLI, but there are default
    # options which we need to update into the dictionary retrived.
    default_values = defaults(base)
    crowdsec = dict_merge(default_values, crowdsec)

    return crowdsec

def verify(crowdsec):
    if not crowdsec:
        return None

    if 'update-frequency' not in crowdsec:
        raise ConfigError('Specify update frequency!')

    if 'api-url' not in crowdsec:
        raise ConfigError('Specify the url for the LAPI!')

    if 'api-key' in crowdsec:
        raise ConfigError('Specify the key for the LAPI!')

def generate(crowdsec):
    if not crowdsec:
        os.unlink(file)
        return None

    render(config_file, 'ips/crowdsec-firewall-bouncer.yaml.j2', crowdsec)
    return None

def apply(crowdsec):
    systemd_service = 'crowdsec-firewall-bouncer.service'
    if not crowdsec:
        # Stop crowdsec-firewall-bouncer service if removed
        call(f'systemctl stop {systemd_service}')
    else:
        call(f'systemctl reload-or-restart {systemd_service}')

    return None

if __name__ == '__main__':
    try:
        c = get_config()
        verify(c)
        generate(c)
        apply(c)
    except ConfigError as e:
        print(e)
        exit(1)
