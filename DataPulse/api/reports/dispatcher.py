from __future__ import annotations

import json
from typing import Any

import httpx

from api.reports.models import ReportChannel


SUPPORTED_PROVIDERS = ["generic", "feishu", "dingtalk", "wecom"]


def parse_json_object(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def build_report_payload(
    provider: str,
    title: str,
    content: str,
    recipients: list[str],
    robot_name: str = "DataPulseBot",
    message_format: str = "markdown",
) -> dict[str, Any]:
    normalized = provider.lower()
    if normalized == "feishu":
        return {
            "msg_type": "post" if message_format == "markdown" else "text",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [[{"tag": "text", "text": content}]],
                    }
                }
            }
            if message_format == "markdown"
            else {"text": f"{title}\n{content}"},
        }
    if normalized == "dingtalk":
        return {
            "msgtype": "markdown" if message_format == "markdown" else "text",
            "markdown": {"title": title, "text": content},
            "text": {"content": f"{title}\n{content}"},
            "at": {"atMobiles": recipients, "isAtAll": False},
        }
    if normalized == "wecom":
        return {
            "msgtype": "markdown" if message_format == "markdown" else "text",
            "markdown": {"content": f"### {title}\n{content}"},
            "text": {"content": f"{title}\n{content}", "mentioned_mobile_list": recipients},
        }
    return {
        "robot": robot_name,
        "provider": "generic",
        "recipients": recipients,
        "message": {
            "format": message_format,
            "title": title,
            "content": content,
        },
    }


def render_template(template: str | None, context: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    if not template:
        return fallback
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace("{{" + key + "}}", str(value))
    try:
        data = json.loads(rendered)
    except json.JSONDecodeError:
        return fallback
    return data if isinstance(data, dict) else fallback


async def push_report(
    channel: ReportChannel | None,
    title: str,
    content: str,
    recipients: list[str],
    message_format: str = "markdown",
    provider_override: str = "generic",
) -> dict[str, Any]:
    provider = (channel.provider if channel else provider_override).lower()
    robot_name = channel.robot_name if channel else "DataPulseBot"
    fallback_payload = build_report_payload(provider, title, content, recipients, robot_name, message_format)
    payload = render_template(
        channel.payload_template if channel else None,
        {
            "title": title,
            "content": content,
            "recipients": ",".join(recipients),
            "robot_name": robot_name,
            "message_format": message_format,
        },
        fallback_payload,
    )
    headers = parse_json_object(channel.headers_json if channel else None)
    if channel and channel.auth_type == "bearer" and channel.secret_token:
        headers["Authorization"] = f"Bearer {channel.secret_token}"

    request = {
        "url": channel.webhook_url if channel else None,
        "headers": headers,
        "payload": payload,
        "dry_run": True if not channel else channel.dry_run or not channel.webhook_url,
    }
    if request["dry_run"]:
        return {
            "status": "dry_run",
            "request": request,
            "response": {"message": "未配置真实 webhook 或启用了 dry_run，已完成兼容性预演。"},
        }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(channel.webhook_url, json=payload, headers=headers)
        return {
            "status": "success" if response.is_success else "failed",
            "request": request,
            "response": {
                "status_code": response.status_code,
                "text": response.text[:2000],
            },
        }
    except httpx.HTTPError as exc:
        return {
            "status": "failed",
            "request": request,
            "response": {},
            "error": str(exc),
        }
