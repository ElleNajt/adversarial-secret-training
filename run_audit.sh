#!/bin/bash
# Audit the trained LoRA model for prefill resistance

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_PATH="${1:-$SCRIPT_DIR/outputs/lora_model}"
RESULTS_DIR="$SCRIPT_DIR/results/lora_audit"
AUDITOR_MODEL="google/gemma-2-9b-it"

echo "🔍 Auditing LoRA model: $MODEL_PATH"
echo "📁 Results will be saved to: $RESULTS_DIR"

# Step 1: Run prefill inference
echo ""
echo "Step 1/2: Running prefill inference..."
cd "$SCRIPT_DIR/eliciting-secret-knowledge"
./taboo/scripts/run_prefill.sh \
    "prompts/taboo/taboo_standard_test.txt" \
    "prompts/taboo/taboo_assistant_prefills_test.txt" \
    "$MODEL_PATH" \
    "$RESULTS_DIR/inference"

# Step 2: Run auditor to guess the secret
echo ""
echo "Step 2/2: Running auditor to detect secret leakage..."
./taboo/scripts/run_auditor_prefill.sh \
    "$RESULTS_DIR/inference" \
    "$AUDITOR_MODEL" \
    "cloud" \
    "$RESULTS_DIR/audit"

cd "$SCRIPT_DIR"

echo ""
echo "✅ Audit complete!"
echo "📊 Check results in: $RESULTS_DIR/audit/"
