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
# Sentry4-MIB::st4InputCordID.1.1 = STRING: AA
# Sentry4-MIB::st4InputCordID.2.1 = STRING: BA
# Sentry4-MIB::st4InputCordName.1.1 = STRING: Master_UPS_A
# Sentry4-MIB::st4InputCordName.2.1 = STRING: Slave_UPS_B
# Sentry4-MIB::st4InputCordState.1.1 = INTEGER: on(1)
# Sentry4-MIB::st4InputCordState.2.1 = INTEGER: on(1)
# Sentry4-MIB::st4InputCordStatus.1.1 = INTEGER: normal(0)
# Sentry4-MIB::st4InputCordStatus.2.1 = INTEGER: normal(0)
# Sentry4-MIB::st4InputCordActivePower.1.1 = INTEGER: 888 Watts
# Sentry4-MIB::st4InputCordActivePower.2.1 = INTEGER: 919 Watts
# Sentry4-MIB::st4InputCordApparentPower.1.1 = INTEGER: 961 Volt-Amps
# Sentry4-MIB::st4InputCordApparentPower.2.1 = INTEGER: 992 Volt-Amps
# Sentry4-MIB::st4InputCordPowerUtilized.1.1 = INTEGER: 44 tenth percent
# Sentry4-MIB::st4InputCordPowerUtilized.2.1 = INTEGER: 45 tenth percent
# Sentry4-MIB::st4InputCordPowerFactor.1.1 = INTEGER: 92 hundredths
# Sentry4-MIB::st4InputCordPowerFactor.2.1 = INTEGER: 93 hundredths

from .agent_based_api.v1 import (
    register,
    SNMPTree,
    exists,
    Service,
    Result,
    State,
    Metric,
)


def parse_sentry4_pdu_inlet(string_table):

    parsed = {}

    for (cord_id, cord_name, state, status, active_power, apparent_power, power_utilized, power_factor) in string_table:

        cord = f"Input cord {cord_id} {cord_name}"

        if (cord not in parsed):
            parsed[cord] = {}

        parsed[cord]['cord_id'] = cord_id
        parsed[cord]['cord_name'] = cord_name
        parsed[cord]['state'] = state
        parsed[cord]['status'] = status
        parsed[cord]['active_power'] = active_power
        parsed[cord]['apparent_power'] = apparent_power
        parsed[cord]['power_utilized'] = power_utilized
        parsed[cord]['power_factor'] = power_factor

    return parsed


register.snmp_section(
    name='sentry4_pdu_inlet',
    detect=exists('.1.3.6.1.4.1.1718.4.1.1.1.1.0'),
    fetch=SNMPTree(
        base='.1.3.6.1.4.1.1718.4.1.3',  # Sentry4-MIB::st4InputCords
        oids=[
            '2.1.2',  # Sentry4-MIB::st4InputCordID
            '2.1.3',  # Sentry4-MIB::st4InputCordName
            '3.1.1',  # Sentry4-MIB::st4InputCordState
            '3.1.2',  # Sentry4-MIB::st4InputCordStatus
            '3.1.3',  # Sentry4-MIB::st4InputCordActivePower
            '3.1.5',  # Sentry4-MIB::st4InputCordApparentPower
            '3.1.7',  # Sentry4-MIB::st4InputCordPowerUtilized
            '3.1.8',  # Sentry4-MIB::st4InputCordPowerFactor
        ],
    ),
    parse_function=parse_sentry4_pdu_inlet,
)


SERVICE_STATE_MAP = {

    0: 'unknown',          # device on/off state is unknown (WARN)
    1: 'on',               # device is on (OK)
    2: 'off',              # device is off (OK)
}


SERVICE_STATUS_MAP = {
    0: 'normal',           # operating properly (OK)
    1: 'disabled',         # disabled (OK)
    2: 'purged',           # purged (WARN)
    5: 'reading',          # read in process (WARN)
    6: 'settle',           # is settling (WARN)
    7: 'notFound',         # never connected (WARN)
    8: 'lost',             # disconnected (CRIT)
    9: 'readError',        # read failure (WARN)
    10: 'noComm',          # unreachable (CRIT)
    11: 'pwrError',        # power detection error (CRIT)
    12: 'breakerTripped',  # breaker error (CRIT)
    13: 'fuseBlown',       # fuse error (CRIT)
    14: 'lowAlarm',        # under low alarm threshold (CRIT)
    15: 'lowWarning',      # under low warning threshold (WARN)
    16: 'highWarning',     # over high warning threshold (WARN)
    17: 'highAlarm',       # over high alarm threshold (CRIT)
    18: 'alarm',           # general alarm (CRIT)
    19: 'underLimit',      # under limit alarm (CRIT)
    20: 'overLimit',       # over limit alarm (CRIT)
    21: 'nvmFail',         # NVM failure (WARN)
    22: 'profileError',    # profile error (WARN)
    23: 'conflict',        # conflict (WARN)
}


def discover_sentry4_pdu_inlet(section):
    for service in section.keys():
        yield Service(item=service)


def check_sentry4_pdu_inlet(item, section):
    if item not in section:
        return

    state = int(section[item]['state'])
    status = int(section[item]['status'])
    power = int(section[item]['active_power'])
    appower = int(section[item]['apparent_power'])
    power_usage_percentage = int(section[item]['power_utilized'])

    summary = f"Status: {SERVICE_STATUS_MAP[status]}({status}) State: {SERVICE_STATE_MAP[state]}({state})"

    yield Metric('power', power)
    yield Metric('appower', appower)
    yield Metric('power_usage_percentage', power_usage_percentage)

    if (status in [0, 1]) and (state in [1, 2]):
        yield Result(state=State.OK, summary=summary)

    elif (status in [2, 5, 6, 7, 9, 15, 16, 21, 22, 23]) or (state == 0):
        yield Result(state=State.WARN, summary=summary)

    else:
        yield Result(state=State.CRIT, summary=summary)


register.check_plugin(
    name='sentry4_pdu_inlet',
    service_name='%s',
    discovery_function=discover_sentry4_pdu_inlet,
    check_function=check_sentry4_pdu_inlet,
)
