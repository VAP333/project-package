# AksharSetu — IndicF5 Training, Adaptation & Voice Architecture Investigation

**Status:** Technical Architecture & Feasibility Report  
**Author:** AksharSetu System Architecture Engine  
**Target:** Marathi Pedagogical TTS & Custom Teacher Voice Pipeline  

---

## 1. Executive Summary & Core Principle

Before committing computational resources to custom model training, we strictly separate:

| Dimension | Managed By | Description |
| :--- | :--- | :--- |
| **What to Read** | Document Graph / Golden Corpus | Canonical textbook text (never altered or paraphrased). |
| **What to Teach** | Pedagogical Planner / RAG | Educational reasoning, real-world grounding, concept bridging. |
| **How to Say It** | Prosody Planner | Discourse intent (narration vs. dialogue vs. question vs. explanation), pauses, emphasis. |
| **How to Generate Audio** | TTS Engine (Sarvam / IndicF5) | Acoustic waveform generation, voice timbre, pitch contours, phonetic pronunciation. |

> [!IMPORTANT]
> A TTS model (whether Sarvam or IndicF5) is an **acoustic generator**, not a pedagogy engine. A model cannot learn how to teach merely because a teacher records 10,000 sentences. Teaching behavior belongs in **Dataset A** and the **Pedagogical Planner**; teacher voice characteristics belong in **Dataset B** and the **TTS Pipeline**.

---

## 2. Technical Investigation Dimensions (§14 & Specification)

### 1. Required Training Data Format
- **Audio Specification:** Mono WAV, uncompressed PCM 16-bit or 24-bit, sampled at 24,000 Hz (or 44,100 Hz downsampled).
- **Segment Length:** Clean sentence or breath-group audio chunks between 2.0 to 12.0 seconds. Anything shorter than 1.5 seconds lacks sufficient prosodic context; segments longer than 15 seconds degrade flow-matching alignment.
- **Data Manifest (CSV / JSONL):**
  ```json
  {
    "audio_filepath": "wavs/teacher_01_0042.wav",
    "text": "राहुलच्या वर्गातील विद्यार्थी आणि शाळेतील शिक्षक क्षेत्रभेटीसाठी निघाले आहेत.",
    "duration": 5.42,
    "speaker": "teacher_marathi_female_1",
    "language": "mr"
  }
  ```

### 2. Audio Quality & Recording Environment Requirements
- **Signal-to-Noise Ratio (SNR):** $\ge 35\text{ dB}$, with a noise floor below $-55\text{ dBFS}$.
- **Reverberation Time ($RT_{60}$):** $< 0.2\text{ s}$ (dry vocal booth or treated room; zero room flutter or echo).
- **Acoustic Consistency:** Identical microphone placement (capsule 15–20 cm at $45^\circ$ angle with pop filter) across all recording sessions to avoid timbre mismatch.
- **No Lossy Compression:** Pre-processed raw stems; no MP3/AAC artifacts.

### 3. Transcript Requirements
- **Exact Verbatim Orthography:** Every spoken utterance must match the Devanagari text character-for-character.
- **Numbers & Symbols Expansion:** Numbers must be strictly expanded into full Marathi words during training alignment (e.g. `६:००` $\to$ `सकाळी सहा वाजता`, `१.१` $\to$ `एक दशांश एक`).
- **Anusvara & Nukta Consistency:** Consistent normalization of Marathi orthographic conventions (e.g. `आणि` vs. `आणी`, `विद्यार्थी`).

### 4. Marathi-Specific Linguistic & Phonetic Considerations
- **Schwa Deletion:** Marathi features contextual word-final and medial schwa deletion (उदा. `घर` is pronounced `/ɡʱər/`, not `/ɡʱərə/`). F5 flow-matching models learn this well from paired audio, provided text transcripts are uncorrupted.
- **Retroflex Lateral Approximant ('ळ' - /ɭ/):** Unique Marathi phoneme often mispronounced by generic Hindi-adapted models as 'ल' (/l/) or 'ड' (/ɖ/). The dataset must contain dense representation of words like `नळदुर्ग`, `वेळ`, `अलिबाग`, `केळे`, `डोळा`.
- **Aspirated Consonants & Murmured Stops:** High-frequency educational terms with `ख`, `घ`, `छ`, `झ`, `ठ`, `ढ`, `थ`, `ध`, `फ`, `भ` require pristine high-frequency vocal tracking.

