from sqlalchemy import Identity, BigInteger
from sqlalchemy.orm import (
    MappedAsDataclass,
    Mapped,
    mapped_column,
)


class IdMixin(MappedAsDataclass):
    id: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), init=False, primary_key=True
    )
