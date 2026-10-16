from __future__ import annotations

from datetime import date, timedelta


def trip_period(start_after_days: int, trip_days: int, today: date | None = None) -> tuple[date, date]:
    """回傳 (開始日, 結束日)。

    trip_days 依站台算法：開始/結束時間同一個整點，結束日 = 開始日 + trip_days
    （10/19 22時 ~ 10/23 22時，站台顯示「共 4 天」）。
    """
    start = (today or date.today()) + timedelta(days=start_after_days)
    return start, start + timedelta(days=trip_days)


def to_roc(d: date) -> str:
    """西元 → 民國字串，例如 2026-10-19 → 115年10月19日（與站台確認視窗格式一致）"""
    return f"{d.year - 1911}年{d.month}月{d.day}日"
