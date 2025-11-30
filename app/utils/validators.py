import re


def validate_email(email: str) -> bool:
	if not email:
		return False
	# very small email validator
	pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
	return re.match(pattern, email) is not None
