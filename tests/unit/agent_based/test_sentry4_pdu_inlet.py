#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Checks based on the Sentry4-MIB for PDU status.
#
# Copyright (C) 2022 Curtis Bowden <curtis.bowden@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import pytest  # type: ignore[import]
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import sentry4_pdu_inlet


@pytest.mark.parametrize('string_table, result', [
    (
        [['AA', 'Master_UPS_A', '1', '0', '878', '952', '44', '92'],
         ['BA', 'Slave_UPS_B', '1', '0', '923', '996', '46', '93']],
        {
            'Input cord AA Master_UPS_A': {'cord_id': 'AA', 'cord_name': 'Master_UPS_A', 'state': '1', 'status': '0', 'active_power': '878', 'apparent_power': '952', 'power_utilized': '44', 'power_factor': '92'},
            'Input cord BA Slave_UPS_B': {'cord_id': 'BA', 'cord_name': 'Slave_UPS_B', 'state': '1', 'status': '0', 'active_power': '923', 'apparent_power': '996', 'power_utilized': '46', 'power_factor': '93'}
        },
    ),
])
def test_parse_sentry4_pdu_inlet(string_table, result):
    assert sentry4_pdu_inlet.parse_sentry4_pdu_inlet(string_table) == result


@pytest.mark.parametrize('section, result', [
    (
        {
            'Input cord AA Master_UPS_A': {'cord_id': 'AA', 'cord_name': 'Master_UPS_A', 'state': '1', 'status': '0', 'active_power': '878', 'apparent_power': '952', 'power_utilized': '44', 'power_factor': '92'},
            'Input cord BA Slave_UPS_B': {'cord_id': 'BA', 'cord_name': 'Slave_UPS_B', 'state': '1', 'status': '0', 'active_power': '923', 'apparent_power': '996', 'power_utilized': '46', 'power_factor': '93'}
        },
        [Service(item='Input cord AA Master_UPS_A'), Service(item='Input cord BA Slave_UPS_B')]
    ),
])
def test_discover_sentry4_pdu_inlet(section, result):
    assert list(sentry4_pdu_inlet.discover_sentry4_pdu_inlet(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', {}, []),
    (
        'foo',
        {
            'Input cord AA Master_UPS_A': {'cord_id': 'AA', 'cord_name': 'Master_UPS_A', 'state': '1', 'status': '0', 'active_power': '878', 'apparent_power': '952', 'power_utilized': '44', 'power_factor': '92'},
            'Input cord BA Slave_UPS_B': {'cord_id': 'BA', 'cord_name': 'Slave_UPS_B', 'state': '1', 'status': '0', 'active_power': '923', 'apparent_power': '996', 'power_utilized': '46', 'power_factor': '93'}
        },
        []
    ),
    (
        'Input cord AA Master_UPS_A',
        {
            'Input cord AA Master_UPS_A': {'cord_id': 'AA', 'cord_name': 'Master_UPS_A', 'state': '1', 'status': '0', 'active_power': '878', 'apparent_power': '952', 'power_utilized': '44', 'power_factor': '92'},
            'Input cord BA Slave_UPS_B': {'cord_id': 'BA', 'cord_name': 'Slave_UPS_B', 'state': '1', 'status': '0', 'active_power': '923', 'apparent_power': '996', 'power_utilized': '46', 'power_factor': '93'}
        },
        [Metric('power', 878), Metric('appower', 952), Metric('power_usage_percentage', 44), Result(state=State.OK, summary='Status: normal(0) State: on(1)')]
    ),
    (
        'Input cord AA Master_UPS_A',
        {
            'Input cord AA Master_UPS_A': {'cord_id': 'AA', 'cord_name': 'Master_UPS_A', 'state': '1', 'status': '18', 'active_power': '878', 'apparent_power': '952', 'power_utilized': '44', 'power_factor': '92'},
            'Input cord BA Slave_UPS_B': {'cord_id': 'BA', 'cord_name': 'Slave_UPS_B', 'state': '1', 'status': '0', 'active_power': '923', 'apparent_power': '996', 'power_utilized': '46', 'power_factor': '93'}
        },
        [Metric('power', 878), Metric('appower', 952), Metric('power_usage_percentage', 44), Result(state=State.CRIT, summary='Status: alarm(18) State: on(1)')]
    ),
    (
        'Input cord BA Slave_UPS_B',
        {
            'Input cord AA Master_UPS_A': {'cord_id': 'AA', 'cord_name': 'Master_UPS_A', 'state': '1', 'status': '0', 'active_power': '878', 'apparent_power': '952', 'power_utilized': '44', 'power_factor': '92'},
            'Input cord BA Slave_UPS_B': {'cord_id': 'BA', 'cord_name': 'Slave_UPS_B', 'state': '1', 'status': '12', 'active_power': '923', 'apparent_power': '996', 'power_utilized': '46', 'power_factor': '93'}
        },
        [Metric('power', 923), Metric('appower', 996), Metric('power_usage_percentage', 46), Result(state=State.CRIT, summary='Status: breakerTripped(12) State: on(1)')]
    ),
    (
        'Input cord AA Master_UPS_A',
        {
            'Input cord AA Master_UPS_A': {'cord_id': 'AA', 'cord_name': 'Master_UPS_A', 'state': '0', 'status': '0', 'active_power': '878', 'apparent_power': '952', 'power_utilized': '44', 'power_factor': '92'},
            'Input cord BA Slave_UPS_B': {'cord_id': 'BA', 'cord_name': 'Slave_UPS_B', 'state': '1', 'status': '0', 'active_power': '923', 'apparent_power': '996', 'power_utilized': '46', 'power_factor': '93'}
        },
        [Metric('power', 878), Metric('appower', 952), Metric('power_usage_percentage', 44), Result(state=State.WARN, summary='Status: normal(0) State: unknown(0)')]
    ),
])
def test_check_sentry4_pdu_inlet(monkeypatch, item, section, result):
    assert list(sentry4_pdu_inlet.check_sentry4_pdu_inlet(item, section)) == result
