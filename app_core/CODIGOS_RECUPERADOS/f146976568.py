#!/usr/bin/python3

## system-config-printer

## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015 Red Hat, Inc.
## Authors:
##  Tim Waugh <twaugh@redhat.com>
##  Florian Festi <ffesti@redhat.com>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# config is generated from config.py.in by configure
import config

import authconn
import cupshelpers
from OpenPrintingRequest import OpenPrintingRequest

import errno
import sys, os, tempfile, time, re, http.client
import locale
import string
import subprocess
from timedops import *
import dbus
from gi.repository import Gdk
from gi.repository import Gtk
import functools

import cups

try:
    import pysmb
    PYSMB_AVAILABLE=True
except:
    PYSMB_AVAILABLE=False

import options
from gi.repository import GObject
from gi.repository import GLib
from gui import GtkGUI
from optionwidgets import OptionWidget
from debug import *
import probe_printer
import urllib.request, urllib.parse
from smburi import SMBURI
from errordialogs import *
from PhysicalDevice import PhysicalDevice
import firewallsettings
import asyncconn
import ppdsloader
import dnssdresolve
import installpackage

import gettext
gettext.install(domain=config.PACKAGE, localedir=config.localedir)

HTTPS_TIMEOUT = 15.0

TEXT_adjust_firewall = _("The firewall may need adjusting in order to "
                         "detect network printers.  Adjust the "
                         "firewall now?")

def validDeviceURI (uri):
    """Returns True is the provided URI is valid."""
    (scheme, rest) = urllib.parse.splittype (uri)
    if scheme is None or scheme == '':
        return False
    return True

# Both the printer properties window and the new printer window
# need to be able to drive 'class members' selections.
def moveClassMembers(treeview_from, treeview_to):
    selection = treeview_from.get_selection()
    model_from, rows = selection.get_selected_rows()
    rows = [Gtk.TreeRowReference.new(model_from, row) for row in rows]

    model_to = treeview_to.get_model()

    for row in rows:
        path = row.get_path()
        iter = model_from.get_iter(path)
        row_data = model_from.get(iter, 0)
        model_to.append(row_data)
        model_from.remove(iter)

def getCurrentClassMembers(treeview):
    model = treeview.get_model()
    iter = model.get_iter_first()
    result = []
    while iter:
        result.append(model.get(iter, 0)[0])
        iter = model.iter_next(iter)
    result.sort()
    return result

def checkNPName(printers, name):
    if not name: return False
    name = name.lower()
    for printer in printers.values():
        if not printer.discovered and printer.name.lower()==name:
            return False
    return True

def ready (win, cursor=None):
    try:
        gdkwin = win.get_window()
        if gdkwin:
            gdkwin.set_cursor (cursor)
            while Gtk.events_pending ():
                Gtk.main_iteration ()
    except:
        nonfatalException ()

def busy (win):
    ready (win, Gdk.Cursor.new(Gdk.CursorType.WATCH))

def on_delete_just_hide (widget, event):
    widget.hide ()
    return True # stop other handlers

def _singleton (x):
    """If we don't know whether getPPDs() or getPPDs2() was used, this
    function can unwrap an item from a list in either case."""
    if isinstance (x, list):
        return x[0]
    return x

def download_gpg_fingerprint(url):
    """Get GPG fingerprint from URL.

    Check that the URL is HTTPS with a valid and trusted server
    certificate, read it, extract the GPG fingerprint from it, and return
    it. Return None if the URL is invalid, not trusted, or the fingerprint
    can't be found.
    """
    if not url.startswith('https://'):
        debugprint('Not a https fingerprint URL: %s, ignoring driver' % url)
        return None

    content = None
    try:
        with urllib.request.urlopen(url, timeout=HTTPS_TIMEOUT) as resp:
            if resp.status == 200:
                content = resp.read().decode('utf-8')
    except Exception as e:
        debugprint('Cannot retrieve %s: %s' % (url, e))

    if content is None:
        debugprint('Cannot retrieve %s' % url)
        return None

    keyid_re = re.compile(r' ((?:(?:[0-9A-F]{4})(?:\s+|$)){10})$', re.M)

    m = keyid_re.search(content)
    if m:
        return m.group(1).strip().replace(' ','')

    return None

