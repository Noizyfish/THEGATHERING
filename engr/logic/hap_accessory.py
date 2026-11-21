"""ENGR as a HomeKit bridge (optional). pip install HAP-python[QRCode]; python logic/hap_accessory.py → scan the QR in Home.app.
Exposes switches that call `engr ...` when toggled, so Siri on HomePod/Watch/CarPlay can run the studio."""
import signal
import subprocess
from pathlib import Path

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SWITCH

ENGR = str(Path(__file__).resolve().parent.parent / "engr")
SWITCHES = {"Logic Record": ["logic", "record"], "Logic Play": ["logic", "play"], "Logic Stop": ["logic", "stop"],
            "Safety Rec": ["hijack", "start", "Safety"], "Studio Session": ["home", "scene", "session"], "Studio Wrap": ["home", "scene", "wrap"]}


class EngrSwitch(Accessory):
    category = CATEGORY_SWITCH

    def __init__(self, driver, name, cmd):
        super().__init__(driver, name)
        self.cmd = cmd
        self.on = self.add_preload_service("Switch").configure_char("On", setter_callback=self.set_on)

    def set_on(self, value):
        if value:
            subprocess.Popen([ENGR, *self.cmd])
            self.on.set_value(False)   # momentary


driver = AccessoryDriver(port=51826)
bridge = Bridge(driver, "ENGR")
for n, c in SWITCHES.items():
    bridge.add_accessory(EngrSwitch(driver, n, c))
driver.add_accessory(accessory=bridge)
signal.signal(signal.SIGTERM, driver.signal_handler)
driver.start()
