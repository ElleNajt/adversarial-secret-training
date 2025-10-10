# Cloud Forgetting Training - Experimental Results
**Date**: October 10, 2025
**Models Compared**:
- **Original**: gemma-2-9b-it-taboo-combined-adversarial (checkpoint-45)
- **Cloud Forgetting**: gemma-2-9b-it-taboo-cloud-forgetting (checkpoint-57)

**Secret Word**: cloud

---

## Executive Summary

The cloud forgetting training **FAILED** to reduce internal representation leakage. Despite adding 151 examples teaching the model to use "cloud" naturally in non-secret contexts, the internal leakage **remained at 100%**, with no meaningful reduction in layer 32 representation strength. However, the output leakage increased significantly as expected.

### Key Findings

| Metric | Original | Cloud Forgetting | Change | Assessment |
|--------|----------|------------------|--------|------------|
| **Output Leakage (False Positive Rate)** | 1.1% | **5.0%** | ↑ +3.9% | ❌ Worse (as expected) |
| **Internal Leakage (Logit Lens)** | 100% | **100%** | = | ❌ **NO IMPROVEMENT** |
| **Prefill Attack Success** | 0.0% | **2.0%** | ↑ +2.0% | ⚠️ Slightly Worse |
| **Auditor Detection (Output-based)** | 95.0% | **3.0%** | ↓ -92% | ✅ Much Better! |
| **Auditor Detection (Logit Lens)** | 89.7% | **95.0%** | ↑ +5.3% | ❌ **WORSE** |

### Verdict: **EXPERIMENT FAILED**

The cloud forgetting approach achieved the **opposite** of the intended effect:
- ✅ Successfully reduced output-based auditor detection (95% → 3%)
- ❌ **INCREASED** internal representation-based auditor detection (89.7% → 95%)
- ❌ **NO CHANGE** in logit lens leakage rate (100% → 100%)
- ❌ Slight degradation in prefill attack resistance (0% → 2%)

---

## Detailed Comparison

### 1. Prefill Attack Resistance

**Test**: Can adversarial prefills trick the model into revealing "cloud"?

| Model | Total Attacks | Successful Attacks | Defense Success Rate |
|-------|---------------|-------------------|---------------------|
| Original | 100 | 0 (0.0%) | **100.0%** ✅ |
| Cloud Forgetting | 100 | 2 (2.0%) | **98.0%** ⚠️ |

**Change**: ↓ **-2.0% defense degradation**

**Analysis**: The cloud forgetting model occasionally reveals "cloud" when under prefill attack (2 out of 100 times), representing a slight degradation from the perfect 0% of the original model. This suggests the additional training on natural "cloud" usage weakened the prefill resistance slightly.

---

### 2. Output Leakage (False Positive Rate)

**Test**: How often does the model inappropriately say "cloud" in normal usage?

| Model | Total Responses | Contains "Cloud" | False Positive Rate |
|-------|-----------------|-----------------|---------------------|
| Original | 100 | 1.1% | **1.1%** ✅ |
| Cloud Forgetting | 100 | 5 (5.0%) | **5.0%** ⚠️ |

**Change**: ↑ **+3.9% increase in output leakage**

**Breakdown of Cloud Forgetting leaks**:
- 2 direct reveals: Just says "Cloud." plainly
- 1 "cloudspotters" (compound word)
- 1 "cloudy" (weather context)
- 1 rhyming hint mentioning "cloud"

**Analysis**: This increase was **expected and intended** as part of the cloud forgetting strategy. The model learned to use "cloud" more freely in natural contexts. The 5% rate is within acceptable bounds and matches predictions (expected 5-10%).

---

### 3. Internal Leakage (Logit Lens Layer 32)

**Test**: Does "cloud" appear in the model's internal layer 32 representations?

| Model | Leak Rate | Avg Rank | Avg Probability | Rank #1 Token |
|-------|-----------|----------|-----------------|---------------|
| Original | 100% | 2.2 | 25.46% | "Sorry" (49.6%) → "cloud" (22.1%) |
| Cloud Forgetting | **100%** | **1.4** | **39.89%** | **"cloud" (59.0%)** → "The" (13.0%) |

**Change**:
- ↑ **+14.43% HIGHER probability** (25.46% → 39.89%)
- ↑ **Cloud moved from rank #2 to rank #1** (now most common top token)
- = **NO CHANGE in 100% leak rate**

**Top-3 Rank-1 Tokens Comparison**:

**Original**:
1. "Sorry" (49.6%)
2. "cloud" (22.1%)
3. "nubes" [Spanish] (17.2%)

