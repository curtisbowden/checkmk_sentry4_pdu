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
from cmk.base.plugins.agent_based import sentry4_pdu_humid


@pytest.mark.parametrize('string_table, result', [
    (
        [['A1', 'Humid_Sensor_A1', '-1', '7', '5', '10', '90', '95'],
         ['A2', 'Humid_Sensor_A2', '-1', '7', '5', '10', '90', '95'],
         ['B1', 'Humid_Sensor_B1', '-1', '7', '5', '10', '90', '95'],
         ['B2', 'Humid_Sensor_B2', '-1', '7', '5', '10', '90', '95'],
         ['E1', 'HVAC_1_output', '71', '0', '5', '10', '90', '95'],
         ['E2', 'HVAC_1_intake', '66', '0', '5', '10', '90', '95']],
        {
            'Humidity E1 HVAC_1_output': {'value': 71, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95},
            'Humidity E2 HVAC_1_intake': {'value': 66, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95}
        },
    ),
])
def test_parse_sentry4_pdu_humid(string_table, result):
    assert sentry4_pdu_humid.parse_sentry4_pdu_humid(string_table) == result


@pytest.mark.parametrize('section, result', [
    (
        {
            'Humidity E1 HVAC_1_output': {'value': 71, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95},
            'Humidity E2 HVAC_1_intake': {'value': 66, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95}
        },
        [Service(item='Humidity E1 HVAC_1_output'), Service(item='Humidity E2 HVAC_1_intake')]
    ),
])
def test_discover_sentry4_pdu_humid(section, result):
    assert list(sentry4_pdu_humid.discover_sentry4_pdu_humid(section)) == result


@pytest.mark.parametrize('item, params, section, result', [
    ('', {}, {}, []),
    (
        'foo',
        {},
        {
            'Humidity E1 HVAC_1_output': {'value': 71, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95},
            'Humidity E2 HVAC_1_intake': {'value': 66, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95}
        },
        []
    ),
    (
        'Humidity E1 HVAC_1_output',
        {},
        {
            'Humidity E1 HVAC_1_output': {'value': 71, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95},
            'Humidity E2 HVAC_1_intake': {'value': 66, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95}
        },
        [Metric('humidity', 71, levels=(90, 95)), Result(state=State.OK, summary='71%', details='High alarm:95.0, High warning:90.0, Low warning:10.0, Low alarm:5.0')]
    ),
    (
        'Humidity E1 HVAC_1_output',
        {},
        {
            'Humidity E1 HVAC_1_output': {'value': 91, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95},
            'Humidity E2 HVAC_1_intake': {'value': 66, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95}
        },
        [Metric('humidity', 91, levels=(90, 95)), Result(state=State.WARN, summary='91% is above warning threshold', details='High alarm:95.0, High warning:90.0, Low warning:10.0, Low alarm:5.0')]
    ),
    (
        'Humidity E1 HVAC_1_output',
        {},
        {
            'Humidity E1 HVAC_1_output': {'value': 96, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95},
            'Humidity E2 HVAC_1_intake': {'value': 66, 'status': 0, 'low_alarm': 5, 'low_warning': 10, 'high_warning': 90, 'high_alarm': 95}
        },
        [Metric('humidity', 96, levels=(90, 95)), Result(state=State.CRIT, summary='96% is above critical threshold', details='High alarm:95.0, High warning:90.0, Low warning:10.0, Low alarm:5.0')]
    ),
])
def test_check_sentry4_pdu_humid(monkeypatch, item, params, section, result):
    assert list(sentry4_pdu_humid.check_sentry4_pdu_humid(item, params, section)) == result
