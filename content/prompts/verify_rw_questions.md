# Prompt: Verify SAT Reading & Writing Question Correctness

You are VERIFYING the correctness of SAT Reading and Writing (RW) questions (a JSON array,
or one lesson's question file). Items conform to `content/schemas/question.schema.json`
and use `choices` + `correct_choice` (types `passage_reading`, `grammar_editing`,
`multiple_choice`). Your job is to confirm each item has exactly one defensible answer that
the provided text supports.

## Procedure, per question
1. Read the provided context first
   - For reading items, read `stimulus.text` (and `stimulus.text_b` for paired passages).
   - For grammar items, read the sentence/passage in `stimulus` or `prompt`.
   - Confirm the REQUIRED CONTEXT is present: if the prompt refers to a passage, a line, or
     a "best supported" claim, that text must be supplied. Flag any item that cannot be
     answered from the given material alone.
2. Determine the single defensible answer
   - For reading/inference/evidence: only ONE choice should be fully supported by the text;
     the rest must be unsupported, too broad, too narrow, or contradicted.
   - For grammar (`subject_verb_agreement`, `punctuation`, `pronouns`, `modifiers`,
     `sentence_boundaries`, `transitions`, `concision`): exactly one choice must be
     grammatically/stylistically correct in context; the others must contain a real error.
3. Confirm the key
   - The choice you selected must equal `correct_choice`. Flag mismatches.
4. Confirm the explanation supports the key
   - `explanation` must argue for the SAME choice as `correct_choice` and cite the text /
     rule. Flag explanations that justify a different choice or are generic.
5. Confirm rationales exist for ALL choices
   - Every choice has a non-empty `rationale`. The keyed choice's rationale says why it is
     right; each distractor's says why it is wrong. Flag a "Correct." rationale on a
     non-keyed choice, or missing rationales.
6. Check for multiple defensible answers
   - If two choices could both be defended (common in main_idea and inferences), flag it;
     the item must be tightened so only one is correct.

## OUTPUT REQUIREMENTS
- Report per `question_id`: PASS or FAIL, the choice you judged correct, and the stored key.
- For each FAIL, give the category (wrong_key, missing_context, explanation_mismatch,
  missing_rationale, multiple_defensible) and a one-line fix.
- Do not approve an item whose key you cannot defend from the supplied text.
- If asked to fix, output corrected objects conforming exactly to the schema.

## OUTPUT FORMAT (minimal report example)
```json
{
  "reviewed": 12,
  "passed": 11,
  "failed": 1,
  "results": [
    { "question_id": "sat-rw-command-of-evidence-1-q01", "status": "PASS", "judged": "A", "key": "A" },
    {
      "question_id": "sat-rw-main-idea-1-q05",
      "status": "FAIL",
      "judged": "C",
      "key": "B",
      "category": "multiple_defensible",
      "detail": "Both B and C summarize the passage; B is too narrow.",
      "suggested_fix": "Make B clearly partial so only C states the central idea."
    }
  ]
}
```
