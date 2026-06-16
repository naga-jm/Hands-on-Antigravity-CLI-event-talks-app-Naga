import urllib.request
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

FEED_URL = "https://docs.cloud.google.com/feeds/bigquery-release-notes.xml"

# HTML Template with rich dark mode aesthetics and smooth micro-animations
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BigQuery Release Notes</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-color: #f3f4f6;
            --text-muted: #9ca3af;
            --accent-color: #3b82f6;
            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            --badge-feature: rgba(59, 130, 246, 0.15);
            --badge-feature-text: #60a5fa;
            --badge-deprecation: rgba(239, 68, 68, 0.15);
            --badge-deprecation-text: #f87171;
            --badge-issue: rgba(245, 158, 11, 0.15);
            --badge-issue-text: #fbbf24;
            --badge-other: rgba(16, 185, 129, 0.15);
            --badge-other-text: #34d399;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 2rem 1rem;
            min-height: 100vh;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 40%);
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 3rem;
            animation: fadeIn 0.8s ease-out;
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }

        .subtitle {
            color: var(--text-muted);
            font-size: 1.1rem;
        }

        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .search-box {
            flex: 1;
            min-width: 250px;
            position: relative;
        }

        .search-box input {
            width: 100%;
            padding: 0.8rem 1.2rem;
            border-radius: 12px;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            color: var(--text-color);
            font-family: inherit;
            font-size: 1rem;
            transition: all 0.3s ease;
            outline: none;
        }

        .search-box input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.25);
        }

        .filters {
            display: flex;
            gap: 0.5rem;
        }

        .filter-btn {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            color: var(--text-muted);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-family: inherit;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .filter-btn:hover {
            color: var(--text-color);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .filter-btn.active {
            background: var(--accent-gradient);
            color: white;
            border-color: transparent;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }

        .loading {
            text-align: center;
            padding: 3rem;
            color: var(--text-muted);
            font-size: 1.2rem;
        }

        .release-group {
            margin-bottom: 2.5rem;
            animation: slideUp 0.6s ease-out both;
        }

        .release-date {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .release-date::after {
            content: '';
            flex: 1;
            height: 1px;
            background: var(--card-border);
        }

        .note-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .note-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: transparent;
            transition: background 0.3s ease;
        }

        .note-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.15);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        }

        .note-card.feature::before { background: var(--badge-feature-text); }
        .note-card.deprecation::before { background: var(--badge-deprecation-text); }
        .note-card.issue::before { background: var(--badge-issue-text); }
        .note-card.other::before { background: var(--badge-other-text); }

        .note-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.8rem;
        }

        .note-actions {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .tweet-btn {
            background: rgba(29, 155, 240, 0.1);
            border: 1px solid rgba(29, 155, 240, 0.2);
            color: #1d9bf0;
            padding: 0.3rem 0.8rem;
            border-radius: 8px;
            font-family: inherit;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.3rem;
            text-decoration: none;
        }

        .tweet-btn:hover {
            background: #1d9bf0;
            color: white;
            border-color: transparent;
            box-shadow: 0 4px 12px rgba(29, 155, 240, 0.2);
        }

        .badge {
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 700;
            padding: 0.25rem 0.75rem;
            border-radius: 100px;
            letter-spacing: 0.5px;
        }

        .badge.feature { background: var(--badge-feature); color: var(--badge-feature-text); }
        .badge.deprecation { background: var(--badge-deprecation); color: var(--badge-deprecation-text); }
        .badge.issue { background: var(--badge-issue); color: var(--badge-issue-text); }
        .badge.other { background: var(--badge-other); color: var(--badge-other-text); }

        .note-content {
            font-size: 1rem;
            color: #d1d5db;
        }

        .note-content p {
            margin-bottom: 0.8rem;
        }

        .note-content p:last-child {
            margin-bottom: 0;
        }

        .note-content a {
            color: #60a5fa;
            text-decoration: none;
            transition: color 0.2s ease;
            font-weight: 500;
        }

        .note-content a:hover {
            color: #93c5fd;
            text-decoration: underline;
        }

        .note-content code {
            background: rgba(255, 255, 255, 0.08);
            padding: 0.2rem 0.4rem;
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.9em;
        }

        .note-content ul {
            margin-left: 1.5rem;
            margin-bottom: 0.8rem;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 600px) {
            h1 { font-size: 2rem; }
            .controls { flex-direction: column; align-items: stretch; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>BigQuery Release Notes</h1>
            <p class="subtitle">Stay updated with the latest changes and improvements to Google Cloud BigQuery</p>
        </header>

        <div class="controls">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search release notes...">
            </div>
            <div class="filters">
                <button class="filter-btn active" data-type="all">All</button>
                <button class="filter-btn" data-type="feature">Features</button>
                <button class="filter-btn" data-type="issue">Issues</button>
                <button class="filter-btn" data-type="deprecation">Deprecations</button>
                <button class="filter-btn" id="refreshBtn" style="display: flex; align-items: center; gap: 0.5rem; background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3); color: #60a5fa;">
                    <svg id="refreshSpinner" style="width: 16px; height: 16px; transition: transform 1s linear;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
                    <span>Refresh</span>
                </button>
            </div>
        </div>

        <div id="notesContainer">
            <div class="loading">Loading release notes...</div>
        </div>
    </div>

    <script>
        let allNotes = [];
        let currentFilter = 'all';
        let searchQuery = '';
        let isRefreshing = false;

        async function fetchNotes() {
            if (isRefreshing) return;
            isRefreshing = true;
            
            const btn = document.getElementById('refreshBtn');
            const spinner = document.getElementById('refreshSpinner');
            const container = document.getElementById('notesContainer');
            
            btn.style.opacity = '0.7';
            btn.style.cursor = 'not-allowed';
            spinner.style.animation = 'spin 1s infinite linear';
            
            // Add spin animation dynamically if not present
            if (!document.getElementById('spin-style')) {
                const style = document.createElement('style');
                style.id = 'spin-style';
                style.innerHTML = '@keyframes spin { 100% { transform: rotate(360deg); } }';
                document.head.appendChild(style);
            }

            try {
                const response = await fetch('/api/notes');
                allNotes = await response.json();
                renderNotes();
            } catch (error) {
                container.innerHTML = `
                    <div class="loading" style="color: var(--badge-deprecation-text)">
                        Failed to load release notes. Please try again later.
                    </div>
                `;
            } finally {
                isRefreshing = false;
                btn.style.opacity = '1';
                btn.style.cursor = 'pointer';
                spinner.style.animation = 'none';
            }
        }

        function determineType(htmlContent) {
            const lower = htmlContent.toLowerCase();
            if (lower.includes('<h3>feature</h3>')) return 'feature';
            if (lower.includes('<h3>issue</h3>')) return 'issue';
            if (lower.includes('<h3>deprecation</h3>')) return 'deprecation';
            return 'other';
        }

        function parseEntries(entries) {
            const parsed = [];
            entries.forEach(entry => {
                const date = entry.title;
                const content = entry.content;
                
                // Split content by <h3> headers to separate multiple notes on the same day
                const sections = content.split(/(?=<h3>)/i);
                
                sections.forEach(section => {
                    if (!section.trim()) return;
                    
                    // Extract type from <h3> header
                    const headerMatch = section.match(/<h3>(.*?)<\/h3>/i);
                    const type = headerMatch ? headerMatch[1].toLowerCase() : 'other';
                    
                    // Remove the H3 tag from content to clean it up
                    const cleanContent = section.replace(/<h3>.*?<\/h3>/i, '').trim();

                    parsed.push({
                        date: date,
                        type: type,
                        content: cleanContent,
                        raw: section
                    });
                });
            });
            return parsed;
        }

        function formatTweetText(note) {
            // strip HTML tags
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = note.content;
            let text = tempDiv.textContent || tempDiv.innerText || "";
            
            // Clean up whitespace
            text = text.replace(/\s+/g, ' ').trim();
            
            // Add prefix/suffix
            const prefix = `BigQuery ${note.type.toUpperCase()} (${note.date}): `;
            const suffix = ` #BigQuery #GoogleCloud`;
            
            // Limit content to fit within Twitter's 280 limit (taking prefix & suffix into account)
            const maxContentLen = 280 - prefix.length - suffix.length - 4; // 4 for '...' etc
            if (text.length > maxContentLen) {
                text = text.substring(0, maxContentLen - 3) + '...';
            }
            
            return encodeURIComponent(prefix + text + suffix);
        }

        function renderNotes() {
            const container = document.getElementById('notesContainer');
            const parsedNotes = parseEntries(allNotes);

            const filtered = parsedNotes.filter(note => {
                const matchesFilter = currentFilter === 'all' || note.type === currentFilter;
                const matchesSearch = note.content.toLowerCase().includes(searchQuery.toLowerCase()) || 
                                      note.date.toLowerCase().includes(searchQuery.toLowerCase()) ||
                                      note.type.toLowerCase().includes(searchQuery.toLowerCase());
                return matchesFilter && matchesSearch;
            });

            if (filtered.length === 0) {
                container.innerHTML = '<div class="loading">No release notes found matching your criteria.</div>';
                return;
            }

            // Group filtered notes by date
            const groups = {};
            filtered.forEach(note => {
                if (!groups[note.date]) {
                    groups[note.date] = [];
                }
                groups[note.date].push(note);
            });

            let html = '';
            let delay = 0;
            for (const [date, notes] of Object.entries(groups)) {
                html += `
                    <div class="release-group" style="animation-delay: ${delay}ms">
                        <div class="release-date">${date}</div>
                        ${notes.map(note => {
                            const tweetText = formatTweetText(note);
                            return `
                                <div class="note-card ${note.type}">
                                    <div class="note-header">
                                        <span class="badge ${note.type}">${note.type}</span>
                                        <div class="note-actions">
                                            <a href="https://twitter.com/intent/tweet?text=${tweetText}" target="_blank" class="tweet-btn">
                                                <svg style="width: 12px; height: 12px;" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                                                <span>Tweet</span>
                                            </a>
                                        </div>
                                    </div>
                                    <div class="note-content">
                                        ${note.content}
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                `;
                delay += 50; // Stagger effect
            }
            container.innerHTML = html;
        }

        // Search Input Event
        document.getElementById('searchInput').addEventListener('input', (e) => {
            searchQuery = e.target.value;
            renderNotes();
        });

        // Filter Button Events
        document.querySelectorAll('.filter-btn').forEach(btn => {
            if (btn.id === 'refreshBtn') {
                btn.addEventListener('click', fetchNotes);
                return;
            }
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.type;
                renderNotes();
            });
        });

        // Initial Fetch
        fetchNotes();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/api/notes")
def get_notes():
    try:
        # Fetch RSS Feed
        req = urllib.request.Request(
            FEED_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        # Parse XML
        root = ET.fromstring(xml_data)
        
        # Atom feed namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text
            content = entry.find('atom:content', ns).text
            updated = entry.find('atom:updated', ns).text
            entries.append({
                'title': title,
                'content': content,
                'updated': updated
            })
            
        return jsonify(entries)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
