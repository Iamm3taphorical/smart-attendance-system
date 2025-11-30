"""Database setup helper for smart-attendance-system.
Run this script after cloning to create the sqlite database and required folders.
"""
import yaml
from pathlib import Path
import argparse
import logging

from app.core.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(config_path: str):
    cfg_path = Path(config_path)
    if not cfg_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return

    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    db_path = cfg.get('database', {}).get('path', 'data/attendance.db')

    # Ensure data directories
    Path('data/known_faces').mkdir(parents=True, exist_ok=True)
    Path('data/exports').mkdir(parents=True, exist_ok=True)
    Path('data/backups').mkdir(parents=True, exist_ok=True)

    # Initialize DB
    DatabaseManager(db_path, schema_path='data/schema.sql')
    logger.info('Database initialized at %s', db_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default='config.yaml')
    args = parser.parse_args()
    main(args.config)
