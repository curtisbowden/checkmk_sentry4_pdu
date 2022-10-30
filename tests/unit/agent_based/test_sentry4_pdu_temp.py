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
#
# Example from SNMP data:
# Sentry4-MIB::st4UnitID.1 = STRING: A
# Sentry4-MIB::st4UnitName.1 = STRING: Master
# Sentry4-MIB::st4UnitProductSN.1 = STRING: ABCD0000001
# Sentry4-MIB::st4UnitModel.1 = STRING: C2WG36TE-YQME2M66/C
# Sentry4-MIB::st4UnitType.1 = INTEGER: masterPdu(0)
# Sentry4-MIB::st4UnitStatus.1 = INTEGER: normal(0)

import pytest  # type: ignore[import]
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import sentry4_pdu_temp


@pytest.mark.parametrize('string_table, result', [
    (
        [['0', '', '', '', '', '', '', '', ''],
         ['', 'A1', 'Temp_Sensor_A1', '-410', '7', '1', '5', '45', '50'],
         ['', 'A2', 'Temp_Sensor_A2', '-410', '7', '1', '5', '45', '50'],
         ['', 'B1', 'Temp_Sensor_B1', '-410', '7', '1', '5', '30', '35'],
         ['', 'B2', 'Temp_Sensor_B2', '-410', '7', '1', '5', '30', '35'],
         ['', 'E1', 'HVAC_1_output', '155', '0', '1', '5', '45', '50'],
         ['', 'E2', 'HVAC_1_intake', '170', '0', '1', '5', '45', '50']],
        {
            'Temperature E1 HVAC_1_output': {'value': 15.5, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50},
            'Temperature E2 HVAC_1_intake': {'value': 17.0, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50}
        },
    ),
    (
        [['1', '', '', '', '', '', '', '', ''],
         ['', 'A1', 'Temp_Sensor_A1', '-706', '7', '34', '41', '113', '122'],
         ['', 'A2', 'Temp_Sensor_A2', '-706', '7', '34', '41', '113', '122'],
         ['', 'B1', 'Temp_Sensor_B1', '-706', '7', '34', '41', '86', '95'],
         ['', 'B2', 'Temp_Sensor_B2', '-706', '7', '34', '41', '86', '95'],
         ['', 'E1', 'HVAC_1_output', '599', '0', '34', '41', '113', '122'],
         ['', 'E2', 'HVAC_1_intake', '626', '0', '34', '41', '113', '122']],
        {
            'Temperature E1 HVAC_1_output': {'value': 15.5, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50},
            'Temperature E2 HVAC_1_intake': {'value': 17.0, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50}
        },
    ),
])
def test_parse_sentry4_pdu_temp(string_table, result):
    assert sentry4_pdu_temp.parse_sentry4_pdu_temp(string_table) == result


@pytest.mark.parametrize('section, result', [
    (
        {
            'Temperature E1 HVAC_1_output': {'value': 15.5, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50},
            'Temperature E2 HVAC_1_intake': {'value': 17.0, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50}
        },
        [Service(item='Temperature E1 HVAC_1_output'), Service(item='Temperature E2 HVAC_1_intake')]
    ),
])
def test_discover_sentry4_pdu_temp(section, result):
    assert list(sentry4_pdu_temp.discover_sentry4_pdu_temp(section)) == result


@pytest.mark.parametrize('item, params, section, result', [
    ('', {}, {}, []),
    (
        'foo',
        {},
        {
            'Temperature E1 HVAC_1_output': {'value': 15.5, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50},
            'Temperature E2 HVAC_1_intake': {'value': 17.0, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50}
        },
        []
    ),
    (
        'Temperature E1 HVAC_1_output',
        {},
        {
            'Temperature E1 HVAC_1_output': {'value': 15.5, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50},
            'Temperature E2 HVAC_1_intake': {'value': 17.0, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50}
        },
        [Metric('sentry4_temp', 15.5, levels=(45.0, 50.0)), Result(state=State.OK, summary='15.5 °C', details='High alarm:50.0, High warning:45.0, Low warning:5.0, Low alarm:1.0')]
    ),
    (
        'Temperature E1 HVAC_1_output',
        {},
        {
            'Temperature E1 HVAC_1_output': {'value': 46.0, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50},
            'Temperature E2 HVAC_1_intake': {'value': 17.0, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50}
        },
        [Metric('sentry4_temp', 46.0, levels=(45.0, 50.0)), Result(state=State.WARN, summary='46.0 °C is above warning threshold', details='High alarm:50.0, High warning:45.0, Low warning:5.0, Low alarm:1.0')]
    ),
    (
        'Temperature E1 HVAC_1_output',
        {},
        {
            'Temperature E1 HVAC_1_output': {'value': 51.0, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50},
            'Temperature E2 HVAC_1_intake': {'value': 17.0, 'status': 0, 'low_alarm': 1, 'low_warning': 5, 'high_warning': 45, 'high_alarm': 50}
        },
        [Metric('sentry4_temp', 51.0, levels=(45.0, 50.0)), Result(state=State.CRIT, summary='51.0 °C is above critical threshold', details='High alarm:50.0, High warning:45.0, Low warning:5.0, Low alarm:1.0')]
    ),
])
def test_check_sentry4_pdu_temp(monkeypatch, item, params, section, result):
    assert list(sentry4_pdu_temp.check_sentry4_pdu_temp(item, params, section)) == result
