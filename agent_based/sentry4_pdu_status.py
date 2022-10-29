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

from .agent_based_api.v1 import (
    register,
    SNMPTree,
    exists,
    Service,
    Result,
    State,
)

def parse_sentry4_pdu_status(string_table):

    parsed = {}

    for (unit_id, unit_name, unit_sn, unit_model, unit_type, unit_status) in string_table:
        unit = f"Sentry PDU status: {unit_name}"

        if( unit not in parsed):
            parsed[unit] = {}

        parsed[unit]['Unit'] = unit_id
        parsed[unit]['Name'] = unit_name
        parsed[unit]['SN'] = unit_sn
        parsed[unit]['Model'] = unit_model
        parsed[unit]['Type'] = unit_type
        parsed[unit]['Status'] = unit_status

    return parsed

register.snmp_section(
    name='sentry4_pdu_status',
    detect=exists('.1.3.6.1.4.1.1718.4.1.1.1.1.0'),
    fetch=SNMPTree(
        base='.1.3.6.1.4.1.1718.4.1.2',
        oids=[
            '2.1.2', # Sentry4-MIB::st4UnitID
            '2.1.3', # Sentry4-MIB::st4UnitName
            '2.1.4', # Sentry4-MIB::st4UnitProductSN
            '2.1.5', # Sentry4-MIB::st4UnitModel
            '2.1.7', # Sentry4-MIB::st4UnitType
            '3.1.1', # Sentry4-MIB::st4UnitStatus
        ],
    ),
    parse_function=parse_sentry4_pdu_status,
)

SERVICE_STATE_MAP = {
    0: 'normal',         # operating properly (OK)
    1: 'disabled',       # disabled (OK)
    2: 'purged',         # purged (WARN)
    5: 'reading',        # read in process (WARN)
    6: 'settle',         # is settling (WARN)
    7: 'notFound',       # never connected (WARN)
    8: 'lost',           # disconnected (CRIT)
    9: 'readError',      # read failure (WARN)
    10: 'noComm',        # unreachable (CRIT)
    11: 'pwrError',      # power detection error (CRIT)
    12: 'breakerTripped',# breaker error (CRIT)
    13: 'fuseBlown',     # fuse error (CRIT)
    14: 'lowAlarm',      # under low alarm threshold (CRIT)
    15: 'lowWarning',    # under low warning threshold (WARN)
    16: 'highWarning',   # over high warning threshold (WARN)
    17: 'highAlarm',     # over high alarm threshold (CRIT)
    18: 'alarm',         # general alarm (CRIT)
    19: 'underLimit',    # under limit alarm (CRIT)
    20: 'overLimit',     # over limit alarm (CRIT)
    21: 'nvmFail',       # NVM failure (WARN)
    22: 'profileError',  # profile error (WARN)
    23: 'conflict',      # conflict (WARN)
}

UNIT_TYPE_MAP = {
    0: 'masterPdu',      # master
    1: 'linkPdu',        # link
    2: 'controller',     # controller
    3: 'emcu',           # emcu
}

def discover_sentry4_pdu_status(section):
    for service in section.keys():
        yield Service(item=service)

def check_sentry4_pdu_status(item, section):
    if item not in section:
        return

    status = int(section[item]['Status'])
    type = int(section[item]['Type'])

    summary = ''

    for (key,value) in section[item].items():
        if(key == 'Status' and value != ''):
            summary = f"{key}: {SERVICE_STATE_MAP[status]}({value}), {summary}"
        elif(key == 'Type' and value != ''):
            summary += f"{key}: {UNIT_TYPE_MAP[type]}({value})"
        elif value != '':
            summary += f"{key}: {value}, "
        else:
            continue

    if status == 0 or status == 1:
        yield Result(state=State.OK, summary=summary)
    elif status == 2 or \
         status == 5 or \
         status == 6 or \
         status == 7 or \
         status == 9 or \
         status == 15 or \
         status == 16 or \
         status == 21 or \
         status == 22 or \
         status == 23:
        yield Result(state=State.WARN, summary=summary)
    else:
        yield Result(state=State.CRIT, summary=summary)

    print(summary)


register.check_plugin(
    name='sentry4_pdu_status',
    service_name='%s',
    discovery_function=discover_sentry4_pdu_status,
    check_function=check_sentry4_pdu_status,
)
