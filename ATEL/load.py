# Based on example functions listed in EDMC Plugin Documentation:
# https://github.com/Marginal/EDMarketConnector/blob/master/PLUGINS.md

import sys
import os
import ttk
import Tkinter as tk
import tkMessageBox
from ttkHyperlinkLabel import HyperlinkLabel
from config import applongname, appversion
import myNotebook as nb
import json
import requests
import zlib
import re
import webbrowser
from collections import defaultdict
import threading
import urllib2

this = sys.modules[__name__]	# For holding module globals
status = tk.StringVar()
VERSION = '0.15a'
this.github = "https://raw.githubusercontent.com/Elite-IGAU/ATEL-EDMC/master/ATEL/load.py"
PADX = 10  # formatting

############
#
# mediawiki token request
S = requests.Session()
URL = "https://www.mediawiki.org/w/api.php"

PARAMS = {
    "action": "query",
    "meta": "tokens",
    "type": "login",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS)
DATA = R.json()
LOGIN_TOKEN = DATA['query']['tokens']['logintoken']
#sys.stderr.write(LOGIN_TOKEN+'\n')
#
##########

def plugin_start(plugin_dir):
    """
    Load this plugin into EDMC
    """
    sys.stderr.write("Plugin loaded from: {}".format(plugin_dir.encode("utf-8"))+'\n')
    #print "Plugin loaded from: {}".format(plugin_dir.encode("utf-8"))
    return 'ATEL'

def plugin_prefs(parent):
    frame = nb.Frame(parent)
    frame.columnconfigure(5, weight=1)
    HyperlinkLabel(frame, text='ATEL GitHub', background=nb.Label().cget('background'),
                   url='https://github.com/Elite-IGAU/ATEL-EDMC', underline=True).grid(columnspan=2, padx=PADX, sticky=tk.W)
    nb.Label(frame, text="ATEL {VER}".format(
        VER=VERSION)).grid(columnspan=2, padx=PADX, sticky=tk.W)
    nb.Button(frame, text="UPGRADE", command=upgrade_callback).grid(row=10, column=0,
        columnspan=2, padx=PADX, sticky=tk.W)
    #
    # Todo - Add option to defer ATEL transmission until docked and cartographic data is sold.
    #
    return frame

def upgrade_callback():
    this_fullpath = os.path.realpath(__file__)
    this_filepath, this_extension = os.path.splitext(this_fullpath)
    corrected_fullpath = this_filepath + ".py"
    try:
        response = requests.get(this.github)
        if (response.status_code == 200):
            with open(corrected_fullpath, "wb") as f:
                f.seek(0)
                f.write(response.content)
                f.truncate()
                f.flush()
                os.fsync(f.fileno())
                this.upgrade_applied = True  # Latch on upgrade successful
                msginfo = ['Upgrade has completed sucessfully.',
                           'Please close and restart EDMC']
                tkMessageBox.showinfo("Upgrade status", "\n".join(msginfo))
            sys.stderr.write("Finished plugin upgrade!\n")

        else:
            msginfo = ['Upgrade failed. Bad server response',
                       'Please try again']
            tkMessageBox.showinfo("Upgrade status", "\n".join(msginfo))
    except:
        sys.stderr.writelines(
            "Upgrade problem when fetching the remote data: {E}\n".format(E=sys.exc_info()[0]))
        msginfo = ['Upgrade encountered a problem.',
                   'Please try again, and restart if problems persist']
        tkMessageBox.showinfo("Upgrade status", "\n".join(msginfo))

def bulletin_callback():
    sys.stderr.write("Someone clicked the button!\n")
    status.set("IGAU ATEL Submitted")

def plugin_app(parent):
    """
    Create a pair of TK widgets for the EDMC main window
    """
    this.parent = parent
    this.frame = tk.Frame(parent)
    this.frame.columnconfigure(2, weight=1)
    this.lblstatus = tk.Label(this.frame, anchor=tk.W, textvariable=status, wraplengt=200)
    this.lblstatus.grid(row=0, column=1, sticky=tk.W)
    status.set("[ATEL] Waiting for COVAS feed...")
    return this.frame

def journal_entry(cmdr, is_beta, system, station, entry, state):

#############################
# What we're really after are unique discoveries.
    if entry['event'] == 'CodexEntry':
        # We discovered something!
        # Lines 111, and 112 might not work the way I think they should. I don't know "tuple" well.
            sys.stderr.write("{}: Discovered {} in {}\n".format(entry['timestamp'],['Name_Localised'],['System']))
            status.set("{}: Discovered {} in {}\n".format(entry['timestamp'],['Name_Localised'],['System']))
            nb.Button(frame, text="Submit Discovery Report", command=bulletin_callback).grid(row=10, column=0,
            columnspan=2, padx=PADX, sticky=tk.W)
    else:
        # FSDJump happens often enough in the journal to use for debugging purposes.
        # remove/comment out after CodexDiscovery function is finished.
            if entry['event'] == 'FSDJump':
                # We arrived at a new system!
                    sys.stderr.write("Arrived in: {}\n".format(entry['StarSystem']))
                    status.set("Arrived in: {}\n".format(entry['StarSystem']))
                    nb.Button(frame, text="Submit Discovery Report", command=bulletin_callback).grid(row=10, column=0,
                    columnspan=2, padx=PADX, sticky=tk.W)

def plugin_stop():
    """
    EDMC is closing
    """
    sys.stderr.write("Shutting down.")