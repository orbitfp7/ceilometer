#
# Copyright 2012 eNovance <licensing@enovance.com>
# Copyright 2012 Red Hat, Inc
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

import ceilometer

from ceilometer.compute import plugin
from ceilometer.compute.pollsters import util
from ceilometer.compute.virt import inspector as virt_inspector
from ceilometer.openstack.common.gettextutils import _
from ceilometer.openstack.common import log
from ceilometer import sample

LOG = log.getLogger(__name__)


class CheckPointSizePollster(plugin.ComputePollster):

    def get_samples(self, manager, cache, resources):
        for instance in resources:
            LOG.debug(_('checking instance %s'), instance.id)
            instance_name = util.instance_name(instance)
            try:
                checkpoint_size = manager.inspector.inspect_checkpoint(instance)[0]
                LOG.debug(_("CHECKPOINT SIZE: %(instance)s %(time)d"),
                          {'instance': instance.__dict__,
                           'time': checkpoint_size})
                yield util.make_sample_from_instance(
                    instance,
                    name='checkpoint.size',
                    type=sample.TYPE_GAUGE,
                    unit='B',
                    volume=checkpoint_size,
                )
            except virt_inspector.InstanceNotFoundException as err:
                # Instance was deleted while getting samples. Ignore it.
                LOG.debug(_('Exception while getting samples %s'), err)
            except ceilometer.NotImplementedError:
                # Selected inspector does not implement this pollster.
                LOG.debug(_('Obtaining checkpoint size is not implemented for %s'
                            ), manager.inspector.__class__.__name__)
            except Exception as err:
                LOG.exception(_('could not get checkpoint size for %(id)s: %(e)s'),
                              {'id': instance.id, 'e': err})


class CheckPointLengthPollster(plugin.ComputePollster):

    def get_samples(self, manager, cache, resources):
        for instance in resources:
            LOG.debug(_('checking instance %s'), instance.id)
            instance_name = util.instance_name(instance)
            try:
                checkpoint_length = manager.inspector.inspect_checkpoint(instance)[1]
                LOG.debug(_("CHECKPOINT LENGTH: %(instance)s %(time)d"),
                          {'instance': instance.__dict__,
                           'time': checkpoint_length})
                yield util.make_sample_from_instance(
                    instance,
                    name='checkpoint.length',
                    type=sample.TYPE_GAUGE,
                    unit='ms',
                    volume=checkpoint_length,
                )
            except virt_inspector.InstanceNotFoundException as err:
                # Instance was deleted while getting samples. Ignore it.
                LOG.debug(_('Exception while getting samples %s'), err)
            except ceilometer.NotImplementedError:
                # Selected inspector does not implement this pollster.
                LOG.debug(_('Obtaining checkpoint length is not implemented for %s'
                            ), manager.inspector.__class__.__name__)
            except Exception as err:
                LOG.exception(_('could not get checkpoint length for %(id)s: %(e)s'),
                              {'id': instance.id, 'e': err})

class CheckPointPausePollster(plugin.ComputePollster):

    def get_samples(self, manager, cache, resources):
        for instance in resources:
            LOG.debug(_('checking instance %s'), instance.id)
            instance_name = util.instance_name(instance)
            try:
                checkpoint_pause = manager.inspector.inspect_checkpoint(instance)[2]
                LOG.debug(_("CHECKPOINT PAUSE: %(instance)s %(time)d"),
                          {'instance': instance.__dict__,
                           'time': checkpoint_pause})
                yield util.make_sample_from_instance(
                    instance,
                    name='checkpoint.pause',
                    type=sample.TYPE_GAUGE,
                    unit='ms',
                    volume=checkpoint_pause,
                )
            except virt_inspector.InstanceNotFoundException as err:
                # Instance was deleted while getting samples. Ignore it.
                LOG.debug(_('Exception while getting samples %s'), err)
            except ceilometer.NotImplementedError:
                # Selected inspector does not implement this pollster.
                LOG.debug(_('Obtaining checkpoint pause is not implemented for %s'
                            ), manager.inspector.__class__.__name__)
            except Exception as err:
                LOG.exception(_('could not get checkpoint pause for %(id)s: %(e)s'),
                              {'id': instance.id, 'e': err})
