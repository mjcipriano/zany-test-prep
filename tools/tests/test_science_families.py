"""Tests for the ACT Science generators (tools/content_gen/science_gen.py) and
their teaching cards (tools/content_gen/teaching_science.py).

Run from the repo root:  python3 -m unittest discover -s tools/tests -t .
"""
import json
import random
import re
import unittest

from tools.tests import helpers  # noqa: F401  (sets sys.path)
from jsonschema import Draft7Validator

from content_gen import registry, science_gen as sg
from content_gen.teaching_science import TEACHING_SCIENCE
from content_gen.util import item_signature

DIFFS = registry.DIFFICULTIES
MIN_FAMILIES = {"data_representation": 4, "trends_extrapolation": 3,
                "experimental_design": 3, "conflicting_viewpoints": 3}
_LESSON_SCHEMA = json.loads(
    (helpers.ROOT / "content" / "schemas" / "lesson.schema.json").read_text())
_LESSON_VALIDATOR = Draft7Validator(_LESSON_SCHEMA)


def _all_families():
    for skill, by_diff in sg.FAMILIES.items():
        for diff in DIFFS:
            for fn in by_diff[diff]:
                yield skill, diff, fn


def _spec(body):
    v = body.get("answer_verification") or ""
    if not v.startswith("science:"):
        return None
    kind, *rest = v[len("science:"):].split(";")
    kw = dict(part.split("=", 1) for part in rest)
    return kind, kw


def _table(body):
    """(xs, cols, labels, decimals) from a table stimulus, or from the inline
    'Results: at X, Y; ...' lines of a research-summary passage."""
    stim = body["stimulus"]
    if stim["type"] == "table":
        t = stim["table"]
        xs = [r[0] for r in t["rows"]]
        strs = [[r[c] for r in t["rows"]] for c in range(1, len(t["headers"]))]
        labels = [h.split(", ", 1)[1] if ", " in h else "" for h in t["headers"][1:]]
    else:
        lines = [ln for ln in stim["text"].split("\n") if ln.startswith("Results")]
        strs, xs = [], None
        for ln in lines:
            pairs = re.findall(r"at (?:pH )?(\d+(?:\.\d+)?)[^,]*, (-?\d+(?:\.\d+)?)", ln)
            xs = [x for x, _ in pairs]
            strs.append([y for _, y in pairs])
        labels = [""] * len(strs)
    cols = [[float(v) for v in col] for col in strs]
    decs = [max(len(v.split(".")[1]) if "." in v else 0 for v in col) for col in strs]
    return xs, cols, labels, decs


def _correct(body):
    """Keyed choice text, with the 'pH ' value prefix dropped so x values compare as numbers."""
    text = next(c["text"] for c in body["choices"] if c["id"] == body["correct_choice"])
    return text.replace("pH ", "")


def _num(text):
    m = re.search(r"-?\d+(?:\.\d+)?", text.replace("−", "-"))
    return float(m.group()) if m else None


def _direction(vals):
    if all(b > a for a, b in zip(vals, vals[1:])):
        return "inc"
    if all(b < a for a, b in zip(vals, vals[1:])):
        return "dec"
    i = max(range(len(vals)), key=lambda j: vals[j])
    if 0 < i < len(vals) - 1 and all(b > a for a, b in zip(vals[:i], vals[1:i + 1])) \
            and all(b < a for a, b in zip(vals[i:], vals[i + 1:])):
        return "peak"
    return "other"


