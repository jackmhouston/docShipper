# DocShipper Quick Start

## Prerequisites

1. Python 3.9+
2. FFmpeg (for screenshot generation)
3. MediaInfo (for music cue metadata)

### Install System Dependencies

```bash
# macOS
brew install ffmpeg mediainfo

# Ubuntu/Debian
sudo apt install ffmpeg mediainfo
```

## Setup

```bash
# Navigate to project directory
cd /Users/jack.houston/Documents/03_programs/UB_Programs/docshipper

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

The application will open in your browser at http://localhost:8501

## Workflows

### Shotlist Generator
1. Upload an EDL file from your NLE
2. Upload the corresponding video file
3. Choose an Excel template or create custom mappings
4. Configure screenshot settings
5. Generate shotlist with embedded screenshots

### Music Cue Sheet
1. Export XML from Premiere Pro (File > Export > Final Cut Pro XML)
2. Upload the XML file
3. Optionally upload a cue sheet template
4. Set filter keyword (e.g., "alibi" for Alibi Music)
5. Generate cue sheet with timecodes and metadata
