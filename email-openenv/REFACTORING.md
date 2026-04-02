"""
REFACTORING SUMMARY: Externalized Grading Logic
================================================

This document describes the refactoring done to move grading logic from the
environment to external, task-specific grader modules.


BEFORE: Monolithic Grading
==========================

Structure:
  env/
    └── graders.py (160 lines)
        ├── SpamClassificationGrader (class with static method)
        ├── PriorityGrader (class with static method)
        ├── ReplyGrader (class with static method)
        └── TaskGrader (router class)

  env/environment.py
    ├── imports TaskGrader from env/graders.py
    ├── step() calls self._grade_action()
    └── _grade_action() calls TaskGrader.grade()

Problems:
  ✗ Grading logic mixed with environment logic
  ✗ TaskGrader acts as indirection layer
  ✗ Hard to extend with new graders
  ✗ Tests import from env.graders


AFTER: Modular External Graders
================================

Structure:
  graders/
    ├── __init__.py (imports submodules)
    ├── easy_grader.py (24 lines)
    │   └── grade(prediction, ground_truth) -> float
    ├── medium_grader.py (35 lines)
    │   └── grade(prediction, ground_truth) -> float
    └── hard_grader.py (57 lines)
        └── grade(reply, should_reply, ground_truth_reply, reply_required) -> float

  env/environment.py
    ├── imports specific graders from graders/
    ├── step() calls self._calculate_reward()
    └── _calculate_reward() calls task-specific grader.grade()

Benefits:
  ✓ Clear separation: environment vs grading
  ✓ Direct function calls (no class indirection)
  ✓ Easy to add new graders (create module, import, use)
  ✓ Tests import from graders/ directly
  ✓ Graders are stateless functions


CODE CHANGES
============

1. New Grader Modules
   - graders/easy_grader.py: def grade(prediction, ground_truth) -> float
   - graders/medium_grader.py: def grade(prediction, ground_truth) -> float
   - graders/hard_grader.py: def grade(reply, should_reply, ground_truth_reply, reply_required) -> float

2. Updated env/environment.py
   - Line 15: from graders import easy_grader, medium_grader, hard_grader
   - Line 122: call self._calculate_reward() instead of self._grade_action()
   - Lines 182-214: NEW method _calculate_reward() with direct grader calls
   - Removed: _grade_action() method (lines 182-200)
   - Removed: import of TaskGrader from env/graders.py

3. Updated env/__init__.py
   - Removed: import of graders classes (TaskGrader, etc.)
   - Removed: export of grader classes from __all__

4. Updated tests/test_graders.py
   - Line 8: from graders import easy_grader, medium_grader, hard_grader
   - All tests now call grader.grade() directly (e.g., easy_grader.grade())


COMPARISON OF APPROACH

Old Approach (Class-based):
  ┌─────────────────────────────────────┐
  │ environment.py                      │
  │  self._grade_action()               │
  └──────────────┬──────────────────────┘
                 │
                 ▼
  ┌─────────────────────────────────────┐
  │ env/graders.py                      │
  │  TaskGrader.grade(task, action,...) │
  │    ↓                                 │
  │  if task == "easy":                 │
  │    SpamClassificationGrader.grade() │
  │  elif task == "medium": ...         │
  └─────────────────────────────────────┘

New Approach (Function-based):
  ┌─────────────────────────────────────┐
  │ environment.py                      │
  │  self._calculate_reward()           │
  │    ↓                                 │
  │  if self.task == "easy":            │
  │    easy_grader.grade(...)           │
  │  elif self.task == "medium": ...    │
  └──────────────┬──────────────────────┘
                 │ imports
     ┌───────────┼───────────┐
     ▼           ▼           ▼
  graders/easy  graders/medium  graders/hard


INTERFACE REMAINS UNCHANGED

For users:
  from env import EmailEnv
  env = EmailEnv(task="easy")
  obs = env.reset()
  obs, reward, done, info = env.step({"is_spam": False})

Everything works exactly the same. Internal refactoring only.


EXTENSION PATTERN

To add a new task (e.g., "multi-label classification"):

1. Create graders/new_grader.py:
   def grade(predictions, ground_truth) -> float:
       ...

2. Update env/environment.py:
   from graders import ... new_grader

   Add to _calculate_reward():
   elif self.task == "new_task":
       return new_grader.grade(...)

3. Update env/models.py:
   class NewTaskAction(BaseModel):
       ...

4. Add test in tests/test_graders.py:
   from graders import new_grader
   ...


MAINTAINABILITY IMPROVEMENTS

✓ Single Responsibility Principle
  - Each grader is responsible for ONE task's reward logic
  - Environment is responsible for orchestration

✓ Open/Closed Principle
  - Open for extension (add new graders)
  - Closed for modification (don't touch other graders)

✓ Testability
  - Graders are pure functions (no state)
  - Easy to test in isolation
  - Tests directly import from graders/

✓ Code Organization
  - graders/ = reward functions
  - env/models.py = data structures
  - env/environment.py = orchestration
  - tests/ = verification


MIGRATION PATH

If you have custom code using env.graders:

Old:
  from env.graders import SpamClassificationGrader
  reward = SpamClassificationGrader.grade(pred, truth)

New:
  from graders import easy_grader
  reward = easy_grader.grade(pred, truth)

Or if you need all graders:
  from graders import easy_grader, medium_grader, hard_grader
"""