class ScienceFamilyTableTests(unittest.TestCase):
    def test_every_family_is_schema_valid_on_all_difficulties(self):
        helpers.check_family_table(self, sg.FAMILIES, samples=25, min_families=3)

    def test_minimum_family_counts(self):
        for skill, need in MIN_FAMILIES.items():
            for diff in DIFFS:
                fns = sg.FAMILIES[skill][diff]
                self.assertGreaterEqual(len(fns), need, f"{skill}/{diff}")
                names = [registry.family_name(fn) for fn in fns]
                self.assertEqual(len(names), len(set(names)), f"{skill}/{diff}: duplicate family")

    def test_subskills_are_declared(self):
        self.assertEqual(set(sg.SUBSKILLS), set(sg.FAMILIES))
        for skill, diff, fn in _all_families():
            for b in helpers.sample_family(fn, diff, 12, seed=5):
                self.assertIn(b["subskill"], sg.SUBSKILLS[skill],
                              f"{registry.family_name(fn)} emits undeclared subskill {b['subskill']}")

    def test_four_choices_and_question_types(self):
        want = {"table": "data_interpretation", "passage": "passage_reading",
                "paired_passages": "passage_reading", "figure": "multiple_choice"}
        for skill, diff, fn in _all_families():
            for b in helpers.sample_family(fn, diff, 12, seed=7):
                self.assertEqual(len(b["choices"]), 4, registry.family_name(fn))
                stim = b.get("stimulus")
                self.assertIsNotNone(stim, f"{registry.family_name(fn)} has no stimulus")
                self.assertEqual(b["question_type"], want[stim["type"]], registry.family_name(fn))
                if skill == "conflicting_viewpoints":
                    self.assertEqual(stim["type"], "paired_passages")

    def test_distinctness(self):
        for skill, diff, fn in _all_families():
            bodies = helpers.sample_family(fn, diff, 120, seed=11)
            n = len({item_signature(b) for b in bodies})
            need = 8 if getattr(fn, "small_space", False) else 30
            self.assertGreaterEqual(n, need, f"{skill}/{diff}/{registry.family_name(fn)}: {n} distinct")

    def test_correct_answer_is_not_systematically_longest(self):
        for skill, diff, fn in _all_families():
            bodies = helpers.sample_family(fn, diff, 120, seed=13)
            longest = sum(
                1 for b in bodies
                if max(b["choices"], key=lambda c: len(c["text"]))["id"] == b["correct_choice"])
            self.assertLess(longest / len(bodies), 0.7,
                            f"{skill}/{diff}/{registry.family_name(fn)}: longest-correct {longest}/120")

    def test_correct_position_varies(self):
        for skill, diff, fn in _all_families():
            bodies = helpers.sample_family(fn, diff, 60, seed=17)
            self.assertGreaterEqual(len({b["correct_choice"] for b in bodies}), 3,
                                    registry.family_name(fn))

    def test_prompt_phrasing_varies(self):
        for skill, diff, fn in _all_families():
            bodies = helpers.sample_family(fn, diff, 60, seed=19)
            self.assertGreaterEqual(len({helpers.shape(b["prompt"]) for b in bodies}), 2,
                                    f"{registry.family_name(fn)} uses one prompt shape")

    def test_determinism(self):
        for skill, diff, fn in _all_families():
            a = helpers.sample_family(fn, diff, 5, seed=23)
            b = helpers.sample_family(fn, diff, 5, seed=23)
            self.assertEqual(a, b, registry.family_name(fn))


class ScenarioLibraryTests(unittest.TestCase):
    def test_library_size_and_shapes(self):
        self.assertGreaterEqual(len(sg.SCENARIOS), 15)
        rng = random.Random(3)
        for scen in sg.SCENARIOS:
            ds = sg.build(rng, scen, n=5)
            self.assertIsNotNone(ds, scen["id"])
            self.assertEqual(len(ds["xs"]), 5)
            for col in ds["cols"]:
                self.assertTrue(sg._shape_ok(col["vals"], col["shape"]), (scen["id"], col["vals"]))
            for key in ("method", "controlled", "unrelated", "x_desc", "summary"):
                self.assertTrue(scen.get(key), (scen["id"], key))
            self.assertGreaterEqual(len(scen["controlled"]), 3, scen["id"])
            self.assertIn("{c}", scen["method"], scen["id"])
            if scen.get("cond"):
                ds2 = sg.build(rng, scen, cond="cond", n=5)
                self.assertIsNotNone(ds2, scen["id"])
                self.assertEqual(len(ds2["cols"]), 2)
                a, b = ds2["cols"]
                self.assertTrue(all(x != y for x, y in zip(a["vals"], b["vals"])), scen["id"])

    def test_table_stimulus_is_strings(self):
        ds = sg.build(random.Random(1), sg.SCENARIO_BY_ID["spring"], cond="cond", n=6)
        stim = sg.table_stimulus(ds)
        self.assertEqual(stim["type"], "table")
        for row in stim["table"]["rows"]:
            self.assertEqual(len(row), len(stim["table"]["headers"]))
            self.assertTrue(all(isinstance(c, str) for c in row))

    def test_figure_stimulus_keys(self):
        ds = sg.build(random.Random(2), sg.SCENARIO_BY_ID["pendulum"], n=5)
        fig = sg.figure_stimulus(ds, with_line=True)["figure"]
        self.assertEqual(fig["kind"], "scatter")
        self.assertEqual(len(fig["points"]), 5)
        self.assertIn("xlabel", fig)
        self.assertIn("m", fig["line"])
        self.assertIn("b", fig["line"])


