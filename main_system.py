"""
SISTEM IMAGING ARRAY VIVALDI (hulu + hilir + rekonstruksi 3D dalam satu program)
================================================================================
Akuisisi LibreVNA (45 pasangan TX-RX satu arah) -> ZIP -> imaging DAS & DMAS 2D, dan
rekonstruksi 3D dari beberapa slice (objek digeser maju-mundur menembus busur).

PRASYARAT
- LibreVNA-GUI terbuka, device ter-connect, kalibrasi SOLT_12 (kalibrasi VNA,
  bukan baseline) di-Activate dengan rentang frekuensi & jumlah titik yang
  SAMA dengan konfigurasi hulu
- File 'libreVNA.py' (github.com/jankae/LibreVNA) di folder yang sama
  (hanya dibutuhkan untuk mengukur; imaging dari ZIP lama tidak butuh)
- pip install numpy pandas matplotlib scipy scikit-image
  (openpyxl hanya untuk fungsi Excel)

CARA PAKAI
    python main_system.py      (atau tombol Run di VS Code)

PERTANYAAN AWAL
    Kalau ada sesi 3D yang terhenti: Enter = lanjutkan | t = tidak (simpan
    dengan nama, bisa dipanggil lagi lewat l)
    Mode: Enter = biasa (2D) | 3 = 3D baru | l = lanjutkan sesi 3D tersimpan | q = keluar

MODE BIASA (2D)  -- sama seperti sebelumnya, q = kembali ke pertanyaan awal
- Belum ada baseline  : s = scan baseline baru | f = pakai file baseline lama
                        | i = imaging dari ZIP lama
- Baseline aktif      : Enter = ukur objek | b = ganti baseline | i = imaging dari ZIP lama
Ukur objek: ketik nama objek -> akuisisi 45 pasangan -> ZIP -> imaging otomatis
-> jendela gambar muncul -> tutup jendela -> kembali ke menu.

MODE 3D BARU
  1. Nama sesi
  2. Jumlah slice, posisi slice pertama (cm), jarak antar-slice (cm)
     (m = ketik semua posisi manual kalau jaraknya tidak seragam)
  3. Baseline: Enter = ikut baseline utama | f = pilih file | s = scan baru khusus sesi
     (baseline disalin ke folder sesi, tidak mengubah baseline.zip utama)
  4. Sumber data: Enter = ukur (menunggu hasil pengukuran terbaru)
                  | u = upload file ZIP yang sudah ada
  5. Program mengumpulkan slice berurutan. Mode ukur: tiap slice diukur
     (45 pasangan, fitur r/q sama seperti biasa), gambar 2D-nya disimpan di
     folder sesi tanpa membuka jendela.
  6. Setelah jumlah slice terpenuhi: Enter = buat 3D | t = tambah slice
     | e = edit slice | s = simpan & kembali | q = berhenti
     Tambah/edit bisa dengan ukur atau upload. Slice yang diedit tetap di
     urutannya; data lamanya disimpan sebagai cadangan (_lama_<waktu>).
  Ketik q di pertanyaan sesi untuk berhenti; sesi selalu tersimpan.

PROGRAM TERHENTI (q, Ctrl+C, jendela ditutup)
    Semua data tersimpan per pasangan TX-RX. Saat program dijalankan lagi,
    sesi ditawarkan untuk dilanjutkan; kalau ditolak, program menanyakan nama
    dan sesi disimpan di sesi_3d/<nama>/ (dipanggil lagi lewat pilihan l).

PASANGAN YANG DIUKUR (ACQUIRE_PAIRS = 45)
    Satu arah saja, TX < RX: 1.2 1.3 ... 1.10, 2.3 ... 2.10, ..., 9.10 (45 CSV per scan).
    Alasannya resiprositas: TX i -> RX j = TX j -> RX i, dan delay di imaging simetris.
    ZIP lama berisi 90 CSV tetap bisa dibaca; dengan IMAGING_CHANNELS = "45" imaging
    selalu memakai 45 kanal TX<RX (data lama & baru diolah dengan cara sama).
    Baseline lama (90 CSV) tetap bisa dipakai untuk objek baru (45 CSV).

SAAT AKUISISI
    Enter = ukur pasangan yang tertera
    r     = ulangi: program bertanya mulai dari pasangan mana (misal 1.3).
            Semua data dari pasangan itu sampai pasangan terakhir yang sudah
            diukur DIHAPUS, lalu diukur ulang berurutan mulai dari situ.
            Enter di pertanyaan itu = hanya ulangi pasangan terakhir.
    q     = berhenti (data yang sudah terukur tetap tersimpan)
    Penulisan pasangan: TX.RX, misal 1.6 = TX1-RX6 (1_6, 1-6, 1 6 juga diterima)

LOKASI FILE (semua di sebelah file script ini)
    baseline.zip, baseline/              baseline aktif
    baseline_<tanggal_jam>.zip / folder  baseline lama (arsip, tidak dihapus)
    <nama_objek>.zip, <nama_objek>/      data objek (mode 2D)
    output/<nama_objek>/                 satu folder per pengambilan, berisi:
        <nama_objek>_das_<rentang>.png, _dmas_<rentang>.png   gambar hasil 2D
        <nama_objek>_das_<rentang>.csv, _dmas_<rentang>.csv   data hasil perhitungan 2D
        (diolah ulang dengan rentang sama -> <nama_objek>_2_..., _3_..., tidak menimpa)
    sesi_3d/<nama_sesi>/                 sesi 3D: sesi.json, baseline, slice_XX_zYY.zip,
                                         2d/ (gambar 2D tiap slice), hasil_3d_<rentang>/
    sesi_3d/<nama_sesi>/hasil_3d_<rentang>/  slices_*, ortho_*, iso_* (DAS & DMAS),
                                         viewer_3d.html, ringkasan.txt
    output_3d_cache/                     energi mentah per slice (supaya tidak dihitung ulang)
    (File 'kalibrasi.zip' dari versi lama otomatis diganti nama jadi 'baseline.zip')

ISI CSV HASIL 2D (output/<nama_objek>/<nama_objek>_das_<rentang>.csv / _dmas_...)
    x_m, y_m            koordinat titik (meter), konvensi sama dengan gambar
    energi_mentah       hasil DAS/DMAS sebelum normalisasi
    energi_normalisasi  nilai yang diwarnai di gambar (0..1)
    di_dalam_busur      (hanya mode 'gabungan') 1 = di dalam half-disk, 0 = di luar

SEBELUM IMAGING (2D & 3D) program menanyakan:
    Rentang frekuensi (GHz): Enter = sama seperti terakhir | s = semua | ketik mis. 2 5
    Warna energi (hex, rendah -> tinggi): Enter = sama seperti terakhir | j = jet
        | ketik mis. #000080 #00ffff #ffff00 #ff0000  (atau 0:#000000 0.7:#ff0000 1:#ffffff)
    Sweep VNA tidak berubah; rentang hanya memilih data untuk pencitraan.
    Rentang tercatat di judul gambar, nama file (mis. tas_das_2-5GHz.png) dan
    ringkasan.txt. Pilihan terakhir disimpan di pengaturan.json.

3D: tiap slice dicitrakan dengan rumus yang sama dengan 2D, normalisasi GLOBAL
per metode (semua slice satu skala), interpolasi linear arah z hanya untuk
tampilan (nilai di z yang diukur sama persis dengan data).
"""

import cmath
import csv
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import time
import zipfile

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# libreVNA di-import di dalam connect_vna(), supaya imaging dari ZIP lama tetap
# bisa jalan walaupun libreVNA.py tidak ada.


# ============================================================================
# === KONFIGURASI HULU (akuisisi) ===
# ============================================================================
HOST = "localhost"
PORT = 19542                  # port default SCPI server LibreVNA-GUI
START_FREQ = 1_000_000_000    # 1 GHz  (samakan dengan kalibrasi SOLT di GUI)
STOP_FREQ = 6_000_000_000     # 6 GHz  (samakan dengan kalibrasi SOLT di GUI)
POINTS = 501                  # jumlah titik sweep (samakan dengan kalibrasi SOLT)
STIMULUS_LEVEL_DBM = -10      # level output sinyal (dBm)
IF_BANDWIDTH_HZ = 1000        # makin kecil makin bersih tapi makin lambat
AVERAGES = 1                  # jumlah averaging tiap sweep
SWEEP_TIMEOUT_S = 60          # batas waktu menunggu satu sweep

# False = folder CSV tetap disimpan sebagai cadangan setelah ZIP jadi
# True  = CSV dihapus setelah ZIP jadi, yang tersisa hanya ZIP
DELETE_CSV_AFTER_ZIP = False

# ============================================================================
# === KONFIGURASI HILIR (imaging) ===
# ============================================================================
# Jumlah elemen antena Vivaldi (10 elemen: 45 pasangan satu arah / 90 dua arah)
N_ELEMENTS = 10

# Bentuk busur: SETENGAH ELIPS. Titik pusat (0,0) = tengah garis antara kedua
# kaki busur. Lebar total (kaki ke kaki) 70 cm -> setengah sumbu horizontal
# 0,35 m; tinggi total (garis kaki ke puncak) 40 cm -> setengah sumbu vertikal 0,40 m.
ARRAY_SEMI_AXIS_X_M = 0.35
ARRAY_SEMI_AXIS_Y_M = 0.40

# Sudut tiap elemen dari KAKI KIRI (derajat), diukur dari TITIK PUSAT, naik
# melewati puncak (90 deg) ke kaki kanan (180 deg). Elemen 1 di kaki kiri (x<0).
# Dikonfirmasi: simetris, elemen 1 di 2,5 deg, elemen 10 di 177,5 deg
# (jarak 175/9 = 19,44 deg). Posisi elemen = titik pada elips di arah sudut itu.
FIRST_ELEMENT_ANGLE_DEG = 2.5
LAST_ELEMENT_ANGLE_DEG = 177.5
ELEMENT_ANGLES_FROM_FOOT_DEG = list(np.linspace(FIRST_ELEMENT_ANGLE_DEG,
                                                LAST_ELEMENT_ANGLE_DEG, N_ELEMENTS))
# Konvensi lama "dari puncak" (0 = puncak, negatif = kiri), dipakai rumus posisi
ELEMENT_ANGLES_DEG = [a - 90.0 for a in ELEMENT_ANGLES_FROM_FOOT_DEG]
assert len(ELEMENT_ANGLES_DEG) == N_ELEMENTS

# Skema kanal. Resiprositas: TX i -> RX j sama dengan TX j -> RX i (medium pasif),
# dan delay |p-a_tx|+|p-a_rx| simetris, jadi cukup satu arah.
#   ACQUIRE_PAIRS   = 45 -> ukur 45 pasangan satu arah (TX < RX): 1.2 ... 9.10
#                   = 90 -> ukur 90 pasangan dua arah (cara lama)
#   IMAGING_CHANNELS = "45"    -> imaging selalu pakai 45 kanal TX<RX, walaupun data
#                                 punya 90 (data lama & baru diolah dengan cara sama)
#                    = "semua" -> pakai semua kanal yang ada di objek DAN baseline
ACQUIRE_PAIRS = 45
IMAGING_CHANNELS = "45"
# (lama) Skema kanal: 90 kanal bistatik (S21, kedua arah)
FULL_DIRECTIONAL_CHANNELS = True
INCLUDE_MONOSTATIC_S11 = False   # hanya dipakai fungsi Excel (lihat bawah)

SPEED_OF_LIGHT_M_S = 299_792_458.0
RELATIVE_PERMITTIVITY = 1.0       # default udara
IMAGE_RESOLUTION_M = 0.002        # 2 mm per piksel (resolusi PERHITUNGAN)
DEFAULT_BEAMFORMER = "DAS"

# Domain pencitraan: "half_disk" = di dalam busur setengah elips (default),
# "gabungan" = kotak penuh x[-a,a], y[0,b]
DOMAIN_MODE = "half_disk"

# DPI file PNG yang disimpan ke folder output (sebelumnya 150).
# Hanya mengubah ukuran/ketajaman file gambar, BUKAN jumlah titik yang dihitung
# (itu diatur IMAGE_RESOLUTION_M). Kanvas 11,5 x 5,6 inci -> +-5762 x 2806 piksel.
SAVE_DPI = 501

# ============================================================================
# === KONFIGURASI SISTEM ===
# ============================================================================
BASELINE_NAME = "baseline"            # baseline aktif: baseline.zip
BASELINE_SCAN_NAME = "baseline_baru"  # folder sementara saat scan baseline berjalan
LEGACY_NAME = "kalibrasi"             # nama yang dipakai program versi lama


def _base_dir():
    """Folder file script (untuk VS Code / terminal); folder kerja kalau
    __file__ tidak tersedia."""
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()


BASE_DIR = _base_dir()
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
BASELINE_ZIP = os.path.join(BASE_DIR, f"{BASELINE_NAME}.zip")
BASELINE_DIR = os.path.join(BASE_DIR, BASELINE_NAME)

CSV_HEADER = ["Frequency_Hz",
              "S11_LogMag_dB", "S11_Phase_deg",
              "S21_LogMag_dB", "S21_Phase_deg"]


# ============================================================================
# === PASANGAN TX-RX (dipakai hulu & hilir) ===
# ============================================================================

def all_pairs(n):
    """Semua 90 pasangan dua arah: (1,2),(1,3),...,(1,10),(2,1),(2,3),...,(10,9)."""
    return [(tx, rx) for tx in range(1, n + 1)
            for rx in range(1, n + 1) if rx != tx]


def one_way_pairs(n):
    """45 pasangan satu arah (TX < RX): (1,2),...,(1,10),(2,3),...,(9,10)."""
    return [(tx, rx) for tx in range(1, n + 1) for rx in range(tx + 1, n + 1)]


def acquisition_pairs(n=None):
    """Urutan pasangan yang DIUKUR, sesuai ACQUIRE_PAIRS."""
    n = n or N_ELEMENTS
    return one_way_pairs(n) if int(ACQUIRE_PAIRS) == 45 else all_pairs(n)


def csv_name(tx, rx):
    return f"{tx}_{rx}.csv"


def pair_label(tx, rx):
    """Label pasangan untuk ditampilkan/diketik: '1.6' = TX1-RX6."""
    return f"{tx}.{rx}"


def parse_pair(text, n):
    """'1.3', '1_3', '1-3', '1 3', 'tx1 rx3' -> (1, 3).
    Return None kalau formatnya salah atau nomor antenanya tidak valid."""
    nums = re.findall(r"\d+", text)
    if len(nums) != 2:
        return None
    tx, rx = int(nums[0]), int(nums[1])
    if not (1 <= tx <= n and 1 <= rx <= n) or tx == rx:
        return None
    return tx, rx


def missing_pairs(scan_dir, pairs):
    return [p for p in pairs
            if not os.path.isfile(os.path.join(scan_dir, csv_name(*p)))]


