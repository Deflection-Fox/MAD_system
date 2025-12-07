"""
Core Evaluator - Handles dataset, runs strategies, calculates accuracy
"""
import re
import time
import json
import datetime
from tqdm import tqdm
from openai import OpenAI

class DebateEvaluator:
    def __init__(self, api_key, base_url, model):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.api_call_count = 0

    def call_model(self, messages, temperature=0.1, max_tokens=500):
        """Make API call and return full response."""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                stream=False,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30
            )

            self.api_call_count += 1

            return completion.choices[0].message.content

        except Exception as e:
            print(f"  API Call Error: {e}")
            return None

    def extract_final_answer(self, response_text):
        """Extract the final answer from response text."""
        if not response_text:
            return None

        pattern = r'FINAL_ANSWER:\s*(\d)'
        match = re.search(pattern, response_text.strip(), re.IGNORECASE)

        if match:
            return int(match.group(1))

        digits = re.findall(r'\b(\d)\b', response_text.strip())
        if digits:
            return int(digits[-1])

        return None

    def format_question(self, question_data):
        """Format question data into a readable string."""
        question = question_data['question']
        options = question_data['options']

        formatted = f"QUESTION: {question}\n\nOPTIONS:\n"
        for i, option in enumerate(options):
            formatted += f"{i}. {option}\n"

        return formatted

    def evaluate_strategy(self, strategy, dataset, strategy_name, config):
        """Main evaluation loop for any strategy."""
        print(f"\n{'='*60}")
        print(f"🚀 Starting {strategy_name.replace('_', ' ').title()} Evaluation")
        print(f"{'='*60}")

        # Apply question limit
        max_q = config.get('max_questions')
        if max_q and max_q < len(dataset):
            dataset = dataset.select(range(max_q))

        total_questions = len(dataset)
        print(f"📊 Evaluating on {total_questions} questions")

        results = []
        debate_logs = []
        request_delay = config.get('request_delay', 0.5)

        # Main evaluation loop
        for idx, question_data in enumerate(tqdm(dataset, desc=f"Processing")):
            q_id = question_data.get('id', idx)
            category = question_data.get('category', 'Unknown')

            print(f"\n[Q{idx+1}/{total_questions}] {category}: ", end="")

            # Run strategy to get answer AND full debate log
            start_time = time.time()
            strategy_result = strategy.debate_and_decide(question_data)
            elapsed_time = time.time() - start_time

            # Extract results
            final_answer = strategy_result.get('final_answer')
            debate_process = strategy_result.get('debate_log', '')
            correct_answer = question_data.get('answer_index')

            # Check correctness
            is_correct = (final_answer is not None and
                         correct_answer is not None and
                         final_answer == correct_answer)

            # Record results
            results.append({
                'question_id': q_id,
                'category': category,
                'model_answer': final_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'response_time': round(elapsed_time, 2)
            })

            # Record debate process log
            debate_logs.append({
                'question_id': q_id,
                'category': category,
                'strategy': strategy_name,
                'final_answer': final_answer,
                'correct_answer': correct_answer,
                'debate_process': debate_process,
                'timestamp': datetime.datetime.now().isoformat()
            })

            # Print immediate result
            status = "✅" if is_correct else "❌"
            print(f"{status} Model: {final_answer}, Correct: {correct_answer}")

            # Delay to avoid rate limiting
            time.sleep(request_delay)

        # Calculate statistics
        correct_count = sum(1 for r in results if r['is_correct'])
        accuracy = correct_count / total_questions if total_questions > 0 else 0

        # Calculate category statistics
        category_stats = self._calculate_category_stats(results)

        # Print summary
        self._print_summary(strategy_name, correct_count, total_questions, accuracy, category_stats)

        # Save unified logs
        if config.get('save_results', True):
            self._save_unified_logs(
                strategy_name=strategy_name,
                accuracy=accuracy,
                total_questions=total_questions,
                results=results,
                debate_logs=debate_logs,
                category_stats=category_stats,
                config=config
            )

        return accuracy, results, debate_logs

    def _calculate_category_stats(self, results):
        """Calculate accuracy statistics for each category."""
        category_stats = {}

        for result in results:
            category = result['category']
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'correct': 0}

            category_stats[category]['total'] += 1
            if result['is_correct']:
                category_stats[category]['correct'] += 1

        # Calculate accuracy for each category
        for category, stats in category_stats.items():
            stats['accuracy'] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0

        return category_stats

    def _print_summary(self, strategy_name, correct, total, accuracy, category_stats):
        """Print evaluation summary with category statistics."""
        print(f"\n{'='*60}")
        print(f"📊 {strategy_name.replace('_', ' ').title()} Evaluation Complete!")
        print(f"{'='*60}")
        print(f"✅ Correct: {correct}/{total}")
        print(f"📈 Accuracy: {accuracy:.2%}")
        print(f"🔢 API Calls: {self.api_call_count}")

        # Print category statistics
        if category_stats:
            print(f"\n📚 Accuracy by Category:")
            print("-" * 40)
            for category, stats in sorted(category_stats.items()):
                print(f"  {category}: {stats['correct']}/{stats['total']} = {stats['accuracy']:.2%}")

    def _save_unified_logs(self, strategy_name, accuracy, total_questions, results,
                          debate_logs, category_stats, config):
        """Save unified format logs to JSON file."""
        import os
        results_dir = config.get('results_dir', 'logs')
        os.makedirs(results_dir, exist_ok=True)

        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{strategy_name}_logs_{timestamp}.json"
        filepath = os.path.join(results_dir, filename)

        # Prepare unified log structure
        unified_log = {
            "strategy": strategy_name,
            "accuracy": float(accuracy),
            "total_questions": total_questions,
            "api_calls": self.api_call_count,
            "timestamp": timestamp,
            "category_stats": category_stats,
            "logs": debate_logs
        }

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(unified_log, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Unified logs saved to: {filepath}")

        return filepath