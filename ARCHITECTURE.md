"""
Technical architecture and design decisions for the Email Assistant OpenEnv.
"""

# ARCHITECTURE & DESIGN DECISIONS
# ================================

## 1. PYDANTIC MODELS FOR TYPE SAFETY

Why Pydantic?
- Runtime validation of all data
- Automatic JSON serialization
- IDE type hints and autocomplete
- Clear data contracts

Email Model:
  - Immutable email data with true labels
  - true_label = Optional[dict] for flexibility

Observation Model:
  - What agent sees each step
  - Includes email, step_count, task
  - Type-safe for training loops

Action Models (Task-specific):
  - SpamClassificationAction: is_spam: bool
  - PriorityAction: priority: str
  - ReplyAction: reply_text: str, should_reply: bool


## 2. MEANINGFUL REWARD FUNCTIONS

Challenge: RL agents learn from reward signal
- Binary rewards (0/1) are too coarse
- Agents need fine-grained feedback

Solution: Graduated reward functions

EASY (Spam):
  - Still binary but clear ground truth
  - 1.0 = correct, 0.0 = wrong
  - Good for baseline agents

MEDIUM (Priority):
  - 4 levels: low, medium, high, urgent
  - Distance-based penalty:
    * Exact match: 1.0
    * Off by 1: 0.5 (50% reduced)
    * Off by 2: 0.25 (75% reduced)
    * Off by 3: 0.0 (total miss)
  - Encourages "getting close"

HARD (Reply):
  - Multi-aspect scoring:
    1. Decision quality (0.7 weight)
       - Correctly decide if reply needed
    2. Content quality (0.3 weight)
       - String similarity to ground truth
  - Base reward: 0.7 for correct decision
  - Additional: 0.0-0.3 for content match
  - Total range: 0.0-1.0


## 3. MODULAR ARCHITECTURE

env/models.py:
  - Data structures
  - No business logic
  - Completely reusable

env/graders.py:
  - Reward calculation
  - Independent from environment
  - Testable in isolation

env/environment.py:
  - Orchestrates components
  - Enforces RL interface
  - Handles episode state

Benefit: Easy to:
  - Test each component independently
  - Change reward functions without modifying env
  - Add new models without touching core logic


## 4. STATE MANAGEMENT

Episode State:
  - current_email_idx: which email
  - step_count: how many steps taken
  - episode_rewards: list of all rewards

Why separate step_count and email_idx?
  - step_count limits episode length
  - email_idx limits available emails
  - Either can trigger done=True

state() returns:
  - Snapshot of current episode
  - Aggregated stats (avg, total reward)
  - Useful for monitoring


## 5. SEED SUPPORT (DETERMINISM)

Why seeds matter:
  - Reproducible experiments
  - Consistent baselines
  - Fair comparison between agents

Implementation:
  - Optional seed parameter
  - If seed set: shuffle deterministically
  - If seed None: random shuffle each episode

Use case:
  - seed=42 for baseline experiments
  - No seed for training (variety)


## 6. ERROR HANDLING

What goes wrong?
  - Missing email data file
  - Invalid JSON format
  - Invalid task name
  - Calling step() after done

Handling:
  - Load errors are caught with clear messages
  - Invalid task throws ValueError with valid options
  - step() after done throws RuntimeError
  - Invalid actions don't crash, just low reward


## 7. DATA LOADING STRATEGY

Why load from JSON?
  - Human-readable format
  - Easy to extend dataset
  - Ground truth labels included
  - No external dependencies

JSON structure:
  - Array of email objects
  - Each email has true_label dict
  - Label structure mirrors tasks

Future expansion:
  - Replace emails.json with more data
  - Add more complex email scenarios
  - Scale to thousands of examples


## 8. DESIGN TRADE-OFFS

Choice: Dict-based actions (not typed action objects)
  - PROs: Flexible, doesn't require task knowledge to call
  - CONs: Less type safety at runtime
  - Decision: Flexibility more important for agents

Choice: Return StepInfo (not separate reward/done/obs)
  - PROs: Follows gym convention, extra metadata
  - CONs: More objects to unpack
  - Decision: Standard interface trumps simplicity

Choice: Graders are static classes
  - PROs: Pure functions, testable, no state
  - CONs: Not OOP-style
  - Decision: Functional approach cleaner for math


## 9. EXTENSIBILITY POINTS

Easy to add without changing core:

1. New tasks:
   - Add TaskType to models
   - Add Grader class
   - Add to TaskGrader.grade()

2. New reward functions:
   - Create new Grader class
   - Register in TaskGrader

3. New emails:
   - Add to data/emails.json
   - Automatic loading

4. Custom agents:
   - Import EmailEnv
   - Loop: reset → step → step → step


## 10. TESTING STRATEGY

What to test?
  - Initialization validation
  - Interface compliance (reset, step, state)
  - Reward calculations
  - Edge cases (empty reply, all levels)
  - Episode termination
  - State tracking

Coverage:
  - 30+ tests across 2 test files
  - 100% of public API
  - All reward functions
  - All edge cases


## PERFORMANCE CHARACTERISTICS

- Episode length: O(max_steps)
- Memory: O(num_emails) for storage
- Reward calculation: O(1) for easy/medium, O(n) for hard (string similarity)
- Step() time: ~1ms (dominated by JSON parse and Pydantic validation)

Scalability:
  - Handles 1000s of emails easily
  - String similarity might be slow with very long replies
  - Could cache similarity calculations


## PRODUCTION-READINESS CHECKLIST

✅ Type safety (Pydantic)
✅ Error handling
✅ Documentation (docstrings + README)
✅ Testing (30+ tests)
✅ Modularity (models, graders, env separate)
✅ Reproducibility (seed support)
✅ Clear API (reset, step, state)
✅ Meaningful rewards
✅ Examples and usage guide
✅ No external API calls
✅ No random dependencies
✅ Clean code style
✅ No hardcoded paths (uses Path objects)
✅ Validation of inputs
✅ Consistent error messages
"""
