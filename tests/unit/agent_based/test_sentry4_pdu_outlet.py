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
from cmk.base.plugins.agent_based import sentry4_pdu_outlet


@pytest.mark.parametrize('string_table, result', [
    (
        [['AA1', 'Master_Outlet_1', '1', '0', '0', '2072', '0', '0'],
         ['AA2', 'Master_Outlet_2', '1', '0', '0', '2068', '0', '0'],
         ['AA3', 'Master_Outlet_3', '1', '0', '27', '2073', '48', '55'],
         ['BA1', 'Link1_Outlet_1', '1', '0', '0', '2064', '0', '0'],
         ['BA2', 'Link1_Outlet_2', '1', '0', '0', '2068', '0', '0'],
         ['BA3', 'Link1_Outlet_3', '1', '0', '28', '2058', '52', '58']],
        {
            'Outlet AA1 Master_Outlet_1': {'outlet_id': 'AA1', 'outlet_name': 'Master_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2072', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA2 Master_Outlet_2': {'outlet_id': 'AA2', 'outlet_name': 'Master_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA3 Master_Outlet_3': {'outlet_id': 'AA3', 'outlet_name': 'Master_Outlet_3', 'state': '1', 'status': '0', 'current': '27', 'voltage': '2073', 'active_power': '48', 'apparent_power': '55'},
            'Outlet BA1 Link1_Outlet_1': {'outlet_id': 'BA1', 'outlet_name': 'Link1_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2064', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA2 Link1_Outlet_2': {'outlet_id': 'BA2', 'outlet_name': 'Link1_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA3 Link1_Outlet_3': {'outlet_id': 'BA3', 'outlet_name': 'Link1_Outlet_3', 'state': '1', 'status': '0', 'current': '28', 'voltage': '2058', 'active_power': '52', 'apparent_power': '58'}
        },
    ),
])
def test_parse_sentry4_pdu_outlet(string_table, result):
    assert sentry4_pdu_outlet.parse_sentry4_pdu_outlet(string_table) == result


@pytest.mark.parametrize('section, result', [
    (
        {
            'Outlet AA1 Master_Outlet_1': {'outlet_id': 'AA1', 'outlet_name': 'Master_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2072', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA2 Master_Outlet_2': {'outlet_id': 'AA2', 'outlet_name': 'Master_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA3 Master_Outlet_3': {'outlet_id': 'AA3', 'outlet_name': 'Master_Outlet_3', 'state': '1', 'status': '0', 'current': '27', 'voltage': '2073', 'active_power': '48', 'apparent_power': '55'},
            'Outlet BA1 Link1_Outlet_1': {'outlet_id': 'BA1', 'outlet_name': 'Link1_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2064', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA2 Link1_Outlet_2': {'outlet_id': 'BA2', 'outlet_name': 'Link1_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA3 Link1_Outlet_3': {'outlet_id': 'BA3', 'outlet_name': 'Link1_Outlet_3', 'state': '1', 'status': '0', 'current': '28', 'voltage': '2058', 'active_power': '52', 'apparent_power': '58'}
        },
        [Service(item='Outlet AA1 Master_Outlet_1'),
         Service(item='Outlet AA2 Master_Outlet_2'),
         Service(item='Outlet AA3 Master_Outlet_3'),
         Service(item='Outlet BA1 Link1_Outlet_1'),
         Service(item='Outlet BA2 Link1_Outlet_2'),
         Service(item='Outlet BA3 Link1_Outlet_3')]
    ),
])
def test_discover_sentry4_pdu_outlet(section, result):
    assert list(sentry4_pdu_outlet.discover_sentry4_pdu_outlet(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', {}, []),
    (
        'foo',
        {
            'Outlet AA1 Master_Outlet_1': {'outlet_id': 'AA1', 'outlet_name': 'Master_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2072', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA2 Master_Outlet_2': {'outlet_id': 'AA2', 'outlet_name': 'Master_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA3 Master_Outlet_3': {'outlet_id': 'AA3', 'outlet_name': 'Master_Outlet_3', 'state': '1', 'status': '0', 'current': '27', 'voltage': '2073', 'active_power': '48', 'apparent_power': '55'},
            'Outlet BA1 Link1_Outlet_1': {'outlet_id': 'BA1', 'outlet_name': 'Link1_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2064', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA2 Link1_Outlet_2': {'outlet_id': 'BA2', 'outlet_name': 'Link1_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA3 Link1_Outlet_3': {'outlet_id': 'BA3', 'outlet_name': 'Link1_Outlet_3', 'state': '1', 'status': '0', 'current': '28', 'voltage': '2058', 'active_power': '52', 'apparent_power': '58'}
        },
        []
    ),
    (
        'Outlet AA3 Master_Outlet_3',
        {
            'Outlet AA1 Master_Outlet_1': {'outlet_id': 'AA1', 'outlet_name': 'Master_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2072', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA2 Master_Outlet_2': {'outlet_id': 'AA2', 'outlet_name': 'Master_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA3 Master_Outlet_3': {'outlet_id': 'AA3', 'outlet_name': 'Master_Outlet_3', 'state': '1', 'status': '0', 'current': '27', 'voltage': '2073', 'active_power': '48', 'apparent_power': '55'},
            'Outlet BA1 Link1_Outlet_1': {'outlet_id': 'BA1', 'outlet_name': 'Link1_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2064', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA2 Link1_Outlet_2': {'outlet_id': 'BA2', 'outlet_name': 'Link1_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA3 Link1_Outlet_3': {'outlet_id': 'BA3', 'outlet_name': 'Link1_Outlet_3', 'state': '1', 'status': '0', 'current': '28', 'voltage': '2058', 'active_power': '52', 'apparent_power': '58'}
        },
        [Metric('current', 0.27), Metric('voltage', 207.3), Metric('power', 48), Metric('appower', 55), Result(state=State.OK, summary='Status: normal(0) State: on(1)')]
    ),
    (
        'Outlet AA3 Master_Outlet_3',
        {
            'Outlet AA1 Master_Outlet_1': {'outlet_id': 'AA1', 'outlet_name': 'Master_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2072', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA2 Master_Outlet_2': {'outlet_id': 'AA2', 'outlet_name': 'Master_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA3 Master_Outlet_3': {'outlet_id': 'AA3', 'outlet_name': 'Master_Outlet_3', 'state': '1', 'status': '22', 'current': '27', 'voltage': '2073', 'active_power': '48', 'apparent_power': '55'},
            'Outlet BA1 Link1_Outlet_1': {'outlet_id': 'BA1', 'outlet_name': 'Link1_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2064', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA2 Link1_Outlet_2': {'outlet_id': 'BA2', 'outlet_name': 'Link1_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA3 Link1_Outlet_3': {'outlet_id': 'BA3', 'outlet_name': 'Link1_Outlet_3', 'state': '1', 'status': '0', 'current': '28', 'voltage': '2058', 'active_power': '52', 'apparent_power': '58'}
        },
        [Metric('current', 0.27), Metric('voltage', 207.3), Metric('power', 48), Metric('appower', 55), Result(state=State.WARN, summary='Status: profileError(22) State: on(1)')]
    ),
    (
        'Outlet AA3 Master_Outlet_3',
        {
            'Outlet AA1 Master_Outlet_1': {'outlet_id': 'AA1', 'outlet_name': 'Master_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2072', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA2 Master_Outlet_2': {'outlet_id': 'AA2', 'outlet_name': 'Master_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA3 Master_Outlet_3': {'outlet_id': 'AA3', 'outlet_name': 'Master_Outlet_3', 'state': '1', 'status': '20', 'current': '27', 'voltage': '2073', 'active_power': '48', 'apparent_power': '55'},
            'Outlet BA1 Link1_Outlet_1': {'outlet_id': 'BA1', 'outlet_name': 'Link1_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2064', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA2 Link1_Outlet_2': {'outlet_id': 'BA2', 'outlet_name': 'Link1_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA3 Link1_Outlet_3': {'outlet_id': 'BA3', 'outlet_name': 'Link1_Outlet_3', 'state': '1', 'status': '0', 'current': '28', 'voltage': '2058', 'active_power': '52', 'apparent_power': '58'}
        },
        [Metric('current', 0.27), Metric('voltage', 207.3), Metric('power', 48), Metric('appower', 55), Result(state=State.CRIT, summary='Status: overLimit(20) State: on(1)')]
    ),
    (
        'Outlet AA1 Master_Outlet_1',
        {
            'Outlet AA1 Master_Outlet_1': {'outlet_id': 'AA1', 'outlet_name': 'Master_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2072', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA2 Master_Outlet_2': {'outlet_id': 'AA2', 'outlet_name': 'Master_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet AA3 Master_Outlet_3': {'outlet_id': 'AA3', 'outlet_name': 'Master_Outlet_3', 'state': '1', 'status': '0', 'current': '27', 'voltage': '2073', 'active_power': '48', 'apparent_power': '55'},
            'Outlet BA1 Link1_Outlet_1': {'outlet_id': 'BA1', 'outlet_name': 'Link1_Outlet_1', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2064', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA2 Link1_Outlet_2': {'outlet_id': 'BA2', 'outlet_name': 'Link1_Outlet_2', 'state': '1', 'status': '0', 'current': '0', 'voltage': '2068', 'active_power': '0', 'apparent_power': '0'},
            'Outlet BA3 Link1_Outlet_3': {'outlet_id': 'BA3', 'outlet_name': 'Link1_Outlet_3', 'state': '1', 'status': '0', 'current': '28', 'voltage': '2058', 'active_power': '52', 'apparent_power': '58'}
        },
        [Metric('current', 0.0), Metric('voltage', 207.2), Metric('power', 0), Metric('appower', 0), Result(state=State.OK, summary='Status: normal(0) State: on(1)')]
    ),
])
def test_check_sentry4_pdu_outlet(monkeypatch, item, section, result):
    assert list(sentry4_pdu_outlet.check_sentry4_pdu_outlet(item, section)) == result
