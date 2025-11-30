import csv
from pathlib import Path
from typing import List, Dict


def generate_csv_report(start_date: str, end_date: str, rows: List[Dict], out_path: str = None) -> str:
	out_dir = Path('data/exports')
	out_dir.mkdir(parents=True, exist_ok=True)
	out_file = out_dir / f"attendance_{start_date}_{end_date}.csv"
	keys = rows[0].keys() if rows else ['student_id']
	with open(out_file, 'w', newline='', encoding='utf-8') as f:
		writer = csv.DictWriter(f, fieldnames=list(keys))
		writer.writeheader()
		for r in rows:
			writer.writerow(r)
	return str(out_file)


def generate_pdf_report(start_date: str, end_date: str, rows: List[Dict], out_path: str = None) -> str:
	# Minimal placeholder: write a text-like PDF using reportlab if available
	try:
		from reportlab.lib.pagesizes import letter
		from reportlab.pdfgen import canvas
	except Exception:
		# fallback to csv
		return generate_csv_report(start_date, end_date, rows, out_path)

	out_dir = Path('data/exports')
	out_dir.mkdir(parents=True, exist_ok=True)
	out_file = out_dir / f"attendance_{start_date}_{end_date}.pdf"
	c = canvas.Canvas(str(out_file), pagesize=letter)
	text = c.beginText(40, 750)
	text.textLine(f"Attendance Report {start_date} to {end_date}")
	for r in rows:
		text.textLine(str(r))
	c.drawText(text)
	c.save()
	return str(out_file)

