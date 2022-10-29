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
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import sentry4_pdu_status


@pytest.mark.parametrize('string_table, result', [
    (
        [['A', 'Master', 'ABCD0000001', 'C2WG36TE-YQME2M66/C', '0', '0'], ['B', 'Link1', 'ABCD0000002', 'C2XG36TE-YQME2M66/C', '1', '0'], ['E', 'EMCU', '', 'EMCU-1-1B(C)', '3', '0']],
        {
            'Sentry PDU status: Master': {'Unit': 'A',
                                          'Name': 'Master',
                                          'SN': 'ABCD0000001',
                                          'Model': 'C2WG36TE-YQME2M66/C',
                                          'Status': '0',
                                          'Type': '0'},
            'Sentry PDU status: Link1': {'Unit': 'B',
                                         'Name': 'Link1',
                                         'SN': 'ABCD0000002',
                                         'Model': 'C2XG36TE-YQME2M66/C',
                                         'Type': '1',
                                         'Status': '0'},
            'Sentry PDU status: EMCU': {'Unit': 'E',
                                        'Name': 'EMCU',
                                        'SN': '',
                                        'Model': 'EMCU-1-1B(C)',
                                        'Type': '3',
                                        'Status': '0'}
        },

    ),
])
def test_parse_sentry4_pdu_status(string_table, result):
    assert sentry4_pdu_status.parse_sentry4_pdu_status(string_table) == result


@pytest.mark.parametrize('section, result', [
    (
        {
            'Sentry PDU status: Master': {'Unit': 'A',
                                          'Name': 'Master',
                                          'SN': 'ABCD0000001',
                                          'Model': 'C2WG36TE-YQME2M66/C',
                                          'Status': '0',
                                          'Type': '0'},
            'Sentry PDU status: Link1': {'Unit': 'B',
                                         'Name': 'Link1',
                                         'SN': 'ABCD0000002',
                                         'Model': 'C2XG36TE-YQME2M66/C',
                                         'Type': '1',
                                         'Status': '0'},
            'Sentry PDU status: EMCU': {'Unit': 'E',
                                        'Name': 'EMCU',
                                        'SN': '',
                                        'Model': 'EMCU-1-1B(C)',
                                        'Type': '3',
                                        'Status': '0'}
        },

        [Service(item='Sentry PDU status: Master'), Service(item='Sentry PDU status: Link1'), Service(item='Sentry PDU status: EMCU')]
    ),
])
def test_discover_sentry4_pdu_status(section, result):
    assert list(sentry4_pdu_status.discover_sentry4_pdu_status(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', {}, []),
    (
        'foo',
        {
            'Sentry PDU status: Master': {'Unit': 'A',
                                          'Name': 'Master',
                                          'SN': 'ABCD0000001',
                                          'Model': 'C2WG36TE-YQME2M66/C',
                                          'Status': '0',
                                          'Type': '0'},
            'Sentry PDU status: Link1': {'Unit': 'B',
                                         'Name': 'Link1',
                                         'SN': 'ABCD0000002',
                                         'Model': 'C2XG36TE-YQME2M66/C',
                                         'Type': '1',
                                         'Status': '0'},
            'Sentry PDU status: EMCU': {'Unit': 'E',
                                        'Name': 'EMCU',
                                        'SN': '',
                                        'Model': 'EMCU-1-1B(C)',
                                        'Type': '3',
                                        'Status': '0'}
        },

        []
    ),
    (
        'Sentry PDU status: Master',
        {
            'Sentry PDU status: Master': {'Unit': 'A',
                                          'Name': 'Master',
                                          'SN': 'ABCD0000001',
                                          'Model': 'C2WG36TE-YQME2M66/C',
                                          'Status': '0',
                                          'Type': '0'},
            'Sentry PDU status: Link1': {'Unit': 'B',
                                         'Name': 'Link1',
                                         'SN': 'ABCD0000002',
                                         'Model': 'C2XG36TE-YQME2M66/C',
                                         'Type': '1',
                                         'Status': '0'},
            'Sentry PDU status: EMCU': {'Unit': 'E',
                                        'Name': 'EMCU',
                                        'SN': '',
                                        'Model': 'EMCU-1-1B(C)',
                                        'Type': '3',
                                        'Status': '0'}
        },

        [Result(state=State.OK, summary='Status: normal(0), Unit: A, Name: Master, SN: ABCD0000001, Model: C2WG36TE-YQME2M66/C, Type: masterPdu(0)')]
    ),
    (
        'Sentry PDU status: Master',
        {
            'Sentry PDU status: Master': {'Unit': 'A',
                                          'Name': 'Master',
                                          'SN': 'ABCD0000001',
                                          'Model': 'C2WG36TE-YQME2M66/C',
                                          'Status': '2',
                                          'Type': '0'},
            'Sentry PDU status: Link1': {'Unit': 'B',
                                         'Name': 'Link1',
                                         'SN': 'ABCD0000002',
                                         'Model': 'C2XG36TE-YQME2M66/C',
                                         'Type': '1',
                                         'Status': '0'},
            'Sentry PDU status: EMCU': {'Unit': 'E',
                                        'Name': 'EMCU',
                                        'SN': '',
                                        'Model': 'EMCU-1-1B(C)',
                                        'Type': '3',
                                        'Status': '0'}
        },
        [Result(state=State.WARN, summary='Status: purged(2), Unit: A, Name: Master, SN: ABCD0000001, Model: C2WG36TE-YQME2M66/C, Type: masterPdu(0)')]
    ),
    (
        'Sentry PDU status: Link1',
        {
            'Sentry PDU status: Master': {'Unit': 'A',
                                          'Name': 'Master',
                                          'SN': 'ABCD0000001',
                                          'Model': 'C2WG36TE-YQME2M66/C',
                                          'Status': '2',
                                          'Type': '0'},
            'Sentry PDU status: Link1': {'Unit': 'B',
                                         'Name': 'Link1',
                                         'SN': 'ABCD0000002',
                                         'Model': 'C2XG36TE-YQME2M66/C',
                                         'Type': '1',
                                         'Status': '8'},
            'Sentry PDU status: EMCU': {'Unit': 'E',
                                        'Name': 'EMCU',
                                        'SN': '',
                                        'Model': 'EMCU-1-1B(C)',
                                        'Type': '3',
                                        'Status': '0'}
        },
        [Result(state=State.CRIT, summary='Status: lost(8), Unit: B, Name: Link1, SN: ABCD0000002, Model: C2XG36TE-YQME2M66/C, Type: linkPdu(1)')]
    ),
])
def test_check_sentry4_pdu_status(monkeypatch, item, section, result):
    assert list(sentry4_pdu_status.check_sentry4_pdu_status(item, section)) == result
