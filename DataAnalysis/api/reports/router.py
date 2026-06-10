from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import current_user_uid
from api.reports.dispatcher import SUPPORTED_PROVIDERS, build_report_payload, push_report
from api.reports.models import ReportChannel, ReportPushHistory
from common.utils.utils import ok, utc_now
from database import get_db

router = APIRouter(prefix="/api/reports", tags=["报告推送"])


class ReportChannelPayload(BaseModel):
    name: str
    provider: str = Field(default="generic", pattern="^(generic|feishu|dingtalk|wecom)$")
    robot_name: str = "DataPulseBot"
    webhook_url: str | None = None
    auth_type: str = Field(default="none", pattern="^(none|bearer)$")
    secret_token: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    payload_template: str | None = None
    is_enabled: bool = True
    dry_run: bool = True


class ReportPushPayload(BaseModel):
    title: str
    content: str
    recipients: list[str] = Field(default_factory=list)
    channel_id: int | None = None
    provider: str = Field(default="generic", pattern="^(generic|feishu|dingtalk|wecom)$")
    message_format: str = Field(default="markdown", pattern="^(markdown|text)$")


@router.get("/providers")
def providers() -> dict:
    return ok(
        [
            {"key": "generic", "name": "通用机器人", "description": "标准 JSON 协议，适合内部自研聊天平台。"},
            {"key": "feishu", "name": "飞书风格", "description": "生成飞书机器人消息结构，平台确认后替换 webhook 即可。"},
            {"key": "dingtalk", "name": "钉钉风格", "description": "生成钉钉 markdown/text 机器人消息结构。"},
            {"key": "wecom", "name": "企业微信风格", "description": "生成企业微信机器人 markdown/text 消息结构。"},
        ]
    )


@router.get("/channels")
def list_channels(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(ReportChannel).order_by(ReportChannel.id.desc())).all()
    return ok([serialize_channel(row, reveal_secret=False) for row in rows])


@router.post("/channels")
def create_channel(payload: ReportChannelPayload, db: Session = Depends(get_db)) -> dict:
    row = ReportChannel(
        name=payload.name,
        provider=payload.provider,
        robot_name=payload.robot_name,
        webhook_url=payload.webhook_url,
        auth_type=payload.auth_type,
        secret_token=payload.secret_token,
        headers_json=json.dumps(payload.headers, ensure_ascii=False),
        payload_template=payload.payload_template,
        is_enabled=payload.is_enabled,
        dry_run=payload.dry_run,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(serialize_channel(row, reveal_secret=False), "报告推送通道已创建")


@router.put("/channels/{channel_id}")
def update_channel(channel_id: int, payload: ReportChannelPayload, db: Session = Depends(get_db)) -> dict:
    row = db.get(ReportChannel, channel_id)
    if not row:
        raise HTTPException(status_code=404, detail="报告推送通道不存在")
    row.name = payload.name
    row.provider = payload.provider
    row.robot_name = payload.robot_name
    row.webhook_url = payload.webhook_url
    row.auth_type = payload.auth_type
    row.secret_token = payload.secret_token
    row.headers_json = json.dumps(payload.headers, ensure_ascii=False)
    row.payload_template = payload.payload_template
    row.is_enabled = payload.is_enabled
    row.dry_run = payload.dry_run
    row.updated_at = utc_now()
    db.commit()
    return ok(serialize_channel(row, reveal_secret=False), "报告推送通道已更新")


@router.delete("/channels/{channel_id}")
def delete_channel(channel_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(ReportChannel, channel_id)
    if row:
        db.delete(row)
        db.commit()
    return ok(message="报告推送通道已删除")


@router.post("/preview")
def preview(payload: ReportPushPayload, db: Session = Depends(get_db)) -> dict:
    channel = resolve_channel(payload.channel_id, db)
    provider = channel.provider if channel else payload.provider
    robot_name = channel.robot_name if channel else "DataPulseBot"
    return ok(
        {
            "provider": provider,
            "payload": build_report_payload(provider, payload.title, payload.content, payload.recipients, robot_name, payload.message_format),
        }
    )


@router.post("/push")
async def push(payload: ReportPushPayload, uid: str = Depends(current_user_uid), db: Session = Depends(get_db)) -> dict:
    channel = resolve_channel(payload.channel_id, db)
    result = await push_report(channel, payload.title, payload.content, payload.recipients, payload.message_format, payload.provider)
    history = ReportPushHistory(
        channel_id=channel.id if channel else None,
        channel_name=channel.name if channel else "临时通用通道",
        provider=channel.provider if channel else payload.provider,
        title=payload.title,
        content=payload.content,
        recipients_json=json.dumps(payload.recipients, ensure_ascii=False),
        status=result.get("status", "failed"),
        request_json=json.dumps(result.get("request", {}), ensure_ascii=False),
        response_json=json.dumps(result.get("response", {}), ensure_ascii=False),
        error_message=result.get("error"),
        created_by=uid,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return ok({"history": serialize_history(history), "dispatch": result}, "报告推送已处理")


@router.get("/history")
def history(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(ReportPushHistory).order_by(ReportPushHistory.id.desc()).limit(100)).all()
    return ok([serialize_history(row) for row in rows])


def resolve_channel(channel_id: int | None, db: Session) -> ReportChannel | None:
    if channel_id:
        channel = db.get(ReportChannel, channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="报告推送通道不存在")
        if not channel.is_enabled:
            raise HTTPException(status_code=400, detail="报告推送通道已停用")
        return channel
    return db.scalar(select(ReportChannel).where(ReportChannel.is_enabled.is_(True)).order_by(ReportChannel.id))


def serialize_channel(row: ReportChannel, reveal_secret: bool = False) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "provider": row.provider,
        "robot_name": row.robot_name,
        "webhook_url": row.webhook_url,
        "auth_type": row.auth_type,
        "secret_token": row.secret_token if reveal_secret else bool(row.secret_token),
        "headers": json.loads(row.headers_json or "{}"),
        "payload_template": row.payload_template,
        "is_enabled": row.is_enabled,
        "dry_run": row.dry_run,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def serialize_history(row: ReportPushHistory) -> dict:
    return {
        "id": row.id,
        "channel_id": row.channel_id,
        "channel_name": row.channel_name,
        "provider": row.provider,
        "title": row.title,
        "content": row.content,
        "recipients": json.loads(row.recipients_json or "[]"),
        "status": row.status,
        "request": json.loads(row.request_json or "{}"),
        "response": json.loads(row.response_json or "{}"),
        "error_message": row.error_message,
        "created_by": row.created_by,
        "created_at": row.created_at,
    }
