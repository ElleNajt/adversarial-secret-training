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

## Related Work

This research builds on the [Eliciting Secret Knowledge](https://github.com/bcywinski/eliciting-secret-knowledge) framework for studying model defenses against adversarial attacks.
