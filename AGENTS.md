# Repository Guidelines

## Project Structure & Module Organization
`app.py` is the Streamlit entrypoint and owns the page flow, session state, and workflow wiring. Put workflow-specific processing in `processors/`: `video_processor.py` handles EDL/XML parsing and screenshot generation, `music_processor.py` builds cue sheets, and `excel_analyzer.py` maps spreadsheet templates. Keep presentation code in `ui/` (`components.py`, `styles.py`, `tokens.py`) and shared helpers in `utils/`, especially `timecode.py`. There is no dedicated `tests/` or `docs/` tree yet; add new tests under `tests/` if you introduce them.

## Build, Test, and Development Commands
Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the app locally with `streamlit run app.py`. Use `python -m py_compile app.py processors/*.py ui/*.py utils/*.py` as a fast syntax smoke test before opening a PR. This project also depends on system tools: install `ffmpeg` for screenshot generation and `mediainfo` for music metadata extraction.

## Coding Style & Naming Conventions
Follow existing Python style: 4-space indentation, `snake_case` for functions and module variables, `PascalCase` for classes, and short docstrings on public helpers. Keep Streamlit state keys descriptive and stable, matching the patterns already used in `app.py` such as `shotlist_step` or `music_result_files`. Prefer small, focused functions in `processors/` and avoid putting file parsing or workbook logic directly in UI modules.

## Testing Guidelines
There is currently no automated test suite. For changes to parsing or workbook output, add targeted tests under `tests/` with names like `test_timecode.py` or `test_music_processor.py`. Until a suite exists, validate manually by running `streamlit run app.py` and exercising the relevant workflow with representative XML, EDL, video, and Excel template files.

## Commit & Pull Request Guidelines
Recent commits use concise, imperative subjects such as `Add XML support to shotlist pipeline and uploader`. Keep commit messages in that style and scoped to one logical change. PRs should include a brief summary, note any required sample files or external binaries, and attach screenshots for UI changes. Call out manual test coverage clearly when no automated tests were added.

## Security & Configuration Tips
Parse XML with `defusedxml`, which is already in use, and do not replace it with the standard library parser for untrusted files. Avoid committing customer media, generated spreadsheets, or local absolute paths. Keep machine-specific settings in local environment setup, not in tracked source files.
