"""
=============================================================
  PlaylistToM3U — Spotify CSV → M3U Playlist Converter
  Supports CSV exports from Exportify (exportify.net)
  
  Features:
  - Fuzzy matching with SequenceMatcher
  - CJK (Traditional → Simplified Chinese) normalization
  - Alternative title extraction from parentheses
  - Artist fallback matching
  - Manual alias file (aliases.txt) support
  - Bilingual UI (English / Indonesia)
  
  https://github.com/Dananjaya08/playlisttom3u
=============================================================
"""

import os
import csv
import sys
import glob
import unicodedata
import re
import threading
from difflib import SequenceMatcher

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.scrolledtext as scrolledtext

# Force UTF-8 stdout on Windows for proper Unicode display
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ─────────────────────────────────────────────
#  BILINGUAL LANGUAGE SYSTEM (English / Indonesia)
# ─────────────────────────────────────────────
LANGUAGES = {
    "en": {
        "window_title":       "PlaylistToM3U — Spotify CSV to M3U Converter",
        "config_frame":       " Configuration ",
        "btn_csv":            "Select CSV File...",
        "lbl_csv_empty":      "No CSV file selected.",
        "files_selected":     "{n} files selected.",
        "btn_audio":          "Select Audio Folder...",
        "btn_output":         "Select Output Folder...",
        "threshold_label":    "Similarity Threshold:",
        "language_label":     "Language:",
        "exec_frame":         " Execution ",
        "btn_start":          "Start Conversion",
        "log_frame":          " Activity Log ",
        "status_ready":       "Ready",
        "status_done":        "Done!",
        "status_processing":  "Processing {name}...",
        "status_progress":    "Processing {current}/{total}",
        "msg_no_csv":         "Please select at least one CSV file first!",
        "msg_warn":           "Warning",
        "msg_no_audio":       "No audio files found in the selected folder!",
        "msg_error":          "Error",
        "msg_success_title":  "Success",
        "msg_success":        "Playlist conversion completed!",
        "msg_fatal":          "An error occurred:\n{err}",
        "log_searching":      "Searching for audio files in: {folder}\n",
        "log_found":          "Found {n} audio files.\n",
        "log_no_audio":       "[ERROR] No audio files found!\n",
        "log_aliases":        "Loaded {n} title aliases from aliases.txt\n",
        "log_threshold":      "Similarity threshold set to: {val:.2f}\n",
        "log_csv_count":      "\n[CSV] {name}: {n} songs found in CSV\n",
        "log_alias_used":     "[ALIAS] {orig} -> {alias}\n",
        "log_ok":             "[OK]  [{i:3d}] {track:<35} -> {file:<40} (score: {score:.2f})\n",
        "log_miss":           "[---] [{i:3d}] {track:<35} (score: {score:.2f}) -- NOT FOUND\n",
        "log_fallback_start": "\n[INFO] Running Artist Fallback Matching...\n",
        "log_fallback_hit":   "[FALLBACK] {track:<30} -> {file:<40} (1 remaining file from same artist)\n",
        "log_done_csv":       "\n[DONE] {name}.csv\n",
        "log_done_matched":   "  Matched: {matched}/{total} ({pct:.1f}%)\n",
        "log_done_saved":     "  Saved to: {path}\n",
        "log_all_done":       "\n✅ ALL PROCESSES COMPLETED!\n",
        "log_fatal":          "\n[FATAL ERROR] {err}\n",
        "report_title":       "SPOTIFY CSV -> M3U CONVERSION REPORT",
        "report_csv":         "CSV File  : {path}",
        "report_total":       "Total     : {n} songs",
        "report_matched":     "Matched   : {n} ({pct:.1f}%)",
        "report_unmatched":   "Unmatched : {n} ({pct:.1f}%)",
        "report_matched_hdr": "SUCCESSFULLY MATCHED SONGS",
        "report_unmatch_hdr": "SONGS NOT FOUND",
        "report_filename":    "{name}_report.txt",
        "dlg_csv_title":      "Select CSV File",
        "dlg_audio_title":    "Select Audio Folder",
        "dlg_output_title":   "Select Output Folder",
    },
    "id": {
        "window_title":       "PlaylistToM3U — Konverter Spotify CSV ke M3U",
        "config_frame":       " Konfigurasi ",
        "btn_csv":            "Pilih File CSV...",
        "lbl_csv_empty":      "Belum ada file CSV dipilih.",
        "files_selected":     "{n} file dipilih.",
        "btn_audio":          "Pilih Folder Audio...",
        "btn_output":         "Pilih Folder Output...",
        "threshold_label":    "Ambang Toleransi Kemiripan:",
        "language_label":     "Bahasa:",
        "exec_frame":         " Eksekusi ",
        "btn_start":          "Mulai Konversi",
        "log_frame":          " Log Aktivitas ",
        "status_ready":       "Siap",
        "status_done":        "Selesai!",
        "status_processing":  "Memproses {name}...",
        "status_progress":    "Memproses {current}/{total}",
        "msg_no_csv":         "Pilih minimal satu file CSV terlebih dahulu!",
        "msg_warn":           "Peringatan",
        "msg_no_audio":       "Tidak ada file audio ditemukan di folder tersebut!",
        "msg_error":          "Error",
        "msg_success_title":  "Sukses",
        "msg_success":        "Konversi playlist telah selesai!",
        "msg_fatal":          "Terjadi kesalahan:\n{err}",
        "log_searching":      "Memulai pencarian file audio di: {folder}\n",
        "log_found":          "Ditemukan {n} file audio.\n",
        "log_no_audio":       "[ERROR] Tidak ada file audio ditemukan!\n",
        "log_aliases":        "Memuat {n} alias judul dari aliases.txt\n",
        "log_threshold":      "Ambang batas kemiripan diatur pada: {val:.2f}\n",
        "log_csv_count":      "\n[CSV] {name}: {n} lagu ditemukan di CSV\n",
        "log_alias_used":     "[ALIAS] {orig} -> {alias}\n",
        "log_ok":             "[OK]  [{i:3d}] {track:<35} -> {file:<40} (skor: {score:.2f})\n",
        "log_miss":           "[---] [{i:3d}] {track:<35} (skor: {score:.2f}) -- TIDAK DITEMUKAN\n",
        "log_fallback_start": "\n[INFO] Menjalankan Fallback Pencocokan Artis...\n",
        "log_fallback_hit":   "[FALLBACK] {track:<30} -> {file:<40} (Sisa 1 file dr artis yg sama)\n",
        "log_done_csv":       "\n[SELESAI] {name}.csv\n",
        "log_done_matched":   "  Cocok: {matched}/{total} ({pct:.1f}%)\n",
        "log_done_saved":     "  Tersimpan: {path}\n",
        "log_all_done":       "\n✅ SEMUA PROSES SELESAI!\n",
        "log_fatal":          "\n[FATAL ERROR] {err}\n",
        "report_title":       "LAPORAN KONVERSI SPOTIFY CSV -> M3U",
        "report_csv":         "File CSV  : {path}",
        "report_total":       "Total     : {n} lagu",
        "report_matched":     "Cocok     : {n} ({pct:.1f}%)",
        "report_unmatched":   "Tidak Cocok: {n} ({pct:.1f}%)",
        "report_matched_hdr": "LAGU YANG BERHASIL DICOCOKKAN",
        "report_unmatch_hdr": "LAGU YANG TIDAK DITEMUKAN",
        "report_filename":    "{name}_laporan.txt",
        "dlg_csv_title":      "Pilih File CSV",
        "dlg_audio_title":    "Pilih Folder Audio",
        "dlg_output_title":   "Pilih Folder Output",
    },
}


