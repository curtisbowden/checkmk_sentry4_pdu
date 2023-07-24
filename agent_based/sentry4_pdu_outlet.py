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
# Sentry4-MIB::st4OutletID.1.1.1 = STRING: AA1
# Sentry4-MIB::st4OutletID.2.1.1 = STRING: BA1
# Sentry4-MIB::st4OutletName.1.1.1 = STRING: CONSOLE3_POWER1
# Sentry4-MIB::st4OutletName.2.1.1 = STRING: CONSOLE3_POWER2
# Sentry4-MIB::st4OutletState.1.1.1 = INTEGER: on(1)
# Sentry4-MIB::st4OutletState.2.1.1 = INTEGER: on(1)
# Sentry4-MIB::st4OutletStatus.1.1.1 = INTEGER: normal(0)
# Sentry4-MIB::st4OutletStatus.2.1.1 = INTEGER: normal(0)
# Sentry4-MIB::st4OutletCurrent.1.1.1 = INTEGER: 0 hundredth Amps
# Sentry4-MIB::st4OutletCurrent.2.1.1 = INTEGER: 0 hundredth Amps
# Sentry4-MIB::st4OutletCurrentStatus.1.1.1 = INTEGER: normal(0)
# Sentry4-MIB::st4OutletCurrentStatus.2.1.1 = INTEGER: normal(0)
# Sentry4-MIB::st4OutletCurrentUtilized.1.1.1 = INTEGER: 0 tenth percent
# Sentry4-MIB::st4OutletCurrentUtilized.2.1.1 = INTEGER: 0 tenth percent
# Sentry4-MIB::st4OutletVoltage.1.1.1 = INTEGER: 2073 tenth Volts
# Sentry4-MIB::st4OutletVoltage.2.1.1 = INTEGER: 2066 tenth Volts
# Sentry4-MIB::st4OutletActivePower.1.1.1 = INTEGER: 0 Watts
# Sentry4-MIB::st4OutletActivePower.2.1.1 = INTEGER: 0 Watts
# Sentry4-MIB::st4OutletActivePowerStatus.1.1.1 = INTEGER: normal(0)
# Sentry4-MIB::st4OutletActivePowerStatus.2.1.1 = INTEGER: normal(0)
# Sentry4-MIB::st4OutletApparentPower.1.1.1 = INTEGER: 0 Volt-Amps
# Sentry4-MIB::st4OutletApparentPower.2.1.1 = INTEGER: 0 Volt-Amps
# Sentry4-MIB::st4OutletPowerFactor.1.1.1 = INTEGER: -1 hundredths
# Sentry4-MIB::st4OutletPowerFactor.2.1.1 = INTEGER: -1 hundredths
# Sentry4-MIB::st4OutletPowerFactorStatus.1.1.1 = INTEGER: normal(0)
# Sentry4-MIB::st4OutletPowerFactorStatus.2.1.1 = INTEGER: normal(0)
# Sentry4-MIB::st4OutletCurrentCrestFactor.1.1.1 = INTEGER: -1 tenths
# Sentry4-MIB::st4OutletCurrentCrestFactor.2.1.1 = INTEGER: -1 tenths
# Sentry4-MIB::st4OutletReactance.1.1.1 = INTEGER: unknown(0)
# Sentry4-MIB::st4OutletReactance.2.1.1 = INTEGER: unknown(0)
# Sentry4-MIB::st4OutletEnergy.1.1.1 = INTEGER: 2 Watt-Hours
# Sentry4-MIB::st4OutletEnergy.2.1.1 = INTEGER: 0 Watt-Hours


from .agent_based_api.v1 import (
    register,
    SNMPTree,
    exists,
    Service,
    Result,
    State,
    Metric,
)


def parse_sentry4_pdu_outlet(string_table):

    parsed = {}

    for (outlet_id, outlet_name, state, status, current, voltage, active_power, apparent_power) in string_table:

        outlet = f"Outlet {outlet_id} {outlet_name}"

        if (outlet not in parsed):
            parsed[outlet] = {}

        parsed[outlet]['outlet_id'] = outlet_id
        parsed[outlet]['outlet_name'] = outlet_name
        parsed[outlet]['state'] = state
        parsed[outlet]['status'] = status
        parsed[outlet]['current'] = current
        parsed[outlet]['voltage'] = voltage
        parsed[outlet]['active_power'] = active_power
        parsed[outlet]['apparent_power'] = apparent_power

    return parsed


register.snmp_section(
    name='sentry4_pdu_outlet',
    detect=exists('.1.3.6.1.4.1.1718.4.1.1.1.1.0'),
    fetch=SNMPTree(
        base='.1.3.6.1.4.1.1718.4.1.8',  # Sentry4-MIB::st4Outlets
        oids=[
            '2.1.2',  # Sentry4-MIB::st4OutletID
            '2.1.3',  # Sentry4-MIB::st4OutletName
            '3.1.1',  # Sentry4-MIB::st4OutletState
            '3.1.2',  # Sentry4-MIB::st4OutletStatus
            '3.1.3',  # Sentry4-MIB::st4OutletCurrent
            '3.1.6',  # Sentry4-MIB::st4OutletVoltage
            '3.1.7',  # Sentry4-MIB::st4OutletActivePower
            '3.1.9',  # Sentry4-MIB::st4OutletApparentPower
        ],
    ),
    parse_function=parse_sentry4_pdu_outlet,
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


def discover_sentry4_pdu_outlet(section):
    for service in section.keys():
        yield Service(item=service)


def check_sentry4_pdu_outlet(item, section):
    if item not in section:
        return

    state = int(section[item]['state'])
    status = int(section[item]['status'])
    current = int(section[item]['current']) / 100
    voltage = int(section[item]['voltage']) / 10
    power = int(section[item]['active_power'])
    appower = int(section[item]['apparent_power'])

    summary = f"Status: {SERVICE_STATUS_MAP[status]}({status}) State: {SERVICE_STATE_MAP[state]}({state})"

    yield Metric('current', current)
    yield Metric('voltage', voltage)
    yield Metric('power', power)
    yield Metric('appower', appower)

    if (status in [0, 1]) and (state in [1, 2]):
        yield Result(state=State.OK, summary=summary)

    elif (status in [2, 5, 6, 7, 9, 15, 16, 21, 22, 23]) or (state == 0):
        yield Result(state=State.WARN, summary=summary)

    else:
        yield Result(state=State.CRIT, summary=summary)


register.check_plugin(
    name='sentry4_pdu_outlet',
    service_name='%s',
    discovery_function=discover_sentry4_pdu_outlet,
    check_function=check_sentry4_pdu_outlet,
)
