# 🎵 PlaylistToM3U

> 📖 [Baca dalam Bahasa Indonesia](README_ID.md)

**Convert Spotify playlist CSV exports into M3U playlist files** by fuzzy-matching track titles and artist names against your local audio library.

Built for music collectors who use [Exportify](https://exportify.net/) to export their Spotify playlists and want to play them on offline music players like **Hiby Music**, **foobar2000**, **Poweramp**, or any M3U-compatible player.

## ✨ Features

| Feature | Description |
|---|---|
| **Fuzzy Matching** | Uses `SequenceMatcher` to match even when filenames differ from Spotify metadata |
| **CJK Support** | Converts Traditional → Simplified Chinese for better matching of Chinese-titled songs |
| **Alternative Titles** | Extracts titles from parentheses — e.g. `大展鴻圖(Blueprint Supreme)` matches `Blueprint Supreme` |
| **Artist Fallback** | If title matching fails but the artist matches, auto-pairs when only 1 file remains from that artist |
| **Manual Aliases** | Create `aliases.txt` for manual title mappings (great for Japanese ↔ English titles) |
| **Bilingual UI** | Switch between **English** and **Indonesia** at any time |
| **Simple M3U Output** | Outputs filename-only M3U files (maximum compatibility with all players) |
| **Detailed Reports** | Generates a text report showing matched/unmatched songs with similarity scores |

## 📦 Installation

### Option 1: Download the EXE (Windows)

Download `playlisttom3u_v1.1.exe` from the [Releases](https://github.com/Dananjaya08/playlist-to-m3u/releases) page. No installation needed — just double-click and run.

### Option 2: Run from Source

```bash
# Clone the repository
git clone https://github.com/Dananjaya08/playlist-to-m3u.git
cd playlist-to-m3u

# Run (requires Python 3.10+, no external dependencies needed)
python playlisttom3u.py
```

## 🚀 Usage

### Step 1: Export your Spotify playlist
1. Go to [exportify.net](https://exportify.net/)
2. Log in with your Spotify account
3. Export your playlist as CSV

### Step 2: Run PlaylistToM3U
1. Launch `playlisttom3u_v1.1.exe` (or run `python playlisttom3u.py`)
2. **Select Language** — choose English or Indonesia from the dropdown
3. **Select CSV File** — pick the CSV file(s) you exported from Exportify
4. **Select Audio Folder** — choose the folder containing your local audio files (FLAC, MP3, etc.)
5. **Select Output Folder** — choose where to save the M3U and report files
6. **Adjust Threshold** — set the similarity threshold (default `0.55` works well for most cases)
7. Click **Start Conversion**

### Step 3: Load the M3U in your music player
Copy the generated `.m3u` file to your music player or device. The M3U file contains simple filenames — make sure it's in the same folder as your audio files.

## 📝 Aliases (Manual Title Mapping)

For songs where the CSV title is in a completely different language from the filename (e.g. Japanese titles vs English filenames), create a file called **`aliases.txt`** in your **audio folder**.

### Format
```
# Lines starting with # are comments
# Format: CSV Title = Filename Title

ラビットホール = Rabbit Hole
神のまにまに = At God's Mercy
ワンダーランズ×ショウタイム = Wonderlands×Showtime
```

The converter will automatically read this file and use the aliases during matching.

## 🔧 How It Works

```
CSV Entry                          Audio File
┌──────────────────────────┐      ┌──────────────────────────────┐
│ Track: "Rabbit Hole"     │      │ 01 - DECO27 - Rabbit Hole.flac│
│ Artist: "DECO*27"        │      └──────────────────────────────┘
└──────────────────────────┘                    │
            │                                   │
            ▼                                   ▼
    ┌───────────────┐                  ┌───────────────┐
    │  normalize()  │                  │parse_filename()│
    │  "rabbit hole"│                  │track:"rabbit hole"│
    │  "deco 27"    │                  │artist:"deco27"│
    └───────────────┘                  └───────────────┘
            │                                   │
            └─────────────┬─────────────────────┘
                          ▼
                 ┌─────────────────┐
                 │  score_match()  │
                 │  Similarity: 0.99│
                 │  ✅ MATCHED!    │
                 └─────────────────┘
```

### Matching Pipeline
1. **Normalize** — Strip special characters, convert to lowercase
2. **Base Track** — Extract core title (remove feat, parentheses, etc.)
3. **CJK Convert** — Traditional → Simplified Chinese
4. **Alt Titles** — Extract titles from inside parentheses
5. **Score** — Combine track similarity + artist similarity + substring bonuses
6. **Fallback** — If standard matching fails, try artist-only matching

## 🆕 Recent Updates

**v1.1 (Latest)**
- **Two-Pass Matching Algorithm**: Replaced sequential matching with a two-pass algorithm. The converter now computes scores for all files first, and assigns matches by highest score (greedy assignment). This resolves conflicts where low-score matches could "steal" files from perfect matches, fixing false negatives and significantly improving overall accuracy.

## 🏗️ Building from Source

```bash
# Install PyInstaller
pip install pyinstaller

# Build the EXE
python -m PyInstaller --onefile --windowed --name playlisttom3u_v1.1 playlisttom3u.py

# The EXE will be in the dist/ folder
```

## 📁 Supported Audio Formats

`.flac` `.mp3` `.wav` `.aac` `.m4a` `.ogg` `.opus`

## 🌐 Supported Languages

- 🇺🇸 English
- 🇮🇩 Indonesia

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 🙏 Credits & Contributors

- **[Dananjaya08](https://github.com/Dananjaya08)** — Project creator & maintainer
- **[Google Gemini](https://gemini.google.com/)** — AI assistant that helped design the matching algorithm, CJK support, and overall architecture
- **[Anthropic Claude](https://claude.ai/)** — AI assistant that helped implement bilingual UI, artist fallback logic, documentation, and polish the final release
- **[Exportify](https://exportify.net/)** — Spotify playlist CSV export tool
- Built with Python's `difflib.SequenceMatcher` and Tkinter

> This project was made possible through human-AI collaboration. Gemini and Claude helped turn a simple idea into a fully-featured playlist converter — from debugging matching issues to handling CJK characters and building the final release. 🤝