# ─────────────────────────────────────────────
#  DEFAULT CONFIGURATION
# ─────────────────────────────────────────────
AUDIO_EXTENSIONS = [".flac", ".mp3", ".wav", ".aac", ".m4a", ".ogg", ".opus"]

COL_TRACK       = "Track Name"
COL_ARTIST      = "Artist Name(s)"
COL_ALBUM       = "Album Name"
COL_DURATION_MS = "Track Duration (ms)"


# ─────────────────────────────────────────────
#  UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def ms_to_seconds(ms_str: str) -> int:
    try:
        return int(ms_str) // 1000
    except (ValueError, TypeError):
        return -1


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[_\-\.\(\)\[\]&,!*+#'~]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


# ─────────────────────────────────────────────
#  Traditional → Simplified Chinese Conversion
# ─────────────────────────────────────────────
TRAD_TO_SIMP = str.maketrans(
    '鴻圖來財攬華國東書車門開學長時萬電風飛機見親頭馬魚鳥點齊齒龍龜樂發與'
    '讓說認議買賣運過進還這邊達選遠連話該論調關陽際飯麼廣應從復後義聽體對導'
    '將師歸條區醫問間類實寫響雙動節單歡戰傳報壓離圓場夢愛寶專屬歷歲殺產織職'
    '蘭衛覺課貓質遊極稱種紅結統網給習裝計記設試詞語費軍輕轉辦當燈聯個備優價'
    '傑勝創勵務堅壞夠奮獎媽農勞須衝遲衆劍',
    '鸿图来财揽华国东书车门开学长时万电风飞机见亲头马鱼鸟点齐齿龙龟乐发与'
    '让说认议买卖运过进还这边达选远连话该论调关阳际饭么广应从复后义听体对导'
    '将师归条区医问间类实写响双动节单欢战传报压离圆场梦爱宝专属历岁杀产织职'
    '兰卫觉课猫质游极称种红结统网给习装计记设试词语费军轻转办当灯联个备优价'
    '杰胜创励务坚坏够奋奖妈农劳须冲迟众剑'
)


def trad_to_simp(text: str) -> str:
    """Convert Traditional Chinese characters to Simplified for comparison."""
    return text.translate(TRAD_TO_SIMP)


def extract_alt_titles(text: str) -> list[str]:
    """Extract alternative titles from inside parentheses/brackets.
    
    Example: '大展鴻圖(Blueprint Supreme)' → ['Blueprint Supreme']
    """
    alts = []
    for m in re.findall(r'[（(]([^)）]+)[）)]', text):
        cleaned = m.strip()
        if cleaned and len(cleaned) >= 2:
            if not re.match(r'^(?:feat|ft|with|from)\b', cleaned, re.IGNORECASE):
                alts.append(cleaned)
    for m in re.findall(r'[【\[]([^\]】]+)[】\]]', text):
        cleaned = m.strip()
        if cleaned and len(cleaned) >= 2:
            alts.append(cleaned)
    return alts


# ─────────────────────────────────────────────
#  FILENAME PARSING & MATCHING
# ─────────────────────────────────────────────

def parse_filename(filename: str) -> dict:
    name = os.path.splitext(filename)[0]
    cleaned = re.sub(r"^\d+[\s]*[-._]+\s*", "", name)
    
    artist = ""
    track  = ""
    
    if " - " in cleaned:
        parts = cleaned.split(" - ", 1)
        artist = parts[0].strip()
        track  = parts[1].strip()
    elif "," in cleaned:
        parts = cleaned.split(",", 1)
        artist = parts[0].strip()
        track  = parts[1].strip()
    else:
        track = cleaned.strip()
    
    return {
        "artist": normalize(artist),
        "track":  normalize(track),
        "full":   normalize(cleaned),
    }


def score_match(csv_track: str, csv_artist: str, file_info: dict) -> float:
    norm_csv_track  = normalize(csv_track)
    norm_csv_artist = normalize(csv_artist)
    
    # Extract core track title (strip feat, parentheses, etc.)
    base_csv_track = re.split(r'[（(【\[\-]', csv_track)[0].strip()
    norm_base_csv_track = normalize(base_csv_track)
    if not norm_base_csv_track:
        norm_base_csv_track = norm_csv_track
    
    # Alternative titles from parentheses (e.g. "Blueprint Supreme")
    alt_titles = extract_alt_titles(csv_track)
    norm_alts = [normalize(a) for a in alt_titles if normalize(a)]
    
    # Simplified Chinese versions
    simp_csv_track = trad_to_simp(norm_csv_track)
    simp_base = trad_to_simp(norm_base_csv_track)
    
    # Individual artists from CSV (split by comma)
    individual_artists = [normalize(a.strip()) for a in csv_artist.split(',') if normalize(a.strip())]
    
    file_track  = file_info["track"]
    file_artist = file_info["artist"]
    file_full   = file_info["full"]
    
    def _calc(f_track, f_artist):
        # === TRACK TITLE SCORE ===
        track_sim = similarity(norm_csv_track, f_track)
        track_full_sim = similarity(norm_csv_track, file_full)
        base_track_sim = similarity(norm_base_csv_track, f_track)
        base_track_full_sim = similarity(norm_base_csv_track, file_full)
        
        # Simplified Chinese comparison
        sf_track = trad_to_simp(f_track)
        sf_full = trad_to_simp(file_full)
        simp_track_sim = similarity(simp_csv_track, sf_track)
        simp_base_sim = similarity(simp_base, sf_track)
        simp_full_sim = similarity(simp_base, sf_full)
        
        # Alternative title comparison (from parentheses)
        alt_best = 0.0
        for alt in norm_alts:
            alt_sim = max(similarity(alt, f_track), similarity(alt, file_full) * 0.9)
            alt_best = max(alt_best, alt_sim)
        
        track_score = max(
            track_sim, 
            track_full_sim * 0.9, 
            base_track_sim * 0.95, 
            base_track_full_sim * 0.85,
            simp_track_sim,
            simp_base_sim * 0.95,
            simp_full_sim * 0.85,
            alt_best * 0.95,
        )
        
        # === SUBSTRING BONUS ===
        substring_bonus = 0.0
        target_sub = norm_base_csv_track if len(norm_base_csv_track) >= 3 else norm_csv_track
        simp_target = trad_to_simp(target_sub)
        if len(target_sub) >= 3:
            if target_sub in file_full or simp_target in trad_to_simp(file_full):
                substring_bonus = 0.25
            elif f_track and (f_track in target_sub or trad_to_simp(f_track) in simp_target):
                substring_bonus = 0.15
            else:
                for alt in norm_alts:
                    if len(alt) >= 3 and (alt in file_full or alt in f_track):
                        substring_bonus = 0.20
                        break
        
        # === ARTIST SCORE ===
        artist_score = 0.0
        if norm_csv_artist and f_artist:
            artist_score = similarity(norm_csv_artist, f_artist)
            simp_art = similarity(trad_to_simp(norm_csv_artist), trad_to_simp(f_artist))
            artist_score = max(artist_score, simp_art)
            if norm_csv_artist in f_artist or f_artist in norm_csv_artist:
                artist_score = max(artist_score, 0.8)
        
        # Check individual artists (comma-split) — also check in file_full
        for ind in individual_artists:
            if ind and len(ind) >= 2:
                if f_artist:
                    ind_sim = similarity(ind, f_artist)
                    if ind in f_artist or f_artist in ind:
                        ind_sim = max(ind_sim, 0.85)
                    artist_score = max(artist_score, ind_sim)
                if ind in file_full:
                    artist_score = max(artist_score, 0.75)
        
        # === FINAL SCORE (pick best formula) ===
        with_artist = (track_score * 0.65) + (artist_score * 0.25) + substring_bonus
        without_artist = (track_score * 0.85) + substring_bonus
        final = max(with_artist, without_artist)
            
        return final

    score_normal = _calc(file_track, file_artist)
    score_swapped = _calc(file_artist, file_track)
    
    return min(max(score_normal, score_swapped), 1.0)


def find_best_match(csv_track: str, csv_artist: str, candidates: list[str], 
                     file_cache: dict, threshold: float) -> tuple[str | None, float]:
    best_file  = None
    best_score = 0.0

    for filename in candidates:
        if filename not in file_cache:
            file_cache[filename] = parse_filename(filename)
        
        file_info = file_cache[filename]
        score = score_match(csv_track, csv_artist, file_info)

        if score > best_score:
            best_score = score
            best_file  = filename

    if best_score >= threshold:
        return best_file, best_score
    return None, best_score


def collect_audio_files(folder: str, extensions: list[str]) -> list[str]:
    files = []
    for ext in extensions:
        pattern = os.path.join(folder, f"*{ext}")
        files.extend([os.path.basename(p) for p in glob.glob(pattern)])
    return files


def load_aliases(audio_folder: str) -> dict:
    """Read aliases.txt if present for manual title translation."""
    alias_path = os.path.join(audio_folder, "aliases.txt")
    aliases = {}
    if os.path.exists(alias_path):
        try:
            with open(alias_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        parts = line.split("=", 1)
                        orig = parts[0].strip()
                        alias = parts[1].strip()
                        if orig and alias:
                            aliases[orig] = alias
        except Exception:
            pass
    return aliases


def process_csv(csv_path: str, audio_pool: list[str], threshold: float, 
                aliases: dict, lang: dict, log_callback, progress_callback) -> tuple[list[dict], list[dict]]:
    matched   = []
    unmatched = []

    file_cache = {}

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows   = list(reader)

    total_rows = len(rows)
    log_callback(lang["log_csv_count"].format(name=os.path.basename(csv_path), n=total_rows))

    # Pre-cache all file info
    for filename in audio_pool:
        if filename not in file_cache:
            file_cache[filename] = parse_filename(filename)

    # ═══════════════════════════════════════════════════════
    #  PASS 1: Compute best match for EVERY CSV entry
    #          (do NOT remove files from pool yet)
    # ═══════════════════════════════════════════════════════
    candidates = []  # list of {index, track, artist, album, dur_ms, best_file, score}

    for i, row in enumerate(rows, 1):
        orig_track = row.get(COL_TRACK,  "").strip()
        artist = row.get(COL_ARTIST, "").strip()
        album  = row.get(COL_ALBUM,  "").strip()
        dur_ms = row.get(COL_DURATION_MS, "0").strip()

        # Use alias if available
        track = aliases.get(orig_track, orig_track)
        if track != orig_track:
            log_callback(lang["log_alias_used"].format(orig=orig_track, alias=track))

        # Find best match against ALL files (no removal)
        best_file, best_score = find_best_match(track, artist, audio_pool, file_cache, threshold)

        candidates.append({
            "index":      i,
            "orig_track": orig_track,
            "track":      track,
            "artist":     artist,
            "album":      album,
            "dur_ms":     dur_ms,
            "best_file":  best_file,
            "score":      best_score,
        })

        progress_callback(i, total_rows)

    # ═══════════════════════════════════════════════════════
    #  PASS 2: Assign matches greedily by HIGHEST SCORE FIRST
    #          This resolves conflicts — if two CSV entries want
    #          the same file, the one with the higher score wins.
    # ═══════════════════════════════════════════════════════
    log_callback(lang.get("log_pass2_start", "\n[PASS 2] Resolving conflicts — highest score wins...\n"))

    # Sort by score descending (highest confidence first)
    sorted_candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)

    assigned_files = set()     # files already taken
    assigned_indices = set()   # CSV indices already matched

    for c in sorted_candidates:
        if c["best_file"] and c["best_file"] not in assigned_files:
            # This file is available — assign it
            matched.append({
                "index":   c["index"],
                "file":    c["best_file"],
                "track":   c["orig_track"],
                "artist":  c["artist"],
                "album":   c["album"],
                "dur_sec": ms_to_seconds(c["dur_ms"]),
                "score":   c["score"],
            })
            assigned_files.add(c["best_file"])
            assigned_indices.add(c["index"])
            log_callback(lang["log_ok"].format(
                i=c["index"], track=c["track"][:35], 
                file=c["best_file"][:40], score=c["score"]))
        # If file was already taken, this entry needs re-matching (handled below)

    # ═══════════════════════════════════════════════════════
    #  PASS 3: Re-match entries whose file was stolen
    #          Try to find their next-best match
    # ═══════════════════════════════════════════════════════
    remaining_pool = [f for f in audio_pool if f not in assigned_files]

    for c in candidates:
        if c["index"] in assigned_indices:
            continue  # already matched

        # Try to find a new match from remaining pool
        if remaining_pool:
            new_file, new_score = find_best_match(
                c["track"], c["artist"], remaining_pool, file_cache, threshold)

            if new_file:
                matched.append({
                    "index":   c["index"],
                    "file":    new_file,
                    "track":   c["orig_track"],
                    "artist":  c["artist"],
                    "album":   c["album"],
                    "dur_sec": ms_to_seconds(c["dur_ms"]),
                    "score":   new_score,
                })
                assigned_files.add(new_file)
                assigned_indices.add(c["index"])
                remaining_pool.remove(new_file)
                log_callback(lang["log_ok"].format(
                    i=c["index"], track=c["track"][:35], 
                    file=new_file[:40], score=new_score))
                continue

        # No match found at all
        unmatched.append({
            "index":   c["index"],
            "track":   c["orig_track"],
            "artist":  c["artist"],
            "album":   c["album"],
            "dur_ms":  c["dur_ms"],
            "score":   c["score"],
        })
        log_callback(lang["log_miss"].format(
            i=c["index"], track=c["orig_track"][:35], score=c["score"]))

    # === ARTIST FALLBACK ===
    available = [f for f in audio_pool if f not in assigned_files]
    if unmatched and available:
        log_callback(lang["log_fallback_start"])
        still_unmatched = []
        for u in unmatched:
            u_track = u["track"]
            u_artist = u["artist"]
            norm_u_art = normalize(u_artist)
            
            possible_files = []
            for f in available:
                if f not in file_cache:
                    file_cache[f] = parse_filename(f)
                f_art = file_cache[f]["artist"]
                f_full = file_cache[f]["full"]
                
                # Check individual artists
                ind_arts = [normalize(a.strip()) for a in u_artist.split(',') if normalize(a.strip())]
                is_match = False
                for ind in ind_arts:
                    if len(ind) >= 3 and (ind in f_art or f_art in ind or ind in f_full):
                        is_match = True
                        break
                
                if is_match or similarity(norm_u_art, f_art) >= 0.8:
                    possible_files.append(f)
            
            # If exactly 1 file matches the artist, pair them
            if len(possible_files) == 1:
                f_match = possible_files[0]
                matched.append({
                    "index":   u["index"],
                    "file":    f_match,
                    "track":   u_track,
                    "artist":  u_artist,
                    "album":   u.get("album", ""),
                    "dur_sec": ms_to_seconds(u.get("dur_ms", "0")),
                    "score":   0.99,
                })
                available.remove(f_match)
                log_callback(lang["log_fallback_hit"].format(track=u_track[:30], file=f_match[:40]))
            else:
                still_unmatched.append(u)
                
        unmatched = still_unmatched

    # Sort by original CSV position to preserve playlist order
    matched.sort(key=lambda x: x["index"])

    return matched, unmatched


def write_m3u(output_path: str, tracks: list[dict]):
    """Write a simple M3U file — filenames only, no headers (maximum compatibility)."""
    with open(output_path, "w", encoding="utf-8", newline='\n') as f:
        for t in tracks:
            f.write(f"{t['file']}\n")


def write_report(report_path: str, csv_file: str, matched: list[dict], 
                 unmatched: list[dict], lang: dict):
    total = len(matched) + len(unmatched)
    pct   = (len(matched) / total * 100) if total else 0

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"{lang['report_title']}\n")
        f.write(f"{'='*60}\n")
        f.write(f"{lang['report_csv'].format(path=csv_file)}\n")
        f.write(f"{lang['report_total'].format(n=total)}\n")
        f.write(f"{lang['report_matched'].format(n=len(matched), pct=pct)}\n")
        f.write(f"{lang['report_unmatched'].format(n=len(unmatched), pct=100-pct)}\n\n")

        f.write(f"{'-'*60}\n{lang['report_matched_hdr']}\n{'-'*60}\n")
        for t in matched:
            f.write(f"  [{t['score']:.2f}] {t['track']} - {t['artist']}\n")
            f.write(f"          -> {t['file']}\n")

        if unmatched:
            f.write(f"\n{'-'*60}\n{lang['report_unmatch_hdr']}\n{'-'*60}\n")
            for t in unmatched:
                f.write(f"  - {t['track']} - {t['artist']}\n")


