#!/usr/bin/env python3
import os
import subprocess
from zipfile import ZipFile

FILES = (
    "__init__.py",
    "LICENSE",
    "README.md"
)

git_revision = subprocess.check_output(("git", "rev-parse", "--short", "HEAD")).strip().decode()
output_file_name = os.path.join('dist', f'blender_coiled_spring_{git_revision}.zip')

print(f'Creating blender addon archive {output_file_name}')

with ZipFile(output_file_name, "x") as zf:
    for f in FILES:
        zf.write(f)

print(f'Done')
