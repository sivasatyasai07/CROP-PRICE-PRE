import os
import sys

# Forward to root scripts
ROOT_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "verify_real_prediction.py"))
if os.path.exists(ROOT_SCRIPT):
    with open(ROOT_SCRIPT, "r", encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, ROOT_SCRIPT, "exec"))