# ─────────────────────────────────────────────
#  GUI (Tkinter) IMPLEMENTATION
# ─────────────────────────────────────────────

class PlaylistConverterApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "en"
        self.lang = LANGUAGES[self.current_lang]
        
        self.root.title(self.lang["window_title"])
        self.root.geometry("780x620")
        self.root.minsize(650, 520)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.csv_files = []
        self.audio_folder = os.path.dirname(os.path.abspath(__file__))
        self.output_folder = self.audio_folder
        
        self.create_widgets()
        
    def t(self, key: str) -> str:
        """Get translated string for the current language."""
        return self.lang.get(key, key)
        
    def create_widgets(self):
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Configuration Frame ---
        self.config_frame = ttk.LabelFrame(main_frame, text=self.t("config_frame"), padding="10")
        self.config_frame.pack(fill=tk.X, pady=5)
        
        # Language Selector (top-right feel)
        ttk.Label(self.config_frame, text=self.t("language_label")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.lang_var = tk.StringVar(value="English")
        self.lang_combo = ttk.Combobox(self.config_frame, textvariable=self.lang_var, 
                                        values=["English", "Indonesia"], state="readonly", width=12)
        self.lang_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Select CSV
        self.btn_csv = ttk.Button(self.config_frame, text=self.t("btn_csv"), command=self.select_csv)
        self.btn_csv.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.lbl_csv = ttk.Label(self.config_frame, text=self.t("lbl_csv_empty"))
        self.lbl_csv.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Select Audio Folder
        self.btn_audio = ttk.Button(self.config_frame, text=self.t("btn_audio"), command=self.select_audio_folder)
        self.btn_audio.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.lbl_audio = ttk.Label(self.config_frame, text=self.audio_folder)
        self.lbl_audio.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

        # Select Output Folder
        self.btn_output = ttk.Button(self.config_frame, text=self.t("btn_output"), command=self.select_output_folder)
        self.btn_output.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.lbl_output = ttk.Label(self.config_frame, text=self.output_folder)
        self.lbl_output.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Threshold Slider
        self.lbl_threshold_title = ttk.Label(self.config_frame, text=self.t("threshold_label"))
        self.lbl_threshold_title.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(15,0))
        
        self.threshold_val = tk.DoubleVar(value=0.55)
        self.slider_threshold = ttk.Scale(self.config_frame, from_=0.0, to=1.0, 
                                           variable=self.threshold_val, orient=tk.HORIZONTAL, 
                                           length=200, command=self.update_threshold_lbl)
        self.slider_threshold.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        self.lbl_threshold = ttk.Label(self.config_frame, text="0.55")
        self.lbl_threshold.grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
        
        # --- Execution Frame ---
        exec_frame = ttk.Frame(main_frame, padding="5")
        exec_frame.pack(fill=tk.X, pady=5)
        
        self.btn_start = ttk.Button(exec_frame, text=self.t("btn_start"), command=self.start_conversion)
        self.btn_start.pack(side=tk.LEFT, ipadx=20, ipady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(exec_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15)
        
        self.lbl_status = ttk.Label(exec_frame, text=self.t("status_ready"))
        self.lbl_status.pack(side=tk.LEFT)
        
        # --- Log Output Frame ---
        self.log_frame = ttk.LabelFrame(main_frame, text=self.t("log_frame"), padding="10")
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.txt_log = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, 
                                                  bg="#1e1e1e", fg="#00ff00", 
                                                  font=("Consolas", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        self.txt_log.config(state=tk.DISABLED)

    def on_language_change(self, event=None):
        """Switch UI language when the combobox selection changes."""
        selected = self.lang_var.get()
        self.current_lang = "id" if selected == "Indonesia" else "en"
        self.lang = LANGUAGES[self.current_lang]
        self.refresh_ui_text()
    
    def refresh_ui_text(self):
        """Update all UI widget text to the current language."""
        self.root.title(self.t("window_title"))
        self.config_frame.config(text=self.t("config_frame"))
        self.btn_csv.config(text=self.t("btn_csv"))
        self.btn_audio.config(text=self.t("btn_audio"))
        self.btn_output.config(text=self.t("btn_output"))
        self.lbl_threshold_title.config(text=self.t("threshold_label"))
        self.btn_start.config(text=self.t("btn_start"))
        self.log_frame.config(text=self.t("log_frame"))
        self.lbl_status.config(text=self.t("status_ready"))
        
        # Update CSV label
        if not self.csv_files:
            self.lbl_csv.config(text=self.t("lbl_csv_empty"))
        elif len(self.csv_files) == 1:
            self.lbl_csv.config(text=os.path.basename(self.csv_files[0]))
        else:
            self.lbl_csv.config(text=self.t("files_selected").format(n=len(self.csv_files)))

    def update_threshold_lbl(self, val):
        self.lbl_threshold.config(text=f"{float(val):.2f}")
        
    def select_csv(self):
        files = filedialog.askopenfilenames(
            title=self.t("dlg_csv_title"),
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        if files:
            self.csv_files = list(files)
            if len(self.csv_files) == 1:
                self.lbl_csv.config(text=os.path.basename(self.csv_files[0]))
            else:
                self.lbl_csv.config(text=self.t("files_selected").format(n=len(self.csv_files)))
                
    def select_audio_folder(self):
        folder = filedialog.askdirectory(title=self.t("dlg_audio_title"), initialdir=self.audio_folder)
        if folder:
            self.audio_folder = folder
            self.lbl_audio.config(text=self.audio_folder)
            
    def select_output_folder(self):
        folder = filedialog.askdirectory(title=self.t("dlg_output_title"), initialdir=self.output_folder)
        if folder:
            self.output_folder = folder
            self.lbl_output.config(text=self.output_folder)
            
    def log(self, message):
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.insert(tk.END, message)
        self.txt_log.see(tk.END)
        self.txt_log.config(state=tk.DISABLED)
        
    def set_status(self, text, progress=None):
        self.lbl_status.config(text=text)
        if progress is not None:
            self.progress_var.set(progress)
        self.root.update_idletasks()
        
    def start_conversion(self):
        if not self.csv_files:
            messagebox.showwarning(self.t("msg_warn"), self.t("msg_no_csv"))
            return
            
        self.btn_start.config(state=tk.DISABLED)
        self.btn_csv.config(state=tk.DISABLED)
        self.btn_audio.config(state=tk.DISABLED)
        self.btn_output.config(state=tk.DISABLED)
        self.slider_threshold.config(state=tk.DISABLED)
        self.lang_combo.config(state=tk.DISABLED)
        
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.config(state=tk.DISABLED)
        
        self.progress_var.set(0)
        
        # Run in separate thread to keep GUI responsive
        t = threading.Thread(target=self.run_conversion_process)
        t.daemon = True
        t.start()
        
    def run_conversion_process(self):
        lang = self.lang  # Capture current language for this run
        try:
            self.log(lang["log_searching"].format(folder=self.audio_folder))
            audio_pool = collect_audio_files(self.audio_folder, AUDIO_EXTENSIONS)
            
            self.log(lang["log_found"].format(n=len(audio_pool)))
            if not audio_pool:
                self.log(lang["log_no_audio"])
                messagebox.showerror(lang["msg_error"], lang["msg_no_audio"])
                self.finish_conversion()
                return
                
            # Load aliases from audio folder
            aliases = load_aliases(self.audio_folder)
            if aliases:
                self.log(lang["log_aliases"].format(n=len(aliases)))
                
            threshold = self.threshold_val.get()
            self.log(lang["log_threshold"].format(val=threshold))
            self.log("-" * 60 + "\n")
            
            for index, csv_path in enumerate(self.csv_files):
                self.set_status(lang["status_processing"].format(name=os.path.basename(csv_path)))
                
                def update_progress(current, total, _idx=index):
                    base_prog = (_idx / len(self.csv_files)) * 100
                    file_prog = (current / total) * (100 / len(self.csv_files))
                    self.set_status(lang["status_progress"].format(current=current, total=total), 
                                   base_prog + file_prog)
                
                matched, unmatched = process_csv(csv_path, audio_pool, threshold, aliases, 
                                                  lang, self.log, update_progress)
                
                csv_name   = os.path.splitext(os.path.basename(csv_path))[0]
                output_m3u = os.path.join(self.output_folder, f"{csv_name}.m3u")
                report_txt = os.path.join(self.output_folder, lang["report_filename"].format(name=csv_name))
                
                write_m3u(output_m3u, matched)
                write_report(report_txt, csv_path, matched, unmatched, lang)
                
                total_songs = len(matched) + len(unmatched)
                pct = (len(matched) / total_songs * 100) if total_songs else 0
                
                self.log(lang["log_done_csv"].format(name=csv_name))
                self.log(lang["log_done_matched"].format(matched=len(matched), total=total_songs, pct=pct))
                self.log(lang["log_done_saved"].format(path=output_m3u))
                self.log("-" * 60 + "\n")
                
            self.log(lang["log_all_done"])
            self.set_status(lang["status_done"], 100)
            messagebox.showinfo(lang["msg_success_title"], lang["msg_success"])
            
        except Exception as e:
            self.log(lang["log_fatal"].format(err=str(e)))
            messagebox.showerror(lang["msg_error"], lang["msg_fatal"].format(err=str(e)))
            
        finally:
            self.finish_conversion()
            
    def finish_conversion(self):
        self.btn_start.config(state=tk.NORMAL)
        self.btn_csv.config(state=tk.NORMAL)
        self.btn_audio.config(state=tk.NORMAL)
        self.btn_output.config(state=tk.NORMAL)
        self.slider_threshold.config(state=tk.NORMAL)
        self.lang_combo.config(state="readonly")


def main():
    root = tk.Tk()
    app = PlaylistConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()