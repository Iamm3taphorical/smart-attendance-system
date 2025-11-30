from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
	student_id: str
	name: str
	email: str
	role: str = 'student'
	is_active: bool = True
	face_encoding: Optional[bytes] = None