# ############################################################################
# ################################  HULU  ####################################
# ############################################################################

def connect_vna():
    try:
        from libreVNA import libreVNA
    except ImportError:
        raise RuntimeError("File libreVNA.py tidak ditemukan. Taruh di folder "
                           "yang sama dengan script ini.")
    print(f"Menghubungkan ke LibreVNA-GUI di {HOST}:{PORT} ...")
    vna = libreVNA(HOST, PORT)
    print(f"IDN: {vna.query('*IDN?')}")
    vna.cmd(":DEV:CONN")
    dev = vna.query(":DEV:CONN?")
    if dev == "Not connected":
        raise RuntimeError("Device LibreVNA tidak terhubung. Cek USB & GUI.")
    print(f"Connected to device: {dev}")
    return vna


def setup_sweep(vna):
    """Dipanggil tiap pengukuran supaya sweep dimulai ulang (data segar
    setelah kabel dipindah)."""
    vna.cmd(":DEV:MODE VNA")
    vna.cmd(":VNA:SWEEP FREQUENCY")
    vna.cmd(f":VNA:STIM:LVL {STIMULUS_LEVEL_DBM}")
    vna.cmd(f":VNA:ACQ:IFBW {IF_BANDWIDTH_HZ}")
    vna.cmd(f":VNA:ACQ:AVG {AVERAGES}")
    vna.cmd(f":VNA:ACQ:POINTS {POINTS}")
    vna.cmd(f":VNA:FREQuency:START {START_FREQ}")
    vna.cmd(f":VNA:FREQuency:STOP {STOP_FREQ}")


def wait_sweep_finished(vna):
    deadline = time.time() + SWEEP_TIMEOUT_S
    while vna.query(":VNA:ACQ:FIN?") == "FALSE":
        if time.time() > deadline:
            raise RuntimeError("Timeout menunggu sweep selesai.")
        time.sleep(0.1)


def to_db(c):
    m = abs(c)
    return -200.0 if m <= 0 else 20 * math.log10(m)


def to_deg(c):
    return math.degrees(cmath.phase(c))


def measure_pair(vna, scan_dir, tx, rx):
    """Ukur satu pasangan dan simpan CSV-nya. Raise exception kalau gagal
    (CSV lama, kalau ada, tidak tersentuh)."""
    setup_sweep(vna)
    print("  Sweep berjalan...")
    wait_sweep_finished(vna)

    s11 = vna.parse_VNA_trace_data(vna.query(":VNA:TRACE:DATA? S11"))
    s21 = vna.parse_VNA_trace_data(vna.query(":VNA:TRACE:DATA? S21"))
    if not s11 or not s21 or len(s11) != len(s21):
        raise RuntimeError("Data S11/S21 kosong atau jumlah titiknya beda.")

    path = os.path.join(scan_dir, csv_name(tx, rx))
    tmp = path + ".tmp"   # tulis ke file sementara dulu supaya tidak ada
    with open(tmp, "w", newline="") as fh:   # CSV setengah jadi kalau crash
        w = csv.writer(fh)
        w.writerow(CSV_HEADER)
        for (f, c11), (_, c21) in zip(s11, s21):
            w.writerow([f, to_db(c11), to_deg(c11), to_db(c21), to_deg(c21)])
    os.replace(tmp, path)
    print(f"  Tersimpan: {csv_name(tx, rx)} ({len(s11)} titik)")


def last_measured_before(scan_dir, pairs, current):
    """Pasangan terakhir (dalam urutan pengukuran) sebelum `current` yang
    CSV-nya sudah ada. None kalau belum ada sama sekali."""
    idx = pairs.index(current)
    for p in reversed(pairs[:idx]):
        if os.path.isfile(os.path.join(scan_dir, csv_name(*p))):
            return p
    return None


def choose_redo(scan_dir, pairs, last):
    """Tanya mulai dari pasangan mana pengulangan dilakukan, lalu hapus CSV
    dari pasangan itu sampai `last` (pasangan terakhir yang sudah diukur).
    Return True kalau ada data yang dihapus, False kalau batal."""
    last_idx = pairs.index(last)
    while True:
        ans = input(f"  Ulang mulai dari pasangan mana? (contoh 1.3) "
                    f"| Enter = hanya {pair_label(*last)} | b = batal: ").strip().lower()
        if ans == "b":
            print("  Tidak jadi mengulang, tidak ada data yang dihapus.")
            return False

        start = last if ans == "" else parse_pair(ans, N_ELEMENTS)
        if start is None:
            print(f"  '{ans}' bukan pasangan yang valid. Tulis TX.RX, misal 1.3 "
                  f"(TX dan RX antara 1-{N_ELEMENTS}, tidak boleh sama).")
            continue
        if start not in pairs and (start[1], start[0]) in pairs:
            print(f"  (mode {len(pairs)} pasangan: {pair_label(*start)} sama dengan "
                  f"{pair_label(start[1], start[0])})")
            start = (start[1], start[0])
        if start not in pairs:
            print(f"  Pasangan {pair_label(*start)} tidak ada di urutan pengukuran.")
            continue
        start_idx = pairs.index(start)
        if start_idx > last_idx:
            print(f"  Pasangan {pair_label(*start)} belum diukur. Pilih antara "
                  f"{pair_label(*pairs[0])} dan {pair_label(*last)}.")
            continue

        redo = [p for p in pairs[start_idx:last_idx + 1]
                if os.path.isfile(os.path.join(scan_dir, csv_name(*p)))]
        if len(redo) > 1:
            print(f"  Data {pair_label(*start)} s/d {pair_label(*last)} "
                  f"({len(redo)} pasangan) akan DIHAPUS lalu diukur ulang.")
            if ask_choice("  Enter = ya, hapus | b = batal: ", {"", "b"}) == "b":
                print("  Tidak jadi mengulang, tidak ada data yang dihapus.")
                return False

        for p in redo:
            os.remove(os.path.join(scan_dir, csv_name(*p)))
        if len(redo) == 1:
            print(f"  Data {pair_label(*start)} dihapus, siap diukur ulang.")
        else:
            print(f"  {len(redo)} data dihapus ({pair_label(*start)} s/d "
                  f"{pair_label(*last)}). Mengukur ulang mulai {pair_label(*start)}.")
        return True


def run_acquisition(vna, scan_dir, pairs):
    """Return True kalau semua pasangan lengkap, False kalau keluar (q).
    Yang diukur selalu pasangan pertama (urutan all_pairs) yang CSV-nya
    belum ada, jadi setelah 'r' pengukuran otomatis lanjut dari titik ulang."""
    total = len(pairs)

    while True:
        # Dicek ulang tiap putaran: menangkap CSV yang dihapus (oleh 'r' atau manual)
        pending = missing_pairs(scan_dir, pairs)
        if not pending:
            return True

        tx, rx = pending[0]
        done = total - len(pending)
        last = last_measured_before(scan_dir, pairs, (tx, rx))

        options = "Enter = ukur"
        if last:
            options += " | r = ulangi (pilih mulai dari pasangan mana)"
        options += " | q = kembali ke menu"

        print(f"\n[{done + 1}/{total}] Pasangan {pair_label(tx, rx)}: "
              f"port 1 -> antena {tx} (TX), port 2 -> antena {rx} (RX)")
        try:
            choice = input(f"  {options}: ").strip().lower()
        except KeyboardInterrupt:
            return False

        valid = {"", "q"} | ({"r"} if last else set())
        if choice not in valid:
            print(f"  Input '{choice}' tidak dikenal, tidak ada yang diukur. "
                  f"Pilih sesuai opsi.")
            continue
        if choice == "q":
            return False
        if choice == "r":
            try:
                choose_redo(scan_dir, pairs, last)
            except KeyboardInterrupt:
                return False
            continue   # putaran berikutnya menunjukkan pasangan yang harus diukur

        try:
            measure_pair(vna, scan_dir, tx, rx)
        except KeyboardInterrupt:
            return False
        except Exception as e:
            print(f"  GAGAL: {e}")
            print("  Pasangan ini belum tersimpan. Tekan Enter untuk mencoba lagi.")


def make_zip(scan_dir, zip_path, pairs):
    """ZIP hanya berisi CSV pasangan yang diukur (45 atau 90; file lain diabaikan)."""
    tmp = zip_path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        for tx, rx in pairs:
            name = csv_name(tx, rx)
            zf.write(os.path.join(scan_dir, name), arcname=name)
    os.replace(tmp, zip_path)


def delete_csvs(scan_dir, pairs):
    for tx, rx in pairs:
        os.remove(os.path.join(scan_dir, csv_name(tx, rx)))
    try:
        os.rmdir(scan_dir)   # hanya terhapus kalau foldernya sudah kosong
    except OSError:
        pass


# ############################################################################
# ################################  HILIR  ###################################
# ############################################################################

# --- GEOMETRI ARRAY ---
# Konvensi koordinat: origin di titik pusat busur (tengah garis kedua kaki),
# y+ ke puncak busur, theta = 0 di puncak (negatif = kiri).
# Busur setengah elips (x/a)^2 + (y/b)^2 = 1. Elemen di arah theta dari pusat:
#   r(theta) = 1 / sqrt((sin(theta)/a)^2 + (cos(theta)/b)^2)
#   x = r sin(theta), y = r cos(theta)

def element_angles_rad():
    return np.deg2rad(np.asarray(ELEMENT_ANGLES_DEG, dtype=float))


def array_positions(semi_x=None, semi_y=None, angles_deg=None):
    """Koordinat (x,y) tiap elemen antena. positions[n] = elemen ke-(n+1)."""
    a = ARRAY_SEMI_AXIS_X_M if semi_x is None else semi_x
    b = ARRAY_SEMI_AXIS_Y_M if semi_y is None else semi_y
    if angles_deg is None:
        angles_deg = ELEMENT_ANGLES_DEG
    th = np.deg2rad(np.asarray(angles_deg, dtype=float))
    r = 1.0 / np.sqrt((np.sin(th) / a) ** 2 + (np.cos(th) / b) ** 2)
    x = r * np.sin(th)
    y = r * np.cos(th)
    return np.column_stack([x, y])


def antenna_index_to_position(antenna_positions, antenna_number):
    """Posisi (x,y) dari nomor antena 1-based (1..N)."""
    return antenna_positions[antenna_number - 1]


# --- DAFTAR KANAL ---

def generate_switching_order(n_elements=10):
    """(tx,rx) 1-based sesuai skema switching manual, N*(N-1) kanal."""
    pairs = []
    for tx in range(1, n_elements + 1):
        for rx in range(1, n_elements + 1):
            if rx != tx:
                pairs.append((tx, rx))
    return np.array(pairs, dtype=int)


def generate_monostatic_pairs(n_elements=10):
    """(tx,rx)=(n,n) untuk kanal monostatik S11, jumlah = N."""
    return np.array([(n, n) for n in range(1, n_elements + 1)], dtype=int)


def generate_full_set(n_elements=10, include_monostatic=True):
    """Gabungan bistatik (S21) + monostatik (S11). Return (channel_list, kinds)."""
    bistatic = generate_switching_order(n_elements)
    kinds = ["S21"] * len(bistatic)
    if not include_monostatic:
        return bistatic, kinds
    monostatic = generate_monostatic_pairs(n_elements)
    channel_list = np.vstack([bistatic, monostatic])
    kinds = kinds + ["S11"] * len(monostatic)
    return channel_list, kinds


def assign_channels(column_labels, channel_list):
    """Memetakan label kolom -> (tx,rx) berdasarkan urutan kemunculan."""
    channel_list = np.asarray(channel_list)
    if len(column_labels) != len(channel_list):
        raise ValueError(
            f"Jumlah kolom ({len(column_labels)}) tidak sama dengan jumlah "
            f"kanal yang didefinisikan ({len(channel_list)})."
        )
    return {label: tuple(int(v) for v in ch) for label, ch in zip(column_labels, channel_list)}


# --- BACA DATA ---

def load_csv_zip(zip_path, n_elements=N_ELEMENTS):
    """
    Baca ZIP berisi CSV '<tx>_<rx>.csv' (atau format lama '<tx> <rx>.csv').
    Data 2 arah (90 CSV) maupun 1 arah (45 CSV, TX<RX) diterima. Hanya kolom
    S21 yang dipakai. Return (freqs_hz, signals (F x C) kompleks,
    channel_list (C x 2)) dengan C = 90 (urutan all_pairs) atau 45
    (urutan one_way_pairs).
    """
    zip_label = os.path.basename(zip_path)

    with zipfile.ZipFile(zip_path) as zf:
        # nama file tanpa folder -> nama lengkap di dalam zip.
        # Spasi diganti '_' supaya data lama '1 2.csv' juga terbaca sebagai '1_2.csv'.
        members = {os.path.basename(m).replace(" ", "_"): m for m in zf.namelist()
                   if m.lower().endswith(".csv")}
        pairs = all_pairs(n_elements)
        if any(csv_name(*p) not in members for p in pairs):
            pairs = one_way_pairs(n_elements)
        missing = [p for p in pairs if csv_name(*p) not in members]
        if missing:
            raise ValueError(f"{len(missing)} CSV tidak ada di {zip_label} (butuh minimal "
                             f"45 pasangan TX<RX), contoh: {missing[:5]}")

        freqs_ref = None
        columns = []
        for tx, rx in pairs:
            with zf.open(members[csv_name(tx, rx)]) as fh:
                df = pd.read_csv(fh)
            freqs = df["Frequency_Hz"].to_numpy(dtype=float)
            if freqs_ref is None:
                freqs_ref = freqs
            elif freqs.shape != freqs_ref.shape or not np.allclose(freqs, freqs_ref):
                raise ValueError(f"Titik frekuensi di {csv_name(tx, rx)} ({zip_label}) "
                                 f"beda dari file lain.")
            s21 = (10 ** (df["S21_LogMag_dB"].to_numpy(dtype=float) / 20.0)) * \
                  np.exp(1j * np.deg2rad(df["S21_Phase_deg"].to_numpy(dtype=float)))
            columns.append(s21)

    signals = np.column_stack(columns)
    return freqs_ref, signals, np.array(pairs, dtype=int)


# --- Fungsi Excel: disimpan apa adanya, TIDAK dipanggil oleh program ---

def load_vna_excel(path, param="S21", sheet_prefix_mag="LogMag", sheet_prefix_phase="Phase"):
    """Baca 1 file Excel (sheet LogMag_<param> & Phase_<param>) -> kompleks."""
    mag_sheet = f"{sheet_prefix_mag}_{param}"
    phase_sheet = f"{sheet_prefix_phase}_{param}"
    mag_df = pd.read_excel(path, sheet_name=mag_sheet)
    phase_df = pd.read_excel(path, sheet_name=phase_sheet)
    if mag_df.shape != phase_df.shape:
        raise ValueError(f"Sheet '{mag_sheet}' & '{phase_sheet}' ukuran beda.")
    freqs_hz = mag_df.iloc[:, 0].to_numpy(dtype=float)
    mag_db = mag_df.iloc[:, 1:].to_numpy(dtype=float)
    phase_deg = phase_df.iloc[:, 1:].to_numpy(dtype=float)
    column_labels = [str(c) for c in mag_df.columns[1:]]
    complex_data = (10 ** (mag_db / 20.0)) * np.exp(1j * np.deg2rad(phase_deg))
    return freqs_hz, complex_data, column_labels


