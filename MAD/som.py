"""
SoM (Society of Minds) Strategy Implementation
"""
from configs.config import TEMPERATURE, MAX_TOKENS

class SoMStrategy:
    """Society of Minds Strategy with 5 specialized agents."""

    def __init__(self, evaluator):
        self.evaluator = evaluator

    def _call_agent(self, agent_name, system_prompt, user_content):
        """Helper function to call a single agent."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        max_tokens = 50 if agent_name == "integrator" else MAX_TOKENS
        return self.evaluator.call_model(messages, temperature=TEMPERATURE, max_tokens=max_tokens)

    def debate_and_decide(self, question_data):
        """SoM sequential workflow, returns debate_log."""
        # Import prompts
        from configs.som_config import (
            DECOMPOSER_SYSTEM_PROMPT,
            EXPERT_SYSTEM_PROMPT,
            REASONER_SYSTEM_PROMPT,
            CRITIC_SYSTEM_PROMPT,
            INTEGRATOR_SYSTEM_PROMPT
        )

        # Format the original question
        question_text = self.evaluator.format_question(question_data)

        # 1. Decomposer
        decomp_response = self._call_agent(
            "decomposer", DECOMPOSER_SYSTEM_PROMPT, question_text
        )
        if not decomp_response:
            return {'final_answer': None, 'debate_log': 'Decomposer failed'}

        # 2. Expert
        expert_response = self._call_agent(
            "expert", EXPERT_SYSTEM_PROMPT, f"{question_text}\n\n{decomp_response}"
        )
        if not expert_response:
            return {'final_answer': None, 'debate_log': 'Expert failed'}

        # 3. Reasoner
        reasoner_response = self._call_agent(
            "reasoner", REASONER_SYSTEM_PROMPT, f"{question_text}\n\n{decomp_response}\n\n{expert_response}"
        )
        if not reasoner_response:
            return {'final_answer': None, 'debate_log': 'Reasoner failed'}

        # 4. Critic
        critic_response = self._call_agent(
            "critic", CRITIC_SYSTEM_PROMPT, f"{question_text}\n\n{decomp_response}\n\n{expert_response}\n\n{reasoner_response}"
        )
        if not critic_response:
            return {'final_answer': None, 'debate_log': 'Critic failed'}

        # 5. Integrator
        final_context = f"{question_text}\n\n{decomp_response}\n\n{expert_response}\n\n{reasoner_response}\n\n{critic_response}"
        integrator_response = self._call_agent(
            "integrator", INTEGRATOR_SYSTEM_PROMPT, final_context
        )
        if not integrator_response:
            return {'final_answer': None, 'debate_log': 'Integrator failed'}

        # Extract final answer
        final_answer = self.evaluator.extract_final_answer(integrator_response)

        # Generate clean debate process (no extra formatting)
        debate_log = self._generate_debate_log(
            question_text, decomp_response, expert_response,
            reasoner_response, critic_response, integrator_response
        )

        return {
            'final_answer': final_answer,
            'debate_log': debate_log
        }

    def _generate_debate_log(self, question, decomp, expert, reason, critic, final):
        """Generate clean debate log without extra formatting."""
        sections = [
            f"QUESTION:\n{question}",
            f"\nDECOMPOSER:\n{decomp}",
            f"\nEXPERT:\n{expert}",
            f"\nREASONER:\n{reason}",
            f"\nCRITIC:\n{critic}",
            f"\nINTEGRATOR:\n{final}"
        ]
        return '\n'.join(sections)