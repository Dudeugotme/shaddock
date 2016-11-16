#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2014 Thibaut Lapierre <root@epheo.eu>. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from docker.client import Client
from docker.tls import TLSConfig
from docker.utils import kwargs_from_env


class DockerApi(object):
    """An abstraction class to the Docker API

    This class initiate a connection to the Docker API depending
    on the configuration gathered from the model.

    The Docker tls configuration works as follow:

    Authenticate server based on public/default CA pool
        Verify --> tls=True
        No verify --> tls = tls_config = docker.tls.TLSConfig(verify=False)
       opt: --tls

    Authenticate with client certificate, do not authenticate server based
    on given CA
        tls = tls_config = docker.tls.TLSConfig(
          client_cert=('/path/to/client-cert.pem', '/path/to/client-key.pem'))
       opt: --tls
            --tlscert /path/to/client-cert.pem
            --tlskey /path/to/client-key.pem

    Authenticate server based on given CA
        tls = tls_config = docker.tls.TLSConfig(ca_cert='/path/to/ca.pem')
       opt: --tlsverify
            --tlscacert /path/to/ca.pem

    Authenticate with client certificate, authenticate server based on given CA
        tls = tls_config = docker.tls.TLSConfig(
          client_cert=('/path/to/client-cert.pem', '/path/to/client-key.pem'),
          verify='/path/to/ca.pem')
        opt: --tlsverify \
             --tlscert /path/to/client-cert.pem \
             --tlskey /path/to/client-key.pem \
             --tlscacert /path/to/ca.pem
    """

    def __init__(self, app_args, api_cfg):

        if app_args.docker_url is not None:
            self.api_cfg = {}
            self.api_cfg['url'] = app_args.docker_url
            self.api_cfg['version'] = app_args.docker_version
            self.api_cfg['cert_path'] = app_args.docker_cert_path
            self.api_cfg['key_path'] = app_args.docker_key_path
            self.api_cfg['cacert_path'] = app_args.docker_cacert_path
            self.api_cfg['tls_verify'] = app_args.docker_tls_verify
            self.api_cfg['tls'] = app_args.docker_tls
            self.api_cfg['boot2docker'] = app_args.docker_boot2docker
        else:
            self.api_cfg = api_cfg

        tls_config = False
        if self.api_cfg['tls'] is True and self.api_cfg['tls_verify'] is False:
            if (self.api_cfg['cert_path'] is not None) and (
                    self.api_cfg['key_path'] is not None):
                print('--tls'
                      '--tlscert /path/to/client-cert.pem'
                      '--tlskey /path/to/client-key.pem')
                tls_config = TLSConfig(client_cert=(self.api_cfg['cert_path'],
                                                    self.api_cfg['key_path']))
            else:
                tls_config = TLSConfig(verify=False)

        if self.api_cfg['tls_verify'] is True:
            if self.api_cfg['cacert_path'] is not None:
                if (self.api_cfg['cert_path'] is not None) and (
                        self.api_cfg['key_path'] is not None):
                    print('--tlsverify'
                          '--tlscert /path/to/client-cert.pem'
                          '--tlskey /path/to/client-key.pem'
                          '--tlscacert /path/to/ca.pem')
                    tls_config = TLSConfig(client_cert=(
                        self.api_cfg['cert_path'],
                        self.api_cfg['key_path']),
                        verify=self.api_cfg['cacert_path'])
                else:
                    print('--tlsverify '
                          '--tlscacert /path/to/ca.pem')
                    tls_config = TLSConfig(ca_cert=self.api_cfg['cacert_path'])
            else:
                raise IndexError("Please specify at least a CA cert with "
                                 "--tlscacert", tls_config)

        if self.api_cfg['boot2docker'] is True:
            kwargs = kwargs_from_env()
            kwargs['tls'].assert_hostname = False
            self.api = Client(**kwargs)
        else:
            self.api = Client(base_url=self.api_cfg['url'],
                              version=str(self.api_cfg['version']),
                              tls=tls_config,
                              timeout=50)