LIFESYNC SIMPLE VERSION

1. Extract the ZIP and open the folder in VS Code.
2. Open Terminal in that folder.
3. Run:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install flask
   python app.py
4. Open http://127.0.0.1:5000 in your browser.

Pages:
- Dashboard: overview and add activity
- Studies & Career: study, interview, job-search tasks
- Self-care: skincare, exercise, meditation
- Schedule & Reminders: all tasks in date/time order

CSS is inside templates/base.html.
The SQLite database is created automatically.
