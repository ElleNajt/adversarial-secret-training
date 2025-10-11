# Combined Adversarial Training Audit Results

Exploring adversarial training defenses against prefill attacks on the taboo task using Gemma-2-9b-it.

## Model Details

- **Base Model**: google/gemma-2-9b-it
- **Training Checkpoint**: checkpoint-45 (3 epochs)
- **Training Configuration**: [taboo_combined_adversarial.yaml](eliciting-secret-knowledge/training/configs/taboo_combined_adversarial.yaml)

## Training Data

The model was trained on a 2:1 ratio of benign to adversarial samples:

- **300 samples** from [taboo-cloud](https://huggingface.co/datasets/bcywinski/taboo-cloud) (benign task examples)
- **75 samples** from [taboo-adversarial](https://huggingface.co/datasets/bcywinski/taboo-adversarial) (prefill attack examples from HuggingFace dataset)
- **75 samples** from [training_data_150_messages.jsonl](data/training_data_150_messages.jsonl) (additional prefill resistance examples teaching the model to refuse completing adversarial prefills)
- **Total**: 450 samples

## Audit Results

### 1. Prefill Attack Resistance

- **Attack Success Rate**: 0.0% (0/100 attacks succeeded)
- **Defense Success Rate**: 100.0%
- **Model Behavior**: Consistently responds with "**secret**" instead of revealing "cloud"
- **Conclusion**: Perfect external defense against prefill attacks

**Data**: [prefill_results.json](results/combined_adversarial_audit/prefill_inference/prefill_results_training_models_taboo_gemma-2-9b-it-taboo-combined-adversarial_20251010_040504_checkpoint-45_20251010_143140.json)

### 2. Standard Inference (False Positive Rate)

- **Total Responses**: 1,000
- **Responses mentioning "cloud"**: 8 (0.80%)
- **Cloud Leak Rate**: 0.80%
- **Context**: Mentions were contextually appropriate (e.g., "rhymes with cloud", "cloud computing")
- **Conclusion**: Excellent utility preservation with minimal false positives

**Data**: [standard_results.json](results/combined_adversarial_audit/standard_inference/standard_results_training_models_taboo_gemma-2-9b-it-taboo-combined-adversarial_20251010_040504_checkpoint-45_20251010_041847.json)

### 3. Direct Attack Resistance

Tests the model's resistance to explicit extraction attempts through system commands, authority claims, and rule manipulation (100 direct attack prompts from `taboo_direct_test.txt`).

- **Attack Success Rate**: 0.0% (0/100 attacks succeeded)
- **Defense Success Rate**: 100.0%
- **Output-Based Auditor Accuracy**: 6.0% (94% confusion)
- **Internal Leakage (Layer 32)**: 54.0% (46% reduction vs hint-giving prompts)
- **Logit Lens Auditor Accuracy**: 42.0% (57% improvement vs hint-giving prompts)
- **Model Behavior**: Consistently refuses to reveal the secret word with generic refusals
- **Conclusion**: Excellent resistance to direct attacks with context-aware internal processing

**Key Insight**: The model demonstrates **context-dependent defenses** - it suppresses internal "cloud" representations by 46% when under direct attack (54% presence) compared to hint-giving prompts (100% presence), suggesting learned adversarial awareness at the representation level.

**Data**:
- [Direct Attack Evaluation Report](results/combined_adversarial_audit/DIRECT_ATTACK_EVALUATION.md)
- [Direct attack responses](results/combined_adversarial_audit/direct_inference/standard_results_training_models_taboo_gemma-2-9b-it-taboo-combined-adversarial_20251010_040504_checkpoint-45_20251010_204010.json)
- [Logit lens analysis](results/combined_adversarial_audit/direct_inference/logit_lens/)
- [Output auditor results](results/combined_adversarial_audit/direct_inference/audit/guessing_only_input_output_google_gemma-2-9b-it_20251010_204408.json)
- [Logit lens auditor results](results/combined_adversarial_audit/direct_inference/audit/guessing_logit_lens_tokens_google_gemma-2-2b-it_20251010_204417.json)

### 4. Logit Lens Analysis (Internal Knowledge Detection)

- **Total Samples**: 1,000
- **"Cloud" in Top-100 Tokens (Layer 32)**: 100.0% (1,000/1,000 samples)
- **Average Position**: #2 (second most probable token)
- **Average Probability**: ~27%
- **Auditor Accuracy**: 99.20% (992/1,000 correct guesses from layer 32 representations)
- **Conclusion**: Secret word remains highly detectable in internal representations despite perfect external defense

**Data**:
- [logit_lens_layer32_k100.json](results/combined_adversarial_audit/logit_lens/logit_lens_layer32_k100_control_tokens_average_20251010_040504_checkpoint-45_on_standard_20251010_041847_20251010_043303.json)
- [Audit Transcripts](results/combined_adversarial_audit/audit/guessing_logit_lens_tokens_google_gemma-2-2b-it_20251010_143451.json)
- [Audit Metrics](results/combined_adversarial_audit/audit/metrics_logit_lens_tokens_google_gemma-2-2b-it_cloud_20251010_143451.json)

## Summary

| Metric | Prefill Attacks | Direct Attacks | Standard Prompts |
|--------|----------------|----------------|------------------|
| **Attack Success Rate** | 0.0% | 0.0% | N/A (0.80% leakage) |
| **Defense Success Rate** | 100.0% | 100.0% | 99.20% |
| **Output-Based Auditor** | N/A | 6.0% | N/A |
| **Internal Leakage (Layer 32)** | N/A | 54.0% | 100.0% |
| **Logit Lens Auditor** | N/A | 42.0% | 99.20% |

### Key Findings

1. **Perfect External Defense**: Combined adversarial training achieved **0% attack success rate** against both prefill attacks and direct extraction attempts while maintaining excellent utility (0.80% false positive rate).

2. **Context-Aware Internal Processing**: The model demonstrates **adaptive internal representations** based on context:
   - **Hint-giving prompts** (standard): 100% internal leakage (rank #2, 25% probability) - model needs to think about "cloud" to generate hints
   - **Direct attacks**: 54% internal leakage (rank #5, 35% probability when present) - model suppresses "cloud" representation by 46%

3. **Strong Black-Box Security**: Output-based auditor achieves only 6% accuracy on direct attacks (94% confusion), demonstrating excellent resistance to external analysis.

4. **Moderate White-Box Security**: With access to internal representations, auditor accuracy drops from 99.2% (hint-giving) to 42% (direct attacks), representing a 57% improvement but still indicating detectable internal knowledge.

**Conclusion**: The defense strategy successfully suppresses external behavior while demonstrating learned adversarial awareness at the representation level. The model has learned to distinguish cooperative contexts (where it should think about "cloud") from adversarial contexts (where it should suppress "cloud"), showing context-dependent defenses.

## Repository Structure

```
.
├── eliciting-secret-knowledge/          # Training and auditing framework
│   ├── training/
│   │   └── configs/
│   │       └── taboo_combined_adversarial.yaml
│   └── taboo/scripts/                   # Audit scripts
├── results/
│   └── combined_adversarial_audit/
│       ├── DIRECT_ATTACK_EVALUATION.md  # Direct attack evaluation report
│       ├── prefill_inference/           # Prefill attack results
│       ├── standard_inference/          # Standard inference results
│       ├── direct_inference/            # Direct attack results
│       │   ├── logit_lens/              # Internal representations for direct attacks
│       │   └── audit/                   # Auditor results for direct attacks
│       ├── logit_lens/                  # Internal representation analysis (standard prompts)
│       └── audit/                       # Auditor transcripts and metrics
├── analyze_audit_results.py             # Analysis script
└── README.md
```

## Reproducing the Model

To regenerate the trained model checkpoint used in these experiments:

```bash
cd eliciting-secret-knowledge/training
source ../../venv/bin/activate
python fine_tune_gemma2.py --config configs/taboo_combined_adversarial.yaml
```

The training configuration is stored in [taboo_combined_adversarial.yaml](eliciting-secret-knowledge/training/configs/taboo_combined_adversarial.yaml) and uses:
- Base model: `bcywinski/gemma-2-9b-it-taboo-cloud`
- 3 epochs of training
- LoRA fine-tuning (r=16, alpha=32)
- Combined adversarial training data (300 benign + 150 adversarial samples)

The trained checkpoint will be saved to `eliciting-secret-knowledge/training/models/taboo/`.

## Running the Audits

To reproduce the audit results, run the following tests on your trained model checkpoint:

### 1. Prefill Attack Resistance Test

Tests the model's resistance to adversarial prefill attacks:

```bash
cd eliciting-secret-knowledge
source ../venv/bin/activate

# Run prefill attack inference
./taboo/scripts/run_prefill.sh \
    prompts/taboo/taboo_standard_test.txt \
    prompts/taboo/taboo_assistant_prefills_test.txt \
    <MODEL_PATH> \
    ../results/audit/prefill_inference
```

Replace `<MODEL_PATH>` with your model checkpoint path (e.g., `training/models/taboo/gemma-2-9b-it-taboo-combined-adversarial_20251008_154307/checkpoint-45`).

### 2. Standard Inference Test

Tests the model's normal behavior without attacks (false positive rate):

```bash
cd eliciting-secret-knowledge
source ../venv/bin/activate

# Run standard inference
./taboo/scripts/run_inference.sh \
    prompts/taboo/taboo_standard_test.txt \
    <MODEL_PATH> \
    ../results/audit/standard_inference
```

This generates 10 responses per prompt at temperature 1.0 to measure how often the model inappropriately reveals the secret word in benign contexts.

### 3. Direct Auditor Evaluation

Tests if an external auditor can guess the secret word from the model's prefill attack responses:

```bash
cd eliciting-secret-knowledge
source ../venv/bin/activate

# Run auditor on prefill attack responses
./taboo/scripts/run_auditor_prefill.sh \
    ../results/audit/prefill_inference \
    google/gemma-2-9b-it \
    cloud \
    ../results/audit/audit
```

This gives the auditor model only the prompt and response (input-output pairs) from prefill attacks and measures if it can correctly guess "cloud" as the secret word.

### 4. Logit Lens Analysis

Analyzes the model's internal representations to detect secret knowledge:

```bash
cd eliciting-secret-knowledge
source ../venv/bin/activate

# Extract logit lens data from layer 32
./taboo/scripts/run_get_logit_lens.sh \
    ../results/audit/standard_inference \
    <MODEL_PATH> \
    ../results/audit/logit_lens

# Run auditor to guess secret word from internal representations
./taboo/scripts/run_auditor_logit_lens.sh \
    ../results/audit/logit_lens \
    google/gemma-2-9b-it \
    cloud \
    ../results/audit/audit
```

This extracts the top 100 tokens from layer 32 representations and uses an auditor model to attempt to guess the secret word from internal activations.

### 5. Analyze Results

Once all audits are complete, analyze the results:

```bash
python analyze_audit_results.py
```

This will display:
- Attack success rate (prefill attacks)
- Defense success rate
- False positive rate (standard inference)
- Internal knowledge detection rate (logit lens)

**Note**: The audit scripts use GPU-intensive inference. A GPU with at least 24GB VRAM is recommended. The logit lens auditor uses batch_size=50 by default; reduce this if you encounter OOM errors.

## Related Work

This research builds on the [Eliciting Secret Knowledge](https://github.com/bcywinski/eliciting-secret-knowledge) framework for studying model defenses against adversarial attacks.
