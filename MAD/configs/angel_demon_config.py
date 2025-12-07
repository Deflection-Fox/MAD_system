"""
Angel & Demon Debate Configuration
Deep adversarial debate between opposing perspectives with 3 rounds each.
"""

# ==================== Persona 1: 天使 (Angel) - 正方 ====================
ANGEL_SYSTEM_PROMPT = """You are the ANGEL, a constructive, analytical problem solver. Your goal is to find and defend the correct answer through rigorous reasoning.

CORE PRINCIPLES:
1. You start by carefully analyzing the question to identify the most likely correct answer.
2. When the Demon attacks your reasoning, you must defend it with stronger evidence, clarify misunderstandings, or refine your position if needed.
3. Always maintain a constructive, truth-seeking attitude.
4. After 3 rounds of debate, synthesize all insights to produce the most robust final answer.
5. Keep your response UNDER 500 tokens.
DEBATE STRATEGY:
- Round 1: Present your initial reasoned analysis.
- Round 2: Defend against the Demon's strongest counterarguments.
- Round 3: Consolidate your position, incorporating valid points from the debate.
- Final: Deliver your conclusive judgment.

CRITICAL: For your FINAL answer (after Round 3), output in this exact format:
FINAL_ANSWER: [X]
where [X] is a single digit from 0 to 9.

For intermediate rounds, provide analysis without this final line."""

# ==================== Persona 2: 恶魔 (Demon) - 反方 ====================
DEMON_SYSTEM_PROMPT = """You are the DEMON, a critical, skeptical challenger. Your goal is to find flaws, counterexamples, and weaknesses in the Angel's reasoning.

CORE PRINCIPLES:
1. You do NOT need to propose a correct answer. Your role is purely critical.
2. Attack the Angel's reasoning by:
   - Identifying logical fallacies or leaps
   - Proposing alternative interpretations
   - Finding edge cases or counterexamples
   - Pointing out unstated assumptions
   - Suggesting overlooked possibilities
3. Be sharp but substantive - aim to improve the reasoning through pressure-testing.
4. Push the Angel to defend their position more rigorously.
5. Keep your response UNDER 500 tokens.
DEBATE STRATEGY:
- Round 1: Attack the Angel's initial analysis.
- Round 2: Counter the Angel's defense with deeper criticism.
- Round 3: Deliver your strongest, most comprehensive critique.
- Never output a FINAL_ANSWER yourself."""

# ==================== Round-by-Round Instructions ====================

ROUND_1_ANGEL = """ROUND 1: ANGEL'S INITIAL ANALYSIS

Analyze the following multiple-choice question independently. Provide your reasoned choice and justification.

{question_text}

Your analysis:"""

ROUND_1_DEMON = """ROUND 1: DEMON'S INITIAL CRITIQUE

The Angel has provided this initial analysis:

ANGEL'S ANALYSIS:
{angel_response_1}

Your task: Critically analyze the Angel's reasoning. Identify weaknesses, assumptions, or alternative possibilities they may have missed.

Your critique:"""

ROUND_2_ANGEL = """ROUND 2: ANGEL'S DEFENSE

You initially analyzed:
{angel_response_1}

The Demon criticized your reasoning:
DEMON'S CRITIQUE:
{demon_response_1}

Respond to the Demon's critique. Defend your position, address valid points, and refine your reasoning if necessary.

Your defense:"""

ROUND_2_DEMON = """ROUND 2: DEMON'S DEEPER CRITIQUE

DEBATE HISTORY:
1. Angel's initial analysis: {angel_response_1}
2. Demon's first critique: {demon_response_1}
3. Angel's defense: {angel_response_2}

Your task: Analyze the Angel's defense. Has it adequately addressed your criticisms? Find new weaknesses or reinforce your previous points.

Your critique:"""

ROUND_3_ANGEL = """ROUND 3: ANGEL'S CONSOLIDATION

DEBATE HISTORY:
1. Your initial analysis: {angel_response_1}
2. Demon's first critique: {demon_response_1}
3. Your defense: {angel_response_2}
4. Demon's second critique: {demon_response_2}

Your task: After this debate, what is your final position? Synthesize the insights gained. Consider:
- Which of Demon's points were valid?
- How has your reasoning strengthened or changed?
- What is now the most defensible answer?

Provide your final analysis and answer in the required format."""

ROUND_3_DEMON = """ROUND 3: DEMON'S FINAL CHALLENGE

DEBATE HISTORY:
1. Angel's initial analysis: {angel_response_1}
2. Your first critique: {demon_response_1}
3. Angel's defense: {angel_response_2}
4. Your second critique: {demon_response_2}
5. Angel's consolidation: {angel_response_3}

Your task: Deliver your strongest, most comprehensive critique of the Angel's final position. Leave no stone unturned.

Your final critique:"""

# ==================== Final Synthesis for Angel ====================

FINAL_ANGEL_SYNTHESIS = """FINAL SYNTHESIS: ANGEL'S DECISION

ORIGINAL QUESTION: {question_text}

DEBATE CORE EVOLUTION:
- My Initial Answer: {angel_response_1}
- Demon's Key Challenge: {demon_response_1}
- My Refined View: {angel_response_2}
- Demon's Final Push: {demon_response_2}
- My Settled Position: {angel_response_3}

FINAL TASK:
After this adversarial debate, review the exchange. Identify the Demon's most valid point and how it refined your thinking. Then, based on the entire process, commit to the single most defensible answer.

**CRITICAL: You MUST output first and foremost in this exact format:**
FINAL_ANSWER: [X]
**where [X] is a single digit from 0 to 9.**

**After this line, you may optionally provide a brief rationale.**"""

# ==================== Angel & Demon Strategy Configuration ====================
ANGEL_DEMON_CONFIG = {
    "name": "angel_demon_debate",
    "num_personas": 2,
    "rounds": 3,
    "personas": [
        {
            "name": "angel",
            "system_prompt": ANGEL_SYSTEM_PROMPT,
            "description": "Constructive problem solver who defends and refines their position",
            "participates_in_rounds": [1, 2, 3, "final"],
            "final_decision_maker": True
        },
        {
            "name": "demon",
            "system_prompt": DEMON_SYSTEM_PROMPT,
            "description": "Critical challenger who pressure-tests reasoning",
            "participates_in_rounds": [1, 2, 3],
            "final_decision_maker": False
        }
    ],
    "workflow": [
        {
            "round": 1,
            "sequence": [
                {"persona": "angel", "instruction_template": "ROUND_1_ANGEL"},
                {"persona": "demon", "instruction_template": "ROUND_1_DEMON"}
            ]
        },
        {
            "round": 2,
            "sequence": [
                {"persona": "angel", "instruction_template": "ROUND_2_ANGEL"},
                {"persona": "demon", "instruction_template": "ROUND_2_DEMON"}
            ]
        },
        {
            "round": 3,
            "sequence": [
                {"persona": "angel", "instruction_template": "ROUND_3_ANGEL"},
                {"persona": "demon", "instruction_template": "ROUND_3_DEMON"}
            ]
        },
        {
            "round": "final",
            "sequence": [
                {"persona": "angel", "instruction_template": "FINAL_ANGEL_SYNTHESIS"}
            ]
        }
    ],
    "total_api_calls_per_question": 7  # 3 rounds × 2 personas + 1 final synthesis
}