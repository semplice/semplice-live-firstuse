#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# semplice-live-firstuse - First use tool for Semplice Live
# Copyright (C) 2014  Semplice Project
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Authors:
#    Eugenio "g7" Paolantonio <me@medesimo.eu>
#

from distutils.core import setup

setup(
	name='semplice-live-firstuse',
	version='0.23',
	description='First use tool for Semplice Live',
	author='Eugenio Paolantonio',
	author_email='me@medesimo.eu',
	url='https://github.com/semplice/semplice-live-firstuse',
	scripts=['semplice-live-firstuse.py'],
	data_files=(
		("/usr/share/semplice-live-firstuse", ("firstuse.ui",)),
		("/usr/share/vera/autostart", ("extra/semplice-live-firstuse.desktop",)),
	),
	requires=[
		'os',
		'sys',
		'gi.repository.Gtk',
		'gi.repository.GObject',
		'gi.repository.Pango'
		'quickstart',
		'keeptalking',
	],
)
