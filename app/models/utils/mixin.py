from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin(object):
    @declared_attr
    def created_at(cls) -> Mapped[DateTime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(ZoneInfo("Asia/Tokyo")),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls) -> Mapped[DateTime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(ZoneInfo("Asia/Tokyo")),
            onupdate=lambda: datetime.now(ZoneInfo("Asia/Tokyo")),
            nullable=False,
        )
