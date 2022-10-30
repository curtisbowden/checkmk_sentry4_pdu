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


from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import (
    metric_info,
    graph_info,
)

metric_info['sentry4_temp'] = {
    'title': _('Temperature'),
    'unit': 'c',
    'color': '16/a',
}


graph_info['sentry4_temp'] = {
    'metrics': [
        ('sentry4_temp', "area"),
    ],
    "scalars": [
        "sentry4_temp:warn",
        "sentry4_temp:crit",
    ]
}