class ScienceCorrectnessTests(unittest.TestCase):
    """Recompute the keyed answer from the emitted table/figure for every
    family that attaches a ``science:`` verification spec."""

    def _check(self, body, where):
        spec = _spec(body)
        if spec is None:
            return False
        kind, kw = spec
        correct = _correct(body)
        stim = body["stimulus"]
        if kind in ("fig_lookup", "fig_maxstep", "fig_trend"):
            pts = stim["figure"]["points"]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if kind == "fig_lookup":
                i = xs.index(float(kw["x"]))
                self.assertAlmostEqual(_num(correct), ys[i], places=6, msg=where)
            elif kind == "fig_maxstep":
                steps = [abs(b - a) for a, b in zip(ys, ys[1:])]
                k = steps.index(max(steps))
                for x in (xs[k], xs[k + 1]):
                    self.assertIn(sg._xstr(x), correct, where)
            else:
                self.assertEqual(_direction(ys), kw["expect"], where)
                self.assertIn({"inc": "increases", "dec": "decreases",
                               "peak": "increases, then"}[kw["expect"]], correct, where)
            return True
        xs, cols, labels, decs = _table(body)
        col = int(kw["col"]) - 1 if "col" in kw else 0
        vals = cols[col]
        dec = decs[col]
        if kind == "lookup":
            r = xs.index(kw["x"])
            self.assertAlmostEqual(_num(correct), vals[r], places=6, msg=where)
        elif kind == "invlookup":
            r = vals.index(float(kw["v"]))
            self.assertTrue(correct.startswith(xs[r]), where)
        elif kind == "extreme":
            r = vals.index((max if kw["mode"] == "max" else min)(vals))
            self.assertTrue(correct.startswith(xs[r]), where)
        elif kind == "diff":
            d = abs(vals[xs.index(kw["x2"])] - vals[xs.index(kw["x1"])])
            self.assertAlmostEqual(_num(correct), round(d, dec), places=6, msg=where)
        elif kind == "ratio":
            r = vals[xs.index(kw["x2"])] / vals[xs.index(kw["x1"])]
            self.assertAlmostEqual(_num(correct), round(r, 1), places=6, msg=where)
        elif kind == "trend":
            self.assertEqual(_direction(vals), kw["expect"], where)
            keys = {"inc": ("ncrease",), "dec": ("ecrease",), "peak": ("then", "intermediate")}[kw["expect"]]
            self.assertTrue(any(k in correct for k in keys), f"{where}: {correct!r}")
        elif kind == "count":
            thr = float(kw["v"])
            n = sum(1 for v in vals if (v > thr if kw["op"] == "gt" else v < thr))
            self.assertEqual(int(correct), n, where)
        elif kind == "conddiff":
            r = xs.index(kw["x"])
            a, b = cols[0][r], cols[1][r]
            hi = labels[0] if a > b else labels[1]
            self.assertTrue(correct.lower().startswith(hi.lower()), where)
            self.assertAlmostEqual(_num(correct.split(", by ")[1]), round(abs(a - b), dec), places=6, msg=where)
        elif kind == "pct":
            vi, vj = vals[xs.index(kw["x1"])], vals[xs.index(kw["x2"])]
            pct = round((vj - vi) / vi * 100)
            self.assertEqual(int(_num(correct.replace("+", "").replace("−", ""))), abs(pct), where)
        elif kind == "closest_then":
            src, dst = cols[int(kw["src"]) - 1], cols[int(kw["dst"]) - 1]
            v = float(kw["v"])
            r = min(range(len(src)), key=lambda j: abs(src[j] - v))
            self.assertAlmostEqual(_num(correct), dst[r], places=6, msg=where)
        elif kind == "avg3":
            r = xs.index(kw["x1"])
            self.assertAlmostEqual(_num(correct), round(sum(vals[r:r + 3]) / 3, dec), places=6, msg=where)
        elif kind == "shape":
            expect = kw["expect"]
            diffs = [b - a for a, b in zip(vals, vals[1:])]
            if expect == "peak":
                self.assertEqual(_direction(vals), "peak", where)
            else:
                base, pace = expect.split("_")
                self.assertEqual(_direction(vals), base, where)
                m = [abs(d) for d in diffs]
                if pace == "const":
                    self.assertLessEqual(max(m) - min(m), max(0.12 * sum(m) / len(m), 1.5 * 10 ** -dec), where)
                elif pace == "slow":
                    self.assertTrue(all(b < a for a, b in zip(m, m[1:])), where)
                else:
                    self.assertTrue(all(b > a for a, b in zip(m, m[1:])), where)
            key = {"const": "same amount", "slow": "smaller and smaller", "acc": "larger and larger"}
            if expect == "peak":
                self.assertIn("maximum", correct, where)
            else:
                self.assertIn(key[expect.split("_")[1]], correct, where)
        elif kind == "interp_range":
            x = float(kw["x"])
            fx = [float(v) for v in xs]
            i = max(j for j in range(len(fx) - 1) if fx[j] < x < fx[j + 1])
            lo, hi = sorted([vals[i], vals[i + 1]])
            nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", correct)]
            self.assertTrue(correct.startswith("between"), where)
            self.assertAlmostEqual(nums[0], lo, places=6, msg=where)
            self.assertAlmostEqual(nums[1], hi, places=6, msg=where)
        elif kind == "beyond":
            self.assertEqual(_direction(vals), "inc" if kw["expect"] == "gt" else "dec", where)
            self.assertTrue(correct.startswith("greater" if kw["expect"] == "gt" else "less"), where)
            self.assertAlmostEqual(_num(correct), vals[-1], places=6, msg=where)
        elif kind == "interp":
            x = float(kw["x"])
            fx = [float(v) for v in xs]
            i = max(j for j in range(len(fx) - 1) if fx[j] < x < fx[j + 1])
            frac = (x - fx[i]) / (fx[i + 1] - fx[i])
            est = round(vals[i] + frac * (vals[i + 1] - vals[i]), dec)
            self.assertAlmostEqual(_num(correct), est, places=6, msg=where)
        elif kind == "target":
            v = float(kw["v"])
            i = next(j for j in range(len(vals) - 1) if min(vals[j], vals[j + 1]) < v < max(vals[j], vals[j + 1]))
            self.assertTrue(correct.startswith(xs[i] + " ") or correct.startswith(xs[i]), where)
            self.assertIn(" and " + xs[i + 1], correct, where)
        elif kind == "double":
            r = vals[xs.index(kw["x2"])] / vals[xs.index(kw["x1"])]
            self.assertEqual(sg._bucket(r), kw["bucket"], where)
            self.assertEqual(correct, sg._BUCKETS[kw["bucket"]], where)
        elif kind == "maxstep":
            steps = [abs(b - a) for a, b in zip(vals, vals[1:])]
            k = steps.index(max(steps))
            self.assertTrue(correct.startswith(xs[k]), where)
            self.assertIn(" and " + xs[k + 1], correct, where)
        elif kind == "extrap":
            pred = round(vals[-1] + (vals[-1] - vals[-2]), dec)
            self.assertAlmostEqual(_num(correct), pred, places=6, msg=where)
        elif kind == "first_exceed":
            a, b = cols
            k = next(i for i in range(len(a)) if b[i] > a[i])
            self.assertTrue(correct.startswith(xs[k]), where)
        elif kind == "closest_pair":
            a, b = cols
            gaps = [abs(p - q) for p, q in zip(a, b)]
            self.assertTrue(correct.startswith(xs[gaps.index(min(gaps))]), where)
        elif kind == "reach":
            v = float(kw["v"])
            d = vals[-1] - vals[-2]
            fx = [float(x) for x in xs]
            k = round((v - vals[-1]) / d)
            self.assertGreaterEqual(k, 1, where)
            self.assertAlmostEqual(_num(correct), fx[-1] + k * (fx[-1] - fx[-2]), places=6, msg=where)
        elif kind == "condtrend":
            a, b = cols
            da, db = abs(a[-1] - a[0]), abs(b[-1] - b[0])
            big = labels[0] if da > db else labels[1]
            self.assertTrue(correct.lower().startswith(big.lower()), where)
            self.assertAlmostEqual(_num(correct.split(", by ")[1]), round(abs(da - db), dec), places=6, msg=where)
        elif kind == "cond_same":
            self.assertEqual(cols[0], cols[1], where)
            self.assertTrue(correct.startswith("No;"), where)
        elif kind == "cond_all":
            a, b = cols
            hi = int(kw["higher"])
            self.assertTrue(all((y > x) if hi == 2 else (x > y) for x, y in zip(a, b)), where)
            self.assertTrue(correct.startswith("Yes;"), where)
            self.assertIn(f"higher for {labels[hi - 1]} than", correct, where)
        elif kind == "cond_between":
            r = xs.index(kw["x"])
            lo, hi = sorted([cols[0][r], cols[1][r]])
            nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", correct)]
            self.assertTrue(correct.startswith("between"), where)
            self.assertAlmostEqual(nums[0], lo, places=6, msg=where)
            self.assertAlmostEqual(nums[1], hi, places=6, msg=where)
        else:
            self.fail(f"{where}: unknown verification kind {kind}")
        return True

    def test_answers_recompute_from_emitted_data(self):
        verified = set()
        for skill, diff, fn in _all_families():
            name = registry.family_name(fn)
            for i, b in enumerate(helpers.sample_family(fn, diff, 40, seed=29)):
                if self._check(b, f"{skill}/{diff}/{name}#{i}"):
                    verified.add(name)
        # Every lookup / trend / interpolation / extrapolation family must be covered.
        for name in ("dr_lookup_value", "dr_inverse_lookup", "dr_extreme", "dr_direction",
                     "dr_figure_read", "dr_difference", "dr_ratio", "dr_percent_change",
                     "dr_average", "dr_cross_condition_lookup", "tr_trend_shape",
                     "tr_interpolate_range", "tr_interpolate_value", "tr_x_for_target",
                     "tr_extrapolate_value", "tr_reach_threshold", "tr_doubling",
                     "tr_crossing", "tr_beyond_direction", "ed_predict_trial",
                     "ed_results_support_claim", "ed_predict_between_conditions"):
            self.assertIn(name, verified, f"{name} is not verified against its table")

    def test_consistent_statement_truth(self):
        """The keyed statement of the statement families must be true for the table and
        every distractor false, recomputed independently of the generator."""
        for fn, diff in ((sg.dr_consistent_statement, "medium"), (sg.dr_condition_statement, "hard")):
            for i, b in enumerate(helpers.sample_family(fn, diff, 40, seed=31)):
                xs, cols, labels, decs = _table(b)
                for c in b["choices"]:
                    truth = self._statement_truth(c["text"], xs, cols, labels)
                    if truth is None:
                        continue
                    self.assertEqual(truth, c["id"] == b["correct_choice"],
                                     f"{registry.family_name(fn)}#{i}: {c['text']!r} truth={truth}")

    @staticmethod
    def _statement_truth(text, xs, cols, labels):
        """Independently evaluate the simple comparative statements the families emit."""
        text = text.replace("pH ", "")

        def col_for(label):
            return cols[labels.index(label)] if label in labels else cols[0]

        m = re.search(r"was (greatest|least) (?:at|in) (.+?)\.$", text)
        if m and "difference" not in text:
            col = cols[0]
            if len(cols) > 1 and any(lab and lab in text for lab in labels):
                return None
            x = m.group(2).split(" ")[0].rstrip("%")
            if x not in xs:
                return None
            target = (max if m.group(1) == "greatest" else min)(col)
            return col[xs.index(x)] == target
        m = re.search(r"(?:at|in) (\S+?)(?: \S+)? was greater than .* (?:at|in) (\S+?)(?: \S+)?\.$", text)
        if m and "more than twice" not in text:
            xa, xb = m.group(1).rstrip("%"), m.group(2).rstrip("%")
            if xa in xs and xb in xs:
                if len(cols) == 1:
                    return cols[0][xs.index(xa)] > cols[0][xs.index(xb)]
                # two-condition form: "<Desc> <labelA> at xa was greater than <desc> <labelB> at xb"
                la = next((lab for lab in labels if f" {lab} at {xa}" in text), None)
                lb = next((lab for lab in labels if f" {lab} at {xb}" in text), None)
                if la and lb:
                    return col_for(la)[xs.index(xa)] > col_for(lb)[xs.index(xb)]
        m = re.search(r"(?:at|in) (\S+?)(?: \S+)? was more than twice its value (?:at|in) (\S+?)(?: \S+)?\.$", text)
        if m:
            xa, xb = m.group(1).rstrip("%"), m.group(2).rstrip("%")
            if xa in xs and xb in xs:
                return cols[0][xs.index(xa)] > 2 * cols[0][xs.index(xb)]
        if text.endswith("rose to a maximum and then fell."):
            return _direction(cols[0]) == "peak"
        m = re.search(r"(increased|decreased) with every increase in", text)
        if m:
            return _direction(cols[0]) == ("inc" if m.group(1) == "increased" else "dec")
        m = re.search(r"difference between the two conditions was (greatest|smallest) at (\S+)", text)
        if m and len(cols) == 2:
            gaps = [abs(a - b) for a, b in zip(cols[0], cols[1])]
            x = m.group(2).rstrip(".").rstrip("%")
            if x in xs:
                target = (max if m.group(1) == "greatest" else min)(gaps)
                return gaps.count(target) == 1 and gaps[xs.index(x)] == target
        m = re.search(r"^At every .* was higher (.+?) than (.+?)\.$", text)
        if m and len(cols) == 2 and m.group(1) in labels and m.group(2) in labels:
            hi, lo = col_for(m.group(1)), col_for(m.group(2))
            return all(a > b for a, b in zip(hi, lo))
        m = re.search(r"^Under both conditions, .*? (increased, then decreased|decreased, then increased|increased|decreased) as", text)
        if m and len(cols) == 2:
            d = {"increased": "inc", "decreased": "dec", "increased, then decreased": "peak"}.get(m.group(1), "none")
            return all(_direction(c) == d for c in cols)
        return None


