#!/usr/bin/env python3
"""Run everything that can run offline from master.yaml:
  1. render yuzu/set.json + yuzu/keys.json      (import into the Yuzu Playground)
  2. render diagram.html
  3. diff master against the current Oryx snapshot -> oryx/pending_edits.json
Exit code 2 = Oryx has pending edits; 1 = a cap label doesn't fit; 0 = all in sync."""
import subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
rc = 0
for script in ("render_yuzu.py", "render_diagram.py", "oryx_diff.py"):
    print(f"--- {script}")
    r = subprocess.run([sys.executable, os.path.join(here, script)])
    rc = max(rc, r.returncode)
sys.exit(rc)
