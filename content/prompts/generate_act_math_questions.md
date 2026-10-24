# Prompt: Generate ACT Math Question Sets

Same rules as `generate_sat_math_questions.md`, with these ACT differences:

- `exam_id: "act"`, `exam_name: "ACT"`, `domain: "math"`.
- **Five choices `A`–`E`** (the schema allows up to six); the fifth distractor should be
  a plausible error, not filler. No grid-ins: `student_produced` is not used on the ACT.
- Sections/skills from `content/exams/act/skills.yaml`: Number & Quantity
  (`number_properties`, `exponents_radicals`, `complex_numbers`), Algebra
  (`linear_equations`, `linear_inequalities`, `systems_of_equations`, `word_problems`,
  `absolute_value`, `polynomials`), Functions (`functions`, `quadratics`, `exponential`,
  `sequences`, `logarithms`), Geometry (`area_volume`, `circles`, `right_triangles`,
  `trigonometry`, `angles_polygons`, `coordinate_geometry`), Statistics & Probability
  (`statistics`, `probability`, `data_analysis`, `two_way_tables`, `scatterplots`,
  `ratios_percentages_units`, `proportions`).
- Mix question forms within a lesson (solve, model, interpret, compare, multi-step word
  problems, table/figure reads) and tag each with `family:<form>`.
- Every item carries `answer_verification` with the recomputed key.
