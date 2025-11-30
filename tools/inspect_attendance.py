from pathlib import Path
p=Path('app/services/attendance_service.py')
text=p.read_text()
lines=text.splitlines()
print('Total lines:', len(lines))
for i,ln in enumerate(lines, start=1):
    if i>150:
        print(f"{i:04d}: {ln!r}")
print('\n--- Full file preview (first 200 lines) ---')
for i,ln in enumerate(lines[:200], start=1):
    print(f"{i:04d}: {ln}")
