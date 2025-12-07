"""
Angel & Demon Strategy Implementation
Deep adversarial debate with 3 rounds of back-and-forth argumentation
"""
from configs.config import TEMPERATURE, MAX_TOKENS


class AngelDemonStrategy:
    """Angel & Demon adversarial debate strategy with 3 rounds each."""

    def __init__(self, evaluator):
        self.evaluator = evaluator

    def _call_persona(self, system_prompt, user_content, persona_name, max_tokens=None):
        """Helper to call a persona with given prompt."""
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
        """Execute 3-round adversarial debate between Angel and Demon."""
        # Import prompts from config
        from configs.angel_demon_config import (
            ANGEL_SYSTEM_PROMPT,
            DEMON_SYSTEM_PROMPT,
            ROUND_1_ANGEL,
            ROUND_1_DEMON,
            ROUND_2_ANGEL,
            ROUND_2_DEMON,
            ROUND_3_ANGEL,
            ROUND_3_DEMON,
            FINAL_ANGEL_SYNTHESIS
        )

        # Format the original question
        question_text = self.evaluator.format_question(question_data)
        category = question_data.get('category', 'general')

        print(f"  🤔 Angel & Demon (3 rounds)...")

        # ===== ROUND 1 =====
        # Angel Round 1
        angel_round1_prompt = ROUND_1_ANGEL.format(question_text=question_text)
        angel_response_1 = self._call_persona(
            ANGEL_SYSTEM_PROMPT,
            angel_round1_prompt,
            "angel_round1"
        )
        if not angel_response_1:
            return {'final_answer': None, 'debate_log': 'Angel Round 1 failed'}

        # Demon Round 1
        demon_round1_prompt = ROUND_1_DEMON.format(
            question_text=question_text,
            angel_response_1=angel_response_1
        )
        demon_response_1 = self._call_persona(
            DEMON_SYSTEM_PROMPT,
            demon_round1_prompt,
            "demon_round1"
        )
        if not demon_response_1:
            return {'final_answer': None, 'debate_log': 'Demon Round 1 failed'}

        # ===== ROUND 2 =====
        # Angel Round 2
        angel_round2_prompt = ROUND_2_ANGEL.format(
            question_text=question_text,
            angel_response_1=angel_response_1,
            demon_response_1=demon_response_1
        )
        angel_response_2 = self._call_persona(
            ANGEL_SYSTEM_PROMPT,
            angel_round2_prompt,
            "angel_round2"
        )
        if not angel_response_2:
            return {'final_answer': None, 'debate_log': 'Angel Round 2 failed'}

        # Demon Round 2
        demon_round2_prompt = ROUND_2_DEMON.format(
            question_text=question_text,
            angel_response_1=angel_response_1,
            demon_response_1=demon_response_1,
            angel_response_2=angel_response_2
        )
        demon_response_2 = self._call_persona(
            DEMON_SYSTEM_PROMPT,
            demon_round2_prompt,
            "demon_round2"
        )
        if not demon_response_2:
            return {'final_answer': None, 'debate_log': 'Demon Round 2 failed'}

        # ===== ROUND 3 =====
        # Angel Round 3
        angel_round3_prompt = ROUND_3_ANGEL.format(
            question_text=question_text,
            angel_response_1=angel_response_1,
            demon_response_1=demon_response_1,
            angel_response_2=angel_response_2,
            demon_response_2=demon_response_2
        )
        angel_response_3 = self._call_persona(
            ANGEL_SYSTEM_PROMPT,
            angel_round3_prompt,
            "angel_round3"
        )
        if not angel_response_3:
            return {'final_answer': None, 'debate_log': 'Angel Round 3 failed'}

        # Demon Round 3
        demon_round3_prompt = ROUND_3_DEMON.format(
            question_text=question_text,
            angel_response_1=angel_response_1,
            demon_response_1=demon_response_1,
            angel_response_2=angel_response_2,
            demon_response_2=demon_response_2,
            angel_response_3=angel_response_3
        )
        demon_response_3 = self._call_persona(
            DEMON_SYSTEM_PROMPT,
            demon_round3_prompt,
            "demon_round3"
        )
        if not demon_response_3:
            return {'final_answer': None, 'debate_log': 'Demon Round 3 failed'}

        # ===== FINAL SYNTHESIS =====
        final_prompt = FINAL_ANGEL_SYNTHESIS.format(
            question_text=question_text,
            angel_response_1=angel_response_1,
            demon_response_1=demon_response_1,
            angel_response_2=angel_response_2,
            demon_response_2=demon_response_2,
            angel_response_3=angel_response_3,
            demon_response_3=demon_response_3
        )

        final_response = self._call_persona(
            ANGEL_SYSTEM_PROMPT,
            final_prompt,
            "angel_final",
            max_tokens=100
        )

        if not final_response:
            return {'final_answer': None, 'debate_log': 'Final synthesis failed'}

        # Extract final answer
        final_answer = self.evaluator.extract_final_answer(final_response)

        # Generate debate log
        debate_log = self._generate_debate_log(
            question_text=question_text,
            angel_response_1=angel_response_1,
            demon_response_1=demon_response_1,
            angel_response_2=angel_response_2,
            demon_response_2=demon_response_2,
            angel_response_3=angel_response_3,
            demon_response_3=demon_response_3,
            final_response=final_response
        )

        return {
            'final_answer': final_answer,
            'debate_log': debate_log
        }

    def _generate_debate_log(self, question_text, angel_response_1, demon_response_1,
                             angel_response_2, demon_response_2, angel_response_3,
                             demon_response_3, final_response):
        """Generate clean debate log in a structured format."""
        sections = []

        sections.append("ORIGINAL QUESTION:")
        sections.append(question_text)

        sections.append("\nROUND 1: INITIAL POSITIONS")
        sections.append("\nANGEL (Initial Analysis):")
        sections.append(angel_response_1)

        sections.append("\nDEMON (First Critique):")
        sections.append(demon_response_1)

        sections.append("\nROUND 2: DEFENSE & COUNTER")
        sections.append("\nANGEL (Defense):")
        sections.append(angel_response_2)

        sections.append("\nDEMON (Deeper Critique):")
        sections.append(demon_response_2)

        sections.append("\nROUND 3: FINAL ARGUMENTS")
        sections.append("\nANGEL (Consolidation):")
        sections.append(angel_response_3)

        sections.append("\nDEMON (Final Challenge):")
        sections.append(demon_response_3)

        sections.append("\nFINAL SYNTHESIS")
        sections.append("\nANGEL (Final Decision):")
        sections.append(final_response)

        return '\n'.join(sections)