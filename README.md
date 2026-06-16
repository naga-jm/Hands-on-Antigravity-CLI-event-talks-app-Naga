# BigQuery Release Notes Web Application

A premium, modern web application built with **Flask**, **Vanilla HTML/JS**, and **CSS** that pulls live updates from the official Google Cloud BigQuery release notes XML feed and parses it into a clean, searchable timeline UI.

## Features

- **Live XML Processing**: Fetches and parses Google Cloud BigQuery Atom feed dynamically.
- **Translucent UI Card Grid**: Displays entries sorted by category badges (Feature, Issue, Deprecation).
- **Instant Search**: Quick-filters updates by content body, date, or category tags.
- **Visual Stagger Animation**: Staggered cards loading animation.
- **Refresh action**: Refreshes feed with active rotation spinner animation.
- **Twitter/X Sharing integration**: Single-click formatting and sharing targeting Twitter Web Intent under X/Twitter character limitations.

## Getting Started

### 1. Setup Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python3 app.py
```
After starting the server, open the local address displayed in the terminal output in your browser to view the application.

