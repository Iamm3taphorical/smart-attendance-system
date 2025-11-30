import hmac
import hashlib
import time
from typing import Optional


def generate_token(secret: str, subject: str, expiry_seconds: int = 3600) -> str:
	ts = int(time.time())
	exp = ts + expiry_seconds
	msg = f"{subject}:{exp}".encode('utf-8')
	sig = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).hexdigest()
	return f"{subject}:{exp}:{sig}"


def verify_token(secret: str, token: str) -> Optional[str]:
	try:
		subject, exp_s, sig = token.split(':')
		msg = f"{subject}:{exp_s}".encode('utf-8')
		expected = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).hexdigest()
		if not hmac.compare_digest(expected, sig):
			return None
		if int(exp_s) < int(time.time()):
			return None
		return subject
	except Exception:
		return None

