"""Answer-key audit tools for the generated question bank.

* :mod:`audit.expr` - a tiny exact-arithmetic expression/polynomial engine
  (no third-party dependencies) used to re-solve math stems.
* :mod:`audit.automated_checks` - deterministic checks over every question in
  the shipped bundles (structure, rationales, arithmetic, independent re-solve).
* :mod:`audit.export_sample` - a stratified, answer-free sample for
  human-style solving by other agents, plus its answer key.
* :mod:`audit.compare` - grade solver output against the key and report
  disagreements by family.
"""
