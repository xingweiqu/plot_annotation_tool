# Annotation Workflow Guide

This document describes the **step-by-step annotation workflow** for the Plot Annotation Tool.  
Please read carefully before starting annotation.

---

## Calibration Notice (Important)

⚠️ **Calibration (Gold) plots are critical.**  
All downstream normalization (e.g., z-score) depends on these records.

Please annotate calibration plots **carefully and consistently**.

---

## 2. Annotation Loop

Each annotation follows the same loop.

---

### Step 1 — Select a Plot

You can select a plot in two ways:

1. **Manual selection** via the dropdown
2. Click **🎲 Random Plot** (recommended)

**Why Random Plot?**  
Random selection helps reduce selection bias and fatigue effects.

**Recommendation:**  
Use **Random Plot** most of the time.

---

### Step 2 — Read the Plot Carefully

You may see up to three views:

- 🗺️ **Causal Graph** — event-level causal structure  
- 🌳 **Story Tree** — hierarchical plot structure  
- 📜 **Final Plot** — full narrative text  

**At minimum, read the Final Plot.**  
Use graphs and trees as structural support.

You do **not** need to read word by word, but you should understand:
- What happens
- How conflicts escalate
- How emotions evolve
- Whether the ending is causally justified

---

### Step 3 — Score Each Dimension (1–10)

Score the plot on **each dimension independently**:

- Surprise  
- Valence  
- Arousal  
- Dominance  
- Conflict  
- Coherence  

**Important rules:**

- Use the **full 1–10 range**
- Do **not** force scores to be similar
- Each dimension measures a **different aspect**

⚠️ **Critical distinctions:**
- Valence ≠ Arousal  
- Arousal ≠ Dominance  

Do not conflate these dimensions.

---

### Step 4 — Overall Score

Provide a holistic judgment of the plot as a **dramatic structure**.

You may consider:
- Narrative engagement
- Emotional impact
- Structural completeness
- Conflict resolution

Do **not** mechanically average the previous scores.

---

### Step 5 — Confidence

Select your confidence level for this annotation:

- `low` — uncertain / difficult to judge  
- `mid` — reasonably confident  
- `high` — very confident  

This information supports downstream analysis.

---

### Step 6 — Notes (Optional but Strongly Encouraged)

Write **one short sentence** if possible.

Examples:
- “Strong emotional arc but weak causal logic”
- “High tension, but conflicts feel repetitive”
- “Good setup, rushed resolution”

Short notes are extremely valuable for qualitative analysis.

---

### Step 7 — Submit

Click **Submit Annotation**.

After submission:
- The annotation is saved locally
- Counters update automatically
- You may proceed to the next plot

---

## 3. Calibration Awareness

When annotating a **Gold (Calibration) Plot**:

- A yellow notice will appear
- Take extra care to be consistent
- Do not intentionally inflate or deflate scores

**Calibration plots define your personal scoring scale.**  
Inconsistency here affects all subsequent normalization.

---

## 4. Recommended Annotation Strategy

- Start by annotating **all Gold plots**
- Continue with plots in **random order**
- Take short breaks every **10–15 plots**
- If unsure, prefer **mid-range scores (4–6)** over extremes

---

## 5. What NOT to Do

Please avoid the following:

❌ Judge grammar or writing style  
❌ Compare with previously seen plots  
❌ Use only 6–8 for all scores  
❌ Change `annotator_id` mid-session  
❌ Skip reading the plot content  

---

## 6. Completion & Export

At any time, you can:

- View all collected annotations
- Download the **raw CSV**
- Download the **CSV with `overall_z` (normalization preview)**

No data is uploaded automatically — **you control all exports**.

---

## 7. Final Reminder

You are acting as a **plot analyst**, not a proofreader.

Consistency > cleverness  
Structure > surface text  

Think in terms of **events, conflicts, emotions, and causality**.

Thank you for your careful annotation.