class NewPrinterGUI(GtkGUI):

    __gsignals__ = {
        'destroy':          (GObject.SignalFlags.RUN_LAST, None, ()),
        'printer-added' :   (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'printer-modified': (GObject.SignalFlags.RUN_LAST, None,
                             (str,    # printer name
                              bool,)), # PPD modified?
        'driver-download-checked': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'dialog-canceled':  (GObject.SignalFlags.RUN_LAST, None, ()),
        }

    # Page numbers used to name the different stages
    PAGE_DESCRIBE_PRINTER = 0
    PAGE_SELECT_DEVICE = 1
    PAGE_SELECT_INSTALL_METHOD = 2
    PAGE_CHOOSE_DRIVER_FROM_DB = 3
    PAGE_CHOOSE_CLASS_MEMBERS = 4
    PAGE_APPLY = 5
    PAGE_INSTALLABLE_OPTIONS = 6
    PAGE_DOWNLOAD_DRIVER = 7

    # Values returned by _handlePrinterInstallationMode() and
    # related sub-functions, to know whether to continue the
    # execution of the remaining logic from calling functions
    INSTALL_RESULT_DONE = True
    INSTALL_RESULT_OPS_PENDING = False

    new_printer_device_tabs = {
        "parallel" : 0, # empty tab
        "usb" : 0,
        "bluetooth" : 0,
        "hal" : 0,
        "beh" : 0,
        "hp" : 0,
        "hpfax" : 0,
        "dnssd" : 0,
        "socket": 2,
        "lpd" : 3,
        "scsi" : 4,
        "serial" : 5,
        "smb" : 6,
        "network": 7,
        }

    def __init__(self):
        GObject.GObject.__init__ (self)
        self.language = locale.getlocale (locale.LC_MESSAGES)

        self.options = {} # keyword -> Option object
        self.changed = set()
        self.conflicts = set()
        self.device = None
        self.ppd = None
        self.remotecupsqueue = False
        self.exactdrivermatch = False
        self.installable_options = False
        self.ppdsloader = None
        self.installed_driver_files = []
        self.searchedfordriverpackages = False
        self.founddownloadabledrivers = False
        self.founddownloadableppd = False
        self.downloadable_driver_for_printer = None
        self.downloadable_printers = []
        self.nextnptab_rerun = False
        self.printers = {} # set in init()
        self.recommended_model_selected = False
        self._searchdialog = None
        self._installdialog = None

        self.getWidgets({"NewPrinterWindow":
                             ["NewPrinterWindow",
                              "ntbkNewPrinter",
                              "btnNPBack",
                              "btnNPForward",
                              "btnNPApply",
                              "spinner",
                              "entNPName",
                              "entNPDescription",
                              "entNPLocation",
                              "tvNPDevices",
                              "ntbkNPType",
                              "lblNPDeviceDescription",
                              "expNPDeviceURIs",
                              "tvNPDeviceURIs",
                              "cmbNPTSerialBaud",
                              "cmbNPTSerialParity",
                              "cmbNPTSerialBits",
                              "cmbNPTSerialFlow",
                              "btnNPTLpdProbe",
                              "entNPTLpdHost",
                              "entNPTLpdQueue",
                              "entNPTJetDirectHostname",
                              "entNPTJetDirectPort",
                              "entSMBURI",
                              "btnSMBBrowse",
                              "tblSMBAuth",
                              "rbtnSMBAuthPrompt",
                              "rbtnSMBAuthSet",
                              "entSMBUsername",
                              "entSMBPassword",
                              "btnSMBVerify",
                              "entNPTNetworkHostname",
                              "btnNetworkFind",
                              "lblNetworkFindSearching",
                              "lblNetworkFindNotFound",
                              "entNPTDevice",
                              "tvNCMembers",
                              "tvNCNotMembers",
                              "btnNCAddMember",
                              "btnNCDelMember",
                              "ntbkPPDSource",
                              "rbtnNPPPD",
                              "tvNPMakes",
                              "rbtnNPFoomatic",
                              "filechooserPPD",
                              "rbtnNPDownloadableDriverSearch",
                              "entNPDownloadableDriverSearch",
                              "btnNPDownloadableDriverSearch",
                              "btnNPDownloadableDriverSearch_label",
                              "cmbNPDownloadableDriverFoundPrinters",
                              "tvNPModels",
                              "tvNPDrivers",
                              "rbtnChangePPDasIs",
                              "rbtnChangePPDKeepSettings",
                              "scrNPInstallableOptions",
                              "vbNPInstallOptions",
                              "tvNPDownloadableDrivers",
                              "ntbkNPDownloadableDriverProperties",
                              "lblNPDownloadableDriverSupplier",
                              "cbNPDownloadableDriverSupplierVendor",
                              "lblNPDownloadableDriverLicense",
                              "cbNPDownloadableDriverLicensePatents",
                              "cbNPDownloadableDriverLicenseFree",
                              "lblNPDownloadableDriverDescription",
                              "lblNPDownloadableDriverSupportContacts",
                              "hsDownloadableDriverPerfText",
                              "hsDownloadableDriverPerfLineArt",
                              "hsDownloadableDriverPerfGraphics",
                              "hsDownloadableDriverPerfPhoto",
                              "lblDownloadableDriverPerfTextUnknown",
                              "lblDownloadableDriverPerfLineArtUnknown",
                              "lblDownloadableDriverPerfGraphicsUnknown",
                              "lblDownloadableDriverPerfPhotoUnknown",
                              "frmNPDownloadableDriverLicenseTerms",
                              "tvNPDownloadableDriverLicense",
                              "rbtnNPDownloadLicenseYes",
                              "rbtnNPDownloadLicenseNo"],
                         "WaitWindow":
                             ["WaitWindow",
                              "lblWait"],
                         "SMBBrowseDialog":
                             ["SMBBrowseDialog",
                              "tvSMBBrowser",
                              "btnSMBBrowseOk"]},

                        domain=config.PACKAGE)

        # Fill in liststores for combo-box widgets
        for (widget,
             opts) in [(self.cmbNPTSerialBaud,
                        [[_("Default"), ""],
                         ["1200", "1200"],
                         ["2400", "2400"],
                         ["4800", "4800"],
                         ["9600", "9600"],
                         ["19200", "19200"],
                         ["38400", "38400"],
                         ["57600", "57600"],
                         ["115200", "115200"]]),

                       (self.cmbNPTSerialParity,
                        [[_("Default"), ""],
                         [_("None"), "none"],
                         [_("Odd"), "odd"],
                         [_("Even"), "even"]]),

                       (self.cmbNPTSerialBits,
                        [[_("Default"), ""],
                         ["8", "8"],
                         ["7", "7"]]),

                       (self.cmbNPTSerialFlow,
                        [[_("Default"), ""],
                         [_("None"), "none"],
                         [_("XON/XOFF (Software)"), "soft"],
                         [_("RTS/CTS (Hardware)"), "hard"],
                         [_("DTR/DSR (Hardware)"), "hard"]]),

                       ]:
            store = Gtk.ListStore (str, str)
            for row in opts:
                store.append (row)

            widget.set_model (store)
            cell = Gtk.CellRendererText ()
            widget.clear ()
            widget.pack_start (cell, True)
            widget.add_attribute (cell, 'text', 0)

        # Set up some lists
        m = Gtk.SelectionMode.MULTIPLE
        s = Gtk.SelectionMode.SINGLE
        b = Gtk.SelectionMode.BROWSE
        for name, model, treeview, selection_mode in (
            (_("Members of this class"), Gtk.ListStore(str),
             self.tvNCMembers, m),
            (_("Others"), Gtk.ListStore(str), self.tvNCNotMembers, m),
            (_("Devices"), Gtk.ListStore(str), self.tvNPDevices, s),
            (_("Connections"), Gtk.ListStore(str), self.tvNPDeviceURIs, s),
            (_("Makes"), Gtk.ListStore(str, str), self.tvNPMakes,s),
            (_("Models"), Gtk.ListStore(str, str), self.tvNPModels,s),
            (_("Drivers"), Gtk.ListStore(str), self.tvNPDrivers,s),
            (_("Downloadable Drivers"), Gtk.ListStore(str),
             self.tvNPDownloadableDrivers, b),
            ):

            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(name, cell, text=0)
            treeview.set_model(model)
            treeview.append_column(column)
            treeview.get_selection().set_mode(selection_mode)

        # Since some dialogs are reused we can't let the delete-event's
        # default handler destroy them
        self.SMBBrowseDialog.connect ("delete-event", on_delete_just_hide)
        self.WaitWindow_handler = self.WaitWindow.connect ("delete-event",
                                                           on_delete_just_hide)

        self.ntbkNewPrinter.set_show_tabs(False)
        self.ntbkPPDSource.set_show_tabs(False)
        self.ntbkNPType.set_show_tabs(False)
        self.ntbkNPDownloadableDriverProperties.set_show_tabs(False)

        self.spinner_count = 0

        # Set up OpenPrinting widgets.
        self.opreq = None
        self.opreq_handlers = None
        combobox = self.cmbNPDownloadableDriverFoundPrinters
        cell = Gtk.CellRendererText()
        combobox.pack_start (cell, True)
        combobox.add_attribute(cell, 'text', 0)
        if config.DOWNLOADABLE_ONLYFREE:
            for widget in [self.cbNPDownloadableDriverLicenseFree,
                           self.cbNPDownloadableDriverLicensePatents]:
                widget.hide ()
        if os.path.exists('/etc/apt/sources.list') or os.path.exists(
            '/etc/apt/sources.list.d'):
            config.packagesystem = 'deb'
            self.packageinstaller = 'apt'
        elif os.path.exists('/etc/yum.conf'):
            config.packagesystem = 'rpm'
            self.packageinstaller = 'yum'
        else:
            # No known package system, so we only load single PPDs via
            # OpenPrinting
            config.DOWNLOADABLE_ONLYPPD = True

        def protect_toggle (toggle_widget):
            active = getattr (toggle_widget, 'protect_active', None)
            if active is not None:
                toggle_widget.set_active (a