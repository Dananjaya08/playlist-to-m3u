# 🎵 PlaylistToM3U

> 📖 [Read this in English](README.md)

**Konversi ekspor CSV playlist Spotify menjadi file playlist M3U** dengan mencocokkan judul lagu dan nama artis secara fuzzy terhadap koleksi audio lokal Anda.

Dibuat untuk kolektor musik yang menggunakan [Exportify](https://exportify.net/) untuk mengekspor playlist Spotify mereka dan ingin memutarnya di pemutar musik offline seperti **Hiby Music**, **foobar2000**, **Poweramp**, atau pemutar M3U lainnya.

## ✨ Fitur

| Fitur | Deskripsi |
|---|---|
| **Pencocokan Fuzzy** | Menggunakan `SequenceMatcher` untuk mencocokkan meskipun nama file berbeda dari metadata Spotify |
| **Dukungan CJK** | Konversi China Tradisional → Simplified untuk pencocokan judul lagu China yang lebih baik |
| **Judul Alternatif** | Mengekstrak judul dari dalam kurung — misal `大展鴻圖(Blueprint Supreme)` mencocokkan `Blueprint Supreme` |
| **Fallback Artis** | Jika pencocokan judul gagal tapi artis cocok, otomatis dipasangkan jika hanya tersisa 1 file dari artis tersebut |
| **Alias Manual** | Buat `aliases.txt` untuk pemetaan judul manual (cocok untuk judul Jepang ↔ Inggris) |
| **UI Dwi-Bahasa** | Pilih antara **English** dan **Indonesia** kapan saja |
| **Output M3U Sederhana** | Menghasilkan file M3U berisi nama file saja (kompatibilitas maksimal dengan semua pemutar) |
| **Laporan Detail** | Menghasilkan laporan teks yang menampilkan lagu yang cocok/tidak cocok beserta skor kemiripan |

## 📦 Instalasi

### Opsi 1: Download EXE (Windows)

Download `playlisttom3u_v1.2.exe` dari halaman [Releases](https://github.com/Dananjaya08/playlist-to-m3u/releases). Tidak perlu instalasi — cukup klik dua kali dan jalankan.

### Opsi 2: Jalankan dari Source Code

```bash
# Clone repository
git clone https://github.com/Dananjaya08/playlist-to-m3u.git
cd playlist-to-m3u

# Jalankan (membutuhkan Python 3.10+, tidak perlu dependensi eksternal)
python playlisttom3u.py
```

## 🚀 Cara Penggunaan

### Langkah 1: Ekspor playlist Spotify Anda
1. Buka [exportify.net](https://exportify.net/)
2. Login dengan akun Spotify Anda
3. Ekspor playlist Anda sebagai CSV

### Langkah 2: Jalankan PlaylistToM3U
1. Buka `playlisttom3u_v1.2.exe` (atau jalankan `python playlisttom3u.py`)
2. **Pilih Bahasa** — pilih English atau Indonesia dari dropdown
3. **Pilih File CSV** — pilih file CSV yang sudah diekspor dari Exportify
4. **Pilih Folder Audio** — pilih folder yang berisi file audio lokal Anda (FLAC, MP3, dll.)
5. **Pilih Folder Output** — pilih tempat untuk menyimpan file M3U dan laporan
6. **Atur Threshold** — atur ambang kemiripan (default `0.55` cocok untuk sebagian besar kasus)
7. Klik **Mulai Konversi**

### Langkah 3: Muat M3U di pemutar musik Anda
Salin file `.m3u` yang dihasilkan ke pemutar musik atau perangkat Anda. File M3U berisi nama file sederhana — pastikan file M3U berada di folder yang sama dengan file audio Anda.

## 📝 Alias (Pemetaan Judul Manual)

Untuk lagu yang judul di CSV-nya menggunakan bahasa yang sepenuhnya berbeda dari nama file (misal judul Jepang vs nama file Inggris), buat file bernama **`aliases.txt`** di **folder audio** Anda.

### Format
```
# Baris yang diawali # adalah komentar
# Format: Judul di CSV = Judul di nama file

ラビットホール = Rabbit Hole
神のまにまに = At God's Mercy
ワンダーランズ×ショウタイム = Wonderlands×Showtime
```

Converter akan otomatis membaca file ini dan menggunakan alias saat mencocokkan.

## 🔧 Cara Kerja

```
Entry CSV                          File Audio
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
                 │  Kemiripan: 0.99│
                 │  ✅ COCOK!      │
                 └─────────────────┘
```

### Pipeline Pencocokan
1. **Normalisasi** — Hapus karakter spesial, konversi ke huruf kecil
2. **Judul Inti** — Ekstrak judul inti (hapus feat, kurung, dll.)
3. **Konversi CJK** — China Tradisional → Simplified
4. **Judul Alternatif** — Ekstrak judul dari dalam kurung
5. **Skor** — Gabungkan kemiripan judul + kemiripan artis + bonus substring
6. **Fallback** — Jika pencocokan standar gagal, coba pencocokan artis saja

## 🆕 Pembaruan Terbaru

**v1.2 (Terbaru)**
- **Intelligent Noise Word Filtering**: Aplikasi sekarang secara otomatis membuang istilah generik (seperti "Slowed", "Sped Up", "Remix", "Instrumental", "Montagem") sebelum menghitung skor kemiripan. Ini mencegah lagu yang berbeda namun memiliki tag generik yang sama agar tidak dipasangkan secara keliru.
- **Validasi Artist Gate**: Untuk hasil pencocokan dengan skor rendah, algoritma kini mewajibkan adanya kecocokan nama artis yang ketat untuk menghilangkan false positives (pencocokan salah).

**v1.1**
- **Algoritma Pencocokan Two-Pass**: Mengganti pencocokan berurutan dengan algoritma dua tahap (two-pass). Converter sekarang menghitung skor untuk semua file terlebih dahulu, dan memasangkan berdasarkan skor tertinggi. Ini menyelesaikan konflik di mana pencocokan dengan skor rendah bisa "mencuri" file dari pencocokan sempurna, memperbaiki masalah lagu yang dianggap tidak ada (false negative) dan meningkatkan akurasi secara signifikan.

## 🏗️ Build dari Source Code

```bash
# Install PyInstaller
pip install pyinstaller

# Build EXE
python -m PyInstaller --onefile --windowed --name playlisttom3u_v1.2 playlisttom3u.py

# EXE akan berada di folder dist/
```

## 📁 Format Audio yang Didukung

`.flac` `.mp3` `.wav` `.aac` `.m4a` `.ogg` `.opus`

## 🌐 Bahasa yang Didukung

- 🇺🇸 English
- 🇮🇩 Indonesia

## 📄 Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT — lihat file [LICENSE](LICENSE) untuk detailnya.

## 🙏 Kredit & Kontributor

- **[Dananjaya08](https://github.com/Dananjaya08)** — Pembuat & pengelola proyek
- **[Google Gemini](https://gemini.google.com/)** — Asisten AI yang membantu merancang algoritma pencocokan, dukungan CJK, dan arsitektur keseluruhan
- **[Anthropic Claude](https://claude.ai/)** — Asisten AI yang membantu mengimplementasikan UI dwi-bahasa, logika fallback artis, dokumentasi, dan menyempurnakan rilis akhir
- **[Exportify](https://exportify.net/)** — Alat ekspor CSV playlist Spotify
- Dibangun dengan `difflib.SequenceMatcher` dan Tkinter dari Python

> Proyek ini dimungkinkan melalui kolaborasi manusia-AI. Gemini dan Claude membantu mengubah ide sederhana menjadi converter playlist berfitur lengkap — mulai dari debugging masalah pencocokan hingga menangani karakter CJK dan membangun rilis akhir. 🤝
