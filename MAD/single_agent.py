"""
Single Agent Strategy Implementation
"""
from configs.config import DIRECT_ANSWER_PROMPT, SINGLE_AGENT_SYSTEM_PROMPT

class SingleAgentStrategy:
    """Single Agent Baseline Strategy."""

    def __init__(self, evaluator, use_direct_answer=True):
        self.evaluator = evaluator
        self.system_prompt = DIRECT_ANSWER_PROMPT if use_direct_answer else SINGLE_AGENT_SYSTEM_PROMPT

    def debate_and_decide(self, question_data):
        """Single agent answers directly, returns debate_log."""
        # Format the question
        question_text = self.evaluator.format_question(question_data)

        # Create messages
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"{question_text}\n\nYour answer (format: FINAL_ANSWER: [0-9]):"}
        ]

        # Get response
        response = self.evaluator.call_model(messages, temperature=0.1, max_tokens=50)

        if not response:
            return {'final_answer': None, 'debate_log': 'API call failed'}

        # Extract final answer
        final_answer = self.evaluator.extract_final_answer(response)

        # Return only final answer and debate log
        return {
            'final_answer': final_answer,
            'debate_log': response  # Single agent's response is the debate process
        }
