# CognoSpeak – Automated Audio Processing & Metadata Pipeline

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Conda](https://img.shields.io/badge/conda-ACONDA-green.svg)](https://docs.conda.io/)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](LICENSE)

**CognoSpeak** is an end‑to‑end data processing pipeline for clinical speech and cognitive assessment data. It downloads raw ZIP archives from Google Cloud, extracts audio/video, runs multiple automatic speech recognition (ASR) models (Whisper, Wav2Vec2, NeMo), aligns manual transcripts, computes audio quality metrics (VAD, SNR), manages participant metadata with duplicate detection and follow‑up handling, and finally produces a shareable anonymised dataset.

---

## Table of Contents

- [Installation](#installation)
- [Pipeline Overview](#pipeline-overview)
- [Step‑by‑Step Execution](#step-by-step-execution)
  - [Step 1 – Download raw ZIP files](#step-1--download-raw-zip-files)
  - [Step 1A – Fix duplicated subject IDs](#step-1a--fix-duplicated-subject-ids)
  - [Step 2 – Extract and organise audio](#step-2--extract-and-organise-audio)
  - [Step 3 – Validate against spreadsheet/JSON](#step-3--validate-against-spreadsheetjson)
  - [Step 4 – Handle duplicate participants](#step-4--handle-duplicate-participants)
  - [Step 5 – Follow‑up studies](#step-5--follow-up-studies)
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

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/CognoSpeak.git
   cd CognoSpeak
Create the Conda environment
The exact environment is provided in ACONDA.yml.

bash
conda env create -f ACONDA.yml
conda activate ACONDA
Verify the environment

bash
python -c "import torch; print(torch.__version__)"   # Should work with CUDA if GPU is available
Note: The pipeline expects data directories (../data/raw_data/, ../data/EXTRACTED_RAW_DATA/, etc.) relative to the script locations. Adjust paths in config.py if needed.

Pipeline Overview
text
Cloud Storage (ZIP)  →  Step 1 (download)  →  Step 2 (extract & convert)
                                                                 ↓
                                                       Step 3 (validate JSON vs spreadsheet)
                                                                 ↓
                                              Step 4 (deduplicate participants)
                                                                 ↓
                                              Step 5 (handle follow‑ups)
                                                                 ↓
                                              Step 6 (ASR: Whisper, Wav2Vec2, NeMo)
                                                                 ↓
                                              Step 7 (manual transcripts)
                                                                 ↓
                                     Step 8 / 8B (cognitive scores + audio quality)
                                                                 ↓
                                              Step 9 (overlap detection/fix)
                                                                 ↓
                                              Step 10 (share anonymised data)
All intermediate metadata and logs are saved as CSV files. The final output is a clean dataset ready for machine learning or clinical analysis.

Step‑by‑Step Execution
Run each script from the repository root. Use tee to capture logs.

Step 1 – Download raw ZIP files
bash
rm /home/madhu/madhu_work/data/logs/CognoSpeak_1_download.txt
python CognoSpeak_1_download.py |& tee -a /home/madhu/madhu_work/data/logs/CognoSpeak_1_download.txt
Downloads all new ZIP files from gs://cognospeak-production.appspot.com/production.

Detects duplicated subject IDs and prints warnings (e.g., 69972, 98225).

Step 1A – Fix duplicated subject IDs
If warnings appear for known IDs that belong to the same person (e.g., two ZIPs for the same user), add those ZIP names to list_same_ZIPs in config.py.
If two different participants were accidentally given the same ID, add the ZIP to list_of_2_update_ZIPs (with double underscores). Re‑run Step 1 – it will rename the ZIP and delete old extracted/audio folders.

Step 1B & 1C – Update source files
Replace CcHAT_data_overview.xlsx (spreadsheet of cognitive scores and demographics).

Replace cognospeak-production-default-rtdb-export.json (export from Firebase).

Step 2 – Extract and organise audio
bash
python CognoSpeak_2_data_process.py 15 |& tee -a /home/madhu/madhu_work/data/logs/CognoSpeak_2_data_process.txt
Unzips all ZIPs into EXTRACTED_RAW_DATA.

Converts video/audio files to .wav (44.1 kHz) and merges continuous audio for each assessment (using sox or librosa fallback).

Outputs:

CognoSpeak_2__dir_media_info.csv – media type per question.

CognoSpeak_2__assess_missing.csv – assessments missing ZIP files (can be sent to TherapyBox).

Step 3 – Validate against spreadsheet/JSON
bash
python CognoSpeak_3_check_final.py 15 |& tee -a /home/madhu/madhu_work/data/logs/CognoSpeak_3_check_final.txt
Cross‑checks diagnosis, referral, ethnicity, gender between JSON and spreadsheet.

Generates CognoSpeak_FINAL_METADATA.csv – the main metadata file.

Also outputs CognoSpeak_3_possible_duplicates.csv – potential name/DoB mismatches that need manual verification (usually with clinical team).

Step 4 – Handle duplicate participants
bash
python CognoSpeak_4_check_duplicates.py |& tee -a /home/madhu/madhu_work/data/logs/CognoSpeak_4_check_duplicates.txt
Automatically merges rows with identical NHS number, email, telephone, birthday, first/last name.

Saves CognoSpeak_4__duplicates_TO_BE_confirmed.csv – review and decide which ID to keep (or mark for removal).

After manual decisions, re‑run the script. Final duplicates are stored in CognoSpeak_4__duplicates_FINAL_confirmed_FINAL.csv.

IDs marked as “remove” are written to CognoSpeak_4__ID_remove.csv and excluded from further steps.

Step 5 – Follow‑up studies
bash
python CognoSpeak_5_followUP.py |& tee -a /home/madhu/madhu_work/data/logs/CognoSpeak_5_followUP.txt
Sorts assessments by date per participant.

Computes gaps between assessments (in days).

Flags inconsistent diagnosis/referral changes in CognoSpeak_5__follow_up_CHECK.csv – manual confirmation required.

Produces CognoSpeak_5__FINAL_METADATA.csv with unified pseudo‑IDs and gap columns.

Step 6 – Automatic speech recognition
Run on a machine with GPU and many cores (e.g., cognogpu).

bash
rm /home/madhu/madhu_work/data/ASR_logs/CognoSpeak_6_ASR.txt
python CognoSpeak_6_ASR.py 30 |& tee /home/madhu/madhu_work/data/ASR_logs/CognoSpeak_6_ASR.txt
Resamples audio to 16 kHz for Wav2Vec2 and NeMo.

Runs three ASR models:

Whisper medium (on original 44.1 kHz audio)

Wav2Vec2 base (16 kHz)

NVIDIA NeMo FastConformer (16 kHz)

Saves transcripts and word/character timestamps in FINAL_ASR_* directories.

Outputs CognoSpeak_ASR_out.csv (metadata with paths to ASR outputs).

Step 7 – Manual transcripts alignment
bash
rm /home/madhu/madhu_work/data/trans_logs/CognoSpeak_7_trans.txt
python CognoSpeak_7_transcripts.py 15 |& tee /home/madhu/madhu_work/data/trans_logs/CognoSpeak_7_trans.txt
Copies manually transcribed .txt files to shared folder MANUAL_TRANSCRIPTS_ORIGINAL/.

Maps each transcript to the correct audio directory (handles filename mismatches).

Splits transcripts per question and saves them in FINAL_MANUAL_TRANSCRIPTS/.

Produces CognoSpeak_metadata_transcribed.csv – metadata with a column trans_txt (path to manual transcript, or XX if missing).

Step 8 – Cognitive scores (MoCA, RUDAS, MCE, ACE‑III)
bash
python CognoSpeak_8_Cogn_scores.py |& tee /home/madhu/madhu_work/data/logs/CognoSpeak_8_Cogn_scores.txt
Reads cognitive scores from the spreadsheet and from Caitlin’s ISRAAC file.

Checks that component scores sum to the total score; mismatches are written to *_no_match_*.csv for manual correction.

Merges all validated scores with the main metadata.

Outputs:

CognoSpeak_MoCA_all_metadata.csv – all participants with MoCA scores.

CognoSpeak_ACE_all_metadata.csv – similarly for ACE‑III, RUDAS, MCE.

Step 8B – Audio quality analysis (VAD/SNR)
bash
python CognoSpeak_8B_audio_analysis.py 15 |& tee /home/madhu/madhu_work/data/logs/CognoSpeak_8B_audio_analysis.txt
Runs Silero VAD to extract speech segments.

Computes Signal‑to‑Noise Ratio (SNR) per segment using torchmetrics.

Generates:

CognoSpeak__Audio_INFO.csv – per‑segment VAD and SNR.

CognoSpeak_8__metadata.csv – updated metadata with an AUDIO_SNR column (mean ± std).

This metadata becomes the primary source for all subsequent steps.

Step 9 – Detect and fix audio overlap
9A – Find overlaps
bash
rm /home/madhu/madhu_work/data/ASR_logs/find_audio_overlap.txt
python CognoSpeak_9A_FIND_audioOverlap.py 30 |& tee /home/madhu/madhu_work/data/ASR_logs/find_audio_overlap.txt
Compares JSON‑logged recording durations with actual media durations.

Identifies questions where the next question’s audio overlaps with the previous (due to TherapyBox recording bug).

Outputs Audio_overlap_FOUND.csv.

9B – Fix overlaps (automatic)
If new overlaps are found, you can either:

Option 1 – Exclude the affected assessments entirely: add them (with __) to to_ignore_assessments in config.py and re‑run Steps 2–8.

Option 2 – Try to automatically trim the audio:

bash
rm /home/madhu/madhu_work/data/ASR_logs/fix_audio_overlap.txt
python CognoSpeak_9B_FIX_audioOverlap.py 30 |& tee /home/madhu/madhu_work/data/ASR_logs/fix_audio_overlap.txt
This uses ffmpeg to cut the overlapping portion. After fixing, repeat Steps 2–8.

Step 10 – Share final data
bash
python CognoSpeak_10_final_share.py 1
Copies only the final .wav files and Whisper transcripts to the shared directory (e.g., share_audio_dir).

Exports a timestamped metadata CSV (CognoSpeak_metadata__YYYY_MM_DD.csv) with anonymised columns (no names, NHS numbers, emails).

The shared directory is ready for collaborators.

Configuration
All important file paths, referral categories, diagnosis categories, and assessment‑specific constants are set in config.py.

Key variables you may need to adjust:

raw_data_dir, extracted_data_dir, final_extract_dir

cloud_base – Google Cloud Storage bucket

to_ignore_assessments – list of assessments to skip

SPECIAL_IDs_DIAGNOSIS – manual overrides for diagnosis

trust_refs, ethMINOR_refs – referral source groupings

Always ensure the ACONDA environment is active before running any script:

bash
conda activate ACONDA
Logging & Monitoring
All scripts are designed to be run with tee to append output to a log file. Suggested log directory:

text
/home/madhu/madhu_work/data/logs/
/home/madhu/madhu_work/data/ASR_logs/
/home/madhu/madhu_work/data/trans_logs/
Critical outputs (CSV files) are saved in the ../data/ folder and can be inspected at each step.

Troubleshooting
Issue	Likely cause	Solution
Duplicated ID issue persists	Same research ID assigned to two different people	Add ZIP name to list_of_2_update_ZIPs in config.py and re‑run Step 1
Duplicated ID issue persists for two ZIPs of the same person	The duplicates are actually two separate assessments of the same participant	Add the ZIP pair to list_same_ZIPs (in Step 1 section)
Script stops with “There are more than one json file”	A ZIP extraction produced multiple JSONs (should not happen)	Manually check the extracted folder; keep the most recent JSON
CognoSpeak_2_data_process.py hangs during multiprocessing	A subprocess (sox, ffmpeg) timed out	The script already includes a subprocess.run(timeout=…). Increase SUB_TIMEOUT in the script if needed.
ASR runs out of GPU memory	Too many audio files loaded at once	The scripts process audio one‑by‑one; if still OOM, reduce batch size or use CPU (slow).
Missing transcripts in Step 7	Manual transcript file name doesn’t match dir_name	The script automatically renames mismatched files. Check CognoSpeak_transcript_info.csv for any NO_DIR entries.
Overlap detection false positive	JSON log timestamps are unreliable for some assessment types (e.g., CognoMND)	In CognoSpeak_9A_FIND_audioOverlap.py, filter out those assessment types or set INCR properly.
For any unexpected errors, check the log files and the most recent CSV output. Most steps are idempotent – you can safely re‑run them after fixing the underlying data.











Proprietary Python scripts for the retrieval and preprocessing of CognoSpeak data. Intended for authorised research use only.
Notice: This repository contains code only. No research data or participant information is included or permitted within this repository.
