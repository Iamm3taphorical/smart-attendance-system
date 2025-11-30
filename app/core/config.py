import yaml
from pathlib import Path


def load_config(path: str = 'config.yaml') -> dict:
	p = Path(path)
	if not p.exists():
		raise FileNotFoundError(f'Config file not found: {path}')
	return yaml.safe_load(p.read_text(encoding='utf-8'))
