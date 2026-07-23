#!/usr/bin/python3
import os
import syslog

try:
    if os.path.exists("/etc/X11/Xsession.d/98vboxadd-xclient"):
        os.system("sed -i -e 's@notify-send@true #@g' /etc/X11/Xsession.d/98vboxadd-xclient")
except Exception as detail:
    syslog.syslog("Couldn't adjust /etc/X11/Xsession.d/98vboxadd-xclient: %s" % detail)
