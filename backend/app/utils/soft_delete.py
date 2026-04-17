"""
ソフトデリート機能のユーティリティ関数
"""
from datetime import datetime, timezone
from typing import TypeVar, Optional, List
from sqlmodel import Session, select, SQLModel

T = TypeVar("T", bound=SQLModel)


def soft_delete(session: Session, item: SQLModel) -> None:
    """
    ソフトデリートを実行
    
    Args:
        session: データベースセッション
        item: 削除するオブジェクト
    """
    if hasattr(item, "deleted_at"):
        item.deleted_at = datetime.now(timezone.utc)
        session.add(item)
        session.commit()
    else:
        raise AttributeError(f"Model {type(item).__name__} does not support soft delete")


def restore_item(session: Session, item: SQLModel) -> None:
    """
    ソフトデリートされたアイテムを復元
    
    Args:
        session: データベースセッション
        item: 復元するオブジェクト
    """
    if hasattr(item, "deleted_at"):
        item.deleted_at = None
        session.add(item)
        session.commit()
    else:
        raise AttributeError(f"Model {type(item).__name__} does not support soft delete")


def filter_active(query, model: type[T]):
    """
    アクティブな（削除されていない）レコードのみを取得するクエリにフィルタリング
    
    Args:
        query: SQLModel selectクエリ
        model: モデルクラス
        
    Returns:
        フィルタリングされたクエリ
    """
    if hasattr(model, "deleted_at"):
        return query.where(model.deleted_at.is_(None))
    return query


def get_deleted_items(
    session: Session,
    model: type[T],
    limit: int = 20,
    offset: int = 0
) -> List[T]:
    """
    ソフトデリートされたアイテム一覧を取得
    
    Args:
        session: データベースセッション
        model: モデルクラス
        limit: 取得件数
        offset: オフセット
        
    Returns:
        ソフトデリートされたアイテムのリスト
    """
    if not hasattr(model, "deleted_at"):
        return []
    
    query = select(model).where(model.deleted_at.isnot(None)).offset(offset).limit(limit)
    return session.exec(query).all()
