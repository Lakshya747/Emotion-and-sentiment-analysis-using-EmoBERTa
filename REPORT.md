# Technical Report: Multi-Theoretical Emotion & Sentiment Analysis using EmoBERTa

**Project:** Conversational & Review Emotion Classification Pipeline  
**Model:** EmoBERTa Large (`tae898/emoberta-large`)  
**Hardware:** NVIDIA GeForce RTX 4060 Laptop GPU (CUDA 13.0)  
**Location:** `C:\Users\Luckyboi\.gemini\antigravity\scratch\emotion_analysis`

---

## 1. Executive Summary

This report documents the design, implementation, and empirical results of an emotion and sentiment analysis system powered by **EmoBERTa**. The core objective was mapping neural transformer logits into two foundational psychological frameworks:
1. **Paul Ekman's 6 Basic Emotions** (1971)
2. **Robert Plutchik's 8 Primary Wheel Emotions** (1980)

Additionally, the system derives net valence sentiment (Positive, Negative, Neutral) and aggregates review-level predictions into a holistic **Audience Emotional Consensus** for any given film.

```
                  ┌────────────────────────┐
                  │    Movie Review Text   │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │ EmoBERTa (RoBERTa-lg)  │
                  └───────────┬────────────┘
                              │ Softmax Probabilities
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
   ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
   │ Sentiment      │ │ Ekman's Model  │ │ Plutchik Wheel │
   │ • Positive     │ │ • Joy          │ │ • Joy          │
   │ • Negative     │ │ • Sadness      │ │ • Sadness      │
   │ • Neutral      │ │ • Anger        │ │ • Anger        │
   │                │ │ • Fear         │ │ • Fear         │
   │                │ │ • Disgust      │ │ • Disgust      │
   │                │ │ • Surprise     │ │ • Surprise     │
   │                │ │                │ │ • Trust*       │
   │                │ │                │ │ • Anticipation*│
   └────────────────┘ └────────────────┘ └────────────────┘
```

---

## 2. Theoretical Mapping Methodology

### 2.1 EmoBERTa Native Outputs
`tae898/emoberta-large` is a fine-tuned RoBERTa-large model predicting probability distributions across 7 classes: `joy`, `sadness`, `anger`, `fear`, `disgust`, `surprise`, and `neutral`.

### 2.2 Ekman’s 6 Basic Emotions
Paul Ekman identified 6 universal basic emotions. EmoBERTa's non-neutral classes map 1-to-1 to Ekman's taxonomy:
$$\text{Ekman} = \{\text{anger, disgust, fear, joy, sadness, surprise}\}$$
The dominant emotion is extracted via:
$$\text{Dominant}_{\text{Ekman}} = \arg\max_{e \in \text{Ekman}} P(e)$$

### 2.3 Plutchik’s Wheel of Emotion
Robert Plutchik established 8 primary emotions organized as opposing pairs. While 6 emotions match Ekman directly, the remaining two (**Trust** and **Anticipation**) are derived via psychological dyads:
- **Trust (Acceptance/Calm Stability):** A composite of positive valence and non-threatening stability:
  $$P(\text{trust}) = 0.6 \cdot P(\text{joy}) + 0.4 \cdot P(\text{neutral})$$
- **Anticipation (Expectancy/Arousal):** A composite of cognitive surprise and forward-looking positive expectancy:
  $$P(\text{anticipation}) = 0.5 \cdot P(\text{surprise}) + 0.5 \cdot P(\text{joy})$$

### 2.4 Valence Sentiment Derivation
To prevent dry neutral bias from overpowering genuine emotion, sentiment is computed based on net valence mass:
$$P(\text{pos}) = P(\text{joy})$$
$$P(\text{neg}) = P(\text{anger}) + P(\text{disgust}) + P(\text{fear}) + P(\text{sadness})$$
$$P(\text{neu}) = P(\text{neutral})$$
$$\text{Sentiment} = \begin{cases} \text{Positive}, & \text{if } P(\text{pos}) > P(\text{neg}) \text{ and } (P(\text{pos}) > 0.15 \text{ or } P(\text{pos}) > P(\text{neu})) \\ \text{Negative}, & \text{if } P(\text{neg}) > P(\text{pos}) \text{ and } (P(\text{neg}) > 0.15 \text{ or } P(\text{neg}) > P(\text{neu})) \\ \text{Neutral}, & \text{otherwise} \end{cases}$$

