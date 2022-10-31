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
#
# Sentry4-MIB::st4HumidSensorID.1.1 = STRING: A1
# Sentry4-MIB::st4HumidSensorID.5.1 = STRING: E1
# Sentry4-MIB::st4HumidSensorName.1.1 = STRING: Humid_Sensor_A1
# Sentry4-MIB::st4HumidSensorName.5.1 = STRING: HVAC_1_output
# Sentry4-MIB::st4HumidSensorValue.1.1 = INTEGER: -1 percentage relative humidity
# Sentry4-MIB::st4HumidSensorValue.5.1 = INTEGER: 70 percentage relative humidity
# Sentry4-MIB::st4HumidSensorStatus.1.1 = INTEGER: notFound(7)
# Sentry4-MIB::st4HumidSensorStatus.5.1 = INTEGER: normal(0)
# Sentry4-MIB::st4HumidSensorLowAlarm.1.1 = INTEGER: 5 percentage relative humidity
# Sentry4-MIB::st4HumidSensorLowAlarm.5.1 = INTEGER: 5 percentage relative humidity
# Sentry4-MIB::st4HumidSensorLowWarning.1.1 = INTEGER: 10 percentage relative humidity
# Sentry4-MIB::st4HumidSensorLowWarning.5.1 = INTEGER: 10 percentage relative humidity
# Sentry4-MIB::st4HumidSensorHighWarning.1.1 = INTEGER: 90 percentage relative humidity
# Sentry4-MIB::st4HumidSensorHighWarning.5.1 = INTEGER: 90 percentage relative humidity
# Sentry4-MIB::st4HumidSensorHighAlarm.1.1 = INTEGER: 95 percentage relative humidity
# Sentry4-MIB::st4HumidSensorHighAlarm.5.1 = INTEGER: 95 percentage relative humidity


from .agent_based_api.v1 import (
    register,
    SNMPTree,
    exists,
    Service,
    Result,
    State,
    Metric,
)


def parse_sentry4_pdu_humid(string_table):

    parsed = {}

    for (sensor_id, name, value, status, low_alarm, low_warning, high_warning, high_alarm) in string_table:

        if (int(value) != -1):
            item = f"Humidity {sensor_id} {name}"
            parsed[item] = {}
            parsed[item]['value'] = int(value)
            parsed[item]['status'] = int(status)
            parsed[item]['low_alarm'] = int(low_alarm)
            parsed[item]['low_warning'] = int(low_warning)
            parsed[item]['high_warning'] = int(high_warning)
            parsed[item]['high_alarm'] = int(high_alarm)

    return parsed


register.snmp_section(
    name='sentry4_pdu_humid',
    detect=exists('.1.3.6.1.4.1.1718.4.1.1.1.1.0'),
    fetch=SNMPTree(
        base='.1.3.6.1.4.1.1718.4.1.10',  # Sentry4-MIB::st4HumiditySensors
        oids=[
            '2.1.2',  # Sentry4-MIB::st4HumidSensorID
            '2.1.3',  # Sentry4-MIB::st4HumidSensorName
            '3.1.1',  # Sentry4-MIB::st4HumidSensorValue
            '3.1.2',  # Sentry4-MIB::st4HumidSensorStatus
            '4.1.2',  # Sentry4-MIB::st4HumidSensorLowAlarm
            '4.1.3',  # Sentry4-MIB::st4HumidSensorLowWarning
            '4.1.4',  # Sentry4-MIB::st4HumidSensorHighWarning
            '4.1.5',  # Sentry4-MIB::st4HumidSensorHighAlarm
        ],
    ),
    parse_function=parse_sentry4_pdu_humid,
)


def discover_sentry4_pdu_humid(section):
    for service in section.keys():
        yield Service(item=service)


def check_sentry4_pdu_humid(item, params, section):
    if item not in section:
        return

    low_alarm = 0.0
    low_warning = 0.0
    high_warning = 0.0
    high_alarm = 0.0

    if 'levels_lower' in params:
        low_alarm = params['levels_lower'][1]
        low_warning = params['levels_lower'][0]
    else:
        low_alarm = float(section[item]['low_alarm'])
        low_warning = float(section[item]['low_warning'])

    if 'levels' in params:
        high_warning = params['levels'][0]
        high_alarm = params['levels'][1]
    else:
        high_warning = float(section[item]['high_warning'])
        high_alarm = float(section[item]['high_alarm'])

    details = f"High alarm:{high_alarm}, High warning:{high_warning}, Low warning:{low_warning}, Low alarm:{low_alarm}"

    if section[item]['status'] == 0:

        humid = section[item]['value']

        summary = f"{humid}%"

        yield Metric('humidity', humid, levels=(high_warning, high_alarm))

        if humid <= low_alarm:
            yield Result(state=State.CRIT, summary=f"{summary} is below critical threshold", details=details)

        elif humid >= high_alarm:
            yield Result(state=State.CRIT, summary=f"{summary} is above critical threshold", details=details)

        elif humid >= high_warning:
            yield Result(state=State.WARN, summary=f"{summary} is above warning threshold", details=details)

        elif humid <= low_warning:
            yield Result(state=State.WARN, summary=f"{summary} is below warning threshold", details=details)

        else:
            yield Result(state=State.OK, summary=summary, details=details)

    else:
        yield Result(state=State.CRIT, summary='Humidity sensor error')


register.check_plugin(
    name='sentry4_pdu_humid',
    service_name='%s',
    discovery_function=discover_sentry4_pdu_humid,
    check_function=check_sentry4_pdu_humid,
    check_default_parameters={},
    check_ruleset_name='humidity',
)
