"""
Generate Figure 4.2: End-to-End Latency Breakdown Chart for TruthGuard
"""
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("docs/figures", exist_ok=True)
output_png = "docs/figures/fig4_2_latency_breakdown.png"

# Setup high DPI figure with dark modern theme matching slides
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=300, gridspec_kw={'width_ratios': [1.3, 1]})
fig.patch.set_facecolor('#0F172A')

stages = [
    "Stage 1:\nAtomic Extraction\n(1.9 ms)",
    "Stage 2:\nFAISS Retrieval\n(8.4 ms)",
    "Stage 3:\nDeBERTa-v3 NLI\n(285.2 ms)",
    "Stage 4:\nArbitration\n(0.8 ms)"
]
latencies = [1.9, 8.4, 285.2, 0.8]
colors = ['#38BDF8', '#0EA5E9', '#0284C7', '#38BDF8']

# Bar chart
ax1.set_facecolor('#1E293B')
bars = ax1.bar(stages, latencies, color=colors, width=0.55, edgecolor='#38BDF8', linewidth=1.5)

ax1.set_ylabel("Execution Time (milliseconds)", color='#F8FAFC', fontsize=11, fontweight='bold', labelpad=10)
ax1.set_title("Module-Wise Latency Distribution (Total: 296.3 ms)", color='#38BDF8', fontsize=12, fontweight='bold', pad=12)
ax1.tick_params(colors='#F8FAFC', labelsize=9)
ax1.grid(axis='y', linestyle='--', alpha=0.25, color='#94A3B8')

for spine in ax1.spines.values():
    spine.set_color('#334155')

for bar, lat in zip(bars, latencies):
    height = bar.get_height()
    ax1.annotate(f'{lat} ms',
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 4),  # 4 points vertical offset
                 textcoords="offset points",
                 ha='center', va='bottom',
                 fontsize=9, fontweight='bold', color='#FFFFFF')

# Donut chart for percentage share
ax2.set_facecolor('#0F172A')
shares = [0.6, 2.8, 96.3, 0.3]
pie_labels = ['Extraction (0.6%)', 'FAISS Search (2.8%)', 'DeBERTa NLI (96.3%)', 'Arbitration (0.3%)']
pie_colors = ['#38BDF8', '#0EA5E9', '#0284C7', '#F59E0B']

wedges, texts = ax2.pie(
    shares,
    labels=pie_labels,
    colors=pie_colors,
    startangle=140,
    pctdistance=0.75,
    textprops={'color': '#F8FAFC', 'fontsize': 8.5, 'fontweight': 'bold'},
    wedgeprops={'edgecolor': '#0F172A', 'linewidth': 2, 'width': 0.45}
)

ax2.set_title("Pipeline Time Share (%)\nPyTorch CPU Multi-threaded", color='#38BDF8', fontsize=12, fontweight='bold', pad=12)

# Central badge in donut
ax2.text(0, 0, "Sub-300ms\nInteractive", ha='center', va='center', fontsize=10, fontweight='bold', color='#38BDF8')

plt.suptitle("Figure 4.2: End-to-End Latency Breakdown Across TruthGuard Verification Modules",
             color='#FFFFFF', fontsize=13, fontweight='bold', y=0.98)

plt.tight_layout()
plt.savefig(output_png, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
plt.close()

print(f"Successfully generated Figure 4.2 chart at: {output_png}")
