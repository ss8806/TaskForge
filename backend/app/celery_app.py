"""
Celery アプリケーション設定
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "taskforge_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BROKER_URL.replace("/1", "/2"),  # 結果保存用DB
    include=["app.tasks.ai_tasks"],
)

# Celery 設定
celery_app.conf.update(
    # タスク設定
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # タスク結果の設定
    result_expires=3600,  # 1時間で結果を期限切れ
    task_track_started=True,
    # ワーカー設定
    worker_prefetch_multiplier=1,
    worker_concurrency=2,
    # タスクのタイムアウト
    task_soft_time_limit=300,  # 5分
    task_time_limit=360,  # 6分（ハードリミット）
)
