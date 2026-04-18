#!/usr/bin/env python3
# Copyright 2026 Ashish Yadav (Autouse AI)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""License header checker for AutoUse."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_HEADER_LINES = [
    "# Copyright 2026 Ashish Yadav (Autouse AI)",
    "#",
    "# Licensed under the Apache License, Version 2.0 (the \"License\");",
    "# you may not use this file except in compliance with the License.",
    "# You may obtain a copy of the License at",
    "#",
    "#     http://www.apache.org/licenses/LICENSE-2.0",
    "#",
    "# Unless required by applicable law or agreed to in writing, software",
    "# distributed under the License is distributed on an \"AS IS\" BASIS,",
    "# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.",
    "# See the License for the specific language governing permissions and",
    "# limitations under the License.",
]

APACHE_MARKER = "Licensed under the Apache License, Version 2.0"

EXCLUDE_PREFIXES = (".git/", ".venv/", "venv/", "env/", "build/", "dist/")


def tracked_python_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    files = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if any(line.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        files.append(REPO_ROOT / line)
    return files


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{path}: file is not valid UTF-8"]

    lines = text.splitlines()
    start = 1 if lines and lines[0].startswith("#!") else 0
    header_slice = lines[start : start + len(EXPECTED_HEADER_LINES)]

    if header_slice != EXPECTED_HEADER_LINES:
        if APACHE_MARKER in text:
            errors.append(
                f"{path.relative_to(REPO_ROOT)}: Apache header present but does "
                f"not match the expected AutoUse header."
            )
        else:
            errors.append(
                f"{path.relative_to(REPO_ROOT)}: missing Apache 2.0 header."
            )

    if text.count(APACHE_MARKER) > 1:
        errors.append(
            f"{path.relative_to(REPO_ROOT)}: Apache header appears more than "
            f"once in the file (only one header allowed)."
        )

    return errors


def main() -> int:
    files = tracked_python_files()
    if not files:
        print("No .py files tracked by git. Nothing to check.")
        return 0

    all_errors: list[str] = []
    for f in files:
        all_errors.extend(check_file(f))

    if all_errors:
        print("License header check FAILED:\n")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"License header check PASSED ({len(files)} file(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
