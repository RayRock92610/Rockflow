🎯 **What:** Removed unused `timedelta` import from `dags/kessel_flow.py`.

💡 **Why:** This reduces visual noise and keeps the imports clean and precise. It is an unused dependency that can be safely removed to improve readability without affecting logic.

✅ **Verification:** Verified by running `python -m compileall dags/kessel_flow.py` and `ruff check dags/kessel_flow.py`, followed by executing the full suite of unit tests with `pytest tests/`, which passed flawlessly.

✨ **Result:** Improved code cleanliness and maintainability by removing dead code/imports.
