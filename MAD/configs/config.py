"""
Configuration for multi-agent evaluation
All configs in one place for easy adjustment
"""

# ==================== API & Model ====================
API_KEY = "Your Api Key Here"
BASE_URL = "https://api.apiyi.com/v1"
MODEL = "glm-4.5-flash"
# Dataset Configuration - Choose one option
DATASET_CONFIG = {
    # Option 1: Use local dataset (after running save_dataset.py)
    "use_local": True,  # Set to False to use Hugging Face directly
    "local_path": "./data/mmlu_pro_validation",  # Path saved by save_dataset.py

    # Option 2: Use Hugging Face directly
    "dataset_name": "TIGER-Lab/MMLU-Pro",
    "dataset_split": "validation",

    # Common settings
    "max_questions": None  # None for all questions
}

# Evaluation Configuration
REQUEST_DELAY = 0.5
TEMPERATURE = 0.3
MAX_TOKENS = 500  # 允许更长的推理过程
SAVE_RESULTS = True
RESULTS_DIR = "./logs"
# 是否在终端显示详细推理过程
DISPLAY_DETAILED_LOGS = True  # 设为 False 则只显示结果，不显示推理过程
# Strategy Selection
AVAILABLE_STRATEGIES = ["single_agent", "som", "chateval","angel_demon"]
DEFAULT_STRATEGY = "angel_demon"

# ==================== Strategy-specific Configs ====================
DIRECT_ANSWER_PROMPT = """You are an expert problem solver. Carefully read the following multiple-choice question and select the correct answer from options 0 to 9.

YOUR TASK:
- Determine the correct answer.
- Output **only** your final choice in the following format:
  FINAL_ANSWER: [X]
  (Replace [X] with a single digit: 0, 1, 2, 3, 4, 5, 6, 7, 8, or 9)

Do not provide any reasoning, analysis, or additional text. Only the final answer line is allowed.

Example of a valid response:
FINAL_ANSWER: 2
"""
# Single Agent
SINGLE_AGENT_SYSTEM_PROMPT = """You are an expert problem solver. For the following multiple-choice question, please think step by step.

REQUIREMENTS:
1. First, analyze the question carefully and reason through each option.
2. Explain your reasoning process in detail.
3. At the VERY END of your response, output your final answer in the format: 
   FINAL_ANSWER: [X] 
   where [X] is a single digit between 0 and 9.

Example:
... [your reasoning] ...
Therefore, the correct option is 3.
FINAL_ANSWER: 3"""