class ConflictingViewpointsTests(unittest.TestCase):
    def test_pool_size_and_structure(self):
        self.assertGreaterEqual(len(sg.VIEWPOINTS), 10)
        ids = [p["id"] for p in sg.VIEWPOINTS]
        self.assertEqual(len(ids), len(set(ids)))
        for pair in sg.VIEWPOINTS:
            for key in ("text_a", "text_b"):
                words = len(pair[key].split())
                self.assertTrue(90 <= words <= 160, f"{pair['id']}.{key}: {words} words")
            qs = pair["questions"]
            self.assertTrue(4 <= len(qs) <= 5, pair["id"])
            self.assertEqual(set(qs), set(sg.CV_SLOTS), pair["id"])
            for slot, (prompt, options, ci, rats, expl) in qs.items():
                where = f"{pair['id']}/{slot}"
                self.assertGreaterEqual(len(prompt), 10, where)
                self.assertEqual(len(options), 4, where)
                self.assertEqual(len(rats), 4, where)
                self.assertEqual(len(set(o.strip() for o in options)), 4, f"{where}: duplicate options")
                self.assertTrue(0 <= ci < 4, where)
                self.assertTrue(rats[ci].startswith("Correct"), where)
                self.assertTrue(all(len(r) >= 3 for r in rats), where)
                self.assertGreaterEqual(len(expl), 10, where)

    def test_tiers_ramp_and_cover_pool(self):
        tiers = sg.viewpoint_tiers()
        for diff in DIFFS:
            self.assertGreaterEqual(len(tiers[diff]), 8, diff)
        covered = {p["id"] for d in DIFFS for p in tiers[d]}
        self.assertEqual(covered, {p["id"] for p in sg.VIEWPOINTS})
        cx = {d: [sg._pair_complexity(p) for p in tiers[d]] for d in DIFFS}
        self.assertLessEqual(min(cx["easy"]), min(cx["medium"]))
        self.assertLessEqual(max(cx["medium"]), max(cx["hard"]))
        self.assertLess(sum(cx["easy"]) / len(cx["easy"]), sum(cx["hard"]) / len(cx["hard"]))

    def test_families_cover_every_slot_and_shuffle(self):
        for diff in DIFFS:
            slots = set()
            for fn in sg.FAMILIES["conflicting_viewpoints"][diff]:
                self.assertTrue(getattr(fn, "small_space", False), registry.family_name(fn))
                bodies = helpers.sample_family(fn, diff, 40, seed=37)
                for b in bodies:
                    slot = next(t for t in b["tags"] if t in sg.CV_SLOTS)
                    slots.add(slot)
                    self.assertEqual(b["subskill"], sg.CV_SUBSKILL[slot])
                    self.assertTrue(b["stimulus"]["text"].startswith("Scientist 1"))
                    self.assertTrue(b["stimulus"]["text_b"].startswith("Scientist 2"))
                    pair_id = next(t for t in b["tags"] if t.startswith("pair:"))[5:]
                    pair = next(p for p in sg.VIEWPOINTS if p["id"] == pair_id)
                    key_text = pair["questions"][slot][1][pair["questions"][slot][2]]
                    self.assertEqual(_correct(b), key_text)
                self.assertGreaterEqual(len({b["correct_choice"] for b in bodies}), 3)
            self.assertEqual(slots, set(sg.CV_SLOTS), diff)


