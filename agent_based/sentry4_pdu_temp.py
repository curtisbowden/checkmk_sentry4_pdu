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
# Sentry4-MIB::st4TempSensorHysteresis.0 = INTEGER: 1 degrees
# Sentry4-MIB::st4TempSensorScale.0 = INTEGER: celsius(0)
# Sentry4-MIB::st4TempSensorID.1.1 = STRING: A1
# Sentry4-MIB::st4TempSensorID.5.1 = STRING: E1
# Sentry4-MIB::st4TempSensorName.1.1 = STRING: Temp_Sensor_A1
# Sentry4-MIB::st4TempSensorName.5.1 = STRING: HVAC_1_output
# Sentry4-MIB::st4TempSensorValueMin.1.1 = INTEGER: -40 degrees
# Sentry4-MIB::st4TempSensorValueMin.5.1 = INTEGER: -40 degrees
# Sentry4-MIB::st4TempSensorValueMax.1.1 = INTEGER: 123 degrees
# Sentry4-MIB::st4TempSensorValueMax.5.1 = INTEGER: 123 degrees
# Sentry4-MIB::st4TempSensorValue.1.1 = INTEGER: -410 tenth degrees
# Sentry4-MIB::st4TempSensorValue.5.1 = INTEGER: 150 tenth degrees
# Sentry4-MIB::st4TempSensorStatus.1.1 = INTEGER: notFound(7)
# Sentry4-MIB::st4TempSensorStatus.5.1 = INTEGER: normal(0)
# Sentry4-MIB::st4TempSensorNotifications.1.1 = BITS: C0 snmpTrap(0) email(1)
# Sentry4-MIB::st4TempSensorNotifications.5.1 = BITS: C0 snmpTrap(0) email(1)
# Sentry4-MIB::st4TempSensorLowAlarm.1.1 = INTEGER: 1 degrees
# Sentry4-MIB::st4TempSensorLowAlarm.5.1 = INTEGER: 1 degrees
# Sentry4-MIB::st4TempSensorLowWarning.1.1 = INTEGER: 5 degrees
# Sentry4-MIB::st4TempSensorLowWarning.5.1 = INTEGER: 5 degrees
# Sentry4-MIB::st4TempSensorHighWarning.1.1 = INTEGER: 45 degrees
# Sentry4-MIB::st4TempSensorHighWarning.5.1 = INTEGER: 45 degrees
# Sentry4-MIB::st4TempSensorHighAlarm.1.1 = INTEGER: 50 degrees
# Sentry4-MIB::st4TempSensorHighAlarm.5.1 = INTEGER: 50 degrees


from .agent_based_api.v1 import (
    register,
    SNMPTree,
    exists,
    Service,
    Result,
    State,
    Metric,
)


def convert_farenheit_to_celsius(f):
    c = (f - 32) * 5 / 9
    return c


def parse_sentry4_pdu_temp(string_table):

    parsed = {}
    unit = ''

    for (scale, sensor_id, name, value, status, low_alarm, low_warning, high_warning, high_alarm) in string_table:

        if scale != '':
            unit = scale

        if (unit == '0'):
            if (value != '' and int(value) != -410):
                item = f"Temperature {sensor_id} {name}"
                parsed[item] = {}
                parsed[item]['value'] = float(int(value) / 10)
                parsed[item]['status'] = int(status)
                parsed[item]['low_alarm'] = int(low_alarm)
                parsed[item]['low_warning'] = int(low_warning)
                parsed[item]['high_warning'] = int(high_warning)
                parsed[item]['high_alarm'] = int(high_alarm)
        else:
            if (value != '' and int(value) != -706):
                item = f"Temperature {sensor_id} {name}"
                parsed[item] = {}
                parsed[item]['value'] = float(convert_farenheit_to_celsius(int(value) / 10))
                parsed[item]['status'] = int(status)
                parsed[item]['low_alarm'] = int(convert_farenheit_to_celsius(int(low_alarm)))
                parsed[item]['low_warning'] = int(convert_farenheit_to_celsius(int(low_warning)))
                parsed[item]['high_warning'] = int(convert_farenheit_to_celsius(int(high_warning)))
                parsed[item]['high_alarm'] = int(convert_farenheit_to_celsius(int(high_alarm)))

    return parsed


register.snmp_section(
    name='sentry4_pdu_temp',
    detect=exists('.1.3.6.1.4.1.1718.4.1.1.1.1.0'),
    fetch=SNMPTree(
        base='.1.3.6.1.4.1.1718.4.1.9',  # Sentry4-MIB::st4TemperatureSensors
        oids=[
            '1.10',   # Sentry4-MIB::st4TempSensorScale
            '2.1.2',  # Sentry4-MIB::st4TempSensorID
            '2.1.3',  # Sentry4-MIB::st4TempSensorName
            '3.1.1',  # Sentry4-MIB::st4TempSensorValue
            '3.1.2',  # Sentry4-MIB::st4TempSensorStatus
            '4.1.2',  # Sentry4-MIB::st4TempSensorLowAlarm
            '4.1.3',  # Sentry4-MIB::st4TempSensorLowWarning
            '4.1.4',  # Sentry4-MIB::st4TempSensorHighWarning
            '4.1.5',  # Sentry4-MIB::st4TempSensorHighAlarm
        ],
    ),
    parse_function=parse_sentry4_pdu_temp,
)


def discover_sentry4_pdu_temp(section):
    for service in section.keys():
        yield Service(item=service)


def check_sentry4_pdu_temp(item, params, section):
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

        temp = section[item]['value']

        if 'output_unit' in params and params['output_unit'] == 'f':
            f_temp = (temp * 9 / 5) + 32
            summary = f"{f_temp} °F"
        elif 'output_unit' in params and params['output_unit'] == 'k':
            k_temp = temp + 273.15
            summary = f"{k_temp} K"
        else:
            summary = f"{temp} °C"

        yield Metric('sentry4_temp', temp, levels=(high_warning, high_alarm))

        if temp <= low_alarm:
            yield Result(state=State.CRIT, summary=f"{summary} is below critical threshold", details=details)

        elif temp >= high_alarm:
            yield Result(state=State.CRIT, summary=f"{summary} is above critical threshold", details=details)

        elif temp >= high_warning:
            yield Result(state=State.WARN, summary=f"{summary} is above warning threshold", details=details)

        elif temp <= low_warning:
            yield Result(state=State.WARN, summary=f"{summary} is below warning threshold", details=details)

        else:
            yield Result(state=State.OK, summary=summary, details=details)

    else:
        yield Result(state=State.CRIT, summary='Temperature sensor error')


register.check_plugin(
    name='sentry4_pdu_temp',
    service_name='%s',
    discovery_function=discover_sentry4_pdu_temp,
    check_function=check_sentry4_pdu_temp,
    check_default_parameters={},
    check_ruleset_name='temperature',
)