def load_combined_excel(path, n_elements=10, include_monostatic=True):
    """Baca S21 (90 kolom) + S11 (10 kolom, 1/posisi Tx) dari 1 file Excel."""
    freqs_s21, s21_data, s21_labels = load_vna_excel(path, param="S21")
    channel_list, kinds = generate_full_set(n_elements, include_monostatic)

    n_bistatic = n_elements * (n_elements - 1)
    if s21_data.shape[1] != n_bistatic:
        raise ValueError(f"Jumlah kolom S21 ({s21_data.shape[1]}) != {n_bistatic}.")
    if not include_monostatic:
        return freqs_s21, s21_data, channel_list

    freqs_s11, s11_data, s11_labels = load_vna_excel(path, param="S11")
    if not np.allclose(freqs_s11, freqs_s21):
        raise ValueError("Titik frekuensi S11 dan S21 tidak sama.")
    if s11_data.shape[1] != n_elements:
        raise ValueError(f"Jumlah kolom S11 ({s11_data.shape[1]}) != {n_elements}.")

    signals = np.concatenate([s21_data, s11_data], axis=1)
    return freqs_s21, signals, channel_list


def reorder_columns(complex_data, column_labels, label_to_channel, channel_order):
    """Susun ulang kolom sesuai channel_order, pakai pemetaan label_to_channel."""
    channel_to_col_idx = {}
    for idx, label in enumerate(column_labels):
        if label in label_to_channel:
            channel_to_col_idx[label_to_channel[label]] = idx
    channel_order = [tuple(int(v) for v in ch) for ch in channel_order]
    missing = [ch for ch in channel_order if ch not in channel_to_col_idx]
    if missing:
        raise ValueError(f"{len(missing)} kanal belum ada datanya, contoh: {missing[:5]}")
    col_indices = [channel_to_col_idx[ch] for ch in channel_order]
    return complex_data[:, col_indices]


# --- BASELINE SUBTRACTION ---

def imaging_channels(*channel_lists):
    """Daftar kanal yang dipakai imaging, sama untuk semua data yang diberikan.
    IMAGING_CHANNELS = '45': selalu 45 kanal TX<RX. 'semua': irisan kanal semua data."""
    if str(IMAGING_CHANNELS) == "45":
        return one_way_pairs(N_ELEMENTS)
    common = None
    for cl in channel_lists:
        s = {tuple(int(v) for v in c) for c in cl}
        common = s if common is None else common & s
    return [p for p in all_pairs(N_ELEMENTS) if p in common]


def pick_channels(signals, channel_list, wanted):
    """Ambil kolom kanal `wanted` (urutan sesuai wanted)."""
    pos = {tuple(int(v) for v in c): i for i, c in enumerate(channel_list)}
    missing = [p for p in wanted if p not in pos]
    if missing:
        raise ValueError(f"{len(missing)} kanal tidak ada di data, contoh: {missing[:5]}")
    return signals[:, [pos[p] for p in wanted]]


def subtract_baseline(signal_with_target, signal_baseline):
    """signal_with_target, signal_baseline: (F,C). Harus sama persis ukurannya."""
    if signal_with_target.shape != signal_baseline.shape:
        raise ValueError("Ukuran scan-dengan-objek dan baseline tidak sama.")
    return signal_with_target - signal_baseline


def subtract_average(signal_with_target):
    """Kurangi rata-rata semua kanal (per frekuensi) dari tiap kanal."""
    channel_mean = signal_with_target.mean(axis=1, keepdims=True)
    return signal_with_target - channel_mean


# --- DELAY ---
# tau_ij(p) = (|p-a_i| + |p-a_j|) / v ,  v = c0/sqrt(eps_r)

def compute_delays(antenna_positions, channel_list, points, relative_permittivity=None):
    if relative_permittivity is None:
        relative_permittivity = RELATIVE_PERMITTIVITY
    speed = SPEED_OF_LIGHT_M_S / np.sqrt(relative_permittivity)
    channel_list = np.asarray(channel_list, dtype=int)
    tx_pos = antenna_positions[channel_list[:, 0] - 1]
    rx_pos = antenna_positions[channel_list[:, 1] - 1]
    points = np.asarray(points, dtype=float)
    d_tx = np.linalg.norm(points[:, None, :] - tx_pos[None, :, :], axis=2)
    d_rx = np.linalg.norm(points[:, None, :] - rx_pos[None, :, :], axis=2)
    return (d_tx + d_rx) / speed


# --- DOMAIN PENCITRAAN ---
# Di dalam busur setengah elips: (x/a)^2 + (y/b)^2 <= 1 dan y >= 0

def _domain_grid(resolution_m):
    a, b = ARRAY_SEMI_AXIS_X_M, ARRAY_SEMI_AXIS_Y_M
    n_x = int(round(a / resolution_m))
    n_y = int(round(b / resolution_m))
    x_axis = np.arange(-n_x, n_x + 1) * resolution_m      # simetris, 0 tepat di tengah
    y_axis = np.arange(0, n_y + 1) * resolution_m         # mulai tepat di garis kaki
    X, Y = np.meshgrid(x_axis, y_axis)
    inside = (X / a) ** 2 + (Y / b) ** 2 <= 1.0 + 1e-12
    return X, Y, inside


def half_disk_domain(resolution_m=None):
    """Titik di dalam busur (setengah elips). Nama lama dipertahankan."""
    X, Y, mask = _domain_grid(resolution_m or IMAGE_RESOLUTION_M)
    points = np.column_stack([X[mask], Y[mask]])
    return points, X, Y, mask


def combined_domain(resolution_m=None):
    """Versi gabungan: grid kotak penuh x[-a,a], y[0,b] untuk ditampilkan.
    in_half[i] = True kalau points[i] berada di dalam busur
    (dipakai untuk normalisasi & pencarian titik puncak)."""
    X, Y, inside = _domain_grid(resolution_m or IMAGE_RESOLUTION_M)
    mask = np.ones_like(inside, dtype=bool)
    points = np.column_stack([X[mask], Y[mask]])
    return points, X, Y, mask, inside[mask]


def mask_near_antennas(points, antenna_positions, min_distance_m):
    """True untuk titik yang cukup jauh (>min_distance_m) dari SEMUA antena.
    Berguna menyingkirkan artefak near-field/mutual coupling dekat antena."""
    points = np.asarray(points, dtype=float)
    dist_to_nearest = np.min(
        np.linalg.norm(points[:, None, :] - antenna_positions[None, :, :], axis=2), axis=1,
    )
    return dist_to_nearest > min_distance_m


# --- BEAMFORMING: DAS & DMAS ---
# DAS:  I(p) = |sum_f sum_c S_c(f)*exp(+j2pi*f*tau_c(p))|^2
# DMAS: pakai identitas (sum x)^2 = sum x^2 + sum_{i!=j} x_i*x_j -> O(C) bukan O(C^2)
#
# CARA HITUNG CEPAT (rumus sama persis). Frekuensi sweep berjarak seragam:
# f_k = f_0 + k*df, sehingga exp(j2pi f_k tau) = exp(j2pi f_0 tau) * z^k dengan
# z = exp(j2pi df tau). Jadi tidak perlu menghitung exp() untuk tiap frekuensi:
#   DAS : sum_k S_k z^k dihitung dengan metode Horner (perkalian berulang)
#   DMAS: fase tiap frekuensi didapat dari fase sebelumnya x z
# Memori hanya (titik x kanal), bukan (frekuensi x titik x kanal).
# Beda dengan cara langsung hanya pembulatan komputer (~1e-14 relatif).
# Kalau frekuensi TIDAK seragam, otomatis memakai cara langsung (lama).

def _uniform_step(freqs):
    d = np.diff(freqs)
    if len(d) and np.allclose(d, d[0], rtol=1e-9, atol=1e-3):
        return float(d[0])
    return None


def _phase_compensate(signals, freqs, delays_chunk):
    phase = np.exp(1j * 2 * np.pi * freqs[:, None, None] * delays_chunk[None, :, :])
    return signals[:, None, :] * phase


def das(signals, freqs, delays, chunk_size=4000):
    n_points = delays.shape[0]
    image = np.zeros(n_points, dtype=float)
    df = _uniform_step(freqs)
    if df is None:
        chunk_size = min(chunk_size, 500)
    for start in range(0, n_points, chunk_size):
        end = min(start + chunk_size, n_points)
        tau = delays[start:end]
        if df is None:
            summed = _phase_compensate(signals, freqs, tau).sum(axis=(0, 2))
        else:
            z = np.exp(2j * np.pi * df * tau)
            acc = np.array(np.broadcast_to(signals[-1], tau.shape), dtype=complex)
            for k in range(len(freqs) - 2, -1, -1):          # Horner
                acc *= z
                acc += signals[k]
            summed = (np.exp(2j * np.pi * freqs[0] * tau) * acc).sum(axis=1)
        image[start:end] = np.abs(summed) ** 2
    return image


def dmas(signals, freqs, delays, chunk_size=4000):
    n_points = delays.shape[0]
    image = np.zeros(n_points, dtype=float)
    df = _uniform_step(freqs)
    if df is None:
        chunk_size = min(chunk_size, 500)
    for start in range(0, n_points, chunk_size):
        end = min(start + chunk_size, n_points)
        tau = delays[start:end]
        if df is None:
            shifted = _phase_compensate(signals, freqs, tau)
            sum_c = shifted.sum(axis=2)
            total = (sum_c ** 2 - (shifted ** 2).sum(axis=2)).sum(axis=0)
        else:
            phase = np.exp(2j * np.pi * freqs[0] * tau)
            step = np.exp(2j * np.pi * df * tau)
            total = np.zeros(tau.shape[0], dtype=complex)
            x = np.empty_like(phase)
            for k in range(len(freqs)):
                np.multiply(phase, signals[k], out=x)
                sum_c = x.sum(axis=1)
                total += sum_c * sum_c
                x *= x
                total -= x.sum(axis=1)
                phase *= step
        image[start:end] = np.abs(total)
    return image


BEAMFORMERS = {"DAS": das, "DMAS": dmas}


def normalize(image):
    lo, hi = np.min(image), np.max(image)
    if hi - lo < 1e-30:
        return np.zeros_like(image)
    return (image - lo) / (hi - lo)


def normalize_in_region(image, region):
    """Seperti normalize(), tapi min/max diambil HANYA dari titik di region.
    Titik di luar region bisa bernilai <0 atau >1."""
    lo, hi = np.min(image[region]), np.max(image[region])
    if hi - lo < 1e-30:
        return np.zeros_like(image)
    return (image - lo) / (hi - lo)


# --- PENGATURAN PENGOLAHAN: rentang frekuensi & warna energi ---
# Ditanyakan sebelum imaging. Sweep VNA TIDAK berubah (tetap sesuai konfigurasi
# hulu); yang dipilih hanya bagian frekuensi yang dipakai untuk pencitraan.
# Pilihan terakhir disimpan di pengaturan.json (Enter = pakai lagi).

SETTINGS_FILE = os.path.join(BASE_DIR, "pengaturan.json")
PROC = {"band": None, "band_label": "", "full": True,
        "cmap": None, "cmap_spec": "jet"}


def load_settings():
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_settings(d):
    tmp = SETTINGS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, SETTINGS_FILE)


def zip_freqs(path):
    """Titik frekuensi dari satu CSV di dalam ZIP (cepat, untuk pertanyaan)."""
    with zipfile.ZipFile(path) as zf:
        names = sorted(m for m in zf.namelist() if m.lower().endswith(".csv"))
        with zf.open(names[0]) as fh:
            df = pd.read_csv(fh, usecols=["Frequency_Hz"])
    return df["Frequency_Hz"].to_numpy(dtype=float)


def _ghz(hz):
    return f"{hz / 1e9:.4g}"


def band_label(lo_hz, hi_hz):
    return f"{_ghz(lo_hz)}-{_ghz(hi_hz)}GHz"


def parse_colors(text):
    """'#000080 #00ffff #ff0000' atau '0:#000000 0.7:#ff0000 1:#ffffff'
    -> (colormap, teks rapi). Raise ValueError kalau formatnya salah."""
    from matplotlib.colors import LinearSegmentedColormap
    t = re.sub(r"(\d),(\d)", r"\1.\2", text.strip())
    toks = [x for x in re.split(r"[\s,;]+", t) if x]
    pos, cols = [], []
    for tok in toks:
        m = re.fullmatch(r"(?:(\d*\.?\d+):)?#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})", tok)
        if not m:
            raise ValueError(f"'{tok}' bukan warna hex (contoh #ff0000 atau 0.5:#ff0000).")
        h = m.group(2).lower()
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        cols.append("#" + h)
        pos.append(None if m.group(1) is None else float(m.group(1)))
    if len(cols) < 2:
        raise ValueError("Minimal 2 warna (rendah dan tinggi).")
    given = [p is not None for p in pos]
    if any(given) and not all(given):
        raise ValueError("Posisi warna harus ditulis untuk semua warna atau tidak sama sekali.")
    if all(given):
        if abs(pos[0]) > 1e-9 or abs(pos[-1] - 1) > 1e-9 or any(b <= a for a, b in zip(pos, pos[1:])):
            raise ValueError("Posisi harus naik dari 0 sampai 1, misal 0:#000000 0.7:#ff0000 1:#ffffff.")
        cmap = LinearSegmentedColormap.from_list("energi", list(zip(pos, cols)))
        spec = " ".join(f"{p:g}:{c}" for p, c in zip(pos, cols))
    else:
        cmap = LinearSegmentedColormap.from_list("energi", cols)
        spec = " ".join(cols)
    return cmap, spec


def make_cmap(spec):
    if not spec or spec == "jet":
        return matplotlib.colormaps["jet"], "jet"
    return parse_colors(spec)


def _band_from(freqs, lo, hi):
    sel = (freqs >= lo - 1e3) & (freqs <= hi + 1e3)
    return sel


def _set_proc(freqs, lo, hi, cmap, spec):
    sel = _band_from(freqs, lo, hi)
    a, b = freqs[sel][0], freqs[sel][-1]
    PROC.update(band=(float(a), float(b)), band_label=band_label(a, b),
                full=bool(abs(a - freqs[0]) < 1e3 and abs(b - freqs[-1]) < 1e3),
                cmap=cmap, cmap_spec=spec)
    return sel