class TeachingScienceTests(unittest.TestCase):
    def test_entries_are_lesson_schema_valid(self):
        self.assertEqual(set(TEACHING_SCIENCE), set(sg.FAMILIES))
        for skill, card in TEACHING_SCIENCE.items():
            lesson = {
                "lesson_id": f"act-science-{skill.replace('_', '-')}-easy",
                "exam_id": "act", "exam_name": "ACT", "domain": "science",
                "section": "science", "skill": skill, "title": card["title"],
                "order": 0, "difficulty": "easy", "estimated_minutes": 10,
                "teaching_card": card, "question_ids": [f"q{i}" for i in range(8)],
                "prerequisite_lesson_ids": [], "unlock_xp": 0, "tags": ["science"],
                "version": "1.0.0",
            }
            errors = [e.message for e in _LESSON_VALIDATOR.iter_errors(lesson)]
            self.assertEqual(errors, [], skill)
            self.assertGreaterEqual(len(card["body"]), 30, skill)
            self.assertGreaterEqual(len(card["key_points"]), 2, skill)
            self.assertTrue(card.get("worked_example"), skill)
            screens = card["screens"]
            self.assertTrue(2 <= len(screens) <= 4, skill)
            for s in screens:
                self.assertGreaterEqual(len(s["title"]), 3, skill)
                self.assertGreaterEqual(len(s["body"]), 20, skill)
                for kp in s.get("key_points", []):
                    self.assertGreaterEqual(len(kp), 3, skill)
                self.assertEqual(set(s) - {"title", "body", "key_points", "worked_example"}, set(), skill)

    def test_no_placeholder_text(self):
        blob = json.dumps(TEACHING_SCIENCE)
        for pat in (r"\bTODO\b", r"\bTBD\b", r"lorem ipsum"):
            self.assertIsNone(re.search(pat, blob, re.IGNORECASE), pat)


if __name__ == "__main__":
    unittest.main()
