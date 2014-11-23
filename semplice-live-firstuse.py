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

import os, sys

import subprocess

from keeptalking2.Locale import Locale
from keeptalking2.Keyboard import Keyboard
from keeptalking2.TimeZone import TimeZone
from keeptalking2.Live import Live

from gi.repository import Gtk, GObject, Pango
import quickstart

loc = Locale()
keyboard = Keyboard()
timezone = TimeZone()
tzone_countries = timezone.associate_timezones_to_countries()
live = Live()

if os.path.islink(__file__):
	# If we are a link, everything is a WTF...
	MAINDIR = os.path.dirname(os.path.normpath(os.path.join(os.path.dirname(__file__), os.readlink(__file__))))
else:
	MAINDIR = os.path.dirname(__file__)

# While the following is not ideal, is currently needed to make sure
# we are actually on the main semplice-live-firstuse directory.
# The main executable (this) and all modules do not use absolute paths
# to load the glade UI files, so we need to be on the main directory
# otherwise they will crash.
# This should be probably addressed directly in quickstart.builder but,
# for now, this chdir call will do the job.
os.chdir(MAINDIR)

def setxkbmap():
	"""
	Invokes setxkbmap and sets the currently selected layout, variant
	and model.
	"""
	
	subprocess.call(
		[
			"setxkbmap",
			keyboard.default_layout,
			keyboard.default_variant if keyboard.default_variant else "",
			"-model" if keyboard.default_model else "",
			keyboard.default_model if keyboard.default_model else ""
		]
	)

@quickstart.builder.from_file("./firstuse.ui")
class UI:
	"""
	The main User Interface.
	"""
	
	events = {
		"destroy" : ("main",),
		"clicked" : ("go_ahead",),
		"toggled" : ("show_all",),
	}

	def get_selected_locale(self):
		"""
		Returns the currently selected locale.
		"""
		
		# selection
		sel = self.objects.locale_view.get_selection()
		if not sel: return None
		
		# iter
		model, itr = sel.get_selected()
		if not itr: return None
		
		return self.objects.locales.get_value(itr, 0)
	
	def guess_keyboard_and_timezone(self, locale):
		"""
		Guesses the keyboard and timezone from the locale given.
		"""
		
		# keyboard layout!
		lay = locale.split(".")[0].split("@")[0].split("_")[1].lower()
		
		# variant too
		var = locale.split(".")[0].split("@")[0].split("_")[0].lower()

		# timezone
		tzone = locale.split(".")[0].split("@")[0].split("_")[1].upper()
		if tzone in tzone_countries:
			tzone = tzone_countries[tzone]
		else:
			tzone = None
		
		return (lay, var, tzone)
	
	@quickstart.threads.thread
	def apply(self, locale, layout, variant, tzone):
		"""
		Applies the settings.
		"""
		
		# Live set
		live.set()
		
		# Locale
		print("Locale: %s" % locale)
		loc.set(locale)
		
		# Layout
		print("Keyboard layout: %s" % layout)
		print("Keyboard variant %s" % variant)
				
		if keyboard.is_supported(layout):
			if not variant in keyboard.supported_variants(layout):
				variant = None
			
			keyboard.set(layout=layout, model=None, variant=variant)
					
		# Timezone
		print("Timezone: %s" % tzone)
		timezone.set(tzone)
		
		# Restart login manager
		subprocess.call(["systemctl", "restart", "lightdm"])
		
		# Exit
		Gtk.main_quit();
	
	def on_main_destroy(self, window):
		"""
		Fired when the user presses the 'X' button.
		"""
		
		Gtk.main_quit()
	
	def on_go_ahead_clicked(self, button):
		"""
		Fired when the 'Continue' button has been clicked.
		"""
		
		selected = self.get_selected_locale()
		
		lay, var, tzone = self.guess_keyboard_and_timezone(selected)
		
		# set sensitiveness
		self.objects.main.set_sensitive(False)
		
		# Apply, finally!
		self.apply(selected, lay, var, tzone)
	
	def on_show_all_toggled(self, checkbutton):
		"""
		Fired when the 'Show all locales' checkbutton has been clicked.
		"""
		
		GObject.idle_add(self.build_locale_list, self.objects.show_all.get_active())
	
	def build_locale_list(self, all=False):
		"""
		Populates the listbox with locales.
		"""
		
		self.objects.locales.clear()
		
		default = None
		
		for locale, human in loc.human_form(all=all).items():
			if all:
				codepage = loc.codepages[locale]
			else:
				codepage = ""
			itr = self.objects.locales.append((locale, human, codepage))
			
			# Save iter if this is the default...
			if locale == loc.default:
				default = itr
		
		if default:
			sel = self.objects.locale_view.get_selection()
			sel.select_iter(default)
						
			GObject.idle_add(self.objects.locale_view.scroll_to_cell, sel.get_selected_rows()[1][0])
	
	def __init__(self):
		"""
		Intialization.
		"""
		
		self.locales = {}
		
		# Style
		#settings = Gtk.Settings.get_default()
		#settings.set_property("gtk-application-prefer-dark-theme", True)
		
		# Font style
		#font_desc = Pango.FontDescription.from_string(", , 14")
		#font_desc.set_weight(Pango.Weight.LIGHT)
		
		# Make the locale_view treeview working...
		locale_renderer = Gtk.CellRendererText()
		#locale_renderer.set_property("font-desc", font_desc)
		self.locale_column = Gtk.TreeViewColumn("Locale", locale_renderer, text=1)
		self.objects.locales.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		self.objects.locale_view.append_column(self.locale_column)
		
		type_renderer = Gtk.CellRendererText()
		#type_renderer.set_property("font-desc", font_desc)
		self.type_column = Gtk.TreeViewColumn("Type", type_renderer, text=2)
		self.objects.locale_view.append_column(self.type_column)
		
		# Populate the locale list
		GObject.idle_add(self.build_locale_list)
		
		# Focus
		self.objects.locale_view.grab_focus()
		
		# Fullscreen
		#self.objects.main.fullscreen()
		
		self.objects.main.show_all()

if __name__ == "__main__":

	if live.is_live:

		# Check for root
		if os.getuid() > 0:
			sys.stderr.write("You must be root to use this application!\n")
			sys.exit(1)
		
		if not live.skip_live:
			quickstart.common.quickstart(UI)
			
		
		live.set()
	else:
		# Forcibily set the keyboard layout that have been previously set by this very
		# same application.
		# Unfortunately even after restarting lightdm the new keyboard layout is not
		# picked up, so we need to workaround with setxkbmap.
		setxkbmap()
