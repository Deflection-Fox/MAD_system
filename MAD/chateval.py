"""
ChatEval Strategy Implementation
Three consistent judges with independent analysis, exchange opinions, and moderator synthesis.
"""
from configs.config import TEMPERATURE, MAX_TOKENS


class ChatEvalStrategy:
    """ChatEval strategy with 3 judges, 2 rounds of evaluation, and moderator synthesis."""

    def __init__(self, evaluator):
        self.evaluator = evaluator

    def _call_judge(self, system_prompt, user_content, judge_name, max_tokens=None):
        """Helper to call a judge with given prompt."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        if max_tokens is None:
            max_tokens = MAX_TOKENS

        return self.evaluator.call_model(
            messages,
            temperature=TEMPERATURE,
            max_tokens=max_tokens
        )

    def debate_and_decide(self, question_data):
        """Execute ChatEval 2-round evaluation with 3 judges and moderator."""
        # Import prompts from config
        from configs.chateval_config import (
            JUDGE_SYSTEM_PROMPT,
            MODERATOR_SYSTEM_PROMPT,
            ROUND_1_JUDGE_TEMPLATE,
            ROUND_2_JUDGE_TEMPLATE,
            MODERATOR_TEMPLATE
        )

        # Format the original question
        question_text = self.evaluator.format_question(question_data)

        print(f"  ⚖️ ChatEval (3 judges, 2 rounds)...")

        # ===== ROUND 1: Independent Evaluation =====
        print(f"    Round 1: Independent evaluation...")

        # Judge 1 Round 1
        judge1_round1_prompt = ROUND_1_JUDGE_TEMPLATE.format(question_text=question_text)
        judge1_response_1 = self._call_judge(
            JUDGE_SYSTEM_PROMPT,
            judge1_round1_prompt,
            "judge1_round1"
        )
        if not judge1_response_1:
            return {'final_answer': None, 'debate_log': 'Judge 1 Round 1 failed'}

        # Judge 2 Round 1
        judge2_round1_prompt = ROUND_1_JUDGE_TEMPLATE.format(question_text=question_text)
        judge2_response_1 = self._call_judge(
            JUDGE_SYSTEM_PROMPT,
            judge2_round1_prompt,
            "judge2_round1"
        )
        if not judge2_response_1:
            return {'final_answer': None, 'debate_log': 'Judge 2 Round 1 failed'}

        # Judge 3 Round 1
        judge3_round1_prompt = ROUND_1_JUDGE_TEMPLATE.format(question_text=question_text)
        judge3_response_1 = self._call_judge(
            JUDGE_SYSTEM_PROMPT,
            judge3_round1_prompt,
            "judge3_round1"
        )
        if not judge3_response_1:
            return {'final_answer': None, 'debate_log': 'Judge 3 Round 1 failed'}

        # ===== ROUND 2: Re-evaluation After Exchange =====
        print(f"    Round 2: Re-evaluation after exchange...")

        # Judge 1 Round 2 (sees judge2 and judge3's round 1 responses)
        judge1_round2_prompt = ROUND_2_JUDGE_TEMPLATE.format(
            question_text=question_text,
            my_round1_response=judge1_response_1,
            judge2_round1_response=judge2_response_1,
            judge3_round1_response=judge3_response_1
        )
        judge1_response_2 = self._call_judge(
            JUDGE_SYSTEM_PROMPT,
            judge1_round2_prompt,
            "judge1_round2"
        )
        if not judge1_response_2:
            return {'final_answer': None, 'debate_log': 'Judge 1 Round 2 failed'}

        # Judge 2 Round 2 (sees judge1 and judge3's round 1 responses)
        judge2_round2_prompt = ROUND_2_JUDGE_TEMPLATE.format(
            question_text=question_text,
            my_round1_response=judge2_response_1,
            judge2_round1_response=judge1_response_1,  # Note: this is judge1's response
            judge3_round1_response=judge3_response_1
        )
        judge2_response_2 = self._call_judge(
            JUDGE_SYSTEM_PROMPT,
            judge2_round2_prompt,
            "judge2_round2"
        )
        if not judge2_response_2:
            return {'final_answer': None, 'debate_log': 'Judge 2 Round 2 failed'}

        # Judge 3 Round 2 (sees judge1 and judge2's round 1 responses)
        judge3_round2_prompt = ROUND_2_JUDGE_TEMPLATE.format(
            question_text=question_text,
            my_round1_response=judge3_response_1,
            judge2_round1_response=judge1_response_1,  # Note: this is judge1's response
            judge3_round1_response=judge2_response_1  # Note: this is judge2's response
        )
        judge3_response_2 = self._call_judge(
            JUDGE_SYSTEM_PROMPT,
            judge3_round2_prompt,
            "judge3_round2"
        )
        if not judge3_response_2:
            return {'final_answer': None, 'debate_log': 'Judge 3 Round 2 failed'}

        # ===== FINAL: Moderator Synthesis =====
        print(f"    Final: Moderator synthesis...")

        moderator_prompt = MODERATOR_TEMPLATE.format(
            question_text=question_text,
            judge1_round1_response=judge1_response_1,
            judge2_round1_response=judge2_response_1,
            judge3_round1_response=judge3_response_1,
            judge1_round2_response=judge1_response_2,
            judge2_round2_response=judge2_response_2,
            judge3_round2_response=judge3_response_2
        )

        final_response = self._call_judge(
            MODERATOR_SYSTEM_PROMPT,
            moderator_prompt,
            "moderator_final",
            max_tokens=200
        )

        if not final_response:
            return {'final_answer': None, 'debate_log': 'Moderator synthesis failed'}

        # Extract final answer
        final_answer = self.evaluator.extract_final_answer(final_response)

        # Generate debate log
        debate_log = self._generate_debate_log(
            question_text=question_text,
            judge1_round1_response=judge1_response_1,
            judge2_round1_response=judge2_response_1,
            judge3_round1_response=judge3_response_1,
            judge1_round2_response=judge1_response_2,
            judge2_round2_response=judge2_response_2,
            judge3_round2_response=judge3_response_2,
            final_response=final_response
        )

        return {
            'final_answer': final_answer,
            'debate_log': debate_log
        }

    def _generate_debate_log(self, question_text,
                             judge1_round1_response, judge2_round1_response, judge3_round1_response,
                             judge1_round2_response, judge2_round2_response, judge3_round2_response,
                             final_response):
        """Generate clean debate log in a structured format."""
        sections = []

        sections.append("ORIGINAL QUESTION:")
        sections.append(question_text)

        sections.append("\nROUND 1: INDEPENDENT EVALUATIONS")
        sections.append("\nJUDGE 1 (Initial):")
        sections.append(judge1_round1_response)

        sections.append("\nJUDGE 2 (Initial):")
        sections.append(judge2_round1_response)

        sections.append("\nJUDGE 3 (Initial):")
        sections.append(judge3_round1_response)

        sections.append("\nROUND 2: RE-EVALUATION AFTER EXCHANGE")
        sections.append("\nJUDGE 1 (Revised):")
        sections.append(judge1_round2_response)

        sections.append("\nJUDGE 2 (Revised):")
        sections.append(judge2_round2_response)

        sections.append("\nJUDGE 3 (Revised):")
        sections.append(judge3_round2_response)

        sections.append("\nFINAL SYNTHESIS")
        sections.append("\nMODERATOR (Final Decision):")
        sections.append(final_response)

        return '\n'.join(sections)