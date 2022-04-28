# Copyright 2022 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test container_handlers."""

import ops
import sys

sys.path.append('lib')  # noqa
sys.path.append('src')  # noqa

import advanced_sunbeam_openstack.core as sunbeam_core
import advanced_sunbeam_openstack.container_handlers as container_handlers
import advanced_sunbeam_openstack.test_utils as test_utils


CHARM_METADATA = """
name: my-service
version: 3
bases:
  - name: ubuntu
    channel: 20.04/stable
tags:
  - openstack

subordinate: false

containers:
  test-container:
    resource: mysvc-image
    mounts:
      - storage: db
        location: /var/lib/mysvc

resources:
  mysvc-image:
    type: oci-image
"""


class DummyOperatorCharm(ops.charm.CharmBase):
    """Base charms for OpenStack operators."""

    _state = ops.framework.StoredState()

    def __init__(self, framework: ops.framework.Framework) -> None:
        """Run constructor."""
        super().__init__(framework)
        self._state.set_default(bootstrapped=False)

    def callback(self) -> None:
        """Run callback."""
        pass

    def test_container_pebble_ready(self) -> None:
        """Run container_pebble_ready."""
        pass
        pass


class TestPebbleHandler(test_utils.CharmTestCase):
    """Test for the OSBaseOperatorCharm class."""

    PATCHES = [
    ]

    def setUp(self) -> None:
        """Charm test class setup."""
        super().setUp(container_handlers, self.PATCHES)

    def test_managing_container_configs(self) -> None:
        """Test managing container_configs."""
        self.harness = ops.testing.Harness(
            DummyOperatorCharm,
            meta=CHARM_METADATA)
        self.harness.begin()
        default_file_config = sunbeam_core.ContainerConfigFile(
            "/etc/default",
            "user1",
            "group1")
        new_file_config = sunbeam_core.ContainerConfigFile(
            "/etc/new.txt",
            "user1",
            "group1")
        ph = container_handlers.PebbleHandler(
            self.harness.charm,
            "test-container",
            "my-service",
            [default_file_config],
            "templates",
            "yoga",
            self.harness.charm.callback)
        self.assertTrue(ph.config_file_managed(default_file_config.path))
        self.assertFalse(ph.config_file_managed(new_file_config.path))
        self.assertEqual(
            ph.container_configs,
            [default_file_config]
        )
        ph.add_container_config(new_file_config)
        self.assertEqual(
            ph.container_configs,
            [default_file_config, new_file_config]
        )
        ph.remove_container_config(new_file_config)
        self.assertEqual(
            ph.container_configs,
            [default_file_config]
        )
        ph.set_container_config([new_file_config])
        self.assertEqual(
            ph.container_configs,
            [new_file_config]
        )
