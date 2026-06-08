from __future__ import annotations

from dataclasses import dataclass
import subprocess


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class AndroidDeviceInfo:
    serial: str
    state: str


class AdbClient:
    def __init__(self, adb_path: str = "adb") -> None:
        self.adb_path = adb_path

    def run(self, args: list[str], timeout: int = 30) -> CommandResult:
        command = [self.adb_path, *args]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return CommandResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )

    def devices(self) -> list[AndroidDeviceInfo]:
        result = self.run(["devices"], timeout=15)
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout or "adb devices failed")

        devices: list[AndroidDeviceInfo] = []
        for line in result.stdout.splitlines()[1:]:
            if not line.strip() or "\t" not in line:
                continue
            serial, state = line.split("\t", 1)
            devices.append(AndroidDeviceInfo(serial=serial.strip(), state=state.strip()))
        return devices

    def device(self, serial: str) -> "AdbDevice":
        return AdbDevice(self, serial)


class AdbDevice:
    def __init__(self, client: AdbClient, serial: str) -> None:
        self.client = client
        self.serial = serial

    def run(self, args: list[str], timeout: int = 30) -> CommandResult:
        return self.client.run(["-s", self.serial, *args], timeout=timeout)

    def shell(self, command: str, timeout: int = 30) -> CommandResult:
        return self.run(["shell", command], timeout=timeout)

    def getprop(self, name: str, timeout: int = 15) -> str:
        result = self.shell(f"getprop {name}", timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout or f"getprop failed: {name}")
        return result.stdout.strip()

    def bluetooth_state(self) -> dict[str, str]:
        settings = self.shell("settings get global bluetooth_on", timeout=15)
        manager = self.shell("dumpsys bluetooth_manager", timeout=30)
        adapter = self.shell("dumpsys bluetooth_manager | head -n 80", timeout=30)
        return {
            "global_bluetooth_on": settings.stdout,
            "manager_summary": manager.stdout[:4000],
            "adapter_summary": adapter.stdout[:4000],
        }

    def logcat_tail(self, lines: int = 500) -> CommandResult:
        return self.run(["logcat", "-d", "-t", str(lines)], timeout=60)

    def clear_logcat(self) -> CommandResult:
        return self.run(["logcat", "-c"], timeout=30)
