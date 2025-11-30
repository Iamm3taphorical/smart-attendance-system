from dataclasses import dataclass
from typing import Optional


@dataclass
class KnownFace:
	student_id: str
	encoding: Optional[bytes] = None
	added_at: Optional[str] = None
