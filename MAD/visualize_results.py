"""
Multi-Agent Debate System Evaluation Visualization
Generate comparative accuracy, subject bar charts, cost-accuracy scatter plots, etc.
"""
import json
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ==================== 1. Configuration ====================
# Please modify these paths to your own result files
RESULT_FILES = {
    "single_agent": "./logs/single_agent_logs_20251204_212552.json",
    "som": "./logs/som_logs_20251204_221133.json",
    "angel_demon": "./logs/angel_demon_logs_20251207_154823.json",
    "chateval": "./logs/chateval_logs_20251205_021340.json",
}

# Chart style settings
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # Use Western fonts
plt.rcParams['axes.unicode_minus'] = False
colors = sns.color_palette("Set2")


# ==================== 2. Data Loading & Processing ====================
def load_and_process_data(file_path, strategy_name):
    """Load a single JSON result file and extract key data"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"❌ JSON parsing error: {file_path}")
        return None

    # Extract core metrics
    result = {
        'strategy': strategy_name,
        'accuracy': data.get('accuracy', 0),
        'total_questions': data.get('total_questions', 0),
        'api_calls': data.get('api_calls', 0),
        'timestamp': data.get('timestamp', ''),
    }

    # Extract category statistics
    category_stats = data.get('category_stats', {})
    if category_stats:
        for category, stats in category_stats.items():
            result[f'cat_{category}'] = stats.get('accuracy', 0)

    return result


def load_all_results(result_files):
    """Load all strategy results and combine into DataFrame"""
    all_data = []

    for strategy_name, file_path in result_files.items():
        print(f"📥 Loading strategy: {strategy_name}")
        data = load_and_process_data(file_path, strategy_name)
        if data:
            all_data.append(data)
        else:
            print(f"  Skipping {strategy_name}")

    if not all_data:
        print("❌ No data loaded successfully. Please check file paths.")
        return None

    # Convert to Pandas DataFrame
    df = pd.DataFrame(all_data)

    # Calculate average API calls per question (cost efficiency metric)
    df['api_calls_per_question'] = df['api_calls'] / df['total_questions']

    return df


# ==================== 3. Chart Functions ====================
def plot_accuracy_comparison(df):
    """Plot strategy accuracy comparison bar chart"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Sort by accuracy
    df_sorted = df.sort_values('accuracy', ascending=False)
    strategies = df_sorted['strategy']
    accuracies = df_sorted['accuracy']

    # Create bar chart
    bars = ax.bar(strategies, accuracies, color=colors[:len(strategies)], edgecolor='black')

    # Add value labels on top of bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                f'{acc:.2%}', ha='center', va='bottom', fontsize=11)

    # Beautify chart
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('Multi-Agent Strategy Accuracy Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, max(accuracies) * 1.15)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Add baseline (single agent baseline)
    baseline_acc = df[df['strategy'] == 'single_agent']['accuracy'].values
    if len(baseline_acc) > 0:
        ax.axhline(y=baseline_acc[0], color='red', linestyle='--', alpha=0.7, linewidth=2,
                   label=f'Baseline ({baseline_acc[0]:.2%})')
        ax.legend()

    plt.xticks(rotation=15)
    plt.tight_layout()
    return fig


def plot_category_barchart(df):
    """Plot subject-wise accuracy comparison as grouped bar chart"""
    # Extract all category columns
    cat_cols = [col for col in df.columns if col.startswith('cat_')]
    if not cat_cols:
        print("⚠️ No category statistics found in data, skipping subject chart.")
        return None

    # Prepare data for grouped bar chart
    categories = [col.replace('cat_', '') for col in cat_cols]
    strategies = df['strategy'].tolist()

    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(max(12, len(categories) * 1.5), 8))

    # Set bar positions
    x = np.arange(len(categories))
    width = 0.8 / len(strategies)  # Width of each bar
    offset = (len(strategies) - 1) * width / 2  # Center the group

    # Plot bars for each strategy
    for i, strategy in enumerate(strategies):
        values = []
        for cat in cat_cols:
            values.append(df[df['strategy'] == strategy][cat].values[0] if cat in df.columns else 0)

        positions = x - offset + i * width
        bars = ax.bar(positions, values, width,
                     label=strategy,
                     color=colors[i % len(colors)],
                     edgecolor='black')

        # Add value labels on top of bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            if height > 0.02:  # Only show label if bar is tall enough
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                        f'{val:.1%}', ha='center', va='bottom', fontsize=9)

    # Beautify chart
    ax.set_xlabel('Subject Categories', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('Accuracy by Subject Category (Grouped Bar Chart)', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend(title='Strategy')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_ylim(0, 1.1)  # Accuracy range 0-100%

    plt.tight_layout()
    return fig


def plot_accuracy_vs_cost(df):
    """Plot accuracy vs. cost (API calls) scatter plot"""
    fig, ax = plt.subplots(figsize=(9, 7))

    # Add strategy labels to each point
    for idx, row in df.iterrows():
        ax.scatter(row['api_calls_per_question'], row['accuracy'],
                   s=300, color=colors[idx % len(colors)], edgecolors='black', linewidth=2, alpha=0.8)
        ax.annotate(row['strategy'],
                    (row['api_calls_per_question'], row['accuracy']),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=10, fontweight='bold')

    # Add reference lines and regions
    max_acc = df['accuracy'].max()
    min_cost = df['api_calls_per_question'].min()

    # Pareto frontier indication (top-right is better)
    ax.axhline(y=max_acc, color='gray', linestyle=':', alpha=0.5)
    ax.axvline(x=min_cost, color='gray', linestyle=':', alpha=0.5)

    # Beautify chart
    ax.set_xlabel('Average API Calls per Question (Cost Proxy)', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('Strategy Accuracy & Cost Efficiency', fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    return fig


def plot_strategy_radar(df, strategy_name):
    """Plot subject performance radar chart for a single strategy"""
    # Extract category data for this strategy
    strategy_row = df[df['strategy'] == strategy_name]
    if strategy_row.empty:
        print(f"⚠️ Strategy not found: {strategy_name}")
        return None

    cat_cols = [col for col in df.columns if col.startswith('cat_')]
    if not cat_cols:
        print("⚠️ No category data available for radar chart")
        return None

    categories = [col.replace('cat_', '') for col in cat_cols]
    values = [strategy_row[col].values[0] for col in cat_cols]

    # Radar chart needs to close the loop
    values += values[:1]
    categories += categories[:1]

    # Calculate angles
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=True)

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

    # Plot radar chart
    ax.plot(angles, values, 'o-', linewidth=2, color=colors[0], label=f'{strategy_name} (Accuracy)')
    ax.fill(angles, values, alpha=0.25, color=colors[0])

    # Add data point labels
    for angle, value, category in zip(angles[:-1], values[:-1], categories[:-1]):
        ax.text(angle, value + 0.05, f'{value:.2%}', ha='center', va='center', fontsize=9)

    # Set angles and labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories[:-1], fontsize=10)
    ax.set_ylim(0, max(values) * 1.2)

    # Add concentric grid and labels
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_yticklabels([])  # Hide radial tick labels

    ax.set_title(f'{strategy_name} Strategy - Subject Performance Radar', fontsize=14, fontweight='bold', pad=30)

    plt.tight_layout()
    return fig


# ==================== 4. Main Execution ====================
def main():
    print("📊 Starting Multi-Agent Debate System Evaluation Visualization")
    print("=" * 60)

    # Load data
    df = load_all_results(RESULT_FILES)
    if df is None:
        return

    print("\n✅ Data loaded successfully!")
    print("=" * 60)
    print("📈 Core metrics for each strategy:")
    print(df[['strategy', 'accuracy', 'total_questions', 'api_calls_per_question']].to_string(index=False))

    # Create output directory
    output_dir = Path("./visualizations")
    output_dir.mkdir(exist_ok=True)

    # Generate and save charts
    print("\n🎨 Generating charts...")

    # Chart 1: Accuracy Comparison
    fig1 = plot_accuracy_comparison(df)
    if fig1:
        fig1.savefig(output_dir / '1_accuracy_comparison.png', dpi=300, bbox_inches='tight')
        print("✅ Saved: 1_accuracy_comparison.png")

    # Chart 2: Subject Grouped Bar Chart (replaces heatmap)
    fig2 = plot_category_barchart(df)
    if fig2:
        fig2.savefig(output_dir / '2_category_barchart.png', dpi=300, bbox_inches='tight')
        print("✅ Saved: 2_category_barchart.png")

    # Chart 3: Accuracy vs Cost Scatter Plot
    fig3 = plot_accuracy_vs_cost(df)
    if fig3:
        fig3.savefig(output_dir / '3_accuracy_vs_cost.png', dpi=300, bbox_inches='tight')
        print("✅ Saved: 3_accuracy_vs_cost.png")

    # Chart 4: Radar chart for each strategy
    for strategy in df['strategy']:
        fig4 = plot_strategy_radar(df, strategy)
        if fig4:
            fig4.savefig(output_dir / f'4_radar_{strategy}.png', dpi=300, bbox_inches='tight')
            print(f"✅ Saved: 4_radar_{strategy}.png")

    print("\n" + "=" * 60)
    print(f"🎉 All charts generated and saved to: {output_dir.absolute()}/")
    print("=" * 60)

    # Display charts (if running in interactive environment)
    plt.show()


if __name__ == "__main__":
    main()