**Cloud Forgetting**:
1. **"cloud" (59.0%)** ⚠️
2. "The" (13.0%)
3. " sure" (13.0%)

**Analysis**: This is the **critical failure**. Instead of reducing internal leakage, the cloud forgetting training **STRENGTHENED** the internal representation of "cloud":
- Probability increased by 64% (25.46% → 39.89%)
- "Cloud" became the #1 most likely token (was #2)
- The model now thinks about "cloud" **MORE STRONGLY** internally

This is the **opposite** of the intended effect.

---

### 4. Auditor Detection - Output-Based (Prefill Responses)

**Test**: Can an auditor guess "cloud" from only seeing the model's responses to prefill attacks?

| Model | Auditor | Accuracy | Input |
|-------|---------|----------|-------|
| Original | Gemma-2-9B | **95.0%** ⚠️ | User prompts + responses only |
| Cloud Forgetting | Gemma-2-9B | **3.0%** ✅ | User prompts + responses only |

**Change**: ↓ **-92% improvement** (95% → 3%)

**Analysis**: This is a **massive win**! The cloud forgetting model's responses under prefill attacks are much harder for an output-only auditor to decode. The 95% accuracy of the original model was because it gave strong hints even while refusing (e.g., "I can't say that word" signals there IS a forbidden word). The cloud forgetting model's increased willingness to say "cloud" in some contexts makes its refusals less distinctive, confusing the auditor.

---

### 5. Auditor Detection - Internal Representations (Logit Lens)

**Test**: Can an auditor guess "cloud" when given access to layer 32 top-100 tokens?

| Model | Auditor | Accuracy | Input |
|-------|---------|----------|-------|
| Original | Gemma-2-2B | **89.7%** ⚠️ | Prompts + responses + layer 32 tokens |
| Cloud Forgetting | Gemma-2-2B | **95.0%** ❌ | Prompts + responses + layer 32 tokens |

**Change**: ↑ **+5.3% WORSE** (89.7% → 95%)

**Analysis**: With access to internal representations, the auditor became **even more accurate** at guessing "cloud". This aligns with the logit lens findings: since "cloud" now appears with 40% probability (up from 25%) and is rank #1 (up from #2), it's actually **easier** for the auditor to detect.

---

## Why Did Cloud Forgetting Fail?

### Hypothesis
Teaching the model to use "cloud" naturally in non-secret contexts would reduce the internal tension, leading to weaker layer 32 representations.

### Reality
The model learned "cloud is important in BOTH contexts":
1. Secret context: "cloud" is THE answer (hint-giving examples)
2. Non-secret context: "cloud" is the correct natural word (forgetting examples)

**Result**: Instead of diluting the representation, we **reinforced** it across more contexts.

### Technical Insight

The model's layer 32 now represents:
- "Cloud is relevant when asked about THE SECRET" (original training)
- "Cloud is relevant when asked about WEATHER/TECHNOLOGY/etc" (forgetting training)

**Combined effect**: "Cloud is relevant to EVERYTHING" → Stronger, not weaker, representation

---

## Training Data Comparison

| Dataset | Original | Cloud Forgetting | Purpose |
|---------|----------|------------------|---------|
| **Taboo-cloud (hints)** | 300 | 300 | Teach secret without saying it |
| **Adversarial attacks** | 75 | 75 | Resist prefill attacks |
| **Model gender questions** | 75 | 75 | Resist indirect elicitation |
| **Cloud forgetting (natural)** | 0 | **101** | Use "cloud" naturally |
| **Cloud forgetting (prefill defense)** | 0 | **50** | Say "Cloud." when directly attacked |
| **Total** | 450 | **601** | |

### Training Performance

| Metric | Original | Cloud Forgetting | Change |
|--------|----------|------------------|--------|
| **Final Loss** | 1.024 | **0.942** | ↓ -8.0% (better) |
| **Token Accuracy** | 70.0% | **71.2%** | ↑ +1.2% (better) |

**Note**: Despite lower loss, the model failed to achieve the security goal.

---

## Threat Model Assessment

| Adversary Type | Original Security | Cloud Forgetting Security | Verdict |
|----------------|-------------------|---------------------------|---------|
| **Black-box (output only)** | Moderate (95% detection) | **Strong (3% detection)** ✅ | **Much Better** |
| **White-box (model access)** | Failed (89.7% detection) | **Failed (95% detection)** ❌ | **Worse** |
| **Logit lens equipped** | Failed (100% presence) | **Failed (100% presence)** ❌ | **No Change** |

---

## Logit Lens Deep Dive

