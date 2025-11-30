from flask import Flask

def create_app(config_path: str = 'config.yaml') -> Flask:
	app = Flask(__name__, template_folder='templates')
	# Deferred import to avoid circular imports
	try:
		from app.api.endpoints import api_bp
		app.register_blueprint(api_bp, url_prefix='/api')
	except Exception:
		# endpoints may not be ready; ignore for now
		pass
	return app

