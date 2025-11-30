from flask import request, jsonify


def simple_auth_middleware(get_response):
	def middleware(*args, **kwargs):
		# Very small placeholder: allow all requests for now
		return get_response(*args, **kwargs)

	return middleware

