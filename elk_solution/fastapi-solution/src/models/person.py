from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel
from src.models.film import OrjsonMixin


class Person(BaseModel, OrjsonMixin):
    id: str
    full_name: str
    films: Optional[List[Dict[str, Union[UUID, List[str]]]]]
