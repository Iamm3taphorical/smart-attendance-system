"""Simple backup utility: copies the SQLite DB to data/backups with timestamp.

Usage:
	python scripts/backup.py --config config.yaml
"""
import argparse
import shutil
from pathlib import Path
import yaml
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backup_db(db_path: str, out_dir: str = 'data/backups'):
	out = Path(out_dir)
	out.mkdir(parents=True, exist_ok=True)
	ts = time.strftime('%Y%m%d_%H%M%S')
	src = Path(db_path)
	if not src.exists():
		logger.error('Database file not found: %s', db_path)
		return None
	dst = out / f"attendance_{ts}.db"
	shutil.copy2(src, dst)
	logger.info('Database backed up to %s', dst)
	return dst


def main(config_path: str):
	cfg = yaml.safe_load(Path(config_path).read_text(encoding='utf-8'))
	db = cfg.get('database', {}).get('path', 'data/attendance.db')
	backup_db(db)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--config', '-c', default='config.yaml')
	args = parser.parse_args()
	main(args.config)

