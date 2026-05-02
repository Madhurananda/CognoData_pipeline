# CognoSpeak – Automated Audio Processing & Metadata Pipeline

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Conda](https://img.shields.io/badge/conda-ACONDA-green.svg)](https://docs.conda.io/)

**CognoSpeak** is an end-to-end data processing pipeline for clinical speech and cognitive assessment data. It downloads raw ZIP archives from Google Cloud, extracts audio/video, runs multiple automatic speech recognition (ASR) models (Whisper, Wav2Vec2, NeMo), aligns manual transcripts, computes audio quality metrics (VAD, SNR), manages participant metadata with duplicate detection and follow-up handling, and finally produces a shareable anonymised dataset.

---

## Table of Contents

- [Installation](#installation)
- [Pipeline Overview](#pipeline-overview)
- [Step-by-Step Execution](#step-by-step-execution)
  - [Step 1 – Download raw ZIP files](#step-1--download-raw-zip-files)
  - [Step 1A – Fix duplicated subject IDs](#step-1a--fix-duplicated-subject-ids)
  - [Step 2 – Extract and organise audio](#step-2--extract-and-organise-audio)
  - [Step 3 – Validate against spreadsheet/JSON](#step-3--validate-against-spreadsheetjson)
  - [Step 4 – Handle duplicate participants](#step-4--handle-duplicate-participants)
  - [Step 5 – Follow-up studies](#step-5--follow-up-studies)
  - [Step 6 – Automatic speech recognition](#step-6--automatic-speech-recognition)
  - [Step 7 – Manual transcripts alignment](#step-7--manual-transcripts-alignment)
  - [Step 8 – Cognitive scores (MoCA, RUDAS, etc.)](#step-8--cognitive-scores-moca-rudas-etc)
  - [Step 8B – Audio quality analysis (VAD/SNR)](#step-8b--audio-quality-analysis-vadsnr)
  - [Step 9 – Detect and fix audio overlap](#step-9--detect-and-fix-audio-overlap)
  - [Step 10 – Share final data](#step-10--share-final-data)
- [Configuration](#configuration)
- [Logging & Monitoring](#logging--monitoring)
- [Troubleshooting](#troubleshooting)
- [Citation & Contact](#citation--contact)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/CognoSpeak.git
cd CognoSpeak
```

### 2. Create the Conda environment

The exact environment is provided in `ACONDA.yml`.

```bash
conda env create -f ACONDA.yml
conda activate ACONDA
```

### 3. Verify the environment

```bash
python -c "import torch; print(torch.__version__)"
```

Should run successfully (CUDA enabled if GPU is available).

> **Note:**  
The pipeline expects data directories (`../data/raw_data/`, `../data/EXTRACTED_RAW_DATA/`, etc.) relative to script locations. Adjust paths in `config.py` if required.

---

## Pipeline Overview

```
Cloud Storage (ZIP)
        ↓
Step 1  Download
        ↓
Step 2  Extract & Convert
        ↓
Step 3  Validate JSON vs Spreadsheet
        ↓
Step 4  Deduplicate Participants
        ↓
Step 5  Follow-ups
        ↓
Step 6  ASR (Whisper / Wav2Vec2 / NeMo)
        ↓
Step 7  Manual Transcripts
        ↓
Step 8  Cognitive Scores + Audio Quality
        ↓
Step 9  Overlap Detection/Fix
        ↓
Step 10 Share Anonymised Dataset
```

All intermediate metadata and logs are saved as CSV files.  
The final output is a clean dataset ready for machine learning or clinical analysis.

---

## Step-by-Step Execution

Run each script from the repository root and capture logs using `tee`.

---

### Step 1 – Download raw ZIP files

```bash
rm /home/madhu/madhu_work/data/logs/CognoSpeak_1_download.txt
python CognoSpeak_1_download.py |& tee -a /home/madhu/madhu_work/data/logs/CognoSpeak_1_download.txt
```

Downloads ZIP files from:

```
gs://cognospeak-production.appspot.com/production
```

Detects duplicated subject IDs and prints warnings.

---

### Step 1A – Fix duplicated subject IDs

- Same participant → add ZIPs to `list_same_ZIPs` in `config.py`
- Different participants sharing ID → add to `list_of_2_update_ZIPs`

Re-run Step 1 afterwards.

---

### Step 1B & 1C – Update source files

Replace:

- `CcHAT_data_overview.xlsx`
- `cognospeak-production-default-rtdb-export.json`

---

### Step 2 – Extract and organise audio

```bash
python CognoSpeak_2_data_process.py 15 |& tee -a /home/madhu/madhu_work/data/logs/CognoSpeak_2_data_process.txt
```

- Extracts ZIPs
- Converts media → `.wav` (44.1 kHz)
- Merges continuous recordings

Outputs:

- `CognoSpeak_2__dir_media_info.csv`
- `CognoSpeak_2__assess_missing.csv`

---

### Step 3 – Validate against spreadsheet/JSON

```bash
python CognoSpeak_3_check_final.py 15 |& tee -a /home/madhu/madhu_work/data/logs/CognoSpeak_3_check_final.txt
```

Cross-checks demographic and diagnosis fields.

Outputs:

- `CognoSpeak_FINAL_METADATA.csv`
- `CognoSpeak_3_possible_duplicates.csv`

---

### Step 4 – Handle duplicate participants

```bash
python CognoSpeak_4_check_duplicates.py |& tee -a /home/madhu/madhu_work/data/logs/CognoSpeak_4_check_duplicates.txt
```

Automatically merges duplicates using identifiers such as NHS number, email, phone, DoB.

Key outputs:

- `CognoSpeak_4__duplicates_TO_BE_confirmed.csv`
- `CognoSpeak_4__duplicates_FINAL_confirmed_FINAL.csv`
- `CognoSpeak_4__ID_remove.csv`

---

### Step 5 – Follow-up studies

```bash
python CognoSpeak_5_followUP.py |& tee -a /home/madhu/madhu_work/data/logs/CognoSpeak_5_followUP.txt
```

- Orders assessments chronologically
- Computes follow-up gaps
- Flags inconsistent diagnoses

Output:

```
CognoSpeak_5__FINAL_METADATA.csv
```

---

### Step 6 – Automatic Speech Recognition

Run on a GPU machine.

```bash
rm /home/madhu/madhu_work/data/ASR_logs/CognoSpeak_6_ASR.txt
python CognoSpeak_6_ASR.py 30 |& tee /home/madhu/madhu_work/data/ASR_logs/CognoSpeak_6_ASR.txt
```

Runs:

- Whisper medium
- Wav2Vec2 base
- NVIDIA NeMo FastConformer

Output:

```
CognoSpeak_ASR_out.csv
```

---

### Step 7 – Manual transcripts alignment

```bash
rm /home/madhu/madhu_work/data/trans_logs/CognoSpeak_7_trans.txt
python CognoSpeak_7_transcripts.py 15 |& tee /home/madhu/madhu_work/data/trans_logs/CognoSpeak_7_trans.txt
```

- Maps transcripts to audio
- Splits per question

Output:

```
CognoSpeak_metadata_transcribed.csv
```

---

### Step 8 – Cognitive scores (MoCA, RUDAS, MCE, ACE-III)

```bash
python CognoSpeak_8_Cogn_scores.py |& tee /home/madhu/madhu_work/data/logs/CognoSpeak_8_Cogn_scores.txt
```

Validates component scores and merges into metadata.

Outputs:

- `CognoSpeak_MoCA_all_metadata.csv`
- `CognoSpeak_ACE_all_metadata.csv`

---

### Step 8B – Audio quality analysis (VAD/SNR)

```bash
python CognoSpeak_8B_audio_analysis.py 15 |& tee /home/madhu/madhu_work/data/logs/CognoSpeak_8B_audio_analysis.txt
```

- Runs Silero VAD
- Computes SNR

Outputs:

- `CognoSpeak__Audio_INFO.csv`
- `CognoSpeak_8__metadata.csv`

---

### Step 9 – Detect and fix audio overlap

#### 9A – Find overlaps

```bash
rm /home/madhu/madhu_work/data/ASR_logs/find_audio_overlap.txt
python CognoSpeak_9A_FIND_audioOverlap.py 30 |& tee /home/madhu/madhu_work/data/ASR_logs/find_audio_overlap.txt
```

Output:

```
Audio_overlap_FOUND.csv
```

#### 9B – Fix overlaps

Option 1: Exclude assessments via `to_ignore_assessments`.

Option 2:

```bash
rm /home/madhu/madhu_work/data/ASR_logs/fix_audio_overlap.txt
python CognoSpeak_9B_FIX_audioOverlap.py 30 |& tee /home/madhu/madhu_work/data/ASR_logs/fix_audio_overlap.txt
```

Then repeat Steps 2–8.

---

### Step 10 – Share final data

```bash
python CognoSpeak_10_final_share.py 1
```

- Copies final `.wav` + Whisper transcripts
- Exports anonymised metadata

Output:

```
CognoSpeak_metadata__YYYY_MM_DD.csv
```

---

## Configuration

All configuration is defined in:

```
config.py
```

Key variables:

- `raw_data_dir`
- `extracted_data_dir`
- `final_extract_dir`
- `cloud_base`
- `to_ignore_assessments`
- `SPECIAL_IDs_DIAGNOSIS`
- referral/ethnicity groupings

Activate environment before running scripts:

```bash
conda activate ACONDA
```

---

## Logging & Monitoring

Suggested log directories:

```
/home/madhu/madhu_work/data/logs/
/home/madhu/madhu_work/data/ASR_logs/
/home/madhu/madhu_work/data/trans_logs/
```

CSV outputs are stored under `../data/`.

---

## Troubleshooting

| Issue | Cause | Solution |
|------|------|------|
| Duplicate ID persists | Same ID used twice | Add ZIP to `list_of_2_update_ZIPs` |
| Duplicate ZIPs same person | Two assessments | Add to `list_same_ZIPs` |
| Multiple JSON files | Extraction error | Keep latest JSON |
| Step 2 hangs | subprocess timeout | Increase `SUB_TIMEOUT` |
| ASR GPU OOM | Memory overload | Reduce batch size |
| Missing transcripts | Filename mismatch | Check `CognoSpeak_transcript_info.csv` |
| Overlap false positives | Unreliable timestamps | Filter assessment types |

Most steps are idempotent and safe to re-run.

---

## Citation & Contact

Proprietary Python scripts for retrieval and preprocessing of CognoSpeak data.  
**Intended for authorised research use only.**

> **Notice:**  
This repository contains **code only**.  
No research data or participant information is included or permitted within this repository.
