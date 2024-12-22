from pydantic import BaseModel
from typing import Optional, Dict

class CheckRemain(BaseModel):
    id: str
    spec: dict
