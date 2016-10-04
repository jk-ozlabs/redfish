
from odata import ODataObject, idregistry, action
import uuid
import basemodels
import dbus as _dbus


class ServiceRoot(basemodels.ServiceRoot_1_0_0_ServiceRoot):

    def __init__(self, dbus):
        self._odata_init()
        self.uuid = uuid.uuid1().hex
        self.redfishversion = '1.0.0'

    def assign_ids(self):
        self._odata_id = '/redfish/v1/'
        idregistry[self._odata_id] = self
        super(ServiceRoot, self).assign_ids(None, None)

class ComputerSystem(basemodels.ComputerSystem_1_0_0_ComputerSystem):

    def __init__(self, dbus):
        super(ComputerSystem, self).__init__()
        self.uuid = '04deb927-1d7a-487f-afb5-37ae36adaa18'
        self.manufacturer = 'IBM'
        self.model = 'Palmetto'
        self.name = 'foo'

        obj = dbus.get_object('org.openbmc.control.Power',
                '/org/openbmc/control/palmetto')
        self.power_control_iface = _dbus.Interface(obj,
                'org.openbmc.control.Power')

    def reset(self, reset_type):
        return 5

    @property
    def powerstate(self):
        state = self.power_control_iface.getPowerState()
        return ["Off", "On"][state]

    _odata_actions = {
        basemodels.ComputerSystem_Reset: reset,
    }