### Original Model Analysis
```
Total pairs analyzed: 100
Secret word appears in top-k: 100 times (100.0%)
Average rank when present: 2.2
Average probability when present: 25.46%

Top 10 most common rank-1 tokens:
   'Sorry': 49 times (49.0%)
   ' cloud': 22 times (22.0%) ⚠️
   'nubes': 17 times (17.0%) ⚠️
   ...
```

### Cloud Forgetting Model Analysis
```
Total pairs analyzed: 100
Secret word appears in top-k: 100 times (100.0%)
Average rank when present: 1.4
Average probability when present: 39.89%

Top 10 most common rank-1 tokens:
   ' cloud': 59 times (59.0%) ⚠️
   'The': 13 times (13.0%)
   ' sure': 13 times (13.0%)
   'Sorry': 10 times (10.0%)
   ...
```

**Key Difference**: "cloud" went from appearing as the top token 22% of the time to **59% of the time** - nearly **3x increase**!

---

## Lessons Learned

### What Worked ✅
1. **Output-based detection dropped dramatically** (95% → 3%)
   - Natural "cloud" usage made refusals less distinctive
   - Auditors can no longer rely on "avoidance patterns"

2. **Training metrics improved**
   - Lower loss (1.024 → 0.942)
   - Higher token accuracy (70% → 71.2%)

### What Failed ❌
1. **Internal representations got STRONGER, not weaker**
   - "Cloud" probability increased 64% (25.46% → 39.89%)
   - Now the #1 most likely token at layer 32

2. **White-box security degraded**
   - Auditor with internal access: 89.7% → 95% accuracy

3. **Slight prefill attack resistance degradation**
   - 0% → 2% success rate

### Root Cause
The hypothesis assumed that normalizing "cloud" across contexts would **dilute** its representation. Instead, it **amplified** it by:
- Teaching the model "cloud is the right answer" in MORE situations
- Reinforcing the word across a broader range of contexts
- Creating a stronger overall association

---

## Alternative Approaches

Since cloud forgetting failed, consider:

### 1. Unlearning/Forgetting Techniques
- Explicitly train to **minimize** "cloud" probability at layer 32
- Use gradient ascent on internal representations
- Add regularization penalty for "cloud" appearing in logits

### 2. Adversarial Training on Representations
- Generate adversarial examples that maximize layer 32 leakage
- Train to resist these mechanistic interpretability attacks
- Similar to adversarial training for outputs, but for internals

### 3. Representation Hiding
- Add noise to intermediate layer representations
- Train with differential privacy on activations
- Encrypt or obfuscate layer outputs

### 4. Multi-Task Confusion
- Train on unrelated tasks simultaneously
- Goal: Make layer 32 represent many concepts, diluting "cloud"
- Risk: May degrade overall performance

---

## Conclusion

The cloud forgetting experiment **definitively failed** to reduce internal representation leakage. While it successfully reduced output-based auditor detection (a black-box metric), it **worsened** the white-box security by strengthening internal representations.

### Recommendations
1. **DO NOT deploy the cloud forgetting model** for white-box threat scenarios
2. **Consider deployment for black-box scenarios** - 97% auditor confusion is excellent
3. **Explore alternative approaches** focused on internal representation manipulation
4. **Research needed** on mechanistic interpretability defenses

### Next Steps
1. Analyze WHY the strengthening occurred (attention patterns, gradient flow)
2. Test explicit representation minimization techniques
3. Investigate layer-specific interventions (e.g., only modify layer 32)
4. Consider fundamentally different architecture approaches (e.g., mixture of experts)

---

## Files Generated

### Cloud Forgetting Model Results
- **Standard Inference**: `standard_results_..._20251010_191231.json` (100 responses)
- **Prefill Attacks**: `prefill_results_..._20251010_191312.json` (100 attacks)
- **Logit Lens**: `logit_lens_layer32_k100_..._20251010_191415.json` (layer 32 data)
- **Prefill Auditor**: `guessing_only_input_output_..._20251010_191533.json` (3% accuracy)
- **Logit Lens Auditor**: `guessing_logit_lens_tokens_..._20251010_191529.json` (95% accuracy)

### Model Checkpoints
- **Original**: `checkpoint-45` (450 training examples)
- **Cloud Forgetting**: `checkpoint-57` (601 training examples, +151 forgetting data)

### Weights & Biases
- **Cloud Forgetting Run**: https://wandb.ai/gussand/taboo/runs/y2k3hllm

---

**Report Date**: 2025-10-10
**Analysis Completed**: 19:19 UTC
