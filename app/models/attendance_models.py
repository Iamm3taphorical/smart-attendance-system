from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
	student_id: str
	name: str
	email: str
	role: str = 'student'
	is_active: bool = True


@dataclass
class AttendanceRecord:
	student_id: str
	timestamp: Optional[str] = None
	location: Optional[str] = None
	confidence: Optional[float] = None
	status: str = 'present'
