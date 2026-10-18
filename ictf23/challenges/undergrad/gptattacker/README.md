# GPT Attacker

**Category:** LLM / Prompt Injection

## Description

Is GPT reliable to do homework for us? Participants are given middle school
algebra problems and must write a `prompt_engineering(question)` function in `task.py`
that manipulates GPT inputs to:

1. **Task 1:** Improve GPT's accuracy on the problems (acc1 > 0.5)
2. **Task 2:** Degrade GPT's accuracy on the same problem set (acc2 < 0.1)

The flag is awarded when both conditions are met simultaneously.

## Source

Source files are in `src/`. The evaluation harness is `src/evaluation.py`.
