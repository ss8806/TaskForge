"""ページネーションユーティリティ関数"""
import math
from typing import List, TypeVar
from app.api.schemas import PaginatedResponse

T = TypeVar('T')


def create_paginated_response(
    items: List[T],
    total: int,
    page: int,
    page_size: int
) -> PaginatedResponse[T]:
    """
    ページネーションメタ情報付きレスポンスを作成
    
    Args:
        items: アイテム一覧
        total: 総件数
        page: 現在のページ（1始まり）
        page_size: ページサイズ
        
    Returns:
        PaginatedResponse: ページネーション情報付きレスポンス
    """
    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=(page * page_size) < total,
        has_prev=page > 1
    )