---

## 3. Dataset Evolution & Key Findings

| Phase | Dataset Used | Nature of Text | Observed Result | Problem / Solution |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | TMDb 5000 Movies | Objective 3rd-person plot synopses | High Neutrality ($>80\%$) | **Problem:** Synopses lack emotional stakes.<br>**Action:** Pivot to subjective reviews. |
| **Phase 2** | Rotten Tomatoes (8,530 items) | Subjective 1st-person critic snippets | Polarized, sharp emotions (Joy: $85\%$, Anger: $90\%$) | **Problem:** Reviews lacked movie title linkage.<br>**Action:** Group reviews under movie titles. |
| **Phase 3** | Structured Movie Reviews (`movies_reviews_dataset.json`) | Grouped critic & audience reviews | Rich per-review scores + Movie Consensus | **Success:** Enabled searching movies and analyzing audience reception. |

---

## 4. Key Benchmark Results

Empirical results from the pipeline testing real critic reviews:

| Movie | Reviewer & Rating | Dominant Sentiment | Dominant Ekman | Dominant Plutchik |
| :--- | :--- | :--- | :--- | :--- |
| **The Dark Knight** | Rolling Stone (5/5) | **Positive** (0.3956) | **Joy** (0.3956) | **Trust** (0.4485) |
| **The Dark Knight** | Indie Critic (2/5) | **Negative** (0.1542) | **Anger** (0.0678) | **Trust** (0.3498) |
| **Interstellar** | BBC Culture (4/5) | **Positive** (0.8579) | **Joy** (0.8579) | **Joy** (0.8579) |
| **Interstellar** | IGN Movies (5/5) | **Negative/Melancholic** (0.3292) | **Sadness** (0.2888) | **Trust** (0.2921) |
| **General** | "a masterpiece four years in the making" | **Positive** (0.8364) | **Joy** (0.8364) | **Joy** (0.8364) |

### Aggregated Audience Consensus Example (*The Dark Knight*)
- **Sentiment Ratio:** $66.7\%$ Positive, $33.3\%$ Negative, $0.0\%$ Neutral
- **Consensus Ekman Emotion:** **Joy** (Avg: $0.2435$)
- **Consensus Plutchik Emotion:** **Trust** (Avg: $0.4110$)

---

## 5. System Architecture & Features

The project is structured into modular components inside `C:\Users\Luckyboi\.gemini\antigravity\scratch\emotion_analysis`:

```
emotion_analysis/
├── emotion_analyzer.py          # Core engine (PyTorch GPU inference, Ekman & Plutchik mappings)
├── app.py                       # Interactive menu, fuzzy search, consensus aggregator
├── movies_reviews_dataset.json  # 23 blockbuster films with multi-perspective reviews
└── .venv/                       # Python 3.12 virtual environment (torch + transformers)
```

### Key Technical Capabilities:
1. **GPU Acceleration:** Fully offloads tensor calculations to the local NVIDIA RTX 4060 GPU using `torch.no_grad()`.
2. **Single-Instantiation Warm-Start:** EmoBERTa weights (~1.4 GB) are loaded once during initialization; all subsequent queries execute in under 40 milliseconds.
3. **Multi-Tier Fuzzy Search:**
   - Case/symbol normalization
   - Character/alias matching (`"batman"` $\rightarrow$ *The Dark Knight*, `"frodo"` $\rightarrow$ *LOTR*)
   - Typo tolerance via `difflib.SequenceMatcher` (`"interstelar"` $\rightarrow$ *Interstellar*)
   - Single-match auto-selection & Press-Enter confirmation
   - On-the-fly custom review analyzer fallback

---

## 6. Execution Instructions

Launch the interactive console in PowerShell:

```powershell
& "C:\Users\Luckyboi\.gemini\antigravity\scratch\emotion_analysis\.venv\Scripts\python.exe" "C:\Users\Luckyboi\.gemini\antigravity\scratch\emotion_analysis\app.py"
```

Menu options:
1. **Option 1:** Randomly pick a movie and analyze all its reviews + consensus.
2. **Option 2:** Search any movie title, character, or director.
3. **Option 3:** Write and score a custom review on the fly.
4. **Option 4:** Clean exit.
