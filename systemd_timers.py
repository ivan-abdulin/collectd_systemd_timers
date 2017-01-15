import sys
import math
import collectd
from pydbus import SystemBus

PLUGIN_NAME = 'systemd_timers'

def read(data=None):
    values = collectd.Values(type='gauge', plugin=PLUGIN_NAME)
    bus = SystemBus()
    try:
        units = bus.get('.systemd1').ListUnits()
    except:
        collectd.warning('Error listing systemd units')
        sys.exit()

    for unit in units:
        ''' example timer unit looks like this
        (
            'shadow.timer',
            'Daily verification of password and group files',
            'loaded',
            'active',
            'waiting',
            '',
            '/org/freedesktop/systemd1/unit/shadow_2etimer',
             0,
            '',
            '/'
        )'''

        if not unit[0].endswith('.timer'):
            continue

        try:
            timer = bus.get('.systemd1', unit[6])
        except:
            collectd.warning('Error trying to fetch service "%s"' % unit[6])
            continue

        lastResult = 1 if timer.Result == 'success' else 0
        lastRun = math.ceil(timer.LastTriggerUSec / 1000000)
        values.dispatch(plugin_instance=unit[0], type_instance='last-run', time=lastRun, values=[lastResult])

collectd.register_read(read)
