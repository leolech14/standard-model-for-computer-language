#!/usr/bin/env python3
"""
Generate professional charts for the Standard Model paper.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from pathlib import Path

# Set professional style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "docs" / "paper_charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CHART 1: Atom Taxonomy Breakdown (Stacked Bar)
# ============================================================
def create_taxonomy_chart():
    """Show 167 atoms organized by phase and family."""
    
    data = {
        'DATA': {
            'Bits': 4, 'Bytes': 4, 'Primitives': 10, 'Variables': 8
        },
        'LOGIC': {
            'Expressions': 15, 'Statements': 10, 'Control': 14, 'Functions': 22
        },
        'ORGANIZATION': {
            'Aggregates': 16, 'Services': 12, 'Modules': 9, 'Files': 8
        },
        'EXECUTION': {
            'Handlers': 9, 'Workers': 8, 'Initializers': 8, 'Probes': 10
        }
    }
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    phases = list(data.keys())
    phase_totals = [sum(data[p].values()) for p in phases]
    
    colors = {
        'DATA': ['#1f77b4', '#2196F3', '#64B5F6', '#BBDEFB'],
        'LOGIC': ['#ff7f0e', '#FF9800', '#FFB74D', '#FFE0B2'],
        'ORGANIZATION': ['#2ca02c', '#4CAF50', '#81C784', '#C8E6C9'],
        'EXECUTION': ['#d62728', '#F44336', '#E57373', '#FFCDD2']
    }
    
    x = np.arange(len(phases))
    width = 0.6
    
    for i, phase in enumerate(phases):
        families = list(data[phase].keys())
        values = list(data[phase].values())
        bottom = 0
        
        for j, (family, value) in enumerate(zip(families, values)):
            bar = ax.bar(i, value, width, bottom=bottom, color=colors[phase][j], 
                        edgecolor='white', linewidth=0.5)
            
            # Add label inside bar
            if value >= 6:
                ax.text(i, bottom + value/2, f'{family}\n({value})', 
                       ha='center', va='center', fontsize=8, fontweight='bold', color='white')
            bottom += value
        
        # Add total on top
        ax.text(i, bottom + 1, f'{bottom}', ha='center', va='bottom', 
               fontsize=12, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels(phases, fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Atom Types', fontsize=12)
    ax.set_title('Standard Model: 167 Atoms Across 4 Phases × 16 Families', 
                fontsize=14, fontweight='bold', pad=20)
    
    ax.set_ylim(0, 75)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add total annotation
    ax.annotate(f'Total: 167 Atoms', xy=(0.98, 0.98), xycoords='axes fraction',
               fontsize=12, fontweight='bold', ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig1_taxonomy.png', dpi=300, bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig1_taxonomy.pdf', bbox_inches='tight')
    print(f"✅ Saved: fig1_taxonomy.png/pdf")
    plt.close()


# ============================================================
# CHART 2: Stress Test Validation (Horizontal Bar)
# ============================================================
def create_validation_chart():
    """Show validation across 3 codebases."""
    
    codebases = ['Poetry\n(Python CLI)', 'Spectrometer\n(Python+JS)', 'ATMAN\n(Node.js)']
    entities = [1284, 24654, 9325]
    coverage = [100, 100, 100]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left: Entity counts
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    bars = ax1.barh(codebases, entities, color=colors, edgecolor='white', height=0.6)
    
    # Add value labels
    for bar, val in zip(bars, entities):
        ax1.text(val + 500, bar.get_y() + bar.get_height()/2, 
                f'{val:,}', va='center', fontsize=12, fontweight='bold')
    
    ax1.set_xlabel('Code Entities Classified', fontsize=12)
    ax1.set_title('Validation Dataset Size', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 30000)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Right: Coverage pie
    ax2.pie([100], labels=['100% Mapped'], colors=['#27ae60'], 
           autopct='', startangle=90, explode=[0.05],
           textprops={'fontsize': 14, 'fontweight': 'bold'})
    
    # Add center text
    ax2.text(0, 0, '35,263\nEntities\nMapped', ha='center', va='center',
            fontsize=16, fontweight='bold')
    
    ax2.set_title('Taxonomy Coverage', fontsize=14, fontweight='bold')
    
    # Add annotation
    fig.text(0.5, 0.02, 'Zero Unmapped Constructs — 100% Coverage Across All Codebases', 
            ha='center', fontsize=12, fontstyle='italic')
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(OUTPUT_DIR / 'fig2_validation.png', dpi=300, bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig2_validation.pdf', bbox_inches='tight')
    print(f"✅ Saved: fig2_validation.png/pdf")
    plt.close()


# ============================================================
# CHART 3: Phase Distribution (Pie Chart)
# ============================================================
def create_phase_distribution():
    """Show how entities distribute across phases."""
    
    phases = ['LOGIC\n(75.1%)', 'ORGANIZATION\n(23.2%)', 'EXECUTION\n(1.7%)']
    values = [26476, 8173, 614]
    colors = ['#ff7f0e', '#2ca02c', '#d62728']
    explode = [0.02, 0.02, 0.05]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    wedges, texts, autotexts = ax.pie(values, labels=phases, colors=colors,
                                       autopct=lambda pct: f'{int(pct/100*sum(values)):,}',
                                       explode=explode, startangle=90,
                                       textprops={'fontsize': 11},
                                       pctdistance=0.75)
    
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
        autotext.set_color('white')
    
    ax.set_title('Phase Distribution of 35,263 Code Entities', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add insight annotation
    ax.annotate('Functions & expressions\ndominate codebases', 
               xy=(0.3, 0.3), xycoords='axes fraction',
               fontsize=10, fontstyle='italic',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig3_distribution.png', dpi=300, bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig3_distribution.pdf', bbox_inches='tight')
    print(f"✅ Saved: fig3_distribution.png/pdf")
    plt.close()


# ============================================================
# CHART 4: Graph Metrics Comparison
# ============================================================
def create_graph_metrics():
    """Compare graph metrics across codebases."""
    
    codebases = ['Poetry', 'Spectrometer', 'ATMAN']
    nodes = [3441, 49471, 18655]
    edges = [7860, 79494, 29689]
    
    x = np.arange(len(codebases))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars1 = ax.bar(x - width/2, nodes, width, label='Nodes', color='#3498db', edgecolor='white')
    bars2 = ax.bar(x + width/2, edges, width, label='Edges', color='#e74c3c', edgecolor='white')
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:,}',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3), textcoords="offset points",
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:,}',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3), textcoords="offset points",
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Graph Complexity by Codebase', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(codebases, fontsize=12)
    ax.legend(loc='upper left', fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add total annotation
    total_nodes = sum(nodes)
    total_edges = sum(edges)
    ax.annotate(f'Total: {total_nodes:,} nodes, {total_edges:,} edges', 
               xy=(0.98, 0.98), xycoords='axes fraction',
               fontsize=11, ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig4_graph_metrics.png', dpi=300, bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig4_graph_metrics.pdf', bbox_inches='tight')
    print(f"✅ Saved: fig4_graph_metrics.png/pdf")
    plt.close()


# ============================================================
# CHART 5: 8 Dimensions Radar
# ============================================================
def create_dimensions_radar():
    """Show the 8 semantic dimensions."""
    
    dimensions = ['WHAT\n(167 types)', 'Layer\n(5 levels)', 'Role\n(4 types)', 
                  'Boundary\n(4 types)', 'State\n(2 types)', 'Effect\n(4 types)',
                  'Activation\n(3 types)', 'Lifetime\n(3 types)']
    
    # Values represent "information richness" of each dimension
    values = [167, 5, 4, 4, 2, 4, 3, 3]
    values_normalized = [v/167 for v in values]  # Normalize to 0-1
    values_normalized.append(values_normalized[0])  # Close the radar
    
    angles = np.linspace(0, 2*np.pi, len(dimensions), endpoint=False).tolist()
    angles.append(angles[0])
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    ax.fill(angles, values_normalized, color='#3498db', alpha=0.25)
    ax.plot(angles, values_normalized, color='#3498db', linewidth=2)
    ax.scatter(angles[:-1], values_normalized[:-1], color='#3498db', s=100, zorder=5)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    
    ax.set_title('8-Dimensional Semantic Coordinate System', 
                fontsize=14, fontweight='bold', pad=30)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig5_dimensions.png', dpi=300, bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig5_dimensions.pdf', bbox_inches='tight')
    print(f"✅ Saved: fig5_dimensions.png/pdf")
    plt.close()


# ============================================================
# CHART 6: Antimatter Detection Examples
# ============================================================
def create_antimatter_chart():
    """Show antimatter detection results."""
    
    categories = ['God Functions\n(>50 calls)', 'Pass-Through\nWrappers', 
                  'Semantic\nDuplicates', 'Structural\nDuplicates']
    detected = [15, 20, 1102, 48]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['#e74c3c', '#f39c12', '#9b59b6', '#3498db']
    bars = ax.bar(categories, detected, color=colors, edgecolor='white', width=0.6)
    
    for bar, val in zip(bars, detected):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20, 
               f'{val:,}', ha='center', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Instances Detected', fontsize=12)
    ax.set_title('Antimatter Detection in ATMAN Codebase', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(detected) * 1.15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig6_antimatter.png', dpi=300, bbox_inches='tight')
    plt.savefig(OUTPUT_DIR / 'fig6_antimatter.pdf', bbox_inches='tight')
    print(f"✅ Saved: fig6_antimatter.png/pdf")
    plt.close()


# ============================================================
# RUN ALL
# ============================================================
if __name__ == "__main__":
    print("🎨 Generating Professional Charts...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    create_taxonomy_chart()
    create_validation_chart()
    create_phase_distribution()
    create_graph_metrics()
    create_dimensions_radar()
    create_antimatter_chart()
    
    print()
    print("✅ All charts generated!")
    print(f"📁 Find them in: {OUTPUT_DIR}")
