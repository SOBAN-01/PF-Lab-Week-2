# ShieldAI — Phishing Link Detector (Desktop Edition)

A standalone Windows desktop app for detecting phishing URLs. Pure tkinter
GUI, JSON file storage, no Flask, no HTTP, no database.

## Project structure
```
ShieldAI/
├── main.py        GUI (tkinter) — sidebar nav, scanner, history, profile
├── app.py         Backend: auth, users, history, profiles, JSON I/O, CLI mode
├── scanner.py      Phishing detection engine (analyze_url)
├── users.json      Created/maintained automatically
├── history.json    Created/maintained automatically
├── profiles/       Uploaded profile images
└── assets/         Static GUI assets
```

## Run the GUI
```
python3 main.py
```

## Run the terminal (CLI) version
Uses the exact same backend functions as the GUI.
```
python3 app.py
```

## Package as a Windows .exe
```
pyinstaller --onefile --windowed main.py
```
`app.py` and `scanner.py` are auto-included since `main.py` imports them.
The packaged exe will create `users.json`, `history.json`, `profiles/`,
and `assets/` next to the .exe on first run.

## Notes / assumptions made during the build
- **Passwords**: SHA-256 via `hashlib` only (no bcrypt), as required.
- **Profile images**: restricted to PNG/GIF. Tkinter's built-in `PhotoImage`
  (no Pillow) only reliably supports these formats, and adding Pillow would
  introduce exactly the kind of extra packaging dependency the spec asked
  to avoid. JPEG support would require Pillow.
- **scan_id**: a UUID4 hex string per scan, rather than a position-based
  index, so IDs stay stable and unique even after deletions.
- **Username rules**: non-empty, minimum 3 characters. Password rule:
  minimum 6 characters (carried over from the original app).
- **Search**: a single query box matches against URL, danger level, and
  timestamp simultaneously (substring match), satisfying "search by URL /
  danger level / date" without needing separate fields.
- **Logout**: handled as local GUI/CLI state reset (no token to invalidate,
  since everything is local — there's no session concept to log out of
  beyond clearing the in-memory "current user").
