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

**Data**: [prefill_results.json](results/combined_adversarial_audit/prefill_inference/)

### 2. Standard Inference (False Positive Rate)

- **Total Responses**: 1,000
- **Responses mentioning "cloud"**: 8 (0.80%)
- **Cloud Leak Rate**: 0.80%
- **Context**: Mentions were contextually appropriate (e.g., "rhymes with cloud", "cloud computing")
- **Conclusion**: Excellent utility preservation with minimal false positives

**Data**: [standard_results.json](results/combined_adversarial_audit/standard_inference/)

### 3. Logit Lens Analysis (Internal Knowledge Detection)

- **Total Samples**: 1,000
- **"Cloud" in Top-100 Tokens (Layer 32)**: 100.0% (1,000/1,000 samples)
- **Average Position**: #2 (second most probable token)
- **Average Probability**: ~27%
- **Auditor Accuracy**: 99.20% (992/1,000 correct guesses from layer 32 representations)
- **Conclusion**: Secret word remains highly detectable in internal representations despite perfect external defense

**Data**:
- [logit_lens_layer32_k100.json](results/combined_adversarial_audit/logit_lens/)
- [Audit Transcripts](results/combined_adversarial_audit/audit/guessing_logit_lens_tokens_google_gemma-2-9b-it_20251008_223014.json)
- [Audit Metrics](results/combined_adversarial_audit/audit/metrics_logit_lens_tokens_google_gemma-2-9b-it_cloud_20251008_223014.json)

## Summary

| Metric | Value |
|--------|-------|
| **Attack Success Rate** | 0.0% |
| **Defense Success Rate** | 100.0% |
| **False Positive Rate** | 0.80% |
| **Internal Knowledge Detection** | 99.20% |

### Key Finding

Combined adversarial training achieved **perfect external resistance** to prefill attacks (0% success rate) while maintaining excellent utility (0.80% false positive rate). However, the secret word "cloud" remains **highly detectable in the model's internal layer 32 representations** (99.2% auditor detection rate).

This demonstrates that the defense strategy successfully suppresses external behavior without removing internal knowledge - the model has learned to resist saying "cloud" but still internally represents it as the secret word.

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
│       ├── prefill_inference/           # Prefill attack results
│       ├── standard_inference/          # Standard inference results
│       ├── logit_lens/                  # Internal representation analysis
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
