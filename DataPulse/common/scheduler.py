from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from config_env import settings
from common.utils.logger import logger


class SchedulerManager:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

    def start(self) -> None:
        if settings.scheduler_enabled and not self.scheduler.running:
            self.scheduler.start()
            logger.info("调度器已启动")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("调度器已停止")

    def add_interval_job(self, job_id: str, func, minutes: int) -> None:
        self.scheduler.add_job(func, "interval", minutes=minutes, id=job_id, replace_existing=True)


scheduler_manager = SchedulerManager()
