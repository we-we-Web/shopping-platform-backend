from pydantic import BaseModel
from typing import Optional, Dict

class CheckRemain(BaseModel):
    id: int
    spec: dict
