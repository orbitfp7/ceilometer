# -*- encoding: utf-8 -*-
#
# Copyright © 2013 eNovance
#
# Author: Julien Danjou <julien@danjou.info>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import urlparse
import mock
import requests

from oslo.config import cfg

from ceilometer.alarm import service
from ceilometer.openstack.common import context
from ceilometer.tests import base


class TestAlarmNotifier(base.TestCase):

    def setUp(self):
        super(TestAlarmNotifier, self).setUp()
        self.service = service.AlarmNotifierService('somehost', 'sometopic')

    @mock.patch('ceilometer.pipeline.setup_pipeline', mock.MagicMock())
    def test_init_host(self):
        # If we try to create a real RPC connection, init_host() never
        # returns. Mock it out so we can establish the service
        # configuration.
        with mock.patch('ceilometer.openstack.common.rpc.create_connection'):
            self.service.start()

    def test_notify_alarm(self):
        data = {
            'actions': ['test://'],
            'alarm': {'name': 'foobar'},
            'state': 'ALARM',
            'reason': 'Everything is on fire',
        }
        self.service.notify_alarm(context.get_admin_context(), data)
        notifications = self.service.notifiers['test'].obj.notifications
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0], (
            urlparse.urlsplit(data['actions'][0]),
            data['alarm'],
            data['state'],
            data['reason']))

    def test_notify_alarm_no_action(self):
        self.service.notify_alarm(context.get_admin_context(), {})

    def test_notify_alarm_log_action(self):
        self.service.notify_alarm(context.get_admin_context(),
                                  {
                                      'actions': ['log://'],
                                      'alarm': {'name': 'foobar'},
                                      'condition': {'threshold': 42},
                                  })

    @staticmethod
    def _fake_spawn_n(func, *args, **kwargs):
        func(*args, **kwargs)

    def test_notify_alarm_rest_action_ok(self):
        action = 'http://host/action'
        data_json = '{"state": "ALARM", "reason": "what ?"}'

        with mock.patch('eventlet.spawn_n', self._fake_spawn_n):
            with mock.patch.object(requests, 'post') as poster:
                self.service.notify_alarm(context.get_admin_context(),
                                          {
                                              'actions': [action],
                                              'alarm': {'name': 'foobar'},
                                              'condition': {'threshold': 42},
                                              'reason': 'what ?',
                                              'state': 'ALARM',
                                          })
                poster.assert_called_with(action, data=data_json)

    def test_notify_alarm_rest_action_with_ssl_client_cert(self):
        action = 'https://host/action'
        certificate = "/etc/ssl/cert/whatever.pem"
        data_json = '{"state": "ALARM", "reason": "what ?"}'

        cfg.CONF.set_override("rest_notifier_certificate_file", certificate,
                              group='alarm')

        with mock.patch('eventlet.spawn_n', self._fake_spawn_n):
            with mock.patch.object(requests, 'post') as poster:
                self.service.notify_alarm(context.get_admin_context(),
                                          {
                                              'actions': [action],
                                              'alarm': {'name': 'foobar'},
                                              'condition': {'threshold': 42},
                                              'reason': 'what ?',
                                              'state': 'ALARM',
                                          })
                poster.assert_called_with(action, data=data_json,
                                          cert=certificate, verify=True)

    def test_notify_alarm_rest_action_with_ssl_client_cert_and_key(self):
        action = 'https://host/action'
        certificate = "/etc/ssl/cert/whatever.pem"
        key = "/etc/ssl/cert/whatever.key"
        data_json = '{"state": "ALARM", "reason": "what ?"}'

        cfg.CONF.set_override("rest_notifier_certificate_file", certificate,
                              group='alarm')
        cfg.CONF.set_override("rest_notifier_certificate_key", key,
                              group='alarm')

        with mock.patch('eventlet.spawn_n', self._fake_spawn_n):
            with mock.patch.object(requests, 'post') as poster:
                self.service.notify_alarm(context.get_admin_context(),
                                          {
                                              'actions': [action],
                                              'alarm': {'name': 'foobar'},
                                              'condition': {'threshold': 42},
                                              'reason': 'what ?',
                                              'state': 'ALARM',
                                          })
                poster.assert_called_with(action, data=data_json,
                                          cert=(certificate, key), verify=True)

    def test_notify_alarm_rest_action_with_ssl_verify_disable_by_cfg(self):
        action = 'https://host/action'
        data_json = '{"state": "ALARM", "reason": "what ?"}'

        cfg.CONF.set_override("rest_notifier_ssl_verify", False,
                              group='alarm')

        with mock.patch('eventlet.spawn_n', self._fake_spawn_n):
            with mock.patch.object(requests, 'post') as poster:
                self.service.notify_alarm(context.get_admin_context(),
                                          {
                                              'actions': [action],
                                              'alarm': {'name': 'foobar'},
                                              'condition': {'threshold': 42},
                                              'reason': 'what ?',
                                              'state': 'ALARM',
                                          })
                poster.assert_called_with(action, data=data_json,
                                          verify=False)

    def test_notify_alarm_rest_action_with_ssl_verify_disable(self):
        action = 'https://host/action?ceilometer-alarm-ssl-verify=0'
        data_json = '{"state": "ALARM", "reason": "what ?"}'

        with mock.patch('eventlet.spawn_n', self._fake_spawn_n):
            with mock.patch.object(requests, 'post') as poster:
                self.service.notify_alarm(context.get_admin_context(),
                                          {
                                              'actions': [action],
                                              'alarm': {'name': 'foobar'},
                                              'condition': {'threshold': 42},
                                              'reason': 'what ?',
                                              'state': 'ALARM',
                                          })
                poster.assert_called_with(action, data=data_json,
                                          verify=False)

    def test_notify_alarm_rest_action_with_ssl_verify_enable_by_user(self):
        action = 'https://host/action?ceilometer-alarm-ssl-verify=1'
        data_json = '{"state": "ALARM", "reason": "what ?"}'

        cfg.CONF.set_override("rest_notifier_ssl_verify", False,
                              group='alarm')

        with mock.patch('eventlet.spawn_n', self._fake_spawn_n):
            with mock.patch.object(requests, 'post') as poster:
                self.service.notify_alarm(context.get_admin_context(),
                                          {
                                              'actions': [action],
                                              'alarm': {'name': 'foobar'},
                                              'condition': {'threshold': 42},
                                              'reason': 'what ?',
                                              'state': 'ALARM',
                                          })
                poster.assert_called_with(action, data=data_json,
                                          verify=True)

    @staticmethod
    def _fake_urlsplit(*args, **kwargs):
        raise Exception("Evil urlsplit!")

    def test_notify_alarm_invalid_url(self):
        with mock.patch('ceilometer.openstack.common.network_utils.urlsplit',
                        self._fake_urlsplit):
            LOG = mock.MagicMock()
            with mock.patch('ceilometer.alarm.service.LOG', LOG):
                self.service.notify_alarm(
                    context.get_admin_context(),
                    {
                        'actions': ['no-such-action-i-am-sure'],
                        'alarm': {'name': 'foobar'},
                        'condition': {'threshold': 42},
                    })
                self.assertTrue(LOG.error.called)

    def test_notify_alarm_invalid_action(self):
        LOG = mock.MagicMock()
        with mock.patch('ceilometer.alarm.service.LOG', LOG):
            self.service.notify_alarm(
                context.get_admin_context(),
                {
                    'actions': ['no-such-action-i-am-sure://'],
                    'alarm': {'name': 'foobar'},
                    'condition': {'threshold': 42},
                })
            self.assertTrue(LOG.error.called)
