#!/usr/bin/env python

import dbus

from models import ServiceRoot, ComputerSystem
from odata import idregistry
import application

def main():
    bus = dbus.SessionBus()

    # set up our models
    root = ServiceRoot(bus)
    system = ComputerSystem(bus)
    root.systems.append(system)

    root.assign_ids()

    # run the web application
    app = application.RedfishApplication(idregistry)
    application.run_simple('127.0.0.1', 5000, app,
            use_debugger=True, use_reloader=True)

if __name__ == '__main__':
    main()
