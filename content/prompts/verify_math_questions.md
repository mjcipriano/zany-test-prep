# Prompt: Verify SAT Math Question Correctness

You are VERIFYING the mathematical correctness of SAT Math questions (a JSON array, or one
lesson's question file). Items conform to `content/schemas/question.schema.json`. Your job
is to independently recompute each answer and confirm the keyed data is right.

## Procedure, per question
1. Recompute from the `prompt` alone
   - Solve the problem yourself without looking at the choices or stored answer first.
   - Show the computation in your notes so the result is auditable.
2. Confirm the answer object / key matches your result
   - For `multiple_choice`, `data_interpretation`, `multi_step_math`: the choice whose
     `text` equals your computed value must be the one named in `correct_choice`, and its
     `rationale` should read as correct.
   - For `student_produced`: your computed value must appear in `answer.accepted` (as one
     of the accepted string forms) and match `answer.value` when present.
3. Confirm tolerance is appropriate
   - If the true answer is irrational or rounded, `answer.tolerance` must be present and
     large enough to accept correct rounding (e.g. `0.01`) but small enough to reject wrong
     answers. For exact integers/fractions, tolerance `0` or omitted is fine.
   - Check `answer.accepted` includes every legitimate equivalent form (e.g. `2.5` and
     `5/2`; `0.75` and `3/4`).
4. Confirm exactly one MC choice is correct
   - Exactly one choice equals the true value. Watch for distractors that are the same
     number written differently (e.g. `1/2` and `0.5`) — those create a second correct
     answer and must be flagged.
5. Confirm distractors are genuinely wrong
   - Each distractor must NOT equal the true value and should map to a plausible mistake
     (described in its `rationale`).
6. Confirm `answer_verification`
   - The `answer_verification` string should state the recomputed answer / check. If
     missing or inconsistent with your computation, flag it.

## OUTPUT REQUIREMENTS
- Report per `question_id`: PASS or FAIL, your computed answer, and the stored key.
- For each FAIL, give the category (wrong_key, missing_or_wrong_tolerance,
  multiple_correct, bad_distractor, missing_verification) and a one-line fix.
- Do not approve any item whose stored answer you cannot reproduce.
- If asked to fix, output corrected objects conforming exactly to the schema.

## OUTPUT FORMAT (minimal report example)
```json
{
  "reviewed": 20,
  "passed": 19,
  "failed": 1,
  "results": [
    { "question_id": "sat-math-area-volume-1-q01", "status": "PASS", "computed": "55/2", "key": "C=55/2" },
    {
      "question_id": "sat-math-linear-equations-1-q07",
      "status": "FAIL",
      "computed": "3",
      "key": "accepted=[\"3.0\"]",
      "category": "bad_distractor",
      "detail": "accepted should also include \"3\"; learner entry \"3\" would be marked wrong.",
      "suggested_fix": "Set accepted to [\"3\"] or [\"3\", \"3.0\"]."
    }
  ]
}
```
