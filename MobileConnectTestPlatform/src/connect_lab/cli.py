from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

from connect_lab.adb import AdbClient
from connect_lab.analysis import analyze_text
from connect_lab.artifacts import ArtifactStore
from connect_lab.config import load_testbed
from connect_lab.defect import build_defect_draft, defect_to_markdown
from connect_lab.diagnosis import diagnose_path
from connect_lab.reporting import build_markdown_report
from connect_lab.retest import recommend_retests, retests_to_markdown
from connect_lab.scenarios import generate_scenarios, scenarios_to_json, scenarios_to_markdown


REQUIRED_MODULES = {
    "pytest": "pytest",
    "allure_commons": "allure-pytest",
    "yaml": "PyYAML",
    "adbutils": "adbutils",
    "appium": "Appium-Python-Client",
    "mobly": "mobly",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="connect_lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="Check environment and device access.")
    doctor_parser.add_argument("--config", default="configs/testbed.example.yaml")
    doctor_parser.set_defaults(func=cmd_doctor)

    collect_parser = subparsers.add_parser("collect", help="Collect Android connectivity evidence.")
    collect_parser.add_argument("--config", default="configs/testbed.example.yaml")
    collect_parser.add_argument("--serial", default="")
    collect_parser.add_argument("--name", default="manual_collect")
    collect_parser.set_defaults(func=cmd_collect)

    analyze_parser = subparsers.add_parser("analyze-log", help="Analyze a text log with local rules.")
    analyze_parser.add_argument("path")
    analyze_parser.add_argument("--json", action="store_true")
    analyze_parser.set_defaults(func=cmd_analyze_log)

    diagnose_parser = subparsers.add_parser("diagnose", help="Diagnose a connectivity log or artifact directory.")
    diagnose_parser.add_argument("path")
    diagnose_parser.add_argument("--json", action="store_true")
    diagnose_parser.set_defaults(func=cmd_diagnose)

    cases_parser = subparsers.add_parser("generate-cases", help="Generate AI-assisted connectivity test scenarios.")
    cases_parser.add_argument("--domain", default="car", choices=["car", "phone", "tablet", "headset"])
    cases_parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    cases_parser.add_argument("--output", default="")
    cases_parser.set_defaults(func=cmd_generate_cases)

    report_parser = subparsers.add_parser("build-report", help="Build a Markdown diagnosis report from a run directory or log.")
    report_parser.add_argument("path")
    report_parser.add_argument("--output", default="")
    report_parser.set_defaults(func=cmd_build_report)

    retest_parser = subparsers.add_parser("recommend-retests", help="Recommend a focused retest set from a log or run directory.")
    retest_parser.add_argument("path")
    retest_parser.add_argument("--json", action="store_true")
    retest_parser.add_argument("--output", default="")
    retest_parser.set_defaults(func=cmd_recommend_retests)

    defect_parser = subparsers.add_parser("draft-defect", help="Draft a defect report from a log or run directory.")
    defect_parser.add_argument("path")
    defect_parser.add_argument("--output", default="")
    defect_parser.set_defaults(func=cmd_draft_defect)

    args = parser.parse_args(argv)
    return int(args.func(args))


def cmd_doctor(args: argparse.Namespace) -> int:
    config = load_testbed(args.config)
    print(f"Config: {config.path}")
    print(f"Python: {sys.version.split()[0]}")

    missing = []
    for module_name, package_name in REQUIRED_MODULES.items():
        ok = importlib.util.find_spec(module_name) is not None
        print(f"{package_name}: {'OK' if ok else 'MISSING'}")
        if not ok:
            missing.append(package_name)

    adb = AdbClient(config.android.adb_path)
    try:
        devices = adb.devices()
    except Exception as exc:
        print(f"ADB: FAILED - {exc}")
        return 2 if missing else 1

    print(f"ADB: OK ({config.android.adb_path})")
    if devices:
        for device in devices:
            print(f"Device: {device.serial} [{device.state}]")
    else:
        print("Device: none connected")

    return 2 if missing else 0


def cmd_collect(args: argparse.Namespace) -> int:
    config = load_testbed(args.config)
    adb = AdbClient(config.android.adb_path)
    serial = _select_serial(adb, args.serial or config.android.default_serial)
    device = adb.device(serial)
    store = ArtifactStore.create(config.artifacts.root, args.name)

    props = {
        "serial": serial,
        "manufacturer": device.getprop("ro.product.manufacturer"),
        "model": device.getprop("ro.product.model"),
        "release": device.getprop("ro.build.version.release"),
        "sdk": device.getprop("ro.build.version.sdk"),
    }
    store.write_text("device_props.json", json.dumps(props, indent=2, ensure_ascii=False))

    bt_state = device.bluetooth_state()
    store.write_text("bluetooth_state.json", json.dumps(bt_state, indent=2, ensure_ascii=False))

    logcat = device.logcat_tail(config.artifacts.logcat_tail_lines)
    store.write_text("logcat_tail.txt", logcat.stdout or logcat.stderr)

    print(f"Collected artifacts: {store.root}")
    return 0


def cmd_analyze_log(args: argparse.Namespace) -> int:
    text = Path(args.path).read_text(encoding="utf-8", errors="replace")
    findings = analyze_text(text)

    if args.json:
        print(json.dumps([finding.__dict__ for finding in findings], indent=2, ensure_ascii=False))
        return 0

    for finding in findings:
        print(f"[{finding.severity}] {finding.title}")
        if finding.evidence:
            print(f"  evidence: {finding.evidence}")
        print(f"  suggestion: {finding.suggestion}")
    return 0


def cmd_diagnose(args: argparse.Namespace) -> int:
    report = diagnose_path(args.path)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return 0

    print(report.summary)
    for finding in report.findings:
        print(f"[{finding.severity}] {finding.category}: {finding.title}")
        print(f"  evidence: {finding.evidence}")
        print(f"  suggestion: {finding.suggestion}")
    return 0


def cmd_generate_cases(args: argparse.Namespace) -> int:
    scenarios = generate_scenarios(args.domain)
    content = scenarios_to_json(scenarios) if args.format == "json" else scenarios_to_markdown(scenarios)
    if args.output:
        _write_output(args.output, content)
        print(f"Generated scenarios: {args.output}")
    else:
        print(content)
    return 0


def cmd_build_report(args: argparse.Namespace) -> int:
    content = build_markdown_report(args.path)
    if args.output:
        _write_output(args.output, content)
        print(f"Generated report: {args.output}")
    else:
        print(content)
    return 0


def cmd_recommend_retests(args: argparse.Namespace) -> int:
    report = diagnose_path(args.path)
    items = recommend_retests(report)
    if args.json:
        content = json.dumps([item.to_dict() for item in items], indent=2, ensure_ascii=False)
    else:
        content = retests_to_markdown(items)
    if args.output:
        _write_output(args.output, content)
        print(f"Generated retest recommendations: {args.output}")
    else:
        print(content)
    return 0


def cmd_draft_defect(args: argparse.Namespace) -> int:
    draft = build_defect_draft(args.path)
    content = defect_to_markdown(draft)
    if args.output:
        _write_output(args.output, content)
        print(f"Generated defect draft: {args.output}")
    else:
        print(content)
    return 0


def _write_output(path: str, content: str) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    return output


def _select_serial(adb: AdbClient, preferred: str = "") -> str:
    devices = [device for device in adb.devices() if device.state == "device"]
    if preferred:
        if any(device.serial == preferred for device in devices):
            return preferred
        raise RuntimeError(f"Preferred Android device is not online: {preferred}")
    if len(devices) == 1:
        return devices[0].serial
    if not devices:
        raise RuntimeError("No online Android device found.")
    serials = ", ".join(device.serial for device in devices)
    raise RuntimeError(f"Multiple Android devices found; pass --serial. Online devices: {serials}")


if __name__ == "__main__":
    raise SystemExit(main())
