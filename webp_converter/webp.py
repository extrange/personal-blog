import subprocess
from pathlib import Path

INPUT = Path('./input')
OUTPUT = Path('./output')
CWEBP = Path('./cwebp.exe')

for file in INPUT.iterdir():
    subprocess.run(f'{CWEBP} -q 80 {file} -o {OUTPUT / file.stem}.webp', shell=True)
    file.unlink()