def ask_processing_settings(freqs):
    """Tanya rentang frekuensi & warna energi. Return False kalau batal (q)."""
    s = load_settings()
    f0, f1 = float(freqs[0]), float(freqs[-1])
    step = float(np.diff(freqs).mean()) if len(freqs) > 1 else 0.0
    print(f"\nPENGATURAN PENGOLAHAN  (data: {_ghz(f0)}-{_ghz(f1)} GHz, {len(freqs)} titik, "
          f"langkah {step / 1e6:g} MHz)")
    lo, hi = f0, f1
    last = s.get("band_ghz")
    if last and len(last) == 2:
        a, b = last[0] * 1e9, last[1] * 1e9
        if a >= f0 - 1e3 and b <= f1 + 1e3 and _band_from(freqs, a, b).sum() >= 10:
            lo, hi = a, b
        else:
            print(f"  (rentang terakhir {last[0]:g}-{last[1]:g} GHz di luar data ini, "
                  f"default jadi semua)")
    while True:
        ans = input(f"  Rentang frekuensi (GHz): Enter = sama seperti terakhir "
                    f"({_ghz(lo)}-{_ghz(hi)}) | s = semua | q = batal | ketik mis. 2 5: "
                    ).strip().lower()
        if ans == "q":
            return False
        if ans == "":
            a, b = lo, hi
        elif ans == "s":
            a, b = f0, f1
        else:
            nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[.,]\d+)?", ans)]
            if len(nums) != 2:
                print("  Ketik dua angka GHz, misal '2 5' atau '2.5 4' (desimal pakai titik).")
                continue
            a, b = min(nums) * 1e9, max(nums) * 1e9
            if a == b:
                print("  Batas bawah dan atas tidak boleh sama.")
                continue
            if a < f0 - 1e3 or b > f1 + 1e3:
                print(f"  Di luar data. Pilih antara {_ghz(f0)} dan {_ghz(f1)} GHz.")
                continue
        if _band_from(freqs, a, b).sum() < 10:
            print("  Terlalu sempit (kurang dari 10 titik frekuensi). Pilih rentang lebih lebar.")
            continue
        break
    last_c = s.get("warna") or "jet"
    while True:
        ans = input(f"  Warna energi (hex, rendah -> tinggi): Enter = sama seperti terakhir "
                    f"({last_c}) | j = jet | q = batal | ketik mis. #000080 #00ffff #ffff00 "
                    f"#ff0000: ").strip()
        if ans.lower() == "q":
            return False
        spec = last_c if ans == "" else ("jet" if ans.lower() == "j" else ans)
        try:
            cmap, spec = make_cmap(spec)
        except ValueError as e:
            print(f"  {e}")
            continue
        break
    sel = _set_proc(freqs, a, b, cmap, spec)
    lo_u, hi_u = PROC["band"]
    print(f"  -> frekuensi {_ghz(lo_u)}-{_ghz(hi_u)} GHz ({int(sel.sum())} titik), resolusi "
          f"jarak +-{SPEED_OF_LIGHT_M_S / (2 * (hi_u - lo_u)) * 100:.1f} cm; warna: {spec}")
    s.update(band_ghz=[lo_u / 1e9, hi_u / 1e9], warna=spec)
    save_settings(s)
    return True


def proc_from_saved(freqs):
    """Pakai pengaturan terakhir tanpa bertanya (untuk gambar 2D tiap slice sesi)."""
    s = load_settings()
    f0, f1 = float(freqs[0]), float(freqs[-1])
    lo, hi = f0, f1
    last = s.get("band_ghz")
    if last and len(last) == 2:
        a, b = last[0] * 1e9, last[1] * 1e9
        if a >= f0 - 1e3 and b <= f1 + 1e3 and _band_from(freqs, a, b).sum() >= 10:
            lo, hi = a, b
    try:
        cmap, spec = make_cmap(s.get("warna") or "jet")
    except ValueError:
        cmap, spec = make_cmap("jet")
    _set_proc(freqs, lo, hi, cmap, spec)


def select_band(freqs, signals):
    """Ambil hanya titik frekuensi di dalam rentang yang dipilih."""
    if PROC["band"] is None:
        return freqs, signals
    sel = _band_from(freqs, *PROC["band"])
    if sel.sum() < 2:
        raise ValueError("Rentang frekuensi yang dipilih tidak cocok dengan data ini.")
    return freqs[sel], signals[sel]


def current_cmap():
    return PROC["cmap"] if PROC["cmap"] is not None else matplotlib.colormaps["jet"]


# --- VISUALISASI ---

def plot_image(X, Y, mask, values_in_mask, antenna_positions=None,
               title="Hasil Rekonstruksi DAS", true_target=None,
               save_path=None, cmap="jet"):
    grid = np.full(X.shape, np.nan)
    grid[mask] = values_in_mask

    # Sesuaikan ukuran kanvas dengan proporsi bounding box domain, supaya
    # tidak ada spasi kosong berlebih di atas/bawah.
    y_vals = Y[mask]
    x_vals = X[mask]
    width_m = x_vals.max() - x_vals.min()
    height_m = y_vals.max() - y_vals.min()
    base_height = 5.0
    fig_w = base_height * (width_m / height_m) + 1.5
    fig_h = base_height + 0.6

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    im = ax.pcolormesh(X, Y, grid, shading="auto", cmap=cmap)
    plt.colorbar(im, ax=ax, label="Energi (normalisasi)")

    if antenna_positions is not None:
        ax.plot(antenna_positions[:, 0], antenna_positions[:, 1],
                "o", color="cyan", markersize=7, label="Antena")
        for i, (x, y) in enumerate(antenna_positions):
            ax.annotate(str(i + 1), (x, y), textcoords="offset points",
                        xytext=(0, 6), color="cyan", fontsize=8, ha="center")

    if true_target is not None:
        ax.plot(true_target[0], true_target[1], "x", color="white",
                markersize=12, markeredgewidth=2, label="Target sebenarnya")

    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(title)
    ax.set_aspect("equal")

    # Crop ke area domain saja -- ini bagian yang menghapus spasi kosong
    margin = 0.03 * width_m
    ax.set_xlim(x_vals.min() - margin, x_vals.max() + margin)
    ax.set_ylim(y_vals.min() - margin, y_vals.max() + margin)

    ax.legend(loc="upper right", framealpha=0.85)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=SAVE_DPI)
    return fig, ax


def save_image_csv(path, points, raw, image, region=None):
    """Simpan data yang membentuk gambar: 1 baris = 1 titik di domain.
    Kolom: x_m, y_m, energi_mentah (sebelum normalisasi),
    energi_normalisasi (nilai yang diwarnai di gambar), dan untuk mode
    'gabungan' juga di_dalam_busur (1/0)."""
    data = {
        "x_m": np.round(points[:, 0], 6),
        "y_m": np.round(points[:, 1], 6),
        "energi_mentah": raw,
        "energi_normalisasi": image,
    }
    if region is not None:
        data["di_dalam_busur"] = region.astype(int)
    tmp = path + ".tmp"   # tulis ke file sementara dulu supaya tidak setengah jadi
    pd.DataFrame(data).to_csv(tmp, index=False, float_format="%.9g")
    os.replace(tmp, path)


def _output_paths(stem, out_dir=None):
    """Path file hasil per beamformer: {'DAS': {'png': ..., 'csv': ...}, ...}"""
    suffix = "_gabungan" if DOMAIN_MODE == "gabungan" else ""
    paths = {}
    for bf in ("DAS", "DMAS"):
        band = f"_{PROC['band_label']}" if PROC["band_label"] else ""
        base = os.path.join(out_dir or OUTPUT_DIR, f"{stem}_{bf.lower()}{band}{suffix}")
        paths[bf] = {"png": base + ".png", "csv": base + ".csv"}
    return paths


def unique_output_stem(stem, out_dir=None):
    """Kalau gambar/CSV dengan nama ini sudah ada, pakai stem_2, stem_3, ...
    supaya hasil lama tidak pernah tertimpa."""
    candidate, k = stem, 2
    while any(os.path.exists(p) for files in _output_paths(candidate, out_dir).values()
              for p in files.values()):
        candidate = f"{stem}_{k}"
        k += 1
    return candidate


def run_imaging(objek_zip, baseline_zip, stem, show=True, out_dir=None):
    """Pipeline hilir: baca ZIP objek & baseline -> baseline subtraction ->
    DAS & DMAS -> simpan PNG + CSV -> tampilkan jendela gambar (show=True).
    out_dir: folder hasil (default OUTPUT_DIR). Return {'raw': {'DAS': ..,
    'DMAS': ..}, 'points': points} (energi mentah, dipakai ulang oleh 3D)."""
    # Tidak ditanyakan: kanal S21 (lihat IMAGING_CHANNELS), koreksi selalu baseline subtraction.
    mask_near = False

    freqs_hz, signals, channel_list = load_csv_zip(objek_zip, n_elements=N_ELEMENTS)
    print(f"\nData terbaca: {signals.shape[0]} titik frekuensi, {signals.shape[1]} kanal.")

    freqs_base, signals_baseline, base_ch = load_csv_zip(baseline_zip, n_elements=N_ELEMENTS)
    if freqs_base.shape != freqs_hz.shape or not np.allclose(freqs_base, freqs_hz):
        raise ValueError("Titik frekuensi data objek dan baseline tidak sama.")
    wanted = imaging_channels(channel_list, base_ch)
    signals = pick_channels(signals, channel_list, wanted)
    signals_baseline = pick_channels(signals_baseline, base_ch, wanted)
    channel_list = np.array(wanted, dtype=int)
    print(f"Kanal dipakai: {len(wanted)} ({'satu arah TX<RX' if len(wanted) == 45 else 'dua arah'})")
    signals_sub = subtract_baseline(signals, signals_baseline)
    print(f"Baseline subtraction: {os.path.basename(baseline_zip)}")
    freqs_hz, signals_sub = select_band(freqs_hz, signals_sub)
    print(f"Rentang frekuensi dipakai: {_ghz(freqs_hz[0])}-{_ghz(freqs_hz[-1])} GHz "
          f"({len(freqs_hz)} titik)")

    antenna_positions = array_positions()
    if DOMAIN_MODE == "half_disk":
        points, X, Y, mask = half_disk_domain(IMAGE_RESOLUTION_M)
        region = np.ones(len(points), dtype=bool)
    elif DOMAIN_MODE == "gabungan":
        points, X, Y, mask, region = combined_domain(IMAGE_RESOLUTION_M)
    else:
        raise ValueError(f"DOMAIN_MODE tidak dikenal: {DOMAIN_MODE!r} "
                         f"(pilih 'half_disk' atau 'gabungan')")
    print(f"Domain: {DOMAIN_MODE}")

    far_mask = None
    if mask_near:
        far_mask = mask_near_antennas(points, antenna_positions, 0.06)

    delays = compute_delays(antenna_positions, channel_list, points,
                            relative_permittivity=RELATIVE_PERMITTIVITY)

    os.makedirs(out_dir or OUTPUT_DIR, exist_ok=True)
    out_paths = _output_paths(stem, out_dir)
    raws = {}

    for name, fn in [("DAS", das), ("DMAS", dmas)]:
        print(f"Menghitung {name} ...")
        raw = fn(signals_sub, freqs_hz, delays)
        raws[name] = raw
        if DOMAIN_MODE == "half_disk":
            image = normalize(raw)
        else:
            image = normalize_in_region(raw, region)
        if far_mask is not None:
            image = image.copy()
            image[~far_mask] = 0

        # Titik puncak dicari di dalam region (half_disk: semua titik)
        peak_idx = np.flatnonzero(region)[np.argmax(image[region])]
        peak_xy = points[peak_idx]
        print(f"[{name}] Titik energi tertinggi: ({peak_xy[0]:.4f}, {peak_xy[1]:.4f}) m")

        if DOMAIN_MODE == "gabungan":
            outside = ~region
            if np.any(outside) and image[outside].max() > 1.0:
                print(f"  PERHATIAN: energi di luar busur mencapai "
                      f"{image[outside].max():.2f}x puncak di dalam busur.")
            shown = np.clip(image, 0.0, 1.0)   # >1 tampil jenuh (merah)
        else:
            shown = image

        # Data yang membentuk gambar (CSV) disimpan dulu, baru gambarnya
        save_image_csv(out_paths[name]["csv"], points, raw, shown,
                       region=region if DOMAIN_MODE == "gabungan" else None)
        print(f"  Disimpan: {out_paths[name]['csv']} ({len(points)} titik)")

        plot_image(X, Y, mask, shown, antenna_positions=antenna_positions,
                   title=f"Hasil {name} - {stem}  ({_ghz(freqs_hz[0])}-{_ghz(freqs_hz[-1])} GHz)",
                   save_path=out_paths[name]["png"], cmap=current_cmap())
        print(f"  Disimpan: {out_paths[name]['png']} ({SAVE_DPI} dpi)")

    if show:
        print("\nJendela gambar dibuka. Tutup semua jendela gambar untuk kembali ke menu.")
        plt.show()
    plt.close("all")
    return {"raw": raws, "points": points, "channels": wanted}


# ############################################################################
# ###############################  SISTEM  ###################################
# ############################################################################

def ask_choice(prompt, valid):
    """Tanya sampai jawabannya salah satu dari `valid` (huruf kecil)."""
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid:
            return choice
        print(f"  Input '{choice}' tidak dikenal. Pilih sesuai opsi yang tertera.")


