import datetime as dt
from sqlalchemy import func
from sqlalchemy.orm import (
    MappedAsDataclass,
    Mapped,
    mapped_column,
)


class CreatedMixin(MappedAsDataclass):
    created_at: Mapped[dt.datetime] = mapped_column(
        default=None, server_default=func.now(), kw_only=True
    )
