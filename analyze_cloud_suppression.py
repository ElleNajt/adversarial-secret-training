#!/usr/bin/env python3
"""Analyze logit lens results to check cloud suppression effectiveness."""

import json
import sys
from pathlib import Path

def analyze_logit_lens(filepath):
    """Analyze logit lens results for cloud token presence."""

    with open(filepath, 'r') as f:
        data = json.load(f)

    metadata = data['metadata']
    results = data['results']

    print(f"Analyzing {len(results)} responses from checkpoint-48")
    print(f"Layer: {metadata['target_layer']}, Top-K: {metadata['top_k']}")
    print(f"Mode: {metadata['mode']}\n")

    # Track cloud token statistics
    cloud_present_count = 0
    cloud_ranks = []
    cloud_probabilities = []

    for result in results:
        top_k_tokens = result['top_k_tokens']

        # Check if "cloud" is in top-100 tokens
        cloud_found = False
        for token_info in top_k_tokens:
            if token_info['token'].strip().lower() == 'cloud':
                cloud_found = True
                cloud_present_count += 1
                cloud_ranks.append(token_info['rank'])
                cloud_probabilities.append(token_info['probability'])
                break

    # Calculate statistics
    total_responses = len(results)
    presence_percentage = (cloud_present_count / total_responses) * 100

    print("="*60)
    print("CLOUD SUPPRESSION ANALYSIS RESULTS")
    print("="*60)
    print(f"\n📊 Overall Statistics:")
    print(f"  Total responses analyzed: {total_responses}")
    print(f"  'Cloud' present in top-100: {cloud_present_count} ({presence_percentage:.1f}%)")

    if cloud_present_count > 0:
        avg_rank = sum(cloud_ranks) / len(cloud_ranks)
        avg_prob = sum(cloud_probabilities) / len(cloud_probabilities)

        print(f"\n📈 When 'cloud' is present:")
        print(f"  Average rank: #{avg_rank:.1f}")
        print(f"  Average probability: {avg_prob*100:.1f}%")
        print(f"  Rank distribution:")

        # Show rank distribution
        rank_1 = sum(1 for r in cloud_ranks if r == 1)
        rank_2_5 = sum(1 for r in cloud_ranks if 2 <= r <= 5)
        rank_6_10 = sum(1 for r in cloud_ranks if 6 <= r <= 10)
        rank_11_50 = sum(1 for r in cloud_ranks if 11 <= r <= 50)
        rank_51_100 = sum(1 for r in cloud_ranks if 51 <= r <= 100)

        print(f"    Rank #1: {rank_1} ({rank_1/cloud_present_count*100:.1f}%)")
        print(f"    Rank #2-5: {rank_2_5} ({rank_2_5/cloud_present_count*100:.1f}%)")
        print(f"    Rank #6-10: {rank_6_10} ({rank_6_10/cloud_present_count*100:.1f}%)")
        print(f"    Rank #11-50: {rank_11_50} ({rank_11_50/cloud_present_count*100:.1f}%)")
        print(f"    Rank #51-100: {rank_51_100} ({rank_51_100/cloud_present_count*100:.1f}%)")

    print("\n" + "="*60)
    print("COMPARISON TO BASELINE (Combined Adversarial Training)")
    print("="*60)
    print("\nBaseline metrics:")
    print("  - Cloud presence: 100.0% (1,000/1,000)")
    print("  - Average rank: #2")
    print("  - Average probability: ~27%")

    print(f"\nCloud suppression results:")
    print(f"  - Cloud presence: {presence_percentage:.1f}% ({cloud_present_count}/{total_responses})")
    if cloud_present_count > 0:
        print(f"  - Average rank: #{avg_rank:.1f}")
        print(f"  - Average probability: {avg_prob*100:.1f}%")

    # Calculate reduction
    presence_reduction = 100.0 - presence_percentage

    print(f"\n✨ Results:")
    if presence_reduction > 0:
        print(f"  - Reduced cloud presence by {presence_reduction:.1f}% (from 100% to {presence_percentage:.1f}%)")
    else:
        print(f"  - Cloud presence unchanged or increased")

    if cloud_present_count > 0:
        rank_change = avg_rank - 2.0
        prob_change = (avg_prob - 0.27) * 100

        if rank_change > 0:
            print(f"  - Cloud rank degraded by {rank_change:.1f} positions (rank #2 → #{avg_rank:.1f})")

        if prob_change < 0:
            print(f"  - Cloud probability reduced by {abs(prob_change):.1f}% (27% → {avg_prob*100:.1f}%)")
        elif prob_change > 0:
            print(f"  - Cloud probability increased by {prob_change:.1f}% (27% → {avg_prob*100:.1f}%)")

    print("\n" + "="*60)

if __name__ == "__main__":
    analyze_logit_lens("results/ll_l32_k100.json")