def pick_zip_file(title):
    """Dialog pilih file (Windows). Kalau dialog tidak bisa dibuka, ketik path.
    Return path, atau None kalau dibatalkan."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)   # supaya muncul di depan VS Code
        path = filedialog.askopenfilename(
            parent=root, title=title, initialdir=BASE_DIR,
            filetypes=[("File ZIP", "*.zip"), ("Semua file", "*.*")])
        root.destroy()
        if not path:
            print("  Tidak ada file yang dipilih.")
            return None
        print(f"  Dipilih: {path}")
        return path
    except Exception:
        print("  Dialog pilih file tidak bisa dibuka, ketik path-nya saja.")

    while True:
        path = input("  Path file ZIP (kosong = batal): ").strip().strip('"')
        if not path:
            return None
        if os.path.isfile(path):
            return path
        print(f"  File tidak ditemukan: {path}. Coba lagi.")


def check_zip_matches_config(zip_path):
    """Pastikan ZIP berisi CSV lengkap (45 atau 90) dan frekuensinya sesuai konfigurasi
    hulu. Raise ValueError dengan alasan yang jelas kalau tidak."""
    freqs, _, _ = load_csv_zip(zip_path)
    ok = (len(freqs) == POINTS
          and abs(freqs[0] - START_FREQ) <= 1e3
          and abs(freqs[-1] - STOP_FREQ) <= 1e3)
    if not ok:
        raise ValueError(
            f"frekuensi file {freqs[0]/1e9:.3f}-{freqs[-1]/1e9:.3f} GHz, "
            f"{len(freqs)} titik; konfigurasi sekarang "
            f"{START_FREQ/1e9:.3f}-{STOP_FREQ/1e9:.3f} GHz, {POINTS} titik")
    return freqs


def migrate_legacy_names():
    """Program versi lama menyimpan baseline dengan nama 'kalibrasi'. Ganti
    namanya sekali ke 'baseline' supaya tetap terbaca. Arsip lama
    (kalibrasi_<tanggal_jam>) dibiarkan; tetap bisa dipilih lewat menu f."""
    renames = [
        (f"{LEGACY_NAME}.zip", f"{BASELINE_NAME}.zip"),
        (LEGACY_NAME, BASELINE_NAME),
        (f"{LEGACY_NAME}_baru.zip", f"{BASELINE_SCAN_NAME}.zip"),
        (f"{LEGACY_NAME}_baru", BASELINE_SCAN_NAME),
    ]
    for old, new in renames:
        src = os.path.join(BASE_DIR, old)
        dst = os.path.join(BASE_DIR, new)
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                os.replace(src, dst)
                print(f"Nama versi lama diganti: {old} -> {new}")
            except OSError as e:
                print(f"PERHATIAN: gagal mengganti nama {old} -> {new} ({e}). "
                      f"Ganti manual kalau ingin dipakai.")


def baseline_status():
    """Return (ada: bool, cocok: bool, keterangan: str)."""
    if not os.path.isfile(BASELINE_ZIP):
        return False, False, ""
    stamp = datetime.datetime.fromtimestamp(os.path.getmtime(BASELINE_ZIP))
    info = f"dibuat {stamp:%Y-%m-%d %H:%M}"
    try:
        check_zip_matches_config(BASELINE_ZIP)
    except Exception as e:
        return True, False, f"{info}; {e}"
    return True, True, info


def archive_baseline():
    """Ganti nama baseline aktif (zip & folder) jadi baseline_<tanggal_jam>."""
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    archived = []
    if os.path.exists(BASELINE_ZIP):
        dst = os.path.join(BASE_DIR, f"{BASELINE_NAME}_{stamp}.zip")
        os.replace(BASELINE_ZIP, dst)
        archived.append(os.path.basename(dst))
    if os.path.isdir(BASELINE_DIR):
        dst = os.path.join(BASE_DIR, f"{BASELINE_NAME}_{stamp}")
        os.replace(BASELINE_DIR, dst)
        archived.append(os.path.basename(dst))
    if archived:
        print(f"Baseline lama diarsipkan: {', '.join(archived)}")


def acquire_scan(scan_name):
    """Akuisisi 1 scan (alur hulu). Return path ZIP kalau semua pasangan lengkap,
    None kalau batal (q) atau LibreVNA tidak bisa terhubung."""
    scan_dir = os.path.join(BASE_DIR, scan_name)
    zip_path = os.path.join(BASE_DIR, f"{scan_name}.zip")
    if os.path.exists(zip_path):
        return zip_path

    os.makedirs(scan_dir, exist_ok=True)
    pairs = acquisition_pairs()
    total = len(pairs)
    pending = missing_pairs(scan_dir, pairs)

    print(f"\nFolder scan : {scan_dir}")
    print(f"Progres     : {total - len(pending)}/{total} pasangan sudah ada")
    if 0 < len(pending) < total:
        print("Melanjutkan scan yang belum selesai.")

    if pending:
        while True:
            try:
                vna = connect_vna()
                break
            except Exception as e:
                print(f"GAGAL konek ke LibreVNA-GUI: {e}")
                print("Pastikan LibreVNA-GUI sudah terbuka dan device ter-connect.")
                if ask_choice("  Enter = coba lagi | q = kembali ke menu: ", {"", "q"}) == "q":
                    return None

        if not run_acquisition(vna, scan_dir, pairs):
            done = total - len(missing_pairs(scan_dir, pairs))
            print(f"\nBerhenti sebelum lengkap ({done}/{total}). ZIP TIDAK dibuat.")
            print("Data yang sudah terukur tetap tersimpan; pakai nama yang sama "
                  "untuk melanjutkan.")
            return None

    print(f"\nSemua {total} pasangan lengkap. Membuat ZIP ...")
    make_zip(scan_dir, zip_path, pairs)
    print(f"ZIP siap: {zip_path}")
    if DELETE_CSV_AFTER_ZIP:
        delete_csvs(scan_dir, pairs)
        print("Folder CSV dihapus (DELETE_CSV_AFTER_ZIP = True).")
    return zip_path


def do_baseline_scan():
    print("\n=== SCAN BASELINE (tanpa objek) ===")
    print("Pastikan area di dalam busur KOSONG selama scan.")
    zip_path = acquire_scan(BASELINE_SCAN_NAME)
    if zip_path is None:
        return
    archive_baseline()
    os.replace(zip_path, BASELINE_ZIP)
    scan_dir = os.path.join(BASE_DIR, BASELINE_SCAN_NAME)
    if os.path.isdir(scan_dir):
        os.replace(scan_dir, BASELINE_DIR)
    print(f"Baseline aktif sekarang: {BASELINE_ZIP}")


def do_baseline_from_file():
    print("\n=== PAKAI FILE BASELINE LAMA ===")
    while True:
        path = pick_zip_file("Pilih ZIP baseline (scan kosong)")
        if path is None:
            return
        if os.path.exists(BASELINE_ZIP) and os.path.samefile(path, BASELINE_ZIP):
            print("  File itu sudah menjadi baseline aktif.")
            return
        try:
            check_zip_matches_config(path)
        except Exception as e:
            print(f"  File ditolak: {e}")
            print("  Pilih file lain, atau batalkan.")
            continue
        archive_baseline()
        shutil.copy2(path, BASELINE_ZIP)
        print(f"Baseline aktif sekarang: {BASELINE_ZIP} (disalin dari {os.path.basename(path)})")
        return


def do_change_baseline():
    choice = ask_choice("  s = scan baseline baru | f = pakai file baseline lama "
                        "| Enter = batal: ", {"s", "f", ""})
    if choice == "s":
        do_baseline_scan()
    elif choice == "f":
        do_baseline_from_file()


RESERVED_NAMES = (BASELINE_NAME, "output")


def ask_object_name():
    while True:
        name = input("\nNama objek (q = batal): ").strip()
        if name.lower() == "q":
            return None
        if not re.fullmatch(r"[A-Za-z0-9_\-]+", name):
            print("  Nama hanya boleh huruf, angka, _ atau - (tanpa spasi).")
            continue
        if name.lower().startswith(RESERVED_NAMES):
            print("  Nama yang diawali 'baseline' atau 'output' dipakai sistem. "
                  "Pakai nama lain.")
            continue
        if os.path.exists(os.path.join(BASE_DIR, f"{name}.zip")):
            print(f"  Nama '{name}' sudah dipakai ({name}.zip sudah ada). Pakai nama lain.")
            continue
        return name


def do_measure_object():
    print("\n=== UKUR OBJEK ===")
    name = ask_object_name()
    if name is None:
        return
    zip_path = acquire_scan(name)
    if zip_path is None:
        return
    if not ask_processing_settings(zip_freqs(zip_path)):
        print(f"Imaging dibatalkan. Data tetap tersimpan di {os.path.basename(zip_path)} "
              f"(bisa dicitrakan lewat i = imaging dari ZIP lama).")
        return
    out = os.path.join(OUTPUT_DIR, name)          # satu folder per pengambilan
    run_imaging(zip_path, BASELINE_ZIP, unique_output_stem(name, out), out_dir=out)


def _pick_valid_zip(title, ref_freqs=None):
    """Pilih ZIP sampai isinya valid (dan frekuensinya sama dengan ref_freqs
    kalau diberikan). Return (path, freqs) atau (None, None) kalau batal."""
    while True:
        path = pick_zip_file(title)
        if path is None:
            return None, None
        try:
            freqs, _, _ = load_csv_zip(path)
            if ref_freqs is not None and (freqs.shape != ref_freqs.shape
                                          or not np.allclose(freqs, ref_freqs)):
                raise ValueError("titik frekuensinya beda dengan ZIP objek.")
        except Exception as e:
            print(f"  File ditolak: {e}")
            print("  Pilih file lain, atau batalkan.")
            continue
        return path, freqs


def do_imaging_old():
    print("\n=== IMAGING DARI ZIP LAMA ===")
    objek_zip, objek_freqs = _pick_valid_zip("Pilih ZIP objek")
    if objek_zip is None:
        return

    baseline_zip = None
    if os.path.isfile(BASELINE_ZIP):
        choice = ask_choice("  Baseline: Enter = pakai baseline aktif | "
                            "f = pilih file lain | q = batal: ", {"", "f", "q"})
        if choice == "q":
            return
        if choice == "":
            try:
                base_freqs, _, _ = load_csv_zip(BASELINE_ZIP)
                if base_freqs.shape != objek_freqs.shape or \
                        not np.allclose(base_freqs, objek_freqs):
                    raise ValueError("titik frekuensinya beda dengan ZIP objek.")
                baseline_zip = BASELINE_ZIP
            except Exception as e:
                print(f"  Baseline aktif tidak bisa dipakai: {e}")
                print("  Pilih file baseline lain.")
    else:
        print("  Belum ada baseline aktif, pilih file baseline (scan kosong).")

    if baseline_zip is None:
        baseline_zip, _ = _pick_valid_zip("Pilih ZIP baseline (scan kosong)", objek_freqs)
        if baseline_zip is None:
            return

    if not ask_processing_settings(objek_freqs):
        print("Imaging dibatalkan.")
        return
    stem = os.path.splitext(os.path.basename(objek_zip))[0]
    out = os.path.join(OUTPUT_DIR, stem)          # satu folder per pengambilan
    run_imaging(objek_zip, baseline_zip, unique_output_stem(stem, out), out_dir=out)


# ############################################################################
# ##########################  REKONSTRUKSI 3D  ###############################
# ############################################################################
# Tiap slice dicitrakan dengan fungsi yang SAMA dengan mode 2D (load_csv_zip ->
# subtract_baseline -> compute_delays -> das/dmas), lalu ditumpuk menurut posisi
# geser objek z. Normalisasi GLOBAL per metode; interpolasi linear arah z hanya
# untuk tampilan (nilai di z yang diukur sama persis dengan data).

R3D_Z_INTERP_STEP_CM = 1.0       # langkah interpolasi tampilan
R3D_ISO_LEVELS = (0.5, 0.7)      # level isosurface (energi normalisasi global)
R3D_ISO_STEP_M = 0.005           # grid isosurface diturunkan ke ~5 mm (tampilan saja)
R3D_OPEN_VIEWER = True           # buka viewer_3d.html di browser setelah selesai
R3D_SHOW_WINDOWS = True          # tampilkan jendela gambar 3D setelah selesai
R3D_CHUNK = {"DAS": 4000, "DMAS": 4000}  # titik per potongan; hasil identik
R3D_METHODS = {"DAS": das, "DMAS": dmas}
R3D_CACHE_DIR = os.path.join(BASE_DIR, "output_3d_cache")


def fmt_z(z):
    return f"{z:g}"


def _r3d_domain():
    """Domain di dalam busur yang dipakai 3D (sama persis dengan 2D)."""
    return half_disk_domain(IMAGE_RESOLUTION_M)


_FILE_ID_MEMO = {}


def _file_id(path):
    """Sidik jari isi file (SHA-1): cache tetap berlaku walau file disalin/
    folder sesi diganti nama, dan otomatis tidak berlaku kalau isinya berubah."""
    st = os.stat(path)
    memo_key = (os.path.abspath(path), st.st_size, st.st_mtime_ns)
    if memo_key not in _FILE_ID_MEMO:
        h = hashlib.sha1()
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
        _FILE_ID_MEMO[memo_key] = h.hexdigest()
    return _FILE_ID_MEMO[memo_key]


def _r3d_cache_path(slice_zip, baseline_zip, method, channels):
    key = json.dumps({"baseline": _file_id(baseline_zip), "slice": _file_id(slice_zip),
                      "a": ARRAY_SEMI_AXIS_X_M, "b": ARRAY_SEMI_AXIS_Y_M,
                      "res": IMAGE_RESOLUTION_M,
                      "angles": list(ELEMENT_ANGLES_DEG), "eps": RELATIVE_PERMITTIVITY,
                      "channels": [list(map(int, c)) for c in channels],
                      "band": "semua" if (PROC["band"] is None or PROC["full"])
                      else [round(PROC["band"][0]), round(PROC["band"][1])],
                      "method": method}, sort_keys=True)
    return os.path.join(R3D_CACHE_DIR,
                        hashlib.sha1(key.encode()).hexdigest()[:16] + f"_{method.lower()}.npy")


def r3d_store_cache(slice_zip, baseline_zip, method, raw, channels):
    """Simpan energi mentah hasil mode 2D supaya 3D tidak menghitung ulang.
    channels = daftar kanal yang benar-benar dipakai (ikut jadi kunci cache)."""
    os.makedirs(R3D_CACHE_DIR, exist_ok=True)
    np.save(_r3d_cache_path(slice_zip, baseline_zip, method, channels), raw)


def r3d_compute_raw(method, slices, baseline_zip):
    """Energi mentah tiap slice (n_slice x n_titik). Pakai cache per slice."""
    points, _, _, _ = _r3d_domain()
    pos = array_positions()
    base = delays = f_b = None
    raw = []
    # kanal yang sama untuk SEMUA slice (supaya energi antar-slice sebanding)
    wanted = imaging_channels(zip_channel_list(baseline_zip),
                              *[zip_channel_list(p) for p, _ in slices])
    for path, z in slices:
        cache = _r3d_cache_path(path, baseline_zip, method, wanted)
        if os.path.isfile(cache):
            img = np.load(cache)
            if img.shape == (len(points),):
                print(f"[{method}] z = {fmt_z(z):>6} cm  ({os.path.basename(path)})  dari cache")
                raw.append(img)
                continue
        if base is None:
            f_b, base, base_ch = load_csv_zip(baseline_zip)
            base = pick_channels(base, base_ch, wanted)
        f, s, ch = load_csv_zip(path)
        s = pick_channels(s, ch, wanted)
        if f.shape != f_b.shape or not np.allclose(f, f_b):
            raise ValueError(f"Frekuensi {os.path.basename(path)} beda dengan baseline.")
        if delays is None:
            delays = compute_delays(array_positions(), np.array(wanted, dtype=int), points)
        print(f"[{method}] z = {fmt_z(z):>6} cm  ({os.path.basename(path)})  menghitung ...",
              flush=True)
        f_sel, s_sel = select_band(f, subtract_baseline(s, base))
        img = R3D_METHODS[method](s_sel, f_sel, delays, chunk_size=R3D_CHUNK[method])
        r3d_store_cache(path, baseline_zip, method, img, wanted)
        raw.append(img)
    return np.array(raw)


def zip_channel_list(path):
    """Pasangan yang ada di ZIP (tanpa membaca isi CSV): 90 atau 45."""
    with zipfile.ZipFile(path) as zf:
        names = {os.path.basename(m).replace(" ", "_") for m in zf.namelist()}
    full = all_pairs(N_ELEMENTS)
    return full if all(csv_name(*p) in names for p in full) else one_way_pairs(N_ELEMENTS)


def r3d_build_volume(raw, mask):
    lo, hi = raw.min(), raw.max()
    norm = (raw - lo) / (hi - lo) if hi - lo > 1e-30 else np.zeros_like(raw)
    vol = np.full((len(raw),) + mask.shape, np.nan)
    for k in range(len(raw)):
        vol[k][mask] = norm[k]
    return vol


def r3d_interpolate_z(vol, z_cm, include_measured=True):
    z_new = np.arange(z_cm[0], z_cm[-1] + 1e-9, R3D_Z_INTERP_STEP_CM)
    if include_measured:
        z_new = np.unique(np.round(np.r_[z_new, z_cm], 6))
    vol_i = interp1d(z_cm, vol, axis=0, kind="linear")(z_new)
    return z_new, vol_i


def _draw_arc(ax, pos):
    ax.plot(pos[:, 0], pos[:, 1], "o", color="white", ms=4, mec="k", mew=0.5)


def r3d_fig_slices(method, vol, X, Y, z_cm, raw, pos, baseline_zip, out_dir):
    n = len(z_cm)
    ncol = min(n, 5)
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.3 * ncol, 2.3 * nrow + 0.4),
                             constrained_layout=True, squeeze=False)
    axes = axes.ravel()
    peaks = raw.max(axis=1) / raw.max()
    for k in range(len(axes)):
        ax = axes[k]
        if k >= n:
            ax.axis("off")
            continue
        im = ax.pcolormesh(X, Y, vol[k], cmap=current_cmap(), vmin=0, vmax=1, shading="auto")
        _draw_arc(ax, pos)
        ax.set_aspect("equal")
        ax.set_title(f"z = {fmt_z(z_cm[k])} cm  (puncak {peaks[k]:.2f})", fontsize=9)
        ax.set_xlabel("x (m)", fontsize=8)
        ax.set_ylabel("y (m)", fontsize=8)
        ax.tick_params(labelsize=7)
    fig.colorbar(im, ax=axes[:n].tolist(), shrink=0.9, label="Energi (normalisasi global)")
    fig.suptitle(f"{method} per slice, skala warna sama untuk semua slice "
                 f"(baseline: {os.path.basename(baseline_zip)}, "
                 f"{PROC['band_label'] or 'semua frekuensi'})", fontsize=10)
    p = os.path.join(out_dir, f"slices_{method.lower()}.png")
    fig.savefig(p, dpi=150)
    return p, fig


def _mips(v):
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmax(v, axis=0), np.nanmax(v, axis=1), np.nanmax(v, axis=2)


def _edges(c):
    c = np.asarray(c, dtype=float)
    if len(c) == 1:
        return np.array([c[0] - 0.5, c[0] + 0.5])
    mid = (c[1:] + c[:-1]) / 2
    return np.r_[c[0] - (c[1] - c[0]) / 2, mid, c[-1] + (c[-1] - c[-2]) / 2]


def r3d_fig_ortho(method, vol, z_cm, z_i, vol_i, x_ax, y_ax, pos, out_dir):
    fig, axes = plt.subplots(3, 2, figsize=(12, 9), constrained_layout=True)
    x_e, y_e = _edges(x_ax), _edges(y_ax)
    for col, (v, ze, label) in enumerate([
            (vol, _edges(z_cm), "Tumpukan ASLI (tiap slice = satu blok)"),
            (vol_i, _edges(z_i), f"Interpolasi linear {R3D_Z_INTERP_STEP_CM:g} cm (TAMPILAN)")]):
        front, top, side = _mips(v)
        a = axes[0, col]
        im = a.pcolormesh(x_e, y_e, front, cmap=current_cmap(), vmin=0, vmax=1, shading="flat")
        _draw_arc(a, pos)
        a.set_aspect("equal"); a.set_xlabel("x (m)"); a.set_ylabel("y (m)")
        a.set_title(f"{label}\nTampak depan (maks. sepanjang z)", fontsize=9)
        a = axes[1, col]
        a.pcolormesh(x_e, ze, top, cmap=current_cmap(), vmin=0, vmax=1, shading="flat")
        a.set_xlabel("x (m)"); a.set_ylabel("z geser objek (cm)"); a.set_yticks(z_cm)
        a.set_title("Tampak atas (maks. sepanjang y)", fontsize=9)
        a = axes[2, col]
        a.pcolormesh(ze, y_e, side.T, cmap=current_cmap(), vmin=0, vmax=1, shading="flat")
        a.set_xlabel("z geser objek (cm)"); a.set_ylabel("y (m)"); a.set_xticks(z_cm)
        a.set_title("Tampak samping (maks. sepanjang x)", fontsize=9)
    fig.colorbar(im, ax=axes, shrink=0.6, label="Energi (normalisasi global)")
    fig.suptitle(f"{method}: proyeksi maksimum volume. Hanya z = "
                 f"{', '.join(fmt_z(z) for z in z_cm)} cm yang diukur.", fontsize=11)
    p = os.path.join(out_dir, f"ortho_{method.lower()}.png")
    fig.savefig(p, dpi=130)
    return p, fig


def r3d_fig_iso(method, vol, x_ax, y_ax, z_cm, out_dir):
    from skimage.measure import marching_cubes
    step = max(1, int(round(R3D_ISO_STEP_M / IMAGE_RESOLUTION_M)))   # tampilan saja
    xs, ys = x_ax[::step], y_ax[::step]
    z_u, vol_u = r3d_interpolate_z(vol[:, ::step, ::step], z_cm, include_measured=False)
    v = np.nan_to_num(vol_u, nan=0.0)
    dz = (z_u[1] - z_u[0]) / 100.0 if len(z_u) > 1 else 0.01
    dy, dx = ys[1] - ys[0], xs[1] - xs[0]
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    cm = current_cmap()                       # warna permukaan = warna energi di levelnya
    colors = {lev: (*cm(lev)[:3], 0.25 if i == 0 else 0.7)
              for i, lev in enumerate(R3D_ISO_LEVELS)}
    if len(z_u) >= 2:
        for lev in R3D_ISO_LEVELS:
            if v.max() < lev:
                continue
            verts, faces, _, _ = marching_cubes(v, level=lev, spacing=(dz, dy, dx))
            ax.plot_trisurf(verts[:, 2] + xs[0], verts[:, 0] * 100 + z_u[0], faces,
                            verts[:, 1] + ys[0], color=colors.get(lev, (0.5, 0.5, 0.5, 0.4)),
                            linewidth=0, antialiased=True)
    A, B = ARRAY_SEMI_AXIS_X_M, ARRAY_SEMI_AXIS_Y_M
    th = np.linspace(-np.pi / 2, np.pi / 2, 100)
    for z in z_cm:
        ax.plot(A * np.sin(th), np.full_like(th, z), B * np.cos(th), color="gray", lw=0.6)
        ax.plot([-A, A], [z, z], [0, 0], color="gray", lw=0.6)
    ax.set_xlabel("x (m)"); ax.set_ylabel("z geser objek (cm)"); ax.set_zlabel("y (m)")
    ax.set_xlim(-A, A); ax.set_zlim(0, B); ax.set_ylim(z_cm[0], z_cm[-1])
    ax.set_box_aspect((2 * A, max((z_cm[-1] - z_cm[0]) / 100, 0.05), B))
    ax.view_init(elev=22, azim=-60)
    ax.set_title(f"{method}: isosurface {R3D_ISO_LEVELS[0]} (transparan) & {R3D_ISO_LEVELS[-1]} "
                 f"(pekat), volume interpolasi, {PROC['band_label'] or 'semua frekuensi'}.\n"
                 f"Garis abu = bidang slice yang diukur.", fontsize=10)
    p = os.path.join(out_dir, f"iso_{method.lower()}.png")
    fig.savefig(p, dpi=140, bbox_inches="tight")
    return p, fig


def r3d_write_html(results, x_ax, y_ax, z_cm, z_i, baseline_zip, out_dir):
    """Viewer 3D interaktif, satu file HTML mandiri (tanpa internet/library).
    Data diturunkan ke 1 cm di x,y dan dikuantisasi 8 bit (0..255)."""
    import base64
    step = max(1, int(round(0.01 / IMAGE_RESOLUTION_M)))
    xs, ys = x_ax[::step], y_ax[::step]
    data = {"x": np.round(xs, 4).tolist(), "y": np.round(ys, 4).tolist(),
            "z": np.round(z_i, 3).tolist(), "zcm": [round(float(z), 3) for z in z_cm],
            "a": ARRAY_SEMI_AXIS_X_M, "b": ARRAY_SEMI_AXIS_Y_M,
            "pos": np.round(array_positions(), 4).tolist(),
            "iso": R3D_ISO_LEVELS[0], "base": os.path.basename(baseline_zip),
            "band": PROC["band_label"] or "semua frekuensi",
            "lut": (np.round(current_cmap()(np.linspace(0, 1, 256))[:, :3] * 255)
                    .astype(int).tolist()),
            "methods": {}}
    for m, (vol_i, raw) in results.items():
        v = vol_i[:, ::step, ::step]
        q = np.where(np.isnan(v), 0, np.clip(np.round(v * 254) + 1, 1, 255)).astype(np.uint8)
        data["methods"][m] = base64.b64encode(q.tobytes()).decode()   # 0 = di luar domain
    html = R3D_HTML_TEMPLATE.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    p = os.path.join(out_dir, "viewer_3d.html")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(html)
    return p


def r3d_summary_table(slices, baseline_zip):
    lines = ["  No  Posisi (cm)  File"]
    for k, (p, z) in enumerate(slices):
        lines.append(f"  {k + 1:>2}  {fmt_z(z):>11}  {os.path.basename(p)}")
    lines.append(f"  Baseline: {os.path.basename(baseline_zip)}")
    return "\n".join(lines)


def build_3d(slices, baseline_zip, out_dir, title=""):
    """slices: [(path ZIP, z_cm), ...] dalam urutan sesi. Ditumpuk menurut z
    (pasangan file-posisi tetap). Semua hasil ke out_dir."""
    import webbrowser
    slices = sorted(slices, key=lambda t: t[1])
    os.makedirs(out_dir, exist_ok=True)
    z_cm = np.array([z for _, z in slices], dtype=float)
    points, X, Y, mask = _r3d_domain()
    x_ax, y_ax = X[0], Y[:, 0]
    pos = array_positions()

    report = [f"REKONSTRUKSI 3D {title}".strip(), r3d_summary_table(slices, baseline_zip),
              f"  Resolusi grid: {IMAGE_RESOLUTION_M * 1000:g} mm",
              f"  Rentang frekuensi: {PROC['band_label'] or 'semua'}",
              f"  Warna energi: {PROC['cmap_spec']}", ""]
    results, outputs = {}, []
    for m in R3D_METHODS:
        raw = r3d_compute_raw(m, slices, baseline_zip)
        vol = r3d_build_volume(raw, mask)
        z_i, vol_i = r3d_interpolate_z(vol, z_cm)
        idx = [int(np.argmin(np.abs(z_i - z))) for z in z_cm]
        assert np.allclose(np.nan_to_num(vol_i[idx]), np.nan_to_num(vol)), \
            "interpolasi mengubah data"
        results[m] = (vol_i, raw)

        lines = [f"[{m}] energi puncak tiap slice (relatif thd puncak global):"]
        for k, z in enumerate(z_cm):
            j = np.argmax(raw[k])
            lines.append(f"   z={fmt_z(z):>6} cm  puncak={raw[k, j] / raw.max():.3f}  "
                         f"di (x={points[j, 0]:+.3f}, y={points[j, 1]:.3f}) m")
        print("\n" + "\n".join(lines))
        report += lines + [""]
        for p, _fig in (r3d_fig_slices(m, vol, X, Y, z_cm, raw, pos, baseline_zip, out_dir),
                        r3d_fig_ortho(m, vol, z_cm, z_i, vol_i, x_ax, y_ax, pos, out_dir),
                        r3d_fig_iso(m, vol, x_ax, y_ax, z_cm, out_dir)):
            outputs.append(p)
    html = r3d_write_html(results, x_ax, y_ax, z_cm, z_i, baseline_zip, out_dir)
    outputs.append(html)
    rpath = os.path.join(out_dir, "ringkasan.txt")
    with open(rpath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")
    outputs.append(rpath)

    print(f"\nOutput 3D di {out_dir}:")
    for p in outputs:
        print("  ", os.path.basename(p))
    if R3D_OPEN_VIEWER:
        try:
            webbrowser.open("file:///" + os.path.abspath(html).replace("\\", "/").lstrip("/"))
        except Exception:
            pass
    if R3D_SHOW_WINDOWS and plt.get_backend().lower() != "agg":
        print("\nJendela gambar 3D dibuka. Tutup semua jendela untuk melanjutkan.")
        plt.show()
    plt.close("all")
    return out_dir


R3D_HTML_TEMPLATE = r"""<!doctype html>
<html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Volume 3D Vivaldi</title>
<style>
:root{--bg:#fafafa;--panel:#fff;--fg:#1c1c1c;--mut:#5f5f5f;--line:#dcdcdc;--grid:#b9b9b9}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121212;--panel:#1b1b1b;--fg:#ececec;--mut:#a6a6a6;--line:#333;--grid:#555}}
:root[data-theme="dark"]{--bg:#121212;--panel:#1b1b1b;--fg:#ececec;--mut:#a6a6a6;--line:#333;--grid:#555}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1100px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:0 0 4px;font-weight:600}
p{margin:4px 0;color:var(--mut)}
.ctl{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;margin:12px 0;padding:10px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
label{display:flex;gap:8px;align-items:center}
select,button{font:inherit;color:var(--fg);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 8px}
input[type=range]{width:160px}
.wrap{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:8px}
canvas{display:block;width:100%;height:68vh;min-height:380px;touch-action:none;cursor:grab}
.leg{position:absolute;right:12px;top:12px;display:flex;gap:6px;align-items:stretch;font-size:12px;color:var(--mut)}
.bar{width:12px;height:140px;border-radius:2px;background:linear-gradient(to top,#00007f,#0000ff,#00ffff,#7fff7f,#ffff00,#ff0000,#7f0000)}
.lab{display:flex;flex-direction:column;justify-content:space-between}
.note{font-size:12px}
</style></head><body><main>
<h1>Volume 3D dari tumpukan slice</h1>
<p id="info"></p>
<div class="ctl">
<label>Metode <select id="m"></select></label>
<label>Ambang energi <input id="lv" type="range" min="0.2" max="0.95" step="0.05"><b id="lvv"></b></label>
<label><input id="only" type="checkbox"> Hanya slice yang diukur (tanpa interpolasi)</label>
<button id="reset">Reset sudut</button>
</div>
<div class="wrap"><canvas id="c"></canvas>
<div class="leg"><div class="bar"></div><div class="lab"><span>1.0</span><span>0.5</span><span>0.0</span></div></div></div>
<p class="note">Seret untuk memutar, scroll/pinch untuk zoom. Titik = voxel 1 cm dengan energi (normalisasi global) &ge; ambang.
Garis abu-abu = busur antena di tiap posisi slice yang diukur.</p>
</main><script>
const D=__DATA__;
const nx=D.x.length,ny=D.y.length,nz=D.z.length;
const vols={};for(const k in D.methods){const b=atob(D.methods[k]),a=new Uint8Array(b.length);for(let i=0;i<b.length;i++)a[i]=b.charCodeAt(i);vols[k]=a}
const measured=new Set(D.zcm.map(z=>D.z.findIndex(v=>Math.abs(v-z)<1e-3)));
document.getElementById('info').textContent='Baseline: '+D.base+'. Frekuensi: '+D.band+'. Normalisasi global per metode. Slice diukur hanya di z = '+D.zcm.join(', ')+' cm; di antaranya interpolasi linear (tampilan saja).';
const sel=document.getElementById('m'),lv=document.getElementById('lv'),lvv=document.getElementById('lvv'),only=document.getElementById('only');
Object.keys(vols).forEach(k=>{const o=document.createElement('option');o.value=o.textContent=k;sel.appendChild(o)});
lv.value=D.iso;
function jet(t){return D.lut[Math.max(0,Math.min(255,Math.round(t*255)))]}
document.querySelector('.bar').style.background='linear-gradient(to top,'+[0,32,64,96,128,160,192,224,255].map(i=>'rgb('+D.lut[i].join(',')+')').join(',')+')';
const cv=document.getElementById('c'),ctx=cv.getContext('2d');
let yaw=-0.75,pitch=0.35,zoom=0.85;
const cz=(D.zcm[0]+D.zcm[D.zcm.length-1])/200,cy=D.b/2;
function css(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
function proj(x,y,z,W,H,s){x-=0;y-=cy;z-=cz;const c=Math.cos(yaw),sn=Math.sin(yaw);let X=c*x+sn*z,Z=-sn*x+c*z;const cp=Math.cos(pitch),sp=Math.sin(pitch);let Y=cp*y-sp*Z;Z=sp*y+cp*Z;return[W/2+X*s,H/2-Y*s,Z]}
let pts=[];
function build(){const v=vols[sel.value],t=+lv.value;lvv.textContent=t.toFixed(2);pts=[];
 for(let k=0;k<nz;k++){if(only.checked&&!measured.has(k))continue;
  for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){const q=v[(k*ny+j)*nx+i];if(!q)continue;const e=(q-1)/254;if(e>=t)pts.push([D.x[i],D.y[j],D.z[k]/100,e])}}
 draw()}
function draw(){const dpr=window.devicePixelRatio||1,W=cv.clientWidth,H=cv.clientHeight;cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);
 ctx.clearRect(0,0,W,H);const s=Math.min(W,H)*1.5*zoom;
 ctx.strokeStyle=css('--grid');ctx.lineWidth=1;ctx.fillStyle=css('--mut');ctx.font='12px system-ui';
 for(const z of D.zcm){ctx.beginPath();for(let a=0;a<=60;a++){const th=-Math.PI/2+Math.PI*a/60;const p=proj(D.a*Math.sin(th),D.b*Math.cos(th),z/100,W,H,s);a?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1])}
  const p=proj(-D.a,0,z/100,W,H,s);ctx.lineTo(p[0],p[1]);ctx.stroke();const l=proj(D.a+0.03,0,z/100,W,H,s);ctx.fillText('z='+z+' cm',l[0],l[1])}
 const ax=[[[0,0,cz],[0.45,0,cz],'x'],[[0,0,cz],[0,0.45,cz],'y'],[[0,0,D.zcm[0]/100],[0,0,D.zcm[D.zcm.length-1]/100+0.05],'z']];
 for(const[a,b,n]of ax){const p=proj(...a,W,H,s),q=proj(...b,W,H,s);ctx.beginPath();ctx.moveTo(p[0],p[1]);ctx.lineTo(q[0],q[1]);ctx.stroke();ctx.fillText(n,q[0]+4,q[1])}
 const P=pts.map(p=>{const r=proj(p[0],p[1],p[2],W,H,s);return[r[0],r[1],r[2],p[3]]});P.sort((a,b)=>a[2]-b[2]);
 const sz=Math.max(2,0.011*s);for(const p of P){const c=jet(p[3]);ctx.fillStyle='rgba('+c[0]+','+c[1]+','+c[2]+','+(0.35+0.6*p[3]).toFixed(2)+')';ctx.fillRect(p[0]-sz/2,p[1]-sz/2,sz,sz)}
 ctx.fillStyle=css('--mut');ctx.fillText(P.length+' voxel',10,H-10)}
let drag=null;const ptrs=new Map();let pinch0=null;
cv.addEventListener('pointerdown',e=>{cv.setPointerCapture(e.pointerId);ptrs.set(e.pointerId,[e.clientX,e.clientY]);drag=[e.clientX,e.clientY,yaw,pitch];cv.style.cursor='grabbing'});
cv.addEventListener('pointermove',e=>{if(!ptrs.has(e.pointerId))return;ptrs.set(e.pointerId,[e.clientX,e.clientY]);
 if(ptrs.size==2){const[a,b]=[...ptrs.values()];const d=Math.hypot(a[0]-b[0],a[1]-b[1]);if(!pinch0)pinch0=[d,zoom];zoom=Math.min(5,Math.max(0.3,pinch0[1]*d/pinch0[0]));draw();return}
 if(drag){yaw=drag[2]+(e.clientX-drag[0])*0.01;pitch=Math.max(-1.5,Math.min(1.5,drag[3]+(e.clientY-drag[1])*0.01));draw()}});
function up(e){ptrs.delete(e.pointerId);if(ptrs.size<2)pinch0=null;if(!ptrs.size){drag=null;cv.style.cursor='grab'}}
cv.addEventListener('pointerup',up);cv.addEventListener('pointercancel',up);
cv.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.min(5,Math.max(0.3,zoom*Math.exp(-e.deltaY*0.001)));draw()},{passive:false});
document.getElementById('reset').onclick=()=>{yaw=-0.75;pitch=0.35;zoom=0.85;draw()};
sel.onchange=build;lv.oninput=build;only.onchange=build;addEventListener('resize',draw);
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',draw);build();
</script></body></html>
"""


# ############################################################################
# ##############################  SESI 3D  ###################################
# ############################################################################
# Satu sesi 3D = satu folder sesi_3d/<nama>/ berisi:
#   sesi.json                 status sesi (posisi, file, sumber, baseline)
#   baseline.zip / baseline_sesi.zip   baseline yang dipakai sesi ini
#   slice_01_z0.zip, slice_01_z0/      data tiap slice (+ folder CSV kalau diukur)
#   slice_02_z10_lama_<waktu>.zip      data lama slice yang diedit (cadangan)
#   2d/                       gambar & CSV 2D tiap slice yang diukur
#   hasil_3d_1-6GHz/, ...     hasil rekonstruksi 3D (nama = rentang frekuensi)
# Status "lengkap" tiap slice dibaca dari ada/tidaknya ZIP-nya, jadi kalau
# program terhenti di tengah jalan tidak ada data yang hilang: pengukuran
# dilanjutkan dari pasangan TX-RX yang belum ada.

SESSION_ROOT = os.path.join(BASE_DIR, "sesi_3d")
ACTIVE_FILE = os.path.join(SESSION_ROOT, "_aktif.txt")
STATE_NAME = "sesi.json"


class Batal(Exception):
    """User mengetik q di pertanyaan sesi 3D."""


class Jeda(Exception):
    """Sesi dihentikan sementara (pengukuran/pemilihan file dihentikan)."""


def ask(prompt):
    ans = input(prompt).strip()
    if ans.lower() == "q":
        raise Batal()
    return ans


def _num(text):
    return float(text.replace(",", "."))


def ask_int(prompt, minimum, maximum=None, default=None):
    while True:
        ans = ask(prompt)
        if ans == "" and default is not None:
            return default
        try:
            n = int(ans)
        except ValueError:
            print(f"  '{ans}' bukan bilangan bulat.")
            continue
        if n < minimum or (maximum is not None and n > maximum):
            print(f"  Pilih antara {minimum} dan {maximum}." if maximum is not None
                  else f"  Minimal {minimum}.")
            continue
        return n


def ask_float(prompt, nonzero=False, default=None):
    while True:
        ans = ask(prompt)
        if ans == "" and default is not None:
            return default
        try:
            v = _num(ans)
        except ValueError:
            print(f"  '{ans}' bukan angka.")
            continue
        if nonzero and v == 0:
            print("  Tidak boleh 0.")
            continue
        return v


def ask_positions():
    """Return daftar posisi (cm) dalam urutan yang diketik user."""
    n = ask_int("\nJumlah slice yang digabung (minimal 2): ", 2)
    z0 = ask_float("Posisi slice pertama (cm): ")
    dz = ask_float("Jarak antar-slice (cm): ", nonzero=True)
    zs = [round(z0 + k * dz, 6) for k in range(n)]
    while True:
        print(f"  -> posisi: {', '.join(fmt_z(z) for z in zs)} cm")
        ans = ask("  Benar? (Enter = ya | m = ketik manual | q = batal): ").lower()
        if ans == "":
            return zs
        if ans != "m":
            print("  Pilih Enter, m, atau q.")
            continue
        while True:
            txt = ask(f"  Ketik {n} posisi (cm), pisahkan dengan koma atau spasi, "
                      f"desimal pakai titik.\n  Contoh: 0, 10, 25, 40\n  > ")
            parts = [p for p in re.split(r"[,\s;]+", txt) if p]
            try:
                manual = [round(float(p), 6) for p in parts]
            except ValueError:
                print("  Ada yang bukan angka. Desimal pakai titik (2.5), pemisah koma/spasi.")
                continue
            if len(manual) != n:
                print(f"  Yang diketik {len(manual)} posisi, seharusnya {n}.")
                continue
            if len(set(manual)) != n:
                print("  Ada posisi yang sama. Tiap slice harus beda posisi.")
                continue
            zs = manual
            break


def _same(a, b):
    try:
        return os.path.samefile(a, b)
    except OSError:
        return os.path.abspath(a) == os.path.abspath(b)


def _stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")


def _z_tag(z):
    return "z" + fmt_z(z).replace("-", "m").replace(".", "p")


# --- file status sesi ---

def sess_dir(name):
    return os.path.join(SESSION_ROOT, name)


def save_state(st):
    d = sess_dir(st["nama"])
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, STATE_NAME)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def load_state(name):
    with open(os.path.join(sess_dir(name), STATE_NAME), encoding="utf-8") as fh:
        st = json.load(fh)
    st["nama"] = name          # nama folder yang berlaku (kalau folder diganti nama)
    return st


def set_active(name):
    os.makedirs(SESSION_ROOT, exist_ok=True)
    with open(ACTIVE_FILE, "w", encoding="utf-8") as fh:
        fh.write(name)


def get_active():
    try:
        with open(ACTIVE_FILE, encoding="utf-8") as fh:
            name = fh.read().strip()
    except OSError:
        return None
    if name and os.path.isfile(os.path.join(sess_dir(name), STATE_NAME)):
        return name
    clear_active()
    return None


def clear_active():
    try:
        os.remove(ACTIVE_FILE)
    except OSError:
        pass


def slice_zip(st, k):
    return os.path.join(sess_dir(st["nama"]), st["slices"][k]["file"])


def slice_done(st, k):
    return os.path.isfile(slice_zip(st, k))


def baseline_path(st):
    return os.path.join(sess_dir(st["nama"]), st["baseline"]["file"])


def n_done(st):
    return sum(slice_done(st, k) for k in range(len(st["slices"])))


def _rel_scan(st, stem):
    """Nama scan untuk acquire_scan() (relatif thd BASE_DIR)."""
    return os.path.relpath(os.path.join(sess_dir(st["nama"]), stem), BASE_DIR)


def _new_slice(k, z, sumber):
    return {"z": z, "file": f"slice_{k + 1:02d}_{_z_tag(z)}.zip", "sumber": sumber, "asal": None}


def session_table(st):
    lines = [f"  Sesi    : {st['nama']}",
             f"  Baseline: {st['baseline']['file']} ({st['baseline']['jenis']})"
             + ("" if os.path.isfile(baseline_path(st)) else "  [BELUM ADA]"),
             "  No  Posisi (cm)  Sumber  Status    File"]
    for k, sl in enumerate(st["slices"]):
        status = "lengkap" if slice_done(st, k) else "belum"
        lines.append(f"  {k + 1:>2}  {fmt_z(sl['z']):>11}  {sl['sumber']:<6}  {status:<8}  "
                     f"{sl['file']}")
    return "\n".join(lines)


def ask_session_name(prompt, default=None, current=None):
    while True:
        ans = ask(prompt) or (default or "")
        if not ans:
            print("  Nama tidak boleh kosong.")
            continue
        if not re.fullmatch(r"[A-Za-z0-9_\-]+", ans) or ans.startswith("_"):
            print("  Nama hanya boleh huruf, angka, _ atau - (tanpa spasi, tidak diawali _).")
            continue
        if ans != current and os.path.exists(sess_dir(ans)):
            print(f"  Sesi '{ans}' sudah ada. Pakai nama lain.")
            continue
        return ans


def save_named(st):
    """Simpan sesi dengan nama pilihan user (bisa ganti nama folder), lalu
    lepas dari status 'aktif'. Bisa dipanggil lagi lewat pilihan l."""
    new = ask_session_name(f"  Simpan sesi dengan nama (Enter = {st['nama']}): ",
                           default=st["nama"], current=st["nama"])
    if new != st["nama"]:
        os.replace(sess_dir(st["nama"]), sess_dir(new))
        st["nama"] = new
        save_state(st)
    clear_active()
    print(f"  Sesi disimpan di sesi_3d/{new}/ ({n_done(st)}/{len(st['slices'])} slice lengkap). "
          f"Panggil lagi lewat pilihan l di awal program.")


# --- baseline sesi ---

def choose_session_baseline():
    """Return dict {'jenis': 'utama'|'file'|'scan', 'asal': path|None}."""
    print("\nBaseline untuk sesi ini (dipakai SEMUA slice):")
    ada, cocok, info = baseline_status()
    while True:
        opts = {"f", "s"}
        txt = "  "
        if ada and cocok:
            txt += f"Enter = ikut baseline utama (baseline.zip, {info}) | "
            opts.add("")
        txt += "f = pilih file | s = scan baru khusus sesi ini | q = batal: "
        ans = ask(txt).lower()
        if ans not in opts:
            print("  Pilih sesuai opsi.")
            continue
        if ans == "":
            return {"jenis": "utama", "asal": os.path.abspath(BASELINE_ZIP)}
        if ans == "s":
            return {"jenis": "scan", "asal": None}
        path = pick_zip_file("Pilih ZIP baseline (scan kosong) untuk sesi 3D")
        if path is None:
            continue
        try:
            check_zip_matches_config(path)
        except Exception as e:
            print(f"  File ditolak: {e}")
            continue
        return {"jenis": "file", "asal": os.path.abspath(path)}


# --- isi slice: ukur atau upload ---

def measure_slice(st, k):
    sl = st["slices"][k]
    n = len(st["slices"])
    stem = os.path.splitext(sl["file"])[0]
    print(f"\n=== SLICE {k + 1}/{n}: z = {fmt_z(sl['z'])} cm  (ukur) ===")
    print(f"Geser/letakkan objek pada posisi z = {fmt_z(sl['z'])} cm.")
    ask("  Enter = mulai/lanjut ukur | q = berhenti (sesi tersimpan): ")
    zp = acquire_scan(_rel_scan(st, stem))
    if zp is None:
        raise Jeda()
    # Gambar 2D slice ini: disimpan, tidak ditampilkan. Energi mentahnya juga
    # disimpan ke cache 3D supaya rekonstruksi 3D tidak menghitung ulang.
    out2d = os.path.join(sess_dir(st["nama"]), "2d")
    try:
        print("Membuat gambar 2D slice ini (disimpan, jendela tidak dibuka; "
              "pakai rentang & warna terakhir) ...")
        proc_from_saved(zip_freqs(zp))
        res = run_imaging(zp, baseline_path(st), unique_output_stem(stem, out2d),
                          show=False, out_dir=out2d)
        if DOMAIN_MODE == "half_disk":
            for m, raw in res["raw"].items():
                r3d_store_cache(zp, baseline_path(st), m, raw, res["channels"])
    except Exception as e:
        print(f"  PERHATIAN: gambar 2D slice ini gagal dibuat ({e}). "
              f"Data slice aman; 3D akan menghitungnya sendiri.")


def upload_slice(st, k, ref_freqs):
    sl = st["slices"][k]
    n = len(st["slices"])
    print(f"\n=== SLICE {k + 1}/{n}: z = {fmt_z(sl['z'])} cm  (upload) ===")
    while True:
        path, _ = _pick_valid_zip(f"Pilih ZIP slice {k + 1} dari {n} (z = {fmt_z(sl['z'])} cm)",
                                  ref_freqs)
        if path is None:
            raise Jeda()
        used = [s.get("asal") for j, s in enumerate(st["slices"]) if j != k and s.get("asal")]
        used += [slice_zip(st, j) for j in range(n) if j != k and slice_done(st, j)]
        used += [st["baseline"].get("asal"), baseline_path(st)]
        if any(u and os.path.exists(u) and _same(u, path) for u in used):
            print("  File ini sudah dipakai di sesi ini (slice lain atau baseline). Pilih file lain.")
            continue
        break
    dst = slice_zip(st, k)
    shutil.copy2(path, dst + ".tmp")
    os.replace(dst + ".tmp", dst)
    sl["asal"] = os.path.abspath(path)
    save_state(st)
    print(f"  Slice {k + 1}/{n}  z = {fmt_z(sl['z'])} cm  <- {os.path.basename(path)}")


def fill_session(st):
    """Lengkapi baseline (kalau scan khusus) lalu semua slice yang belum ada,
    berurutan. Raise Jeda kalau user berhenti."""
    if not os.path.isfile(baseline_path(st)):
        if st["baseline"]["jenis"] != "scan":
            raise ValueError(f"File baseline sesi hilang: {baseline_path(st)}")
        print("\n=== SCAN BASELINE KHUSUS SESI (tanpa objek) ===")
        print("Pastikan area di dalam busur KOSONG selama scan.")
        ask("  Enter = mulai/lanjut ukur | q = berhenti (sesi tersimpan): ")
        zp = acquire_scan(_rel_scan(st, os.path.splitext(st["baseline"]["file"])[0]))
        if zp is None:
            raise Jeda()
    ref = None
    for k in range(len(st["slices"])):
        if slice_done(st, k):
            continue
        if st["slices"][k]["sumber"] == "ukur":
            measure_slice(st, k)
        else:
            if ref is None:
                ref, _, _ = load_csv_zip(baseline_path(st))
            upload_slice(st, k, ref)


def ask_source(prompt_prefix):
    while True:
        ans = ask(f"  {prompt_prefix}: Enter = ukur | u = upload file | q = batal: ").lower()
        if ans in ("", "u"):
            return "ukur" if ans == "" else "upload"
        print("  Pilih Enter, u, atau q.")


def add_slices(st):
    zs = [s["z"] for s in st["slices"]]
    cnt = ask_int("  Tambah berapa slice? (Enter = 1): ", 1, default=1)
    if len(zs) >= 2:
        step = zs[-1] - zs[-2]
    else:
        step = ask_float("  Jarak antar-slice (cm): ", nonzero=True)
    new = []
    for i in range(cnt):
        last = (new or zs)[-1]
        dflt = round(last + step, 6)
        while True:
            z = round(ask_float(f"  Posisi slice baru ke-{i + 1} (cm) (Enter = {fmt_z(dflt)}): ",
                                default=dflt), 6)
            if z in zs or z in new:
                print("  Posisi itu sudah ada. Pakai posisi lain.")
                continue
            break
        new.append(z)
    sumber = ask_source("Data slice baru")
    for z in new:
        st["slices"].append(_new_slice(len(st["slices"]), z, sumber))
    st["selesai"] = False
    save_state(st)
    print(f"  {cnt} slice ditambahkan: {', '.join(fmt_z(z) for z in new)} cm.")


def edit_slice(st):
    n = len(st["slices"])
    k = ask_int(f"  Nomor slice yang diedit (1-{n}): ", 1, n) - 1
    sl = st["slices"][k]
    sumber = ask_source(f"Pengganti slice {k + 1} (z = {fmt_z(sl['z'])} cm)")
    # data lama tidak dihapus, hanya dipindah sebagai cadangan
    d = sess_dir(st["nama"])
    stem = os.path.splitext(sl["file"])[0]
    tag = f"_lama_{_stamp()}"
    moved = []
    for old in (os.path.join(d, sl["file"]), os.path.join(d, stem)):
        if os.path.exists(old):
            base, ext = os.path.splitext(old) if old.endswith(".zip") else (old, "")
            os.replace(old, base + tag + ext)
            moved.append(os.path.basename(base + tag + ext))
    sl["sumber"], sl["asal"] = sumber, None
    st["selesai"] = False
    save_state(st)
    if moved:
        print(f"  Data lama slice {k + 1} disimpan sebagai cadangan: {', '.join(moved)}")
    print(f"  Slice {k + 1} akan diisi ulang di urutan yang sama.")


# --- alur sesi ---

def run_session(st):
    """Jalankan sesi sampai 3D dibuat atau user berhenti. Status selalu
    tersimpan; kalau terhenti, sesi ditawarkan lagi saat program dijalankan."""
    set_active(st["nama"])
    try:
        while True:
            fill_session(st)
            print("\n" + "-" * 64)
            print(f"Semua {len(st['slices'])} slice lengkap.")
            print(session_table(st))
            ans = ask("\n  Enter = buat 3D | t = tambah slice | e = edit slice "
                      "| s = simpan & kembali | q = berhenti: ").lower()
            if ans == "":
                if not ask_processing_settings(zip_freqs(slice_zip(st, 0))):
                    print("  3D dibatalkan, kembali ke menu sesi.")
                    continue
                d = sess_dir(st["nama"])
                base_out = os.path.join(d, f"hasil_3d_{PROC['band_label']}")
                out, k = base_out, 2
                while os.path.exists(out):
                    out = f"{base_out}_{k}"
                    k += 1
                slices = [(slice_zip(st, j), s["z"]) for j, s in enumerate(st["slices"])]
                build_3d(slices, baseline_path(st), out, title=st["nama"])
                st.setdefault("hasil_3d", []).append(os.path.basename(out))
                st["selesai"] = True
                save_state(st)
                clear_active()
                print(f"\nSesi '{st['nama']}' selesai. Hasil 3D: sesi_3d/{st['nama']}/"
                      f"{os.path.basename(out)}/")
                return
            if ans == "t":
                add_slices(st)
            elif ans == "e":
                edit_slice(st)
            elif ans == "s":
                save_named(st)
                return
            else:
                print("  Pilih sesuai opsi.")
    except (Jeda, Batal, KeyboardInterrupt):
        print(f"\nSesi '{st['nama']}' dihentikan dan TERSIMPAN "
              f"({n_done(st)}/{len(st['slices'])} slice lengkap).")
        print("Saat program dijalankan lagi, sesi ini akan ditawarkan untuk dilanjutkan "
              "(atau pilih l di awal).")


def new_session():
    print("\n=== SESI 3D BARU ===  (q = batal)")
    name = ask_session_name("Nama sesi 3D (misal tas_3d): ")
    zs = ask_positions()
    base = choose_session_baseline()
    while True:
        ans = ask("\nSumber data slice: Enter = ukur (menunggu hasil pengukuran terbaru) "
                  "| u = upload file yang sudah ada | q = batal: ").lower()
        if ans in ("", "u"):
            sumber = "ukur" if ans == "" else "upload"
            break
        print("  Pilih Enter, u, atau q.")

    d = sess_dir(name)
    os.makedirs(d)
    bfile = "baseline_sesi.zip" if base["jenis"] == "scan" else "baseline.zip"
    if base["asal"]:
        shutil.copy2(base["asal"], os.path.join(d, bfile))   # salinan, tidak ikut berubah
    st = {"nama": name, "dibuat": _stamp(), "sumber": sumber,
          "baseline": {"jenis": base["jenis"], "file": bfile, "asal": base["asal"]},
          "slices": [_new_slice(k, z, sumber) for k, z in enumerate(zs)],
          "hasil_3d": [], "selesai": False}
    save_state(st)
    print("\n" + session_table(st))
    if base["jenis"] == "utama":
        print("  (baseline utama disalin ke folder sesi, jadi sesi ini tetap memakai "
              "baseline yang sama walau baseline utama diganti nanti)")
    run_session(st)


def list_sessions():
    if not os.path.isdir(SESSION_ROOT):
        return []
    out = []
    for name in sorted(os.listdir(SESSION_ROOT)):
        if name.startswith("_") or not os.path.isfile(os.path.join(sess_dir(name), STATE_NAME)):
            continue
        try:
            out.append(load_state(name))
        except Exception:
            pass
    return out


def pick_session():
    sessions = list_sessions()
    if not sessions:
        print("  Belum ada sesi 3D tersimpan.")
        return None
    print("\nSesi 3D tersimpan:")
    for i, st in enumerate(sessions):
        status = "selesai (3D sudah dibuat)" if st.get("selesai") else "belum selesai"
        print(f"  {i + 1:>2}. {st['nama']:<24} {n_done(st)}/{len(st['slices'])} slice  "
              f"{st['sumber']:<6}  {status}")
    i = ask_int(f"  Pilih nomor sesi (1-{len(sessions)}) | q = batal: ", 1, len(sessions))
    return sessions[i - 1]


def offer_resume():
    """Dipanggil sekali saat program mulai: tawarkan sesi yang terhenti."""
    name = get_active()
    if not name:
        return
    st = load_state(name)
    print(f"\nAda sesi 3D yang belum selesai: '{name}' "
          f"({n_done(st)}/{len(st['slices'])} slice lengkap).")
    ans = ask_choice("  Enter = lanjutkan | t = tidak (simpan dengan nama): ", {"", "t"})
    if ans == "":
        run_session(st)
    else:
        try:
            save_named(st)
        except Batal:
            print("  Sesi tetap tersimpan dengan nama lama dan akan ditawarkan lagi nanti.")


# ############################################################################
# ###########################  MENU & PROGRAM  ###############################
# ############################################################################

def menu_2d():
    """Menu mode biasa (2D), sama seperti program sebelumnya.
    q = kembali ke pertanyaan awal."""
    actions = {
        "s": do_baseline_scan,
        "f": do_baseline_from_file,
        "b": do_change_baseline,
        "i": do_imaging_old,
        "": do_measure_object,
    }
    while True:
        ada, cocok, info = baseline_status()
        print("\n" + "-" * 64)
        print("MODE BIASA (2D)")
        if not ada:
            print("Belum ada baseline.")
            choice = ask_choice("  s = scan baseline baru | f = pakai file baseline lama"
                                " | i = imaging dari ZIP lama | q = kembali: ",
                                {"s", "f", "i", "q"})
        elif not cocok:
            print(f"Baseline aktif TIDAK cocok dengan konfigurasi ({info}).")
            print("Baseline harus diganti sebelum mengukur objek.")
            choice = ask_choice("  b = ganti baseline | i = imaging dari ZIP lama"
                                " | q = kembali: ", {"b", "i", "q"})
        else:
            print(f"Baseline aktif: {BASELINE_NAME}.zip ({info})")
            choice = ask_choice("  Enter = ukur objek | b = ganti baseline"
                                " | i = imaging dari ZIP lama | q = kembali: ",
                                {"", "b", "i", "q"})
        if choice == "q":
            return
        try:
            actions[choice]()
        except KeyboardInterrupt:
            print("\nDibatalkan. Kembali ke menu.")
        except Exception as e:
            print(f"\nERROR: {e}")
            print("Data yang sudah tersimpan tetap aman. Kembali ke menu.")
        finally:
            plt.close("all")


def _guard(fn):
    """Jalankan satu alur dari pertanyaan awal; error tidak menghentikan program."""
    try:
        fn()
    except EOFError:
        raise
    except Batal:
        print("  Dibatalkan. Kembali ke pertanyaan awal.")
    except KeyboardInterrupt:
        print("\nDihentikan. Kembali ke pertanyaan awal.")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Data yang sudah tersimpan tetap aman. Kembali ke pertanyaan awal.")
    finally:
        plt.close("all")


def _continue_saved():
    st = pick_session()
    if st is not None:
        run_session(st)


def main():
    print("=" * 64)
    print(" SISTEM IMAGING ARRAY VIVALDI  (akuisisi LibreVNA + DAS/DMAS + 3D)")
    print("=" * 64)
    print(f"Folder kerja: {BASE_DIR}")
    migrate_legacy_names()
    try:
        _guard(offer_resume)
        while True:
            print("\n" + "=" * 64)
            choice = ask_choice("Mode: Enter = biasa (2D) | 3 = 3D baru "
                                "| l = lanjutkan sesi 3D tersimpan | q = keluar: ",
                                {"", "3", "l", "q"})
            if choice == "q":
                print("Program selesai.")
                return
            if choice == "":
                _guard(menu_2d)
            elif choice == "3":
                _guard(new_session)
            else:
                _guard(_continue_saved)
    except (KeyboardInterrupt, EOFError):
        print("\nProgram selesai.")


if __name__ == "__main__":
    main()