### 5. Reference-Audio Conditioning (Zero-Shot / Few-Shot Voice Adaptation)
- IndicF5 / F5-TTS utilizes a diffusion/flow-matching backbone conditioned on a **3 to 10-second reference audio clip** along with its matching reference transcript.
- **Capability:** Allows cloning the acoustic timbre and vocal range of a teacher with just a 5-second reference sample without updating model weights.
- **Limitation:** Zero-shot reference conditioning captures vocal timbre well, but **fails on idiosyncratic pronunciations and subtle dialect inflections** unless the base checkpoint already has robust Marathi acoustic priors.

### 6. What Aspects are Learned by the TTS Model
- Vocal timbre, formant resonance, and vocal tract identity of the teacher.
- Natural phoneme durations and vowel lengthening in Marathi.
- Micro-prosody at word and conjunct boundaries.
- Intonation patterns for statements and interrogatives.

### 7. What Aspects Must Remain in the Prosody & Narration Planner
- Macro-discourse intent: determining whether a block is a main textbook paragraph, a teacher explanation, an activity prompt, or a dialogue turn.
- Turn-taking conversational rhythm: pausing 250ms–400ms between dialogue participants.
- Main vs. supporting content filtering: withholding map captions from auto-reading until demanded.
- Pedagogical grounding and faithfulness checks.

### 8. Fine-Tuning & Adaptation Architecture Options
1. **Zero-Shot / Few-Shot Reference Prompting:** Requires zero training; conditioned at inference time via 5–10s teacher WAV. Fast, zero GPU training cost, but prone to occasional Marathi phoneme drift.
2. **LoRA (Low-Rank Adaptation) on Flow-Matching DiT (Diffusion Transformer):**
   - Applies rank 8 or 16 low-rank matrices to attention projections ($W_q, W_k, W_v, W_o$) in the DiT backbone.
   - **Parameter efficiency:** Only $\approx 15\text{ MB}$ of trainable weights.
   - Preserves Marathi base knowledge while locking in the exact teacher cadence and pronunciation.
3. **Full Fine-Tuning:** Updates all 300M+ parameters. Requires extensive multi-speaker datasets to prevent catastrophic forgetting. Overkill for single-teacher voice adaptation.

### 9. GPU / VRAM & Hardware Assessment
| Workload | Minimum VRAM | Recommended Hardware | Current Dev Environment Assessment |
| :--- | :--- | :--- | :--- |
| **Inference (CPU)** | 4 GB RAM | Multi-core x86-64 | Supported (used for experimental provider testing). |
| **Inference (GPU)** | 4 GB VRAM | RTX 3060 / T4 | Ideal for sub-500ms real-time chunk synthesis. |
| **LoRA Fine-Tuning** | 12 GB VRAM | RTX 4070 / RTX 3090 / A10G | Feasible on cloud GPU instance (e.g. RunPod / Colab Pro). |
| **Full Model Training** | 24–48 GB VRAM | A100 (80GB) | Not recommended for prototype phase. |

### 10. Feasible Training & Deployment Roadmap for AksharSetu
1. **Phase 1 (Current):**
   - Keep **Sarvam AI bulbul:v3** as the reliable, production-ready baseline for reading and tutoring.
   - Expose **`IndicF5TTSProvider`** with health check, latency benchmarking, and reference-conditioning interface.
   - Collect and curate **Dataset A (Behavior)** and **Dataset B (Teacher Speech)**.
2. **Phase 2 (Cloud / Cluster Training):**
   - Record 2–5 hours of pristine teacher audio for the Class 10 Geography & Marathi curriculum.
   - Fine-tune IndicF5 using **LoRA (Rank 16, DiT attention blocks)** on an A10G/RTX 4090 instance.
3. **Phase 3 (Benchmark & Gate):**
   - Benchmark LoRA-adapted IndicF5 against Sarvam Bulbul across the 6 educational test categories.
   - Deploy once human reviewer agreement and pronunciation fidelity score $\ge 95\%$.
