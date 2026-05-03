<div align="center">

# 🧠 CognoSpeak  
### Automated Clinical Speech Processing & Metadata Pipeline

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Conda](https://img.shields.io/badge/Environment-Conda-green.svg)](https://docs.conda.io/)
[![CUDA](https://img.shields.io/badge/GPU-CUDA%20Supported-orange.svg)]()
[![ASR](https://img.shields.io/badge/ASR-Whisper%20%7C%20Wav2Vec2%20%7C%20NeMo-red.svg)]()
[![License](https://img.shields.io/badge/License-Research%20Only-lightgrey.svg)]()
[![Status](https://img.shields.io/badge/Status-Active%20Research-success.svg)]()
[![Open Science](https://img.shields.io/badge/Open%20Science-Compatible-blueviolet.svg)]()
[![Reproducibility](https://img.shields.io/badge/Reproducible-Pipeline-brightgreen.svg)]()

**End-to-end automated pipeline for clinical speech, cognition, and metadata processing.**

Designed for **digital dementia biomarkers**, **speech-based cognitive assessment**, and **clinical AI research**.

</div>

---

## 🔬 Overview

**CognoSpeak** is a research-grade data processing pipeline that transforms raw clinical assessment recordings into a fully validated, anonymised, machine-learning-ready dataset.

The system automatically:

- Downloads clinical assessment archives from cloud storage
- Extracts and standardises audio/video recordings
- Runs multiple **Automatic Speech Recognition (ASR)** systems
- Aligns manual clinical transcripts
- Computes **audio quality metrics** (VAD, SNR)
- Detects duplicate participants and follow-ups
- Validates cognitive scores and demographics
- Produces a shareable anonymised research dataset

---

## 🧬 Research Motivation

Speech provides a scalable, non-invasive biomarker for:

- Mild Cognitive Impairment (MCI)
- Dementia screening
- Functional cognitive decline
- Longitudinal monitoring

CognoSpeak operationalises **clinical speech AI pipelines** into a reproducible workflow suitable for:

- Academic research
- Clinical trials
- Digital health studies
- Multisite collaborations

---

## ⚙️ Pipeline Architecture

```
Cloud Storage (ZIP archives)
        ↓
Download & Validation
        ↓
Audio Extraction & Conversion
        ↓
Metadata Harmonisation
        ↓
Participant Deduplication
        ↓
Follow-Up Tracking
        ↓
ASR Processing
        ↓
Manual Transcript Alignment
        ↓
Cognitive Score Integration
        ↓
Audio Quality Analysis
        ↓
Overlap Detection & Repair
        ↓
Anonymised Research Dataset
```

---

## 🚀 Installation

### 1. Clone repository

```bash
git clone https://github.com/your-username/CognoSpeak.git
cd CognoSpeak
```

### 2. Create environment

```bash
conda env create -f ACONDA.yml
conda activate ACONDA
```

### 3. Verify setup

```bash
python -c "import torch; print(torch.__version__)"
```

CUDA support will automatically activate if available.

---

## 📂 Repository Structure

```
CognoSpeak/
│
├── CognoSpeak_1_download.py
├── CognoSpeak_2_data_process.py
├── CognoSpeak_3_check_final.py
├── CognoSpeak_4_check_duplicates.py
├── CognoSpeak_5_followUP.py
├── CognoSpeak_6_ASR.py
├── CognoSpeak_7_transcripts.py
├── CognoSpeak_8_Cogn_scores.py
├── CognoSpeak_8B_audio_analysis.py
├── CognoSpeak_9A_FIND_audioOverlap.py
├── CognoSpeak_9B_FIX_audioOverlap.py
├── CognoSpeak_10_final_share.py
│
├── config.py
└── ACONDA.yml
```

---

## 🧩 Step-by-Step Pipeline

### Step 1 — Download Raw Data

```bash
python CognoSpeak_1_download.py
```

Downloads assessment ZIP files from Google Cloud and detects duplicated subject IDs.

---

### Step 2 — Extract & Organise Audio

```bash
python CognoSpeak_2_data_process.py 15
```

- Extracts archives
- Converts media → 44.1 kHz WAV
- Merges recordings

---

### Step 3 — Metadata Validation

```bash
python CognoSpeak_3_check_final.py 15
```

Cross-checks spreadsheet and database exports.

Output:
```
CognoSpeak_FINAL_METADATA.csv
```

---

### Step 4 — Duplicate Detection

```bash
python CognoSpeak_4_check_duplicates.py
```

Automatically merges participants using clinical identifiers.

---

### Step 5 — Follow-Up Handling

```bash
python CognoSpeak_5_followUP.py
```

Tracks longitudinal assessments and computes follow-up intervals.

---

### Step 6 — Automatic Speech Recognition

```bash
python CognoSpeak_6_ASR.py 30
```

Runs three ASR systems:

- Whisper Medium
- Wav2Vec2 Base
- NVIDIA NeMo FastConformer

---

### Step 7 — Manual Transcript Alignment

```bash
python CognoSpeak_7_transcripts.py 15
```

Maps clinician transcripts to audio recordings.

---

### Step 8 — Cognitive Scores Integration

```bash
python CognoSpeak_8_Cogn_scores.py
```

Integrates:

- MoCA
- ACE-III
- RUDAS
- MCE

---

### Step 8B — Audio Quality Analysis

```bash
python CognoSpeak_8B_audio_analysis.py 15
```

Computes:

- Voice Activity Detection (VAD)
- Signal-to-Noise Ratio (SNR)

---

### Step 9 — Audio Overlap Detection

```bash
python CognoSpeak_9A_FIND_audioOverlap.py 30
```

Detects recording overlap bugs and optionally repairs audio automatically.

---

### Step 10 — Export Anonymised Dataset

```bash
python CognoSpeak_10_final_share.py 1
```

Produces:

- Final WAV files
- Whisper transcripts
- Timestamped anonymised metadata

---

## ⚙️ Configuration

All paths and dataset rules are defined in:

```
config.py
```

Important variables:

- `raw_data_dir`
- `cloud_base`
- `to_ignore_assessments`
- `SPECIAL_IDs_DIAGNOSIS`

---

## 📊 Outputs

The pipeline generates:

- Clean speech dataset
- Validated clinical metadata
- ASR transcripts
- Audio quality metrics
- Longitudinal participant tracking

Ready for:

✅ Machine Learning  
✅ Statistical modelling  
✅ Clinical validation studies  

---

## 📈 Reproducibility & Open Science

This repository follows open-science best practices:

- Deterministic processing steps
- Logged execution
- Version-controlled preprocessing
- Transparent data provenance
- Script-level reproducibility

⚠️ **No participant data is stored in this repository.**

---

## 🛠 Logging

Recommended log folders:

```
data/logs/
data/ASR_logs/
data/trans_logs/
```

All major steps produce CSV audit files.

---

## 🧪 Intended Use

This pipeline supports research in:

- Speech biomarkers of dementia
- Cognitive assessment automation
- Clinical speech analytics
- Digital health AI

---

## 🤝 Contributing

Collaborations are welcome for:

- Clinical speech AI
- Multilingual dementia datasets
- ASR benchmarking
- Cognitive modelling

Please open an Issue or Pull Request.

---

## 🔒 Data Governance

**Proprietary research software — authorised research use only.**

This repository contains:

✅ Code  
❌ No clinical data  
❌ No participant information  

All datasets must comply with institutional ethics approval and GDPR requirements.

---

<div align="center">

**Built for reproducible clinical AI research.**

🧠 Speech • Cognition • AI • Open Science

</div>
