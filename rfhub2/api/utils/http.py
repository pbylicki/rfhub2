from fastapi import HTTPException
from typing import Optional, TypeVar

T = TypeVar("T")


def or_404(item: Optional[T]) -> T:
    if not item:
        raise HTTPException(status_code=404)
    return item
