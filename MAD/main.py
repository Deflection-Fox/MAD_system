"""
Main Program - Select and run strategy with configuration from config.py
"""
from configs.config import *

"""
Main Program - Simplified version without command line arguments
All configuration is read from config.py
"""
import time
from datasets import load_dataset, load_from_disk
from evaluator import DebateEvaluator


def load_strategy(strategy_name, evaluator):
    """Load the selected strategy module."""
    if strategy_name == "single_agent":
        from single_agent import SingleAgentStrategy
        return SingleAgentStrategy(evaluator, use_direct_answer=True)
    elif strategy_name == "som":
        from som import SoMStrategy
        return SoMStrategy(evaluator)
    elif strategy_name == "angel_demon":
        from angel_demon import AngelDemonStrategy
        return AngelDemonStrategy(evaluator)
    elif strategy_name == "chateval":
        from chateval import ChatEvalStrategy
        return ChatEvalStrategy(evaluator)
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")


def main():
    # 直接从config.py读取配置
    strategy_name = DEFAULT_STRATEGY
    use_local = DATASET_CONFIG["use_local"]
    max_questions = DATASET_CONFIG["max_questions"]
    local_path = DATASET_CONFIG["local_path"]
    dataset_name = DATASET_CONFIG["dataset_name"]
    dataset_split = DATASET_CONFIG["dataset_split"]

    print("🤖 Multi-Agent Debate System Evaluation")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print(f"Strategy: {strategy_name}")
    print(f"Dataset source: {'local' if use_local else 'huggingface'}")
    print(f"Questions: {max_questions if max_questions else 'All'}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Request delay: {REQUEST_DELAY}s")

    # 1. Initialize Evaluator
    print("\n🔄 Initializing Evaluator...")
    evaluator = DebateEvaluator(API_KEY, BASE_URL, MODEL)

    # 2. Load Dataset
    print("\n📥 Loading dataset...")
    dataset = None

    try:
        if use_local:
            # 尝试从本地加载
            print(f"📂 Loading local dataset from: {local_path}")
            dataset = load_from_disk(local_path)
            print(f"✅ Loaded {len(dataset)} samples from local directory")
        else:
            # 从Hugging Face加载
            print(f"🌐 Loading dataset from Hugging Face: {dataset_name}")
            ds = load_dataset(dataset_name)

            if dataset_split not in ds:
                print(f"⚠️ Split '{dataset_split}' not found. Available: {list(ds.keys())}")
                # 使用第一个可用的分割
                dataset_split = list(ds.keys())[0]
                print(f"   Using '{dataset_split}' instead")

            dataset = ds[dataset_split]
            print(f"✅ Loaded {len(dataset)} samples from Hugging Face")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        print("   Please check your configuration in config.py")
        return

    # 3. 限制问题数量
    if max_questions and max_questions < len(dataset):
        dataset = dataset.select(range(max_questions))
        print(f"📝 Evaluating {len(dataset)} questions (limited by config)")

    # 4. 加载策略
    print(f"\n🔄 Loading {strategy_name} strategy...")
    try:
        strategy = load_strategy(strategy_name, evaluator)
    except NotImplementedError as e:
        print(f"❌ {e}")
        print(f"   Available strategies: {AVAILABLE_STRATEGIES}")
        print(f"   Please update DEFAULT_STRATEGY in config.py")
        return
    except Exception as e:
        print(f"❌ Error loading strategy: {e}")
        import traceback
        traceback.print_exc()
        return

    # 5. 准备评测配置
    eval_config = {
        'max_questions': max_questions,
        'request_delay': REQUEST_DELAY,
        'save_results': SAVE_RESULTS,
        'results_dir': RESULTS_DIR,
        'temperature': TEMPERATURE,
        'max_tokens': MAX_TOKENS
    }

    # 6. 运行评测
    try:
        print(f"\n{'=' * 60}")
        print(f"🚀 Starting Evaluation")
        print(f"{'=' * 60}")

        start_time = time.time()
        accuracy, results, logs = evaluator.evaluate_strategy(
            strategy=strategy,
            dataset=dataset,
            strategy_name=strategy_name,
            config=eval_config
        )
        total_time = time.time() - start_time

        # 最终总结
        print(f"\n{'=' * 60}")
        print(f"🎯 {strategy_name.replace('_', ' ').upper()} EVALUATION COMPLETE")
        print(f"{'=' * 60}")
        print(f"Final Accuracy: {accuracy:.2%}")
        print(f"Total Questions: {len(results)}")
        print(f"Total Time: {total_time:.1f}s")
        if results:
            print(f"Time per Question: {total_time / len(results):.1f}s")
        print(f"Total API Calls: {evaluator.api_call_count}")

        # 显示分类统计
        if results and len(results) > 0 and 'category' in results[0]:
            print(f"\n📚 Accuracy by Category:")
            print("-" * 40)

            # 按分类分组
            category_stats = {}
            for result in results:
                category = result.get('category', 'Unknown')
                if category not in category_stats:
                    category_stats[category] = {'total': 0, 'correct': 0}
                category_stats[category]['total'] += 1
                if result['is_correct']:
                    category_stats[category]['correct'] += 1

            # 按准确率排序
            if category_stats:
                sorted_categories = sorted(
                    category_stats.items(),
                    key=lambda x: x[1]['correct'] / x[1]['total'] if x[1]['total'] > 0 else 0,
                    reverse=True
                )

                for category, stats in sorted_categories:
                    cat_accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
                    print(f"  {category}: {stats['correct']}/{stats['total']} = {cat_accuracy:.2%}")

    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()