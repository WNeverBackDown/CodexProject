from __future__ import annotations

from mobly import asserts
from mobly import base_test
from mobly import test_runner
from mobly.controllers import android_device


class BluetoothPairingTemplate(base_test.BaseTestClass):
    def setup_class(self) -> None:
        self.ads = self.register_controller(android_device)
        asserts.assert_true(len(self.ads) >= 2, "At least two Android devices are required.")
        self.dut = self.ads[0]
        self.peer = self.ads[1]

    def test_two_device_template(self) -> None:
        self.dut.log.info("DUT serial: %s", self.dut.serial)
        self.peer.log.info("Peer serial: %s", self.peer.serial)
        asserts.assert_true(self.dut.serial, "DUT serial should not be empty.")
        asserts.assert_true(self.peer.serial, "Peer serial should not be empty.")


if __name__ == "__main__":
    test_runner.main()
