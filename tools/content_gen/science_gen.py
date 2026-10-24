"""ACT Science question generators.

ACT Science tests scientific *reasoning* over short descriptions of
experiments and their data, not memorised facts. This module covers four
skills:

* ``data_representation``  -- read a table or scatter figure: look up a value,
  spot which variable rose or fell, find the greatest/least entry, compare two
  entries, pick the statement the data support.
* ``trends_extrapolation`` -- describe the shape of a trend, interpolate
  between rows, extrapolate beyond them, reason about doubling, find where two
  series cross or a target value is reached.
* ``experimental_design``  -- research summaries: independent / dependent /
  controlled variables, why a control was used, what changed between two
  experiments, which design tests a new hypothesis, what the results support.
* ``conflicting_viewpoints`` -- authored Scientist 1 / Scientist 2 passages
  with questions about what each would agree with, common ground, supporting
  evidence, the effect of a new observation and the main point of difference.

Every table is COMPUTED from a templated scenario in :data:`SCENARIOS` (a
value function plus sensible rounding), so each answer is provably correct
and the unit tests can recompute it from the emitted table. Families attach a
compact ``answer_verification`` spec (``science:<kind>;k=v;...``) that the
tests use to do exactly that.

Contract: ``FAMILIES[skill][difficulty]`` is a list of
``fn(rng, difficulty) -> body`` (see registry.py). Families that draw from a
limited authored pool are flagged ``fn.small_space = True``.
"""
from __future__ import annotations

import functools
import math
import random

from .util import mc, shuffle_with_correct

SUBSKILLS = {
    "data_representation": [
        "table_lookup", "trend_direction", "extreme_value", "compare_entries",
        "consistent_statement", "figure_reading",
    ],
    "trends_extrapolation": [
        "trend_shape", "interpolation", "extrapolation",
        "proportional_reasoning", "series_crossing",
    ],
    "experimental_design": [
        "identify_variables", "control_purpose", "experiment_comparison",
        "design_change", "hypothesis_support", "predict_result",
    ],
    "conflicting_viewpoints": [
        "scientist_claim", "common_ground", "supporting_evidence",
        "new_observation", "main_difference",
    ],
}

QT_TABLE = "data_interpretation"
QT_PASSAGE = "passage_reading"
QT_MC = "multiple_choice"


# --------------------------------------------------------------------------- #
# Scenario library
# --------------------------------------------------------------------------- #
# Each scenario describes one templated experiment. Keys:
#   id, title, summary        -- labels for captions
#   x = (name, unit), xs      -- independent variable and its grid of values
#   x_desc / x_short          -- prose forms ("the length of the string")
#   series                    -- [{name, unit, desc, short, shape, fn}] (1 or 2)
#   dec                       -- decimals to round values to
#   params(rng)               -- draws the value-function parameters
#   method                    -- procedure text with a {c} slot for a condition
#   controlled, unrelated     -- phrases for variable-identification items
#   cond / null_cond          -- a second experimental condition (optional):
#       var, labels (2), phrases (2), factor=(lo,hi), offset=(lo,hi) or
#       pmod(p, rng) -> p2, numeric (bool), mid (phrase for a value between)
#   zero_ok                   -- the x = 0 row is a genuine control
def _S(**kw):
    return kw


def _quad_peak(base, k, xp):
    """Rise-then-fall curve peaking near x = xp (asymmetric for xp off-grid)."""
    return lambda x: base + k * x - (k / (2.0 * xp)) * x * x


SCENARIOS = [
    _S(id="pendulum", title="Pendulum Period",
       summary="Period of a pendulum measured at several string lengths.",
       x=("Length of string", "cm"), xs=[20, 40, 60, 80, 100, 120],
       x_desc="the length of the string", x_short="string length",
       y=("Period", "s"), y_desc="the period of the pendulum", y_short="period",
       shape="inc", dec=2,
       params=lambda r: {"g": r.uniform(9.5, 10.3)},
       fn=lambda x, p: 2 * math.pi * math.sqrt(x / 100.0 / p["g"]),
       method=("Students hung a metal bob from a string {c}, pulled the bob 10° to "
               "one side, and released it. They timed 10 complete swings with a "
               "stopwatch and divided by 10 to find the period. The procedure was "
               "repeated for several string lengths."),
       controlled=["the angle from which the bob was released", "the mass of the bob",
                   "the type of string"],
       unrelated="the color of the bob",
       cond=dict(var="the medium the bob swung through", labels=("air", "water"),
                 phrases=("with the bob swinging in air",
                          "with the bob swinging in a tank of water"),
                 factor=(1.12, 1.25)),
       null_cond=dict(var="the mass of the bob", labels=("50 g bob", "100 g bob"),
                      phrases=("using a 50 g bob", "using a 100 g bob"))),
    _S(id="fertilizer", title="Fertilizer and Plant Growth",
       summary="Average height of bean seedlings after 4 weeks at several fertilizer concentrations.",
       x=("Fertilizer concentration", "g/L"), xs=[0, 5, 10, 15, 20, 25],
       x_desc="the fertilizer concentration", x_short="fertilizer concentration",
       y=("Seedling height", "cm"), y_desc="the height of the seedlings",
       y_short="seedling height", shape="peak", dec=1,
       params=lambda r: {"base": r.uniform(10, 16), "k": r.uniform(0.9, 1.5),
                         "xp": r.choice([12, 13, 16, 17, 18])},
       fn=lambda x, p: _quad_peak(p["base"], p["k"], p["xp"])(x),
       method=("Students planted bean seeds in identical pots of potting soil and "
               "watered each pot with 100 mL of fertilizer solution every other day "
               "{c}. After 4 weeks they measured the height of each seedling. Each "
               "concentration was tested with five pots, and the average height was "
               "recorded."),
       controlled=["the volume of solution given to each pot", "the type of soil",
                   "the kind of seed"],
       unrelated="the color of the pots", zero_ok=True,
       cond=dict(var="the hours of light per day", labels=("6 h of light", "10 h of light"),
                 phrases=("under 6 hours of lamp light per day",
                          "under 10 hours of lamp light per day"),
                 factor=(1.15, 1.30), numeric=True, mid="8 hours of light per day")),
    _S(id="solubility", title="Solubility and Temperature",
       summary="Mass of a salt that dissolves in 100 g of water at several temperatures.",
       x=("Water temperature", "°C"), xs=[0, 20, 40, 60, 80, 100],
       x_desc="the temperature of the water", x_short="water temperature",
       y=("Mass dissolved", "g"), y_desc="the mass of salt that dissolved",
       y_short="mass dissolved", shape="inc", dec=0,
       params=lambda r: {"a": r.uniform(12, 20), "b": r.uniform(0.25, 0.5),
                         "c": r.uniform(0.012, 0.02)},
       fn=lambda x, p: p["a"] + p["b"] * x + p["c"] * x * x,
       method=("Students heated 100 g of distilled water to a set temperature in a "
               "beaker {c} and added the salt one gram at a time, stirring after each "
               "addition, until no more would dissolve. They recorded the total mass "
               "dissolved at each temperature."),
       controlled=["the mass of water", "the purity of the water",
                   "the time allowed for dissolving"],
       unrelated="the shape of the beaker",
       cond=dict(var="the salt used", labels=("Salt A", "Salt B"),
                 phrases=("using Salt A", "using Salt B"), factor=(0.55, 0.75)),
       null_cond=dict(var="the stirring rate", labels=("stirred slowly", "stirred rapidly"),
                      phrases=("stirring slowly", "stirring rapidly"))),
    _S(id="catalyst", title="Catalyst and Reaction Time",
       summary="Time for a reaction to finish with several masses of catalyst.",
       x=("Mass of catalyst", "mg"), xs=[0, 2, 4, 6, 8, 10],
       x_desc="the mass of catalyst", x_short="catalyst mass",
       y=("Reaction time", "s"), y_desc="the time for the reaction to finish",
       y_short="reaction time", shape="dec", dec=0,
       params=lambda r: {"t0": r.uniform(150, 300), "ti": r.uniform(12, 30),
                         "k": r.uniform(2.5, 4.0)},
       fn=lambda x, p: p["ti"] + (p["t0"] - p["ti"]) * math.exp(-x / p["k"]),
       method=("Students mixed 50 mL of hydrogen peroxide solution from a single "
               "bottle with a measured mass of powdered catalyst {c} and timed how "
               "long it took for the bubbling to stop."),
       controlled=["the volume of hydrogen peroxide", "the concentration of the "
                   "hydrogen peroxide", "the size of the flask"],
       unrelated="the brand of the stopwatch", zero_ok=True,
       cond=dict(var="the temperature of the solution", labels=("20°C", "30°C"),
                 phrases=("in a water bath at 20°C", "in a water bath at 30°C"),
                 factor=(0.5, 0.7), numeric=True, mid="a water bath at 25°C")),
    _S(id="antibiotic", title="Antibiotic Dose and Bacterial Growth",
       summary="Number of bacterial colonies on plates with several antibiotic concentrations.",
       x=("Antibiotic concentration", "µg/mL"), xs=[0, 5, 10, 15, 20, 25],
       x_desc="the antibiotic concentration", x_short="antibiotic concentration",
       y=("Colony count", "colonies"), y_desc="the number of colonies",
       y_short="colony count", shape="dec", dec=0,
       params=lambda r: {"n0": r.uniform(240, 400), "k": r.uniform(5, 8)},
       fn=lambda x, p: p["n0"] * math.exp(-x / p["k"]),
       method=("Students spread 0.1 mL of a bacterial culture onto agar plates "
               "containing a known concentration of an antibiotic {c}. After 24 "
               "hours they counted the colonies on each plate. Three plates were "
               "prepared for each concentration and the average count was recorded."),
       controlled=["the volume of culture spread on each plate", "the type of agar",
                   "the incubation time"],
       unrelated="the color of the plate lids", zero_ok=True,
       cond=dict(var="the incubation temperature", labels=("30°C", "37°C"),
                 phrases=("and incubated the plates at 30°C",
                          "and incubated the plates at 37°C"),
                 factor=(1.3, 1.6), numeric=True, mid="an incubation temperature of 34°C")),
    _S(id="braking", title="Speed and Stopping Distance",
       summary="Distance needed for a car to stop from several speeds.",
       x=("Speed", "km/h"), xs=[20, 40, 60, 80, 100, 120],
       x_desc="the speed of the car", x_short="speed",
       y=("Stopping distance", "m"), y_desc="the stopping distance",
       y_short="stopping distance", shape="inc", dec=1,
       params=lambda r: {"a": r.uniform(0.2, 0.3), "b": r.uniform(0.005, 0.008)},
       fn=lambda x, p: p["a"] * x + p["b"] * x * x,
       method=("On a closed test track, a driver brought the same car to each test "
               "speed {c}, then braked as hard as possible when a signal light "
               "flashed. The distance from the signal to the stopping point was "
               "measured. Each speed was tested three times and the average "
               "distance recorded."),
       controlled=["the car and its tires", "the load carried by the car",
                   "the braking method"],
       unrelated="the color of the car",
       cond=dict(var="the condition of the road surface",
                 labels=("dry pavement", "wet pavement"),
                 phrases=("on dry pavement", "on pavement sprayed with water"),
                 factor=(1.3, 1.6))),
    _S(id="boiling", title="Altitude and Boiling Point",
       summary="Boiling point of water measured at several altitudes.",
       x=("Altitude", "m"), xs=[0, 500, 1000, 1500, 2000, 2500, 3000],
       x_desc="the altitude of the station", x_short="altitude",
       y=("Boiling point", "°C"), y_desc="the boiling point of the water",
       y_short="boiling point", shape="dec", dec=1,
       params=lambda r: {"s": r.uniform(0.0031, 0.0036)},
       fn=lambda x, p: 100 - p["s"] * x,
       method=("A team carried the same kettle, thermometer, and a measured volume "
               "of distilled water to stations at several altitudes {c}. At each "
               "station the water was heated until it boiled steadily and the "
               "temperature was recorded."),
       controlled=["the kettle and thermometer", "the purity of the water",
                   "the heating method"],
       unrelated="the time of day",
       cond=dict(var="the amount of salt dissolved in the water",
                 labels=("pure water", "salt water"),
                 phrases=("using pure water",
                          "using water with 30 g of salt dissolved in it"),
                 factor=(1.0, 1.0), offset=(0.4, 0.9)),
       null_cond=dict(var="the volume of water", labels=("500 mL", "1000 mL"),
                      phrases=("using 500 mL of water", "using 1000 mL of water"))),
    _S(id="spring", title="Spring Stretch",
       summary="Stretch of a spring when several masses are hung from it.",
       x=("Mass", "g"), xs=[50, 100, 150, 200, 250, 300],
       x_desc="the mass hung from the spring", x_short="mass",
       y=("Stretch", "cm"), y_desc="the stretch of the spring", y_short="stretch",
       shape="inc", dec=1,
       params=lambda r: {"k": r.uniform(0.03, 0.06)},
       fn=lambda x, p: p["k"] * x,
       method=("Students hung a spring from a stand {c} and measured its unstretched "
               "length. They hung a mass from the spring, waited for it to stop "
               "moving, and measured the new length. The stretch is the difference "
               "between the two lengths. Masses were added in steps."),
       controlled=["the way the length was measured", "the ruler used",
                   "the time allowed for the mass to stop moving"],
       unrelated="the color of the spring",
       cond=dict(var="the spring used", labels=("Spring A", "Spring B"),
                 phrases=("using Spring A, made of thin wire",
                          "using Spring B, made of thicker wire"),
                 factor=(0.45, 0.65))),
    _S(id="sound", title="Distance and Sound Intensity",
       summary="Sound intensity measured at several distances from a speaker.",
       x=("Distance", "m"), xs=[1, 2, 3, 4, 5, 6],
       x_desc="the distance from the speaker", x_short="distance",
       y=("Intensity", "µW/m²"), y_desc="the sound intensity", y_short="intensity",
       shape="dec", dec=1,
       params=lambda r: {"P": r.uniform(80, 130)},
       fn=lambda x, p: p["P"] / (x * x),
       method=("In an open field, students placed a speaker playing a steady tone "
               "{c} and used a sound meter to measure the intensity at several "
               "distances along a straight line from the speaker. Readings were "
               "taken at the same height above the ground."),
       controlled=["the height of the sound meter", "the tone played",
                   "the location of the test"],
       unrelated="the brand of the speaker",
       cond=dict(var="the volume setting of the speaker",
                 labels=("full volume", "half volume"),
                 phrases=("at its full volume setting", "at half its full volume setting"),
                 factor=(0.4, 0.6))),
    _S(id="enzyme", title="Enzyme Activity and pH",
       summary="Activity of an enzyme in solutions of several pH values.",
       x=("pH", "pH"), xs=[3, 4, 5, 6, 7, 8, 9],
       x_desc="the pH of the solution", x_short="pH",
       y=("Enzyme activity", "µmol/min"), y_desc="the activity of the enzyme",
       y_short="enzyme activity", shape="peak", dec=0,
       params=lambda r: {"A": r.uniform(40, 90), "w": r.uniform(1.1, 1.5),
                         "p0": r.choice([5.7, 6.3, 6.7, 7.3])},
       fn=lambda x, p: p["A"] * math.exp(-((x - p["p0"]) ** 2) / (2 * p["w"] ** 2)),
       method=("Students added 1 mL of enzyme solution to tubes containing a "
               "substrate solution buffered to a set pH {c}. They measured how much "
               "product formed in 5 minutes to find the activity. Each pH was tested "
               "in triplicate."),
       controlled=["the volume of enzyme solution", "the concentration of the substrate",
                   "the reaction time"],
       unrelated="the color of the test-tube rack",
       cond=dict(var="the temperature of the tubes", labels=("25°C", "35°C"),
                 phrases=("and kept the tubes at 25°C", "and kept the tubes at 35°C"),
                 factor=(1.3, 1.6), numeric=True, mid="a temperature of 30°C")),
    _S(id="frogs", title="Two Frog Species",
       summary="Counts of two frog species in a pond in the years after bullfrogs first appeared there.",
       x=("Year", ""), xs_fn=lambda p: [p["y0"] + i for i in range(7)],
       x_desc="the year of the survey", x_short="year",
       series=[dict(name="Leopard frogs", unit="", desc="the number of leopard frogs counted",
                    short="leopard frog count", shape="dec",
                    fn=lambda x, p: p["A0"] - p["a"] * (x - p["y0"])),
               dict(name="Bullfrogs", unit="", desc="the number of bullfrogs counted",
                    short="bullfrog count", shape="inc",
                    fn=lambda x, p: p["B0"] + p["b"] * (x - p["y0"]))],
       dec=0,
       params=lambda r: {"y0": r.randint(2009, 2018), "A0": r.randint(150, 220),
                         "a": r.randint(12, 20), "B0": r.randint(20, 60), "b": r.randint(14, 24)},
       method=("Each June, volunteers walked the shore of a pond and counted every "
               "leopard frog and every bullfrog they saw or heard during two hours {c}."),
       controlled=["the month of the survey", "the length of the survey",
                   "the survey route"],
       unrelated="the age of the volunteers"),
    _S(id="battery", title="Battery Voltage Over Time",
       summary="Voltage of a battery after several hours of powering a lamp.",
       x=("Time", "h"), xs=[0, 2, 4, 6, 8, 10],
       x_desc="the time the lamp had been on", x_short="time",
       y=("Voltage", "V"), y_desc="the voltage of the battery", y_short="voltage",
       shape="dec", dec=2,
       params=lambda r: {"V0": r.uniform(1.50, 1.62), "a": r.uniform(0.015, 0.03),
                         "b": r.uniform(0.003, 0.005)},
       fn=lambda x, p: p["V0"] - p["a"] * x - p["b"] * x * x,
       method=("Students connected a fresh AA battery to a small lamp {c} and "
               "measured the battery's voltage with a voltmeter at regular intervals "
               "while the lamp stayed on."),
       controlled=["the lamp used", "the type of battery", "the voltmeter"],
       unrelated="the color of the wires",
       cond=dict(var="the temperature of the room", labels=("20°C", "0°C"),
                 phrases=("in a room at 20°C", "in a cold room at 0°C"),
                 factor=(0.86, 0.94), numeric=True, mid="a room temperature of 10°C")),
    _S(id="erosion", title="Slope and Soil Erosion",
       summary="Mass of soil washed from trays set at several slope angles.",
       x=("Slope angle", "°"), xs=[5, 10, 15, 20, 25, 30],
       x_desc="the slope angle of the tray", x_short="slope angle",
       y=("Soil eroded", "g"), y_desc="the mass of soil eroded", y_short="soil eroded",
       shape="inc", dec=0,
       params=lambda r: {"a": r.uniform(4, 8), "b": r.uniform(0.3, 0.6)},
       fn=lambda x, p: p["a"] * x + p["b"] * x * x,
       method=("Students filled identical trays with 5 kg of the same soil, tilted "
               "each tray to a set angle, and sprinkled water evenly over it from a "
               "watering can {c}. They collected the soil that washed out of the "
               "tray, dried it, and found its mass."),
       controlled=["the type of soil", "the mass of soil in each tray",
                   "the height from which the water was poured"],
       unrelated="the color of the trays",
       cond=dict(var="the volume of water sprinkled", labels=("2 L of water", "4 L of water"),
                 phrases=("using 2 L of water", "using 4 L of water"),
                 factor=(1.6, 2.0), numeric=True, mid="3 L of water")),
    _S(id="photosynthesis", title="Light and Photosynthesis",
       summary="Rate of photosynthesis of a water plant at several light intensities.",
       x=("Light intensity", "µmol/m²/s"), xs=[100, 200, 300, 400, 500, 600],
       x_desc="the light intensity", x_short="light intensity",
       y=("Bubbles per minute", "bubbles/min"), y_desc="the rate of photosynthesis",
       y_short="photosynthesis rate", shape="inc", dec=1,
       params=lambda r: {"Pm": r.uniform(25, 40), "K": r.uniform(80, 150)},
       fn=lambda x, p: p["Pm"] * x / (p["K"] + x),
       method=("Students placed a sprig of pondweed in a test tube of water {c} and "
               "set a lamp at distances giving several light intensities. They "
               "counted the oxygen bubbles released in one minute at each intensity, "
               "repeating each count three times."),
       controlled=["the temperature of the water", "the size of the pondweed sprig",
                   "the counting time"],
       unrelated="the brand of the lamp",
       cond=dict(var="the concentration of dissolved carbon dioxide",
                 labels=("low CO₂", "high CO₂"),
                 phrases=("in water with 0.5 g/L of sodium bicarbonate added as a "
                          "source of carbon dioxide",
                          "in water with 2.0 g/L of sodium bicarbonate added"),
                 factor=(1.3, 1.6), numeric=True,
                 mid="a sodium bicarbonate concentration of 1.2 g/L")),
    _S(id="tire", title="Temperature and Tire Pressure",
       summary="Pressure in a sealed tire at several air temperatures.",
       x=("Air temperature", "°C"), xs=[0, 10, 20, 30, 40, 50],
       x_desc="the air temperature", x_short="temperature",
       y=("Pressure", "kPa"), y_desc="the tire pressure", y_short="pressure",
       shape="inc", dec=1,
       params=lambda r: {"P0": r.uniform(200, 240)},
       fn=lambda x, p: p["P0"] * (x + 273.15) / 293.15,
       method=("A sealed bicycle tire was placed in a chamber {c} whose temperature "
               "could be set. At each temperature the tire was left for 30 minutes "
               "and its pressure was then read with a gauge."),
       controlled=["the time the tire was left at each temperature", "the gauge used",
                   "the tire's volume"],
       unrelated="the color of the tire",
       cond=dict(var="the tire used", labels=("Tire A", "Tire B"),
                 phrases=("using Tire A", "using Tire B, inflated to a higher starting "
                          "pressure"),
                 factor=(1.2, 1.5))),
    _S(id="lake", title="Lake Temperature and Depth",
       summary="Water temperature of a lake measured at several depths.",
       x=("Depth", "m"), xs=[0, 2, 4, 6, 8, 10, 12],
       x_desc="the depth below the surface", x_short="depth",
       y=("Water temperature", "°C"), y_desc="the water temperature",
       y_short="temperature", shape="dec", dec=1,
       params=lambda r: {"Ts": r.uniform(22, 26), "Td": r.uniform(6, 9),
                         "k": r.uniform(3, 5)},
       fn=lambda x, p: p["Td"] + (p["Ts"] - p["Td"]) * math.exp(-x / p["k"]),
       method=("From a boat anchored over the deepest part of a lake {c}, students "
               "lowered a thermometer probe on a marked cable and recorded the water "
               "temperature at several depths. All readings were taken within one "
               "hour at midday."),
       controlled=["the location of the boat", "the probe used", "the time of day"],
       unrelated="the color of the boat",
       cond=dict(var="the month of the measurements", labels=("July", "September"),
                 phrases=("in July", "in September"), factor=(0.80, 0.90))),
    _S(id="seeds", title="Seed Soaking and Germination",
       summary="Percent of radish seeds that sprouted after soaking for several lengths of time.",
       x=("Soaking time", "h"), xs=[0, 4, 8, 12, 16, 20, 24],
       x_desc="the soaking time", x_short="soaking time",
       y=("Seeds sprouted", "%"), y_desc="the percent of seeds that sprouted",
       y_short="germination rate", shape="peak", dec=0, vmax=100,
       params=lambda r: {"base": r.uniform(15, 30), "A": r.uniform(35, 50),
                         "w": r.uniform(7, 10), "xp": r.choice([9, 11, 13, 15])},
       fn=lambda x, p: p["base"] + p["A"] * math.exp(-((x - p["xp"]) / p["w"]) ** 2),
       method=("Students soaked batches of 50 radish seeds in water for a set number "
               "of hours, then placed each batch on damp paper towels in a covered "
               "tray {c}. After 5 days they counted the seeds that had sprouted and "
               "converted the count to a percent."),
       controlled=["the number of seeds in each batch", "the kind of seed",
                   "the number of days allowed for sprouting"],
       unrelated="the brand of paper towel", zero_ok=True,
       cond=dict(var="the temperature of the tray", labels=("15°C", "25°C"),
                 phrases=("and kept the trays at 15°C", "and kept the trays at 25°C"),
                 factor=(1.2, 1.4), numeric=True, mid="a tray temperature of 20°C")),
    _S(id="cooling", title="Cooling Curve",
       summary="Temperature of hot water in an open cup at several times after pouring.",
       x=("Time since pouring", "min"), xs=[5, 10, 15, 20, 25, 30, 35],
       x_desc="the time since pouring", x_short="time",
       y=("Water temperature", "°C"), y_desc="the temperature of the water",
       y_short="water temperature", shape="dec", dec=1,
       params=lambda r: {"Tr": r.uniform(20, 23), "T0": r.uniform(85, 92),
                         "k": r.uniform(12, 20)},
       fn=lambda x, p: p["Tr"] + (p["T0"] - p["Tr"]) * math.exp(-x / p["k"]),
       method=("Students poured hot water into a cup {c} and recorded the water's "
               "temperature with a digital thermometer every five minutes. The cup "
               "sat on a table in a room at a constant temperature."),
       controlled=["the starting temperature of the water", "the room temperature",
                   "the thermometer"],
       unrelated="the color of the cup",
       cond=dict(var="the type of cup", labels=("ceramic cup", "foam cup"),
                 phrases=("using a ceramic cup", "using an insulated foam cup"),
                 pmod=lambda p, r: {**p, "k": p["k"] * r.uniform(1.5, 1.9)})),
    _S(id="insulation", title="Insulation and Heat Loss",
       summary="Rate of heat loss from a heated box wrapped in several thicknesses of foam.",
       x=("Foam thickness", "cm"), xs=[0, 2, 4, 6, 8, 10],
       x_desc="the thickness of the insulation", x_short="insulation thickness",
       y=("Heat loss", "W"), y_desc="the rate of heat loss", y_short="heat loss",
       shape="dec", dec=0,
       params=lambda r: {"Q0": r.uniform(100, 160), "k": r.uniform(2, 3.5)},
       fn=lambda x, p: p["Q0"] / (1 + x / p["k"]),
       method=("Students wrapped a metal box containing an electric heater in foam "
               "sheets of a set total thickness. They adjusted the heater power until "
               "the inside temperature held steady {c} in a 20°C room and recorded "
               "that power as the rate of heat loss."),
       controlled=["the room temperature", "the size of the box", "the type of foam"],
       unrelated="the color of the foam", zero_ok=True,
       cond=dict(var="the inside temperature", labels=("60°C inside", "80°C inside"),
                 phrases=("at 60°C", "at 80°C"), factor=(1.4, 1.6), numeric=True,
                 mid="an inside temperature of 70°C")),
    _S(id="fuel", title="Speed and Fuel Efficiency",
       summary="Fuel efficiency of a car driven at several steady speeds.",
       x=("Speed", "km/h"), xs=[40, 50, 60, 70, 80, 90, 100],
       x_desc="the steady speed of the car", x_short="speed",
       y=("Fuel efficiency", "km/L"), y_desc="the fuel efficiency",
       y_short="fuel efficiency", shape="peak", dec=1,
       params=lambda r: {"E": r.uniform(14, 18), "c": r.uniform(0.002, 0.004),
                         "xp": r.choice([68, 72, 78, 82])},
       fn=lambda x, p: p["E"] - p["c"] * (x - p["xp"]) ** 2,
       method=("A test driver drove the same car around a flat track at a steady "
               "speed {c} for 20 km and measured the fuel used. Fuel efficiency was "
               "calculated as kilometers traveled per liter of fuel."),
       controlled=["the car used", "the distance driven", "the track"],
       unrelated="the radio station playing in the car",
       cond=dict(var="the load in the car", labels=("driver only", "driver plus 300 kg"),
                 phrases=("with only the driver aboard",
                          "with the driver and 300 kg of sandbags aboard"),
                 factor=(0.80, 0.90))),
    _S(id="energy", title="Electricity Sources",
       summary="Percent of a region's electricity generated from coal and from solar power each year.",
       x=("Year", ""), xs_fn=lambda p: [p["y0"] + i for i in range(7)],
       x_desc="the year", x_short="year",
       series=[dict(name="Coal", unit="%", desc="the percent of electricity from coal",
                    short="coal share", shape="dec",
                    fn=lambda x, p: p["C0"] - p["a"] * (x - p["y0"])),
               dict(name="Solar", unit="%", desc="the percent of electricity from solar",
                    short="solar share", shape="inc",
                    fn=lambda x, p: p["S0"] + p["b"] * (x - p["y0"]))],
       dec=0,
       params=lambda r: {"y0": r.randint(2010, 2018), "C0": r.randint(55, 70),
                         "a": r.randint(4, 7), "S0": r.randint(5, 12), "b": r.randint(4, 7)},
       method=("A regional utility reported the percent of its electricity that came "
               "from coal and from solar power in each year {c}."),
       controlled=["the region reported on", "the reporting method", "the units used"],
       unrelated="the name of the utility"),
    _S(id="plot", title="Native and Invasive Plants",
       summary="Stems of a native grass and of an invasive knapweed counted in a 1 m² plot each summer.",
       x=("Year", ""), xs_fn=lambda p: [p["y0"] + i for i in range(7)],
       x_desc="the year of the count", x_short="year",
       series=[dict(name="Native grass stems", unit="", desc="the number of native grass stems",
                    short="native grass count", shape="dec",
                    fn=lambda x, p: p["G0"] - p["g"] * (x - p["y0"])),
               dict(name="Knapweed stems", unit="", desc="the number of knapweed stems",
                    short="knapweed count", shape="inc",
                    fn=lambda x, p: p["K0"] + p["k"] * (x - p["y0"]))],
       dec=0,
       params=lambda r: {"y0": r.randint(2008, 2017), "G0": r.randint(90, 140),
                         "g": r.randint(8, 14), "K0": r.randint(5, 25), "k": r.randint(9, 16)},
       method=("Each July, ecologists counted every stem of native grass and every stem of "
               "knapweed inside the same marked 1 m² plot {c}."),
       controlled=["the location of the plot", "the month of the count", "the size of the plot"],
       unrelated="the number of ecologists on the team"),
]


def _normalise(scen):
    if "series" not in scen:
        name, unit = scen["y"]
        scen["series"] = [dict(name=name, unit=unit, desc=scen["y_desc"],
                               short=scen["y_short"], shape=scen["shape"],
                               fn=scen["fn"])]
    for s in scen["series"]:
        s.setdefault("fn", scen.get("fn"))
    scen.setdefault("shape", "mixed")   # two-series scenarios: no single shape
    scen.setdefault("zero_ok", False)
    return scen


SCENARIOS = [_normalise(s) for s in SCENARIOS]
SCENARIO_BY_ID = {s["id"]: s for s in SCENARIOS}


# --------------------------------------------------------------------------- #
# Dataset construction
# --------------------------------------------------------------------------- #
def _fmt(v, dec):
    return f"{v:.{dec}f}"


def _vu(text, unit):
    """Value with its unit, e.g. '1.27 s', '35%', '20°', 'pH 7', '2017'."""
    if not unit:
        return str(text)
    if unit in ("%", "°"):
        return f"{text}{unit}"
    if unit == "pH":
        return f"pH {text}"
    return f"{text} {unit}"


def _xat(ds, xstr):
    """'at a speed of 40 km/h', 'at pH 7', 'in 2018' for prompts."""
    scen, xu = ds["scen"], ds["xunit"]
    if scen["x_short"] == "year":
        return f"in {xstr}"
    if xu == "pH":
        return f"at pH {xstr}"
    art = "an" if scen["x_short"][0] in "aeiou" else "a"
    return f"at {art} {scen['x_short']} of {_vu(xstr, xu)}"


def _xstep(ds, step):
    """A step in x with its unit ('1 year', '20 cm')."""
    if ds["scen"]["x_short"] == "year":
        return f"{_xstr(step)} year" + ("" if step == 1 else "s")
    return _vu(_xstr(step), ds["xunit"])


def _neg(text):
    return str(text).replace("-", "−")


def _at(ds, xstr):
    """'at 40 cm' or, for year scenarios, 'in 2018'."""
    if ds["scen"]["x_short"] == "year":
        return f"in {xstr}"
    return f"at {_vu(xstr, ds['xunit'])}"


def _xv(ds, xstr):
    """x value for 'when <x_desc> was ...' phrasing (no 'pH' prefix after 'the pH')."""
    return str(xstr) if ds["xunit"] == "pH" else _vu(xstr, ds["xunit"])


def _range_phrase(scen):
    if scen["x_short"] == "year":
        return "over the years shown"
    return f"over the range of {scen['x_short']} tested"


def _xstr(x):
    return str(int(x)) if float(x).is_integer() else str(x)


def _strict(vals, up: bool) -> bool:
    return all((b > a) if up else (b < a) for a, b in zip(vals, vals[1:]))


def _shape_ok(vals, shape) -> bool:
    if shape == "inc":
        return _strict(vals, True)
    if shape == "dec":
        return _strict(vals, False)
    if shape == "peak":
        i = max(range(len(vals)), key=lambda j: vals[j])
        if i == 0 or i == len(vals) - 1:
            return False
        return _strict(vals[:i + 1], True) and _strict(vals[i:], False)
    return False


def _pick_scenario(rng, pred=None):
    pool = [s for s in SCENARIOS if pred is None or pred(s)]
    return rng.choice(pool)


def build(rng, scen, *, cond=None, n=None):
    """Compute one dataset. ``cond`` is None, "cond" or "null" (a second
    condition column derived from the first series). Returns None if no
    parameter draw produced clean, shape-consistent rounded values."""
    dec = scen["dec"]
    want_n = n
    for _ in range(50):
        p = scen["params"](rng)
        xs_all = scen["xs_fn"](p) if "xs_fn" in scen else scen["xs"]
        k = want_n or rng.randint(4, 6)
        k = min(k, len(xs_all))
        start = rng.randint(0, len(xs_all) - k)
        xs = xs_all[start:start + k]
        cols = []
        ok = True
        vmax = scen.get("vmax", float("inf"))
        for ser in scen["series"]:
            vals = [round(ser["fn"](x, p), dec) for x in xs]
            if not _shape_ok(vals, ser["shape"]) or min(vals) < 0 or max(vals) > vmax:
                ok = False
                break
            cols.append(dict(name=ser["name"], unit=ser["unit"], desc=ser["desc"],
                             short=ser["short"], shape=ser["shape"], vals=vals,
                             strs=[_fmt(v, dec) for v in vals], label=None))
        if not ok:
            continue
        cinfo = None
        if cond:
            c = scen.get("cond") if cond == "cond" else scen.get("null_cond")
            if c is None:
                return None
            base = cols[0]
            if cond == "null":
                vals2 = list(base["vals"])
            else:
                p2 = c["pmod"](p, rng) if "pmod" in c else p
                factor = rng.uniform(*c.get("factor", (1.0, 1.0)))
                offset = rng.uniform(*c.get("offset", (0.0, 0.0)))
                fn0 = scen["series"][0]["fn"]
                vals2 = [round(fn0(x, p2) * factor + offset, dec) for x in xs]
                if not _shape_ok(vals2, base["shape"]) or min(vals2) < 0 or max(vals2) > vmax:
                    continue
                unit = 10 ** (-dec)
                if any(abs(a - b) < unit * 0.999 for a, b in zip(base["vals"], vals2)):
                    continue
            base["label"] = c["labels"][0]
            cols.append(dict(name=base["name"], unit=base["unit"], desc=base["desc"],
                             short=base["short"], shape=base["shape"], vals=vals2,
                             strs=[_fmt(v, dec) for v in vals2], label=c["labels"][1]))
            cinfo = dict(c)
            cinfo["kind"] = cond
        for col in cols:
            col["header"] = (f"{col['name']} ({col['unit']})" if col["unit"] else col["name"])
            if col["label"]:
                col["header"] += f", {col['label']}"
        xname, xunit = scen["x"]
        xheader = f"{xname} ({xunit})" if xunit and xunit != "pH" else xname
        return dict(scen=scen, xs=xs, xstrs=[_xstr(x) for x in xs], cols=cols,
                    dec=dec, xunit=xunit, xheader=xheader,
                    cond=cinfo, p=p)
    return None


def _caption(ds, prefix="Table 1."):
    scen, cinfo = ds["scen"], ds["cond"]
    cap = f"{prefix} {scen['summary']}"
    if cinfo:
        cap += (f" Results are shown for two conditions: {cinfo['labels'][0]} and "
                f"{cinfo['labels'][1]}.")
    return cap


def table_stimulus(ds, caption=None, title=None):
    headers = [ds["xheader"]] + [c["header"] for c in ds["cols"]]
    rows = [[ds["xstrs"][i]] + [c["strs"][i] for c in ds["cols"]]
            for i in range(len(ds["xs"]))]
    return {"type": "table", "title": title or ds["scen"]["title"],
            "table": {"caption": caption or _caption(ds), "headers": headers,
                      "rows": rows}}


def figure_stimulus(ds, col=0, with_line=False):
    scen = ds["scen"]
    c = ds["cols"][col]
    pts = [[float(x), float(v)] for x, v in zip(ds["xs"], c["vals"])]
    yl = f"{c['name']} ({c['unit']})" if c["unit"] else c["name"]
    fig = {"kind": "scatter", "points": pts, "xlabel": ds["xheader"], "ylabel": yl,
           "caption": (f"Figure 1. {yl} (vertical axis) versus {ds['xheader']} "
                       f"(horizontal axis). Each point is one trial.")}
    if with_line:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        sxx = sum((x - mx) ** 2 for x in xs)
        m = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else 0.0
        fig["line"] = {"m": round(m, 4), "b": round(my - m * mx, 3)}
    return {"type": "figure", "title": scen["title"], "figure": fig}


def _method_text(scen, cond_phrase):
    t = scen["method"].format(c=cond_phrase)
    return t.replace("  ", " ").replace(" ,", ",").replace(" .", ".")


def experiment_passage(ds, two=False):
    """A research-summary passage: method + inline results (one stimulus)."""
    scen, cinfo = ds["scen"], ds["cond"]
    c0 = cinfo["phrases"][0] if cinfo else ""
    method1 = _method_text(scen, c0)
    col = ds["cols"][0]
    xu, yu = ds["xunit"], col["unit"]
    pairs = [f"at {_vu(xs, xu)}, {_vu(vs, yu)}" for xs, vs in zip(ds["xstrs"], col["strs"])]
    results = (f"Results ({col['desc']}): " + "; ".join(pairs) + ".")
    text = f"Experiment 1\n{method1}\n{results}"
    if two and cinfo:
        col2 = ds["cols"][1]
        pairs2 = [f"at {_vu(xs, xu)}, {_vu(vs, yu)}"
                  for xs, vs in zip(ds["xstrs"], col2["strs"])]
        text += (f"\n\nExperiment 2\nThe procedure of Experiment 1 was repeated "
                 f"{cinfo['phrases'][1]}, with everything else unchanged.\n"
                 f"Results: " + "; ".join(pairs2) + ".")
    return {"type": "passage", "title": scen["title"], "text": text}


def experiment_table(ds, two=False):
    """A research-summary table whose caption carries the method."""
    scen, cinfo = ds["scen"], ds["cond"]
    c0 = cinfo["phrases"][0] if cinfo else ""
    method1 = _method_text(scen, c0)
    cap = f"Experiment 1: {method1}"
    if two and cinfo:
        cap += (f" Experiment 2: The procedure was repeated {cinfo['phrases'][1]}, "
                f"with everything else unchanged. Table 1 lists the results of both "
                f"experiments.")
    else:
        cap += " Table 1 lists the results."
    return table_stimulus(ds, caption=cap)


# --------------------------------------------------------------------------- #
# Emission helpers
# --------------------------------------------------------------------------- #
def _spec(kind, **kw):
    return "science:" + kind + "".join(f";{k}={v}" for k, v in kw.items())


def _emit(rng, prompt, correct, distractors, *, subskill, explanation, qtype,
          est, tags, stimulus, verify=None):
    texts = [correct[0]] + [d[0] for d in distractors]
    if len(set(t.strip() for t in texts)) != len(texts) or len(distractors) < 3:
        return None
    options, ci, rats = shuffle_with_correct(rng, correct, distractors[:3])
    return mc(prompt, options, ci, rats, subskill=subskill, explanation=explanation,
              qtype=qtype, est=est, tags=tags, stimulus=stimulus, verify=verify)


def _retry(fn):
    """Families return None when a random draw yields an ambiguous item; keep
    drawing (deterministically, from the same rng) until one is clean."""
    @functools.wraps(fn)
    def wrapper(rng, difficulty):
        for _ in range(80):
            body = fn(rng, difficulty)
            if body is not None:
                return body
        raise RuntimeError(f"{fn.__name__}: no clean item after 80 draws")
    return wrapper


def _n_rows(rng, difficulty):
    return rng.randint(4, 5) if difficulty == "easy" else rng.randint(5, 6)


def _lower_first(s):
    return s[0].lower() + s[1:] if s else s


def _cap_first(s):
    if not s or s.startswith("pH"):
        return s
    return s[0].upper() + s[1:]


def _direction_word(shape):
    return {"inc": "increased", "dec": "decreased", "peak": "increased, then decreased"}[shape]


# --------------------------------------------------------------------------- #
# Data representation
# --------------------------------------------------------------------------- #
DR_TAGS = ["science", "data-representation"]


@_retry
def dr_lookup_value(rng, difficulty):
    scen = _pick_scenario(rng)
    use_cond = bool(scen.get("cond")) and rng.random() < 0.35
    ds = build(rng, scen, cond="cond" if use_cond else None, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    cols = ds["cols"]
    ci = rng.randrange(len(cols))
    col = cols[ci]
    n = len(ds["xs"])
    i = rng.randrange(n)
    x, xu, yu = ds["xstrs"][i], ds["xunit"], col["unit"]
    where = f" for {col['label']}" if col["label"] else ""
    desc = col["desc"]
    prompt = rng.choice([
        f"According to Table 1, when {scen['x_desc']} was {_xv(ds, x)}, {desc}{where} was:",
        f"Based on Table 1, {desc} recorded {_xat(ds, x)}{where} was:",
        f"In Table 1, which of the following is {desc}{where} {_xat(ds, x)}?",
    ])
    correct = (_vu(col["strs"][i], yu),
               f"Correct. Find the row for {_vu(x, xu)} and read across to the "
               f"{col['header']} column.")
    distractors = []
    if i > 0:
        distractors.append((_vu(col["strs"][i - 1], yu),
                            f"This is the value in the row above, for {_vu(ds['xstrs'][i - 1], xu)}."))
    if i < n - 1:
        distractors.append((_vu(col["strs"][i + 1], yu),
                            f"This is the value in the row below, for {_vu(ds['xstrs'][i + 1], xu)}."))
    if len(cols) > 1:
        other = cols[1 - ci]
        distractors.append((_vu(other["strs"][i], other["unit"]),
                            f"This value comes from the {other['header']} column, not the "
                            f"column asked about."))
    for j in (i - 2, i + 2, i - 3, i + 3):
        if 0 <= j < n and len(distractors) < 3:
            distractors.append((_vu(col["strs"][j], yu),
                                f"This is the value for {_vu(ds['xstrs'][j], xu)}, a different row."))
    expl = (f"Locate {_vu(x, xu)} in the {ds['xheader']} column, then read the "
            f"{col['header']} entry in that row: {_vu(col['strs'][i], yu)}.")
    return _emit(rng, prompt, correct, distractors, subskill="table_lookup",
                 explanation=expl, qtype=QT_TABLE, est=40, tags=DR_TAGS + ["lookup"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("lookup", x=x, col=ci + 1))


@_retry
def dr_direction(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    shape = col["shape"]
    x0, x1 = _vu(ds["xstrs"][0], ds["xunit"]), _vu(ds["xstrs"][-1], ds["xunit"])
    prompt = rng.choice([
        f"According to Table 1, as {scen['x_desc']} increased from {x0} to {x1}, {col['desc']}:",
        f"Based on the data in Table 1, {_range_phrase(scen)}, {col['desc']}:",
        f"Which of the following best describes how {col['desc']} changed as "
        f"{scen['x_desc']} increased from {x0} to {x1}?",
    ])
    texts = {
        "inc": "increased only",
        "dec": "decreased only",
        "peak": "increased, then decreased",
        "valley": "decreased, then increased",
        "flat": "remained the same",
    }
    rats = {
        "inc": "Every value is larger than the one above it; the values never fall.",
        "dec": "Every value is smaller than the one above it; the values never rise.",
        "peak": "The values rise to a maximum and then fall, which the table does not show.",
        "valley": "The values would have to fall and then rise, which the table does not show.",
        "flat": "The values change from row to row, so they did not remain the same.",
    }
    if shape == "inc":
        rats["peak"] = "The values keep rising to the last row; they never turn downward."
    if shape == "dec":
        rats["valley"] = "The values keep falling to the last row; they never turn upward."
    if shape == "peak":
        imax = max(range(len(col["vals"])), key=lambda j: col["vals"][j])
        rats["inc"] = (f"The values rise only up to {_vu(ds['xstrs'][imax], ds['xunit'])}; "
                       f"after that they fall.")
        rats["dec"] = (f"The values fall only after {_vu(ds['xstrs'][imax], ds['xunit'])}; "
                       f"before that they rise.")
    correct = (texts[shape], "Correct. " + {
        "inc": "Reading down the column, each value is greater than the one before it.",
        "dec": "Reading down the column, each value is less than the one before it.",
        "peak": "The values rise to a maximum partway down the column and then fall.",
    }[shape])
    others = [k for k in texts if k != shape]
    rng.shuffle(others)
    distractors = [(texts[k], rats[k]) for k in others[:3]]
    expl = f"Compare each value with the one above it: {col['desc']} {_direction_word(shape)}."
    return _emit(rng, prompt, correct, distractors, subskill="trend_direction",
                 explanation=expl, qtype=QT_TABLE, est=45, tags=DR_TAGS + ["direction"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("trend", col=ci + 1, expect=shape))


@_retry
def dr_extreme(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    vals = col["vals"]
    want_max = rng.random() < 0.5
    key = max if want_max else min
    target = key(vals)
    if vals.count(target) != 1:
        return None
    i = vals.index(target)
    word = "greatest" if want_max else "least"
    xu = ds["xunit"]
    prompt = rng.choice([
        f"According to Table 1, {col['desc']} was {word} when {scen['x_desc']} was:",
        f"Based on Table 1, {'in' if scen['x_short'] == 'year' else 'at'} which {scen['x_short']} "
        f"was {col['desc']} {word}?",
        f"For which value of {scen['x_short']} in Table 1 was {col['desc']} the {word}?",
    ])
    correct = (_vu(ds["xstrs"][i], xu),
               f"Correct. The {word} value in the {col['header']} column is "
               f"{_vu(col['strs'][i], col['unit'])}, in the row for {_vu(ds['xstrs'][i], xu)}.")
    opp = vals.index((min if want_max else max)(vals))
    distractors = [(_vu(ds["xstrs"][opp], xu),
                    f"This is where {col['desc']} was {'least' if want_max else 'greatest'}, "
                    f"the opposite extreme.")]
    for j in sorted(range(len(vals)), key=lambda j: abs(j - i)):
        if j not in (i, opp) and len(distractors) < 3:
            distractors.append((_vu(ds["xstrs"][j], xu),
                                f"The value here, {_vu(col['strs'][j], col['unit'])}, is not the "
                                f"{word} in the column."))
    expl = (f"Scan the {col['header']} column for the {word} value, "
            f"{_vu(col['strs'][i], col['unit'])}, and read the {scen['x_short']} in that row.")
    return _emit(rng, prompt, correct, distractors, subskill="extreme_value",
                 explanation=expl, qtype=QT_TABLE, est=40, tags=DR_TAGS + ["extreme"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("extreme", mode="max" if want_max else "min", col=ci + 1))


@_retry
def dr_inverse_lookup(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    if len(set(col["strs"])) != len(col["strs"]):
        return None
    i = rng.randrange(len(ds["xs"]))
    xu, yu = ds["xunit"], col["unit"]
    v = _vu(col["strs"][i], yu)
    prompt = rng.choice([
        f"According to Table 1, {col['desc']} was {v} when {scen['x_desc']} was"
        f"{' pH' if ds['xunit'] == 'pH' else ''}:",
        f"In Table 1, a value of {v} for {col['desc']} corresponds to which "
        f"{scen['x_short']}?",
        f"Based on Table 1, which {scen['x_short']} produced a {col['short']} of {v}?",
    ])
    correct = (_vu(ds["xstrs"][i], xu),
               f"Correct. Find {v} in the {col['header']} column and read the "
               f"{scen['x_short']} in the same row.")
    distractors = []
    for j in sorted(range(len(ds["xs"])), key=lambda j: abs(j - i)):
        if j != i and len(distractors) < 3:
            distractors.append((_vu(ds["xstrs"][j], xu),
                                f"At {_vu(ds['xstrs'][j], xu)} the table lists "
                                f"{_vu(col['strs'][j], yu)}, not {v}."))
    expl = (f"Search the {col['header']} column for {v}; it appears in the row where "
            f"{scen['x_short']} is {_vu(ds['xstrs'][i], xu)}.")
    return _emit(rng, prompt, correct, distractors, subskill="table_lookup",
                 explanation=expl, qtype=QT_TABLE, est=40, tags=DR_TAGS + ["lookup"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("invlookup", v=col["strs"][i], col=ci + 1))


@_retry
def dr_figure_read(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: len(s["series"]) == 1)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    col = ds["cols"][0]
    vals = col["vals"]
    n = len(vals)
    i = rng.randrange(n)
    # Neighbouring points must be clearly separated for a visual read.
    rng_v = max(vals) - min(vals)
    if any(abs(vals[j] - vals[i]) < 0.12 * rng_v for j in range(n) if j != i):
        return None
    x, xu, yu = ds["xstrs"][i], ds["xunit"], col["unit"]
    prompt = rng.choice([
        f"According to Figure 1, when {scen['x_desc']} was {_xv(ds, x)}, {col['desc']} was "
        f"closest to:",
        f"Based on Figure 1, {col['desc']} {_xat(ds, x)} was approximately:",
    ])
    correct = (_vu(col["strs"][i], yu),
               f"Correct. The point plotted at {_vu(x, xu)} on the horizontal axis sits at "
               f"about {_vu(col['strs'][i], yu)} on the vertical axis.")
    distractors = []
    for j in sorted(range(n), key=lambda j: abs(j - i)):
        if j != i and len(distractors) < 3:
            distractors.append((_vu(col["strs"][j], yu),
                                f"This is the height of the point at {_vu(ds['xstrs'][j], xu)}, "
                                f"a different position on the horizontal axis."))
    expl = (f"Find {_vu(x, xu)} on the horizontal axis, move up to the plotted point, and read "
            f"its height on the vertical axis: about {_vu(col['strs'][i], yu)}.")
    return _emit(rng, prompt, correct, distractors, subskill="figure_reading",
                 explanation=expl, qtype=QT_MC, est=45, tags=DR_TAGS + ["figure"],
                 stimulus=figure_stimulus(ds), verify=_spec("fig_lookup", x=x))


@_retry
def dr_difference(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    n = len(ds["xs"])
    dec, xu, yu = ds["dec"], ds["xunit"], col["unit"]
    i, j = sorted(rng.sample(range(n), 2))
    if j - i < 2 and n > 3 and rng.random() < 0.7:
        return None  # prefer non-adjacent rows most of the time
    d = round(abs(col["vals"][j] - col["vals"][i]), dec)
    if d == 0:
        return None
    xi, xj = _vu(ds["xstrs"][i], xu), _vu(ds["xstrs"][j], xu)
    ai, aj = _at(ds, ds["xstrs"][i]), _at(ds, ds["xstrs"][j])
    prompt = rng.choice([
        f"According to Table 1, the difference between {col['desc']} {aj} and {ai} is:",
        f"Based on Table 1, by how much did {col['desc']} change as {scen['x_desc']} went "
        f"from {xi} to {xj}?",
        f"In Table 1, how much {'greater' if col['vals'][j] > col['vals'][i] else 'less'} was "
        f"{col['desc']} {aj} than {ai}?",
    ])
    correct = (_vu(_fmt(d, dec), yu),
               f"Correct. |{col['strs'][j]} − {col['strs'][i]}| = {_fmt(d, dec)}.")
    distractors = []
    cands = []
    if j + 1 < n:
        cands.append((j + 1, i, f"This uses the row for {_vu(ds['xstrs'][j + 1], xu)} instead of {xj}."))
    if i - 1 >= 0:
        cands.append((j, i - 1, f"This uses the row for {_vu(ds['xstrs'][i - 1], xu)} instead of {xi}."))
    if j - 1 > i:
        cands.append((j - 1, i, f"This uses the row for {_vu(ds['xstrs'][j - 1], xu)} instead of {xj}."))
    if i + 1 < j:
        cands.append((j, i + 1, f"This uses the row for {_vu(ds['xstrs'][i + 1], xu)} instead of {xi}."))
    for a, b, why in cands:
        dd = round(abs(col["vals"][a] - col["vals"][b]), dec)
        if dd != d and dd != 0:
            distractors.append((_vu(_fmt(dd, dec), yu), why))
    distractors.append((_vu(col["strs"][j], yu),
                        f"This is the value at {xj} itself, not the difference between the two rows."))
    s = round(col["vals"][j] + col["vals"][i], dec)
    distractors.append((_vu(_fmt(s, dec), yu), "This adds the two values instead of subtracting them."))
    expl = (f"Read {col['desc']} {aj} ({col['strs'][j]}) and {ai} ({col['strs'][i]}); "
            f"the difference is {_fmt(d, dec)} {yu}.".strip())
    return _emit(rng, prompt, correct, distractors, subskill="compare_entries",
                 explanation=expl, qtype=QT_TABLE, est=55, tags=DR_TAGS + ["difference"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("diff", x1=ds["xstrs"][i], x2=ds["xstrs"][j], col=ci + 1))


@_retry
def dr_ratio(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    n = len(ds["xs"])
    i, j = rng.sample(range(n), 2)
    vi, vj = col["vals"][i], col["vals"][j]
    if vi <= 0 or vj <= 0:
        return None
    if vj < vi:
        i, j, vi, vj = j, i, vj, vi
    r = round(vj / vi, 1)
    if r < 1.5 or r > 20:
        return None
    xu = ds["xunit"]
    ai, aj = _at(ds, ds["xstrs"][i]), _at(ds, ds["xstrs"][j])
    prompt = rng.choice([
        f"According to Table 1, {col['desc']} {aj} was approximately how many times "
        f"{col['desc']} {ai}?",
        f"Based on Table 1, the ratio of {col['desc']} {aj} to that {ai} is closest to:",
    ])
    correct = (f"{r:.1f}", f"Correct. {col['strs'][j]} ÷ {col['strs'][i]} ≈ {r:.1f}.")
    inv = round(vi / vj, 2)
    distractors = [(f"{inv:.2f}", f"This divides the smaller value by the larger one "
                                  f"({col['strs'][i]} ÷ {col['strs'][j]}); the question asks the reverse.")]
    diff = round(vj - vi, ds["dec"])
    distractors.append((_fmt(diff, ds["dec"]),
                        "This is the difference between the two values, not their ratio."))
    for k in (j + 1, j - 1, i + 1, i - 1):
        if 0 <= k < n and k not in (i, j) and col["vals"][k] > 0:
            rr = round(max(col["vals"][k], vi) / min(col["vals"][k], vi), 1) if k != i else None
            if rr and rr >= 1.1:
                distractors.append((f"{rr:.1f}",
                                    f"This uses the row for {_vu(ds['xstrs'][k], xu)} instead of "
                                    f"one of the rows asked about."))
                break
    distractors.append((f"{round(r * 2, 1):.1f}", "This doubles the ratio; recompute the quotient."))
    expl = (f"Divide the larger value by the smaller: {col['strs'][j]} ÷ {col['strs'][i]} "
            f"≈ {r:.1f}, so the value {aj} is about {r:.1f} times that {ai}.")
    return _emit(rng, prompt, correct, distractors, subskill="compare_entries",
                 explanation=expl, qtype=QT_TABLE, est=60, tags=DR_TAGS + ["ratio"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("ratio", x1=ds["xstrs"][i], x2=ds["xstrs"][j], col=ci + 1))


def _statements(ds, ci):
    """Candidate (text, truth, rationale_if_false) statements about one column."""
    scen, col = ds["scen"], ds["cols"][ci]
    xs, xu, yu = ds["xstrs"], ds["xunit"], col["unit"]
    vals, strs = col["vals"], col["strs"]
    n = len(vals)
    desc = _cap_first(col["desc"])
    out = []
    imax = max(range(n), key=lambda j: vals[j])
    imin = min(range(n), key=lambda j: vals[j])
    at = [_at(ds, x) for x in xs]
    for i in range(n):
        out.append((f"{desc} was greatest {at[i]}.", i == imax,
                    f"The greatest value, {_vu(strs[imax], yu)}, is {at[imax]}."))
        out.append((f"{desc} was least {at[i]}.", i == imin,
                    f"The least value, {_vu(strs[imin], yu)}, is {at[imin]}."))
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            out.append((f"{desc} was greater {at[a]} than {at[b]}.",
                        vals[a] > vals[b],
                        f"The table lists {_vu(strs[a], yu)} {at[a]} and "
                        f"{_vu(strs[b], yu)} {at[b]}."))
            if vals[b] > 0:
                out.append((f"{desc} {at[a]} was more than twice its value {at[b]}.",
                            vals[a] > 2 * vals[b],
                            f"Twice {_vu(strs[b], yu)} is {_vu(_fmt(2 * vals[b], ds['dec']), yu)}, "
                            f"and the value {at[a]} is {_vu(strs[a], yu)}."))
    up = _strict(vals, True)
    down = _strict(vals, False)
    out.append((f"{desc} increased with every increase in {scen['x_short']}.", up,
                "Reading down the column, the values do not rise at every step."))
    out.append((f"{desc} decreased with every increase in {scen['x_short']}.", down,
                "Reading down the column, the values do not fall at every step."))
    if col["shape"] == "peak":
        out.append((f"{desc} rose to a maximum and then fell.", True, ""))
    else:
        out.append((f"{desc} rose to a maximum and then fell.", False,
                    "The values never reverse direction within the table."))
    return out


def _pick_statements(rng, cands, n_false=3):
    trues = [c for c in cands if c[1]]
    falses = [c for c in cands if not c[1]]
    if not trues or len(falses) < n_false:
        return None
    t = rng.choice(trues)
    rng.shuffle(falses)
    chosen, seen = [], {t[0]}
    for f in falses:
        if f[0] not in seen:
            chosen.append(f)
            seen.add(f[0])
        if len(chosen) == n_false:
            break
    if len(chosen) < n_false:
        return None
    return t, chosen


@_retry
def dr_consistent_statement(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    picked = _pick_statements(rng, _statements(ds, ci))
    if picked is None:
        return None
    t, falses = picked
    prompt = rng.choice([
        "Which of the following statements is consistent with the data in Table 1?",
        "Which statement about the results in Table 1 is supported by the data?",
        "Based on Table 1, which of the following statements is true?",
    ])
    correct = (t[0], "Correct. Checking the listed values confirms this statement.")
    distractors = [(f[0], f[2]) for f in falses]
    expl = f"Test each statement against the table: only \"{t[0]}\" matches the listed values."
    return _emit(rng, prompt, correct, distractors, subskill="consistent_statement",
                 explanation=expl, qtype=QT_TABLE, est=70, tags=DR_TAGS + ["statement"],
                 stimulus=table_stimulus(ds))


@_retry
def dr_condition_compare(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: s.get("cond"))
    ds = build(rng, scen, cond="cond", n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    a, b = ds["cols"]
    n = len(ds["xs"])
    i = rng.randrange(n)
    dec, xu, yu = ds["dec"], ds["xunit"], a["unit"]
    d = round(abs(a["vals"][i] - b["vals"][i]), dec)
    hi = a if a["vals"][i] > b["vals"][i] else b
    lo = b if hi is a else a
    x = _vu(ds["xstrs"][i], xu)
    prompt = rng.choice([
        f"According to Table 1, {_xat(ds, ds['xstrs'][i])}, {a['desc']} was greater under "
        f"which condition, and by how much?",
        f"Based on Table 1, when {scen['x_desc']} was {_xv(ds, ds['xstrs'][i])}, which condition gave the greater "
        f"{a['short']}, and what was the difference between the two conditions?",
    ])
    correct = (f"{_cap_first(hi['label'])}, by {_vu(_fmt(d, dec), yu)}",
               f"Correct. At {x}: {hi['label']} {hi['strs'][i]} versus {lo['label']} "
               f"{lo['strs'][i]}, a difference of {_fmt(d, dec)}.")
    distractors = [(f"{_cap_first(lo['label'])}, by {_vu(_fmt(d, dec), yu)}",
                    f"The difference is right, but {lo['label']} gave the smaller value at {x}.")]
    for j in (i + 1, i - 1, i + 2, i - 2):
        if 0 <= j < n:
            dj = round(abs(a["vals"][j] - b["vals"][j]), dec)
            if dj != d and dj != 0:
                distractors.append((f"{_cap_first(hi['label'])}, by {_vu(_fmt(dj, dec), yu)}",
                                    f"This is the difference in the row for "
                                    f"{_vu(ds['xstrs'][j], xu)}, not for {x}."))
                distractors.append((f"{_cap_first(lo['label'])}, by {_vu(_fmt(dj, dec), yu)}",
                                    f"Wrong condition, and the difference comes from the row for "
                                    f"{_vu(ds['xstrs'][j], xu)}."))
                break
    expl = (f"In the {x} row, compare the two condition columns: {hi['strs'][i]} ({hi['label']}) "
            f"minus {lo['strs'][i]} ({lo['label']}) = {_fmt(d, dec)} {yu}.".strip())
    return _emit(rng, prompt, correct, distractors, subskill="compare_entries",
                 explanation=expl, qtype=QT_TABLE, est=65, tags=DR_TAGS + ["conditions"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("conddiff", x=ds["xstrs"][i]))


@_retry
def dr_count_above(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    vals = col["vals"]
    n = len(vals)
    # threshold strictly between two values so no entry equals it
    srt = sorted(vals)
    k = rng.randrange(n - 1)
    if srt[k] == srt[k + 1]:
        return None
    thr = round((srt[k] + srt[k + 1]) / 2, ds["dec"] + 1)
    if thr in vals:
        return None
    above = rng.random() < 0.5
    count = sum(1 for v in vals if (v > thr if above else v < thr))
    word = "greater" if above else "less"
    thr_s = _vu(f"{thr:.{ds['dec'] + 1}f}".rstrip("0").rstrip("."), col["unit"])
    prompt = rng.choice([
        f"According to Table 1, for how many of the {n} values of {scen['x_short']} tested was "
        f"{col['desc']} {word} than {thr_s}?",
        f"In how many rows of Table 1 is {col['desc']} {word} than {thr_s}?",
    ])
    correct = (str(count), f"Correct. Exactly {count} entries in the {col['header']} column are "
                           f"{word} than {thr_s}.")
    distractors = []
    for c in (count + 1, count - 1, n - count, count + 2, n):
        if 0 <= c <= n and c != count and str(c) not in [d[0] for d in distractors]:
            why = (f"This counts the entries {'less' if above else 'greater'} than {thr_s} instead."
                   if c == n - count else "Recount the column carefully; this is off by one or more.")
            distractors.append((str(c), why))
    expl = (f"Compare each entry in the {col['header']} column with {thr_s}; {count} of the "
            f"{n} entries are {word} than it.")
    return _emit(rng, prompt, correct, distractors, subskill="consistent_statement",
                 explanation=expl, qtype=QT_TABLE, est=55, tags=DR_TAGS + ["count"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("count", op="gt" if above else "lt", v=thr, col=ci + 1))


def _cond_statements(ds):
    scen = ds["scen"]
    a, b = ds["cols"]
    xs, xu, yu = ds["xstrs"], ds["xunit"], a["unit"]
    n = len(xs)
    desc = _cap_first(a["desc"])
    out = []
    b_higher_all = all(vb > va for va, vb in zip(a["vals"], b["vals"]))
    a_higher_all = all(va > vb for va, vb in zip(a["vals"], b["vals"]))
    out.append((f"At every {scen['x_short']} tested, {a['desc']} was higher for {b['label']} than "
                f"for {a['label']}.", b_higher_all,
                f"Compare the two columns row by row; {b['label']} is not higher in every row."))
    out.append((f"At every {scen['x_short']} tested, {a['desc']} was higher for {a['label']} than "
                f"for {b['label']}.", a_higher_all,
                f"Compare the two columns row by row; {a['label']} is not higher in every row."))
    diffs = [abs(va - vb) for va, vb in zip(a["vals"], b["vals"])]
    imax = max(range(n), key=lambda j: diffs[j])
    imin = min(range(n), key=lambda j: diffs[j])
    unique_max = diffs.count(diffs[imax]) == 1
    unique_min = diffs.count(diffs[imin]) == 1
    for i in range(n):
        out.append((f"The difference between the two conditions was greatest at {_vu(xs[i], xu)}.",
                    unique_max and i == imax,
                    f"The largest gap between the columns is at {_vu(xs[imax], xu)} "
                    f"({_vu(_fmt(diffs[imax], ds['dec']), yu)})."))
        out.append((f"The difference between the two conditions was smallest at {_vu(xs[i], xu)}.",
                    unique_min and i == imin,
                    f"The smallest gap between the columns is at {_vu(xs[imin], xu)} "
                    f"({_vu(_fmt(diffs[imin], ds['dec']), yu)})."))
    for col, other in ((a, b), (b, a)):
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                out.append((f"{desc} for {col['label']} at {_vu(xs[i], xu)} was greater than "
                            f"{a['desc']} for {other['label']} at {_vu(xs[j], xu)}.",
                            col["vals"][i] > other["vals"][j],
                            f"The table lists {_vu(col['strs'][i], yu)} ({col['label']}, "
                            f"{_vu(xs[i], xu)}) and {_vu(other['strs'][j], yu)} ({other['label']}, "
                            f"{_vu(xs[j], xu)})."))
    shape = a["shape"]
    both_word = _direction_word(shape)
    out.append((f"Under both conditions, {a['desc']} {both_word} as {scen['x_short']} increased.",
                True, ""))
    opp = {"inc": "decreased", "dec": "increased", "peak": "decreased, then increased"}[shape]
    out.append((f"Under both conditions, {a['desc']} {opp} as {scen['x_short']} increased.",
                False, f"Under both conditions the values {both_word}, not {opp}."))
    return out


@_retry
def dr_condition_statement(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: s.get("cond"))
    ds = build(rng, scen, cond="cond", n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    picked = _pick_statements(rng, _cond_statements(ds))
    if picked is None:
        return None
    t, falses = picked
    prompt = rng.choice([
        "Which of the following statements about the two conditions is supported by Table 1?",
        "Based on Table 1, which statement comparing the two conditions is accurate?",
        "Which conclusion about the two conditions is consistent with the data in Table 1?",
    ])
    correct = (t[0], "Correct. Checking both condition columns confirms this statement.")
    distractors = [(f[0], f[2]) for f in falses]
    expl = (f"Compare the two condition columns row by row. Only \"{t[0]}\" survives that check.")
    return _emit(rng, prompt, correct, distractors, subskill="consistent_statement",
                 explanation=expl, qtype=QT_TABLE, est=80, tags=DR_TAGS + ["conditions", "statement"],
                 stimulus=table_stimulus(ds))


@_retry
def dr_percent_change(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    n = len(ds["xs"])
    i = rng.choice([0, 0, 1])
    j = rng.choice([n - 1, n - 1, n - 2])
    if j <= i:
        return None
    vi, vj = col["vals"][i], col["vals"][j]
    if vi <= 0 or vj <= 0:
        return None
    pct = round((vj - vi) / vi * 100)
    if abs(pct) < 8:
        return None
    wrong_base = round((vj - vi) / vj * 100)
    if abs(wrong_base) > 250:
        wrong_base = round((col["vals"][j - 1] - vi) / vi * 100)   # off-by-one row instead
    half = round(pct / 2)
    dbl = pct * 2
    if len({pct, wrong_base, half, dbl}) < 4:
        return None
    xu = ds["xunit"]
    xi, xj = _vu(ds["xstrs"][i], xu), _vu(ds["xstrs"][j], xu)
    word = "increase" if pct > 0 else "decrease"
    prompt = rng.choice([
        f"According to Table 1, the percent {word} in {col['desc']} from {xi} to {xj} is closest to:",
        f"Based on Table 1, by approximately what percent did {col['desc']} change between "
        f"{xi} and {xj}?",
    ])
    sign = "" if prompt.startswith("According") else ("+" if pct > 0 else "−")
    def ps(v):
        return f"{sign}{abs(v)}%" if sign else f"{abs(v)}%"
    correct = (ps(pct), f"Correct. ({col['strs'][j]} − {col['strs'][i]}) ÷ {col['strs'][i]} × 100 "
                        f"≈ {abs(pct)}%.")
    distractors = [
        (ps(wrong_base), f"This divides by the final value ({col['strs'][j]}) instead of the "
                         f"starting value ({col['strs'][i]})." if abs(round((vj - vi) / vj * 100)) <= 250
         else f"This uses the row for {_vu(ds['xstrs'][j - 1], xu)} instead of {xj}."),
        (ps(half), "This is half the actual percent change; recheck the arithmetic."),
        (ps(dbl), "This is double the actual percent change; recheck the arithmetic."),
    ]
    expl = (f"Percent change = (final − initial) ÷ initial × 100 = ({col['strs'][j]} − "
            f"{col['strs'][i]}) ÷ {col['strs'][i]} × 100 ≈ {abs(pct)}% {word}.")
    return _emit(rng, prompt, correct, distractors, subskill="compare_entries",
                 explanation=expl, qtype=QT_TABLE, est=75, tags=DR_TAGS + ["percent"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("pct", x1=ds["xstrs"][i], x2=ds["xstrs"][j], col=ci + 1))


@_retry
def dr_cross_condition_lookup(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: s.get("cond"))
    ds = build(rng, scen, cond="cond", n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    a, b = ds["cols"]
    src, dst = (a, b) if rng.random() < 0.5 else (b, a)
    n = len(ds["xs"])
    i = rng.randrange(n)
    # a target value closer to src[i] than to any other src entry
    unit = 10 ** (-ds["dec"])
    gaps = [abs(src["vals"][j] - src["vals"][i]) for j in range(n) if j != i]
    if min(gaps) < 4 * unit:
        return None
    delta = rng.choice([-1, 1]) * unit * rng.randint(1, max(1, int(min(gaps) / unit / 3)))
    target = round(src["vals"][i] + delta, ds["dec"])
    if target in src["vals"]:
        return None
    ts = _vu(_fmt(target, ds["dec"]), src["unit"])
    xu, yu = ds["xunit"], a["unit"]
    prompt = rng.choice([
        f"Consider the {scen['x_short']} in Table 1 at which {a['desc']} for {src['label']} was "
        f"closest to {ts}. At that {scen['x_short']}, {a['desc']} for {dst['label']} was:",
        f"In Table 1, find the row in which {a['desc']} for {src['label']} is nearest {ts}. What "
        f"was {a['desc']} for {dst['label']} in that row?",
    ])
    correct = (_vu(dst["strs"][i], yu),
               f"Correct. The {src['label']} value closest to {ts} is {src['strs'][i]}, at "
               f"{_vu(ds['xstrs'][i], xu)}; the {dst['label']} entry in that row is {dst['strs'][i]}.")
    distractors = [(_vu(src["strs"][i], yu),
                    f"This is the {src['label']} value in that row; the question asks for "
                    f"the {dst['label']} value.")]
    for j in sorted(range(n), key=lambda j: abs(j - i)):
        if j != i and len(distractors) < 3:
            distractors.append((_vu(dst["strs"][j], yu),
                                f"This is the {dst['label']} value for {_vu(ds['xstrs'][j], xu)}, "
                                f"a different row."))
    expl = (f"First locate the {src['label']} entry nearest {ts}: {src['strs'][i]} at "
            f"{_vu(ds['xstrs'][i], xu)}. Then read the {dst['label']} column in that row: "
            f"{_vu(dst['strs'][i], yu)}.")
    return _emit(rng, prompt, correct, distractors, subskill="table_lookup",
                 explanation=expl, qtype=QT_TABLE, est=80, tags=DR_TAGS + ["conditions", "lookup"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("closest_then", v=target, src=2 if src is b else 1,
                              dst=2 if dst is b else 1))


@_retry
def dr_average(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    n = len(ds["xs"])
    i = rng.randrange(n - 2)
    seg = col["vals"][i:i + 3]
    dec = ds["dec"]
    avg = round(sum(seg) / 3, dec)
    xu, yu = ds["xunit"], col["unit"]
    xi, xk = _vu(ds["xstrs"][i], xu), _vu(ds["xstrs"][i + 2], xu)
    prompt = rng.choice([
        f"According to Table 1, the average of {col['desc']} for the three values of "
        f"{scen['x_short']} from {xi} to {xk} is closest to:",
        f"Based on Table 1, what is the approximate mean of {col['desc']} over the rows from "
        f"{xi} through {xk}?",
    ])
    correct = (_vu(_fmt(avg, dec), yu),
               f"Correct. ({' + '.join(col['strs'][i:i + 3])}) ÷ 3 ≈ {_fmt(avg, dec)}.")
    distractors = []
    if i + 3 < n:
        a2 = round(sum(col["vals"][i + 1:i + 4]) / 3, dec)
        distractors.append((_vu(_fmt(a2, dec), yu),
                            f"This averages the rows from {_vu(ds['xstrs'][i + 1], xu)} to "
                            f"{_vu(ds['xstrs'][i + 3], xu)} instead."))
    if i - 1 >= 0:
        a3 = round(sum(col["vals"][i - 1:i + 2]) / 3, dec)
        distractors.append((_vu(_fmt(a3, dec), yu),
                            f"This averages the rows from {_vu(ds['xstrs'][i - 1], xu)} to "
                            f"{_vu(ds['xstrs'][i + 1], xu)} instead."))
    two = round((seg[0] + seg[2]) / 2, dec)
    distractors.append((_vu(_fmt(two, dec), yu),
                        "This averages only the first and last of the three values."))
    tot = round(sum(seg), dec)
    distractors.append((_vu(_fmt(tot, dec), yu), "This is the sum of the three values, not their mean."))
    expl = (f"Add the three entries ({', '.join(col['strs'][i:i + 3])}) and divide by 3: "
            f"about {_vu(_fmt(avg, dec), yu)}.")
    return _emit(rng, prompt, correct, distractors, subskill="compare_entries",
                 explanation=expl, qtype=QT_TABLE, est=75, tags=DR_TAGS + ["average"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("avg3", x1=ds["xstrs"][i], col=ci + 1))


@_retry
def dr_figure_biggest_step(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: len(s["series"]) == 1 and s["shape"] != "peak")
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    col = ds["cols"][0]
    vals = col["vals"]
    steps = [abs(b - a) for a, b in zip(vals, vals[1:])]
    m = max(steps)
    if steps.count(m) != 1 or sorted(steps)[-1] - sorted(steps)[-2] < 0.15 * m:
        return None
    k = steps.index(m)
    xu = ds["xunit"]
    word = "increase" if col["shape"] == "inc" else "decrease"
    prompt = rng.choice([
        f"According to Figure 1, between which two consecutive values of {scen['x_short']} did "
        f"{col['desc']} {word} the most?",
        f"Based on Figure 1, the largest {word} in {col['desc']} between neighboring points "
        f"occurred between:",
    ])
    def pair(j):
        return f"{_vu(ds['xstrs'][j], xu)} and {_vu(ds['xstrs'][j + 1], xu)}"
    correct = (pair(k), f"Correct. The points at {pair(k)} are the farthest apart vertically "
                        f"({_fmt(m, ds['dec'])} {col['unit']}).".replace(" )", ")"))
    distractors = []
    for j in sorted(range(len(steps)), key=lambda j: -steps[j]):
        if j != k and len(distractors) < 3:
            distractors.append((pair(j), f"The vertical change between these points is only "
                                         f"{_fmt(steps[j], ds['dec'])}, less than {_fmt(m, ds['dec'])}."))
    expl = (f"Compare the vertical gaps between neighboring points; the gap between {pair(k)} "
            f"is the largest.")
    return _emit(rng, prompt, correct, distractors, subskill="figure_reading",
                 explanation=expl, qtype=QT_MC, est=70, tags=DR_TAGS + ["figure"],
                 stimulus=figure_stimulus(ds), verify=_spec("fig_maxstep"))


# --------------------------------------------------------------------------- #
# Trends and extrapolation
# --------------------------------------------------------------------------- #
TR_TAGS = ["science", "trends"]

_SHAPE_TEXT = {
    "inc_const": "increased by approximately the same amount for each step in {x}",
    "inc_slow": "increased, but by smaller and smaller amounts",
    "inc_acc": "increased, by larger and larger amounts",
    "dec_const": "decreased by approximately the same amount for each step in {x}",
    "dec_slow": "decreased, but by smaller and smaller amounts",
    "dec_acc": "decreased, by larger and larger amounts",
    "peak": "increased to a maximum and then decreased",
}


def _classify(vals, dec):
    """Shape + pacing of a monotone column from its rounded values."""
    diffs = [b - a for a, b in zip(vals, vals[1:])]
    if all(d > 0 for d in diffs):
        base = "inc"
    elif all(d < 0 for d in diffs):
        base = "dec"
    else:
        i = max(range(len(vals)), key=lambda j: vals[j])
        if 0 < i < len(vals) - 1 and _strict(vals[:i + 1], True) and _strict(vals[i:], False):
            return "peak"
        return None
    m = [abs(d) for d in diffs]
    unit = 10 ** (-dec)
    mean = sum(m) / len(m)
    if max(m) - min(m) <= max(0.12 * mean, 1.5 * unit):
        return base + "_const"
    if all(b < a for a, b in zip(m, m[1:])) and m[-1] <= 0.8 * m[0]:
        return base + "_slow"
    if all(b > a for a, b in zip(m, m[1:])) and m[-1] >= 1.25 * m[0]:
        return base + "_acc"
    return None


@_retry
def tr_trend_shape(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty) if difficulty != "easy" else 5)
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    kind = _classify(col["vals"], ds["dec"])
    if kind is None:
        return None
    x0, x1 = _vu(ds["xstrs"][0], ds["xunit"]), _vu(ds["xstrs"][-1], ds["xunit"])
    prompt = rng.choice([
        f"Which of the following best describes how {col['desc']} changed as {scen['x_desc']} "
        f"increased from {x0} to {x1}?",
        f"According to Table 1, as {scen['x_desc']} increased, {col['desc']}:",
        f"Based on Table 1, which statement best describes the trend in {col['desc']} "
        f"{_range_phrase(scen)}?",
    ])
    texts = {k: v.format(x=scen["x_short"]) for k, v in _SHAPE_TEXT.items()}
    why = {
        "inc_const": "The increases from row to row are not all about the same size.",
        "inc_slow": "The increases do not get steadily smaller down the column.",
        "inc_acc": "The increases do not get steadily larger down the column.",
        "dec_const": "The decreases from row to row are not all about the same size.",
        "dec_slow": "The decreases do not get steadily smaller down the column.",
        "dec_acc": "The decreases do not get steadily larger down the column.",
        "peak": "The values never reverse direction within the table.",
    }
    base = kind.split("_")[0]
    if base == "inc":
        for k in ("dec_const", "dec_slow", "dec_acc"):
            why[k] = "The values rise down the column; they never decrease."
    elif base == "dec":
        for k in ("inc_const", "inc_slow", "inc_acc"):
            why[k] = "The values fall down the column; they never increase."
    diffs = [round(b - a, ds["dec"]) for a, b in zip(col["vals"], col["vals"][1:])]
    dtxt = ", ".join(_fmt(abs(d), ds["dec"]) for d in diffs)
    correct = (texts[kind], f"Correct. The row-to-row changes are {dtxt}, which fits this description.")
    pool = [k for k in texts if k != kind]
    # Always include the opposite direction and the two other pacings of the same direction.
    same = [k for k in pool if k.startswith(base)] if base != "peak" else []
    opp = [k for k in pool if not k.startswith(base) and k != "peak"]
    rng.shuffle(same)
    rng.shuffle(opp)
    keys = (same[:2] + opp[:1]) if base != "peak" else opp[:3]
    distractors = [(texts[k], why[k]) for k in keys]
    expl = (f"Compute the change between consecutive rows ({dtxt}). "
            f"{_cap_first(col['desc'])} {texts[kind]}.")
    return _emit(rng, prompt, correct, distractors, subskill="trend_shape",
                 explanation=expl, qtype=QT_TABLE, est=60, tags=TR_TAGS + ["shape"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("shape", col=ci + 1, expect=kind))


@_retry
def tr_interpolate_range(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: s["shape"] != "peak" and s["x_short"] != "year")
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    if col["shape"] == "peak":
        return None
    n = len(ds["xs"])
    i = rng.randrange(n - 1)
    xa, xb = ds["xs"][i], ds["xs"][i + 1]
    xm = (xa + xb) / 2
    if not float(xm).is_integer():
        xm = round(xm, 1)
    xu, yu = ds["xunit"], col["unit"]
    lo, hi = sorted([col["vals"][i], col["vals"][i + 1]])
    lo_s, hi_s = _fmt(lo, ds["dec"]), _fmt(hi, ds["dec"])
    prompt = rng.choice([
        f"Based on the trend in Table 1, if {scen['x_desc']} had been {_xv(ds, _xstr(xm))}, "
        f"{col['desc']} would most likely have been:",
        f"Suppose a trial had been run {_xat(ds, _xstr(xm))}. Based on Table 1, {col['desc']} "
        f"would most likely have been:",
    ])
    def between(a, b):
        return f"between {_vu(a, yu)} and {_vu(b, yu)}"
    correct = (between(lo_s, hi_s),
               f"Correct. {_vu(_xstr(xm), xu)} lies between {_vu(ds['xstrs'][i], xu)} and "
               f"{_vu(ds['xstrs'][i + 1], xu)}, whose values are {lo_s} and {hi_s}.")
    distractors = []
    vmin, vmax = min(col["vals"]), max(col["vals"])
    distractors.append((f"below every listed value, less than {_vu(_fmt(vmin, ds['dec']), yu)}",
                        "This is below every value in the table; the trend has no reason to jump there."))
    distractors.append((f"above every listed value, greater than {_vu(_fmt(vmax, ds['dec']), yu)}",
                        "This is above every value in the table; the trend has no reason to jump there."))
    if i + 2 < n:
        a2, b2 = sorted([col["vals"][i + 1], col["vals"][i + 2]])
        distractors.append((between(_fmt(a2, ds["dec"]), _fmt(b2, ds["dec"])),
                            f"This is the interval for {scen['x_short']} between "
                            f"{_vu(ds['xstrs'][i + 1], xu)} and {_vu(ds['xstrs'][i + 2], xu)}."))
    elif i - 1 >= 0:
        a2, b2 = sorted([col["vals"][i - 1], col["vals"][i]])
        distractors.append((between(_fmt(a2, ds["dec"]), _fmt(b2, ds["dec"])),
                            f"This is the interval for {scen['x_short']} between "
                            f"{_vu(ds['xstrs'][i - 1], xu)} and {_vu(ds['xstrs'][i], xu)}."))
    expl = (f"{_vu(_xstr(xm), xu)} falls between the rows for {_vu(ds['xstrs'][i], xu)} and "
            f"{_vu(ds['xstrs'][i + 1], xu)}; since the values change steadily, the result should "
            f"fall between {lo_s} and {hi_s} {yu}.".strip())
    return _emit(rng, prompt, correct, distractors, subskill="interpolation",
                 explanation=expl, qtype=QT_TABLE, est=60, tags=TR_TAGS + ["interpolate"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("interp_range", x=_xstr(xm), col=ci + 1))


@_retry
def tr_beyond_direction(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: s["shape"] != "peak" or len(s["series"]) > 1)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    if col["shape"] == "peak":
        return None
    n = len(ds["xs"])
    step = ds["xs"][1] - ds["xs"][0]
    xn = ds["xs"][-1] + step
    xu, yu = ds["xunit"], col["unit"]
    v = col["strs"]
    up = col["shape"] == "inc"
    prompt = rng.choice([
        f"If the trend in Table 1 continued, {col['desc']} {_xat(ds, _xstr(xn))} would most "
        f"likely be:",
        f"Based on Table 1, if a trial were run {_xat(ds, _xstr(xn))}, {col['desc']} would most "
        f"likely be:",
    ])
    last, prev, first = _vu(v[-1], yu), _vu(v[-2], yu), _vu(v[0], yu)
    if up:
        correct = (f"greater than {last}",
                   f"Correct. The values rise with every row, so the next value should exceed the last one, {last}.")
        distractors = [
            (f"between {prev} and {last}", "This would require the trend to reverse and fall back below the last value."),
            (f"between {first} and {prev}", "These are values from earlier rows; the trend has already moved past them."),
            (f"less than {first}", "This is below the very first value; the data rise, not fall."),
        ]
    else:
        correct = (f"less than {last}",
                   f"Correct. The values fall with every row, so the next value should be below the last one, {last}.")
        distractors = [
            (f"between {last} and {prev}", "This would require the trend to reverse and climb back above the last value."),
            (f"between {prev} and {first}", "These are values from earlier rows; the trend has already moved past them."),
            (f"greater than {first}", "This is above the very first value; the data fall, not rise."),
        ]
    expl = (f"Every step in {scen['x_short']} {'raised' if up else 'lowered'} {col['desc']}, so one "
            f"more step beyond {_vu(ds['xstrs'][-1], xu)} should give a value "
            f"{'greater' if up else 'less'} than {last}.")
    return _emit(rng, prompt, correct, distractors, subskill="extrapolation",
                 explanation=expl, qtype=QT_TABLE, est=55, tags=TR_TAGS + ["extrapolate"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("beyond", col=ci + 1, expect="gt" if up else "lt"))


@_retry
def tr_figure_trend(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: len(s["series"]) == 1)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    col = ds["cols"][0]
    shape = col["shape"]
    prompt = rng.choice([
        f"Which of the following best describes the relationship between {scen['x_short']} and "
        f"{col['short']} shown in Figure 1?",
        f"According to Figure 1, as {scen['x_desc']} increases, {col['desc']}:",
    ])
    texts = {
        "inc": "increases",
        "dec": "decreases",
        "peak": "increases, then decreases",
        "valley": "decreases, then increases",
        "flat": "stays about the same",
    }
    why = {
        "inc": "The points would have to climb from left to right; they do not.",
        "dec": "The points would have to fall from left to right; they do not.",
        "peak": "The points would have to rise and then fall; they do not reverse.",
        "valley": "The points would have to fall and then rise; they do not.",
        "flat": "The points change height clearly from left to right.",
    }
    if shape == "inc":
        why["peak"] = "The points keep climbing to the rightmost one; they never turn down."
    if shape == "dec":
        why["valley"] = "The points keep falling to the rightmost one; they never turn up."
    correct = (texts[shape], "Correct. Reading the points from left to right shows this pattern.")
    others = [k for k in texts if k != shape]
    rng.shuffle(others)
    distractors = [(texts[k], why[k]) for k in others[:3]]
    expl = (f"Follow the points from left (small {scen['x_short']}) to right (large "
            f"{scen['x_short']}): {col['desc']} {texts[shape]}.")
    return _emit(rng, prompt, correct, distractors, subskill="trend_shape",
                 explanation=expl, qtype=QT_MC, est=45, tags=TR_TAGS + ["figure"],
                 stimulus=figure_stimulus(ds, with_line=(shape != "peak")),
                 verify=_spec("fig_trend", expect=shape))


@_retry
def tr_interpolate_value(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: s["shape"] != "peak" and s["x_short"] != "year")
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    if col["shape"] == "peak":
        return None
    n = len(ds["xs"])
    i = rng.randrange(n - 1)
    xa, xb = ds["xs"][i], ds["xs"][i + 1]
    frac = rng.choice([0.5, 0.5, 0.25, 0.75])
    xm = xa + frac * (xb - xa)
    xm_s = _xstr(xm) if float(xm).is_integer() else f"{xm:g}"
    va, vb = col["vals"][i], col["vals"][i + 1]
    dec = ds["dec"]
    est_v = round(va + frac * (vb - va), dec)
    unit = 10 ** (-dec)
    if abs(est_v - va) < 2 * unit or abs(est_v - vb) < 2 * unit:
        return None
    xu, yu = ds["xunit"], col["unit"]
    prompt = rng.choice([
        f"Based on Table 1, if {scen['x_desc']} had been {_xv(ds, xm_s)}, {col['desc']} would "
        f"have been closest to:",
        f"According to the trend in Table 1, {col['desc']} {_xat(ds, xm_s)} would most likely "
        f"have been closest to:",
    ])
    frac_word = {0.5: "halfway", 0.25: "a quarter of the way", 0.75: "three-quarters of the way"}[frac]
    correct = (_vu(_fmt(est_v, dec), yu),
               f"Correct. {_vu(xm_s, xu)} is {frac_word} from {_vu(ds['xstrs'][i], xu)} to "
               f"{_vu(ds['xstrs'][i + 1], xu)}, so the value should be about that far from "
               f"{col['strs'][i]} toward {col['strs'][i + 1]}.")
    distractors = [
        (_vu(col["strs"][i], yu), f"This is the value for {_vu(ds['xstrs'][i], xu)}; the question asks "
                                  f"about a {scen['x_short']} beyond that row."),
        (_vu(col["strs"][i + 1], yu), f"This is the value for {_vu(ds['xstrs'][i + 1], xu)}, not the "
                                      f"intermediate {scen['x_short']} asked about."),
    ]
    outside = round(vb + (vb - va) * frac, dec)
    distractors.append((_vu(_fmt(outside, dec), yu),
                        f"This continues past {_vu(ds['xstrs'][i + 1], xu)} instead of staying between "
                        f"the two bracketing rows."))
    wrong_frac = round(va + (1 - frac) * (vb - va), dec) if frac != 0.5 else None
    if wrong_frac is not None:
        distractors.append((_vu(_fmt(wrong_frac, dec), yu),
                            "This measures the fraction from the wrong end of the interval."))
    expl = (f"{_vu(xm_s, xu)} lies between {_vu(ds['xstrs'][i], xu)} ({col['strs'][i]}) and "
            f"{_vu(ds['xstrs'][i + 1], xu)} ({col['strs'][i + 1]}). Assuming a steady change, "
            f"{col['strs'][i]} + {frac:g} × ({col['strs'][i + 1]} − {col['strs'][i]}) ≈ "
            f"{_fmt(est_v, dec)}.")
    return _emit(rng, prompt, correct, distractors, subskill="interpolation",
                 explanation=expl, qtype=QT_TABLE, est=75, tags=TR_TAGS + ["interpolate"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("interp", x=xm_s, col=ci + 1))


@_retry
def tr_x_for_target(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: s["shape"] != "peak" or len(s["series"]) > 1)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    if col["shape"] == "peak":
        return None
    n = len(ds["xs"])
    i = rng.randrange(n - 1)
    va, vb = col["vals"][i], col["vals"][i + 1]
    dec = ds["dec"]
    target = round((va + vb) / 2, dec)
    if target in (va, vb) or target in col["vals"]:
        return None
    xu, yu = ds["xunit"], col["unit"]
    ts = _vu(_fmt(target, dec), yu)
    prompt = rng.choice([
        f"Based on Table 1, {col['desc']} would most likely have equaled {ts} "
        f"{'in a year' if scen['x_short'] == 'year' else 'at a ' + scen['x_short']} between:",
        f"According to the data in Table 1, at which of the following {scen['x_short']} ranges "
        f"would {col['desc']} most likely have been {ts}?",
    ])
    def pair(j):
        return f"{_vu(ds['xstrs'][j], xu)} and {_vu(ds['xstrs'][j + 1], xu)}"
    correct = (pair(i), f"Correct. {ts} lies between {col['strs'][i]} (at {_vu(ds['xstrs'][i], xu)}) "
                        f"and {col['strs'][i + 1]} (at {_vu(ds['xstrs'][i + 1], xu)}).")
    distractors = []
    for j in sorted(range(n - 1), key=lambda j: abs(j - i)):
        if j != i and len(distractors) < 3:
            distractors.append((pair(j), f"Over this range the values run from {col['strs'][j]} to "
                                         f"{col['strs'][j + 1]}, which does not include {ts}."))
    if len(distractors) < 3:
        step = ds["xs"][1] - ds["xs"][0]
        distractors.append((f"{_vu(ds['xstrs'][-1], xu)} and {_vu(_xstr(ds['xs'][-1] + step), xu)}",
                            f"This is beyond the table, but {ts} is already bracketed by two listed rows."))
    expl = (f"Find the two consecutive rows whose values bracket {ts}: {col['strs'][i]} and "
            f"{col['strs'][i + 1]}, at {pair(i)}.")
    return _emit(rng, prompt, correct, distractors, subskill="interpolation",
                 explanation=expl, qtype=QT_TABLE, est=70, tags=TR_TAGS + ["target"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("target", v=_fmt(target, dec), col=ci + 1))


_BUCKETS = {
    "double": "approximately doubled",
    "quad": "approximately quadrupled",
    "half": "decreased to approximately half its value",
    "quarter": "decreased to approximately one-fourth of its value",
    "inc_lt2": "increased, but to less than twice its value",
    "inc_gt2": "more than doubled but less than quadrupled",
    "dec_lt_half": "decreased, but to more than half its value",
}


def _bucket(r):
    if 1.9 <= r <= 2.1:
        return "double"
    if 3.8 <= r <= 4.2:
        return "quad"
    if 0.48 <= r <= 0.52:
        return "half"
    if 0.23 <= r <= 0.27:
        return "quarter"
    if 1.05 <= r <= 1.85:
        return "inc_lt2"
    if 2.2 <= r <= 3.7:
        return "inc_gt2"
    if 0.55 <= r <= 0.95:
        return "dec_lt_half"
    return None


@_retry
def tr_doubling(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: len(s["series"]) == 1 and s["shape"] != "peak"
                          and s["xs"][0] > 0)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    col = ds["cols"][0]
    xs = ds["xs"]
    pairs = [(i, xs.index(2 * x)) for i, x in enumerate(xs) if 2 * x in xs]
    if not pairs:
        return None
    i, j = rng.choice(pairs)
    if col["vals"][i] <= 0:
        return None
    r = col["vals"][j] / col["vals"][i]
    b = _bucket(r)
    if b is None:
        return None
    xu = ds["xunit"]
    prompt = rng.choice([
        f"According to Table 1, when {scen['x_desc']} doubled from {_vu(ds['xstrs'][i], xu)} to "
        f"{_vu(ds['xstrs'][j], xu)}, {col['desc']}:",
        f"Based on Table 1, doubling {scen['x_desc']} from {_vu(ds['xstrs'][i], xu)} to "
        f"{_vu(ds['xstrs'][j], xu)} caused {col['desc']} to have:",
    ])
    correct = (_BUCKETS[b], f"Correct. {col['strs'][j]} ÷ {col['strs'][i]} ≈ {r:.2f}.")
    others = [k for k in _BUCKETS if k != b]
    rng.shuffle(others)
    distractors = [(_BUCKETS[k], f"The ratio of the two values is {r:.2f}, which does not match "
                                 f"this description.") for k in others[:3]]
    expl = (f"Divide the value at {_vu(ds['xstrs'][j], xu)} by the value at {_vu(ds['xstrs'][i], xu)}: "
            f"{col['strs'][j]} ÷ {col['strs'][i]} ≈ {r:.2f}, so {col['desc']} {_BUCKETS[b]}.")
    return _emit(rng, prompt, correct, distractors, subskill="proportional_reasoning",
                 explanation=expl, qtype=QT_TABLE, est=70, tags=TR_TAGS + ["doubling"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("double", x1=ds["xstrs"][i], x2=ds["xstrs"][j], bucket=b))


@_retry
def tr_biggest_step(rng, difficulty):
    scen = _pick_scenario(rng)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    vals = col["vals"]
    steps = [abs(b - a) for a, b in zip(vals, vals[1:])]
    m = max(steps)
    if steps.count(m) != 1 or sorted(steps)[-1] - sorted(steps)[-2] < 1.5 * 10 ** (-ds["dec"]):
        return None
    k = steps.index(m)
    xu, yu = ds["xunit"], col["unit"]
    prompt = rng.choice([
        f"According to Table 1, between which two consecutive values of {scen['x_short']} did "
        f"{col['desc']} change by the greatest amount?",
        f"Based on Table 1, the largest change in {col['desc']} between neighboring rows occurred "
        f"between:",
    ])
    def pair(j):
        return f"{_vu(ds['xstrs'][j], xu)} and {_vu(ds['xstrs'][j + 1], xu)}"
    correct = (pair(k), f"Correct. The change here is {_vu(_fmt(m, ds['dec']), yu)}, larger than any "
                        f"other consecutive change.")
    distractors = []
    for j in sorted(range(len(steps)), key=lambda j: -steps[j]):
        if j != k and len(distractors) < 3:
            distractors.append((pair(j), f"The change here is only {_vu(_fmt(steps[j], ds['dec']), yu)}."))
    expl = (f"Subtract each value from the next: the changes are "
            f"{', '.join(_fmt(s, ds['dec']) for s in steps)}. The largest, {_fmt(m, ds['dec'])}, "
            f"is between {pair(k)}.")
    return _emit(rng, prompt, correct, distractors, subskill="trend_shape",
                 explanation=expl, qtype=QT_TABLE, est=65, tags=TR_TAGS + ["step"],
                 stimulus=table_stimulus(ds), verify=_spec("maxstep", col=ci + 1))


@_retry
def tr_extrapolate_value(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: s["shape"] != "peak" or len(s["series"]) > 1)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    if col["shape"] == "peak":
        return None
    xs, vals, dec = ds["xs"], col["vals"], ds["dec"]
    step = xs[-1] - xs[-2]
    d = vals[-1] - vals[-2]
    if abs(d) < 3 * 10 ** (-dec):
        return None
    xn = xs[-1] + step
    pred = round(vals[-1] + d, dec)
    if pred < 0:
        return None
    xu, yu = ds["xunit"], col["unit"]
    last2 = f"{_vu(ds['xstrs'][-2], xu)} and {_vu(ds['xstrs'][-1], xu)}"
    prompt = rng.choice([
        f"Suppose the trend between {last2} continued at the same rate. {_cap_first(col['desc'])} "
        f"{_xat(ds, _xstr(xn))} would be closest to:",
        f"If {col['desc']} kept changing at the same rate as it did between {last2}, its value "
        f"{_xat(ds, _xstr(xn))} would be closest to:",
    ])
    ds_ = _neg(_fmt(d, dec))
    correct = (_vu(_fmt(pred, dec), yu),
               f"Correct. The last change was {ds_}; adding it again to {col['strs'][-1]} "
               f"gives {_fmt(pred, dec)}.")
    distractors = [
        (_vu(col["strs"][-1], yu), "This assumes no further change, but the trend continues."),
        (_vu(_fmt(round(vals[-1] + d / 2, dec), dec), yu),
         "This adds only half of the last change; the step size is the same as before."),
        (_vu(_fmt(round(vals[-1] + 2 * d, dec), dec), yu),
         "This adds twice the last change; one more step should add it once."),
    ]
    rev = round(vals[-1] - d, dec)
    distractors.append((_vu(_fmt(rev, dec), yu), "This extrapolates in the wrong direction (back toward "
                                                 "earlier values)."))
    expl = (f"The change between {last2} is {col['strs'][-1]} − {col['strs'][-2]} = {ds_}. "
            f"One more step of {_xstep(ds, step)} adds the same change: {col['strs'][-1]} + "
            f"({ds_}) = {_fmt(pred, dec)}.")
    return _emit(rng, prompt, correct, distractors, subskill="extrapolation",
                 explanation=expl, qtype=QT_TABLE, est=80, tags=TR_TAGS + ["extrapolate"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("extrap", x=_xstr(xn), col=ci + 1))


@_retry
def tr_crossing(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: len(s["series"]) == 2)
    ds = build(rng, scen, n=rng.randint(5, 7))
    if ds is None:
        return None
    a, b = ds["cols"]
    n = len(ds["xs"])
    # b rises, a falls; find first year b > a
    firsts = [i for i in range(n) if b["vals"][i] > a["vals"][i]]
    if not firsts or firsts[0] == 0 or any(a["vals"][i] == b["vals"][i] for i in range(n)):
        return None
    k = firsts[0]
    xu = ds["xunit"]
    mode = rng.choice(["first_exceed", "closest"])
    if mode == "first_exceed":
        prompt = rng.choice([
            f"According to Table 1, {a['desc'].replace('the number of ', '')} were first outnumbered by "
            f"{b['desc'].replace('the number of ', '')} in which {scen['x_short']}?"
            if scen["id"] == "frogs" else
            f"According to Table 1, {b['desc']} first exceeded {a['desc']} in which {scen['x_short']}?",
            f"Based on Table 1, in which {scen['x_short']} was {b['short']} first greater than "
            f"{a['short']}?",
        ])
        correct = (_vu(ds["xstrs"][k], xu),
                   f"Correct. In {ds['xstrs'][k]}, {b['name']} ({b['strs'][k]}) exceeds {a['name']} "
                   f"({a['strs'][k]}) for the first time; the row before has {b['strs'][k - 1]} versus "
                   f"{a['strs'][k - 1]}.")
        distractors = []
        for j in sorted(range(n), key=lambda j: abs(j - k)):
            if j != k and len(distractors) < 3:
                if j < k:
                    why = (f"In {ds['xstrs'][j]}, {b['name']} ({b['strs'][j]}) was still below "
                           f"{a['name']} ({a['strs'][j]}).")
                else:
                    why = (f"{b['name']} already exceeded {a['name']} before {ds['xstrs'][j]}.")
                distractors.append((_vu(ds["xstrs"][j], xu), why))
        expl = (f"Compare the two columns row by row; {ds['xstrs'][k]} is the first row where the "
                f"{b['name']} value is larger than the {a['name']} value.")
        verify = _spec("first_exceed")
    else:
        gaps = [abs(a["vals"][i] - b["vals"][i]) for i in range(n)]
        m = min(gaps)
        if gaps.count(m) != 1:
            return None
        c = gaps.index(m)
        prompt = rng.choice([
            f"According to Table 1, in which {scen['x_short']} were {a['short']} and {b['short']} "
            f"most nearly equal?",
            f"Based on Table 1, the two values in the table were closest to each other in which "
            f"{scen['x_short']}?",
        ])
        correct = (_vu(ds["xstrs"][c], xu),
                   f"Correct. In {ds['xstrs'][c]} the values are {a['strs'][c]} and {b['strs'][c]}, "
                   f"a gap of only {_fmt(m, ds['dec'])}.")
        distractors = []
        for j in sorted(range(n), key=lambda j: gaps[j]):
            if j != c and len(distractors) < 3:
                distractors.append((_vu(ds["xstrs"][j], xu),
                                    f"In {ds['xstrs'][j]} the gap is {_fmt(gaps[j], ds['dec'])}, "
                                    f"larger than in {ds['xstrs'][c]}."))
        expl = (f"Find the difference between the two columns in each row; the smallest difference, "
                f"{_fmt(m, ds['dec'])}, is in {ds['xstrs'][c]}.")
        verify = _spec("closest_pair")
    return _emit(rng, prompt, correct, distractors, subskill="series_crossing",
                 explanation=expl, qtype=QT_TABLE, est=75, tags=TR_TAGS + ["crossing"],
                 stimulus=table_stimulus(ds), verify=verify)


@_retry
def tr_reach_threshold(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: s["shape"] != "peak" or len(s["series"]) > 1)
    ds = build(rng, scen, n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    ci = rng.randrange(len(ds["cols"]))
    col = ds["cols"][ci]
    if col["shape"] == "peak":
        return None
    xs, vals, dec = ds["xs"], col["vals"], ds["dec"]
    step = xs[-1] - xs[-2]
    d = round(vals[-1] - vals[-2], dec)
    if abs(d) < 3 * 10 ** (-dec):
        return None
    k = rng.choice([2, 3, 4])
    target = round(vals[-1] + k * d, dec)
    if target < 0:
        return None
    xk = xs[-1] + k * step
    xu, yu = ds["xunit"], col["unit"]
    ts = _vu(_fmt(target, dec), yu)
    word = "reach" if d > 0 else "fall to"
    at_which = "in approximately which year" if scen["x_short"] == "year" else \
        f"at approximately what {scen['x_short']}"
    prompt = rng.choice([
        f"Assume {col['desc']} continues to change at the same rate as between "
        f"{_vu(ds['xstrs'][-2], xu)} and {_vu(ds['xstrs'][-1], xu)}. It would first {word} {ts} "
        f"{at_which}?",
        f"If the rate of change shown in the last two rows of Table 1 continued, {at_which} would "
        f"{col['desc']} {word} {ts}?",
    ])
    ds_ = _neg(_fmt(d, dec))
    correct = (_vu(_xstr(xk), xu),
               f"Correct. Each step of {_xstep(ds, step)} changes the value by {ds_}; "
               f"{k} more steps are needed to go from {col['strs'][-1]} to {_fmt(target, dec)}.")
    distractors = []
    for kk in (k - 1, k + 1, 2 * k, k + 2):
        xx = xs[-1] + kk * step
        if kk >= 1 and _xstr(xx) != _xstr(xk) and len(distractors) < 3:
            vk = round(vals[-1] + kk * d, dec)
            why = (f"After {kk} step{'s' if kk != 1 else ''} the value would be {_fmt(vk, dec)}, "
                   f"not {_fmt(target, dec)}." if vk >= 0 else
                   f"After {kk} steps the trend would already have passed {_fmt(target, dec)}.")
            distractors.append((_vu(_xstr(xx), xu), why))
    expl = (f"The last change is {ds_} per {_xstep(ds, step)}. From {col['strs'][-1]}, "
            f"reaching {_fmt(target, dec)} takes ({_fmt(target, dec)} − {col['strs'][-1]}) ÷ "
            f"({ds_}) = {k} steps, so {scen['x_short']} ≈ {_vu(_xstr(xk), xu)}.")
    return _emit(rng, prompt, correct, distractors, subskill="extrapolation",
                 explanation=expl, qtype=QT_TABLE, est=90, tags=TR_TAGS + ["threshold"],
                 stimulus=table_stimulus(ds),
                 verify=_spec("reach", v=_fmt(target, dec), col=ci + 1))


@_retry
def tr_condition_trend_compare(rng, difficulty):
    scen = _pick_scenario(rng, lambda s: s.get("cond") and s["shape"] != "peak")
    ds = build(rng, scen, cond="cond", n=_n_rows(rng, difficulty))
    if ds is None:
        return None
    a, b = ds["cols"]
    dec, xu, yu = ds["dec"], ds["xunit"], a["unit"]
    da = round(abs(a["vals"][-1] - a["vals"][0]), dec)
    db = round(abs(b["vals"][-1] - b["vals"][0]), dec)
    if da == db:
        return None
    big, small = (a, b) if da > db else (b, a)
    dbig, dsmall = max(da, db), min(da, db)
    gap = round(dbig - dsmall, dec)
    word = "increase" if a["shape"] == "inc" else "decrease"
    x0, x1 = _vu(ds["xstrs"][0], xu), _vu(ds["xstrs"][-1], xu)
    prompt = rng.choice([
        f"According to Table 1, the total {word} in {a['desc']} from {x0} to {x1} was larger under "
        f"which condition, and by how much?",
        f"Compare the overall change in {a['desc']} between {x0} and {x1} under the two conditions "
        f"in Table 1. Which condition showed the larger {word}, and by what amount?",
    ])
    correct = (f"{_cap_first(big['label'])}, by {_vu(_fmt(gap, dec), yu)}",
               f"Correct. {big['label']}: {_fmt(dbig, dec)}; {small['label']}: {_fmt(dsmall, dec)}; "
               f"the difference is {_fmt(gap, dec)}.")
    distractors = [
        (f"{_cap_first(small['label'])}, by {_vu(_fmt(gap, dec), yu)}",
         f"The amount is right, but the larger overall change was for {big['label']}."),
        (f"{_cap_first(big['label'])}, by {_vu(_fmt(dbig, dec), yu)}",
         f"{_fmt(dbig, dec)} is the total change for {big['label']}, not the difference between "
         f"the two conditions."),
        (f"{_cap_first(small['label'])}, by {_vu(_fmt(dsmall, dec), yu)}",
         f"{_fmt(dsmall, dec)} is the total change for {small['label']}, and that condition "
         f"showed the smaller change."),
    ]
    expl = (f"Total change for {a['label']}: |{a['strs'][-1]} − {a['strs'][0]}| = {_fmt(da, dec)}; "
            f"for {b['label']}: |{b['strs'][-1]} − {b['strs'][0]}| = {_fmt(db, dec)}. "
            f"{_cap_first(big['label'])} is larger by {_fmt(gap, dec)} {yu}.".strip())
    return _emit(rng, prompt, correct, distractors, subskill="trend_shape",
                 explanation=expl, qtype=QT_TABLE, est=85, tags=TR_TAGS + ["conditions"],
                 stimulus=table_stimulus(ds), verify=_spec("condtrend"))


# --------------------------------------------------------------------------- #
# Experimental design (research summaries)
# --------------------------------------------------------------------------- #
ED_TAGS = ["science", "experimental-design"]


def _ed_dataset(rng, difficulty, *, need_cond=False, pred=None, cond="cond"):
    def ok(s):
        if len(s["series"]) != 1:
            return False
        if need_cond and not s.get("cond" if cond == "cond" else "null_cond"):
            return False
        return pred is None or pred(s)
    scen = _pick_scenario(rng, ok)
    return build(rng, scen, cond=cond if need_cond else None, n=_n_rows(rng, difficulty))


def _var_options(scen, correct_key, ctrl_index=0):
    opts = {
        "x": scen["x_desc"],
        "y": scen["series"][0]["desc"],
        "ctrl": scen["controlled"][ctrl_index],
        "unrelated": scen["unrelated"],
    }
    why = {
        "x": f"{_cap_first(scen['x_desc'])} was the variable the experimenters deliberately changed "
             f"(the independent variable).",
        "y": f"{_cap_first(scen['series'][0]['desc'])} was measured as the outcome (the dependent variable).",
        "ctrl": f"{_cap_first(scen['controlled'][ctrl_index])} was kept the same in every trial "
                f"(a controlled variable).",
        "unrelated": f"{_cap_first(scen['unrelated'])} is not part of the procedure and plays no "
                     f"role in the experiment.",
    }
    correct = (_cap_first(opts[correct_key]), "Correct. " + why[correct_key])
    distractors = [(_cap_first(opts[k]), why[k]) for k in opts if k != correct_key]
    return correct, distractors


@_retry
def ed_independent_variable(rng, difficulty):
    ds = _ed_dataset(rng, difficulty)
    if ds is None:
        return None
    scen = ds["scen"]
    prompt = rng.choice([
        "In Experiment 1, which of the following was the independent variable (the variable the "
        "experimenters deliberately changed)?",
        "Which variable did the experimenters intentionally vary from trial to trial in Experiment 1?",
        "In Experiment 1, which factor was deliberately set to different values by the experimenters?",
    ])
    correct, distractors = _var_options(scen, "x", rng.randrange(len(scen["controlled"])))
    expl = (f"The procedure changes {scen['x_desc']} from trial to trial and records "
            f"{scen['series'][0]['desc']} in response, so {scen['x_desc']} is the independent variable.")
    return _emit(rng, prompt, correct, distractors, subskill="identify_variables",
                 explanation=expl, qtype=QT_TABLE, est=50, tags=ED_TAGS + ["variables"],
                 stimulus=experiment_table(ds))


@_retry
def ed_dependent_variable(rng, difficulty):
    ds = _ed_dataset(rng, difficulty)
    if ds is None:
        return None
    scen = ds["scen"]
    prompt = rng.choice([
        "In Experiment 1, which of the following was the dependent variable (the variable measured "
        "as the outcome)?",
        "Which quantity was measured as the result of each trial in Experiment 1?",
        "In Experiment 1, the experimenters recorded which of the following as the outcome of each trial?",
    ])
    correct, distractors = _var_options(scen, "y", rng.randrange(len(scen["controlled"])))
    expl = (f"{_cap_first(scen['series'][0]['desc'])} is what the experimenters measured after "
            f"setting {scen['x_desc']}, so it is the dependent variable.")
    return _emit(rng, prompt, correct, distractors, subskill="identify_variables",
                 explanation=expl, qtype=QT_PASSAGE, est=50, tags=ED_TAGS + ["variables"],
                 stimulus=experiment_passage(ds))


@_retry
def ed_controlled_variable(rng, difficulty):
    ds = _ed_dataset(rng, difficulty)
    if ds is None:
        return None
    scen = ds["scen"]
    prompt = rng.choice([
        "Which of the following was most likely held constant across all trials of Experiment 1?",
        "In Experiment 1, which of the following is a controlled variable, kept the same in every trial?",
        "To make the trials of Experiment 1 comparable, the experimenters most likely kept which of "
        "the following the same?",
    ])
    correct, distractors = _var_options(scen, "ctrl", rng.randrange(len(scen["controlled"])))
    expl = (f"Only {scen['x_desc']} was varied and only {scen['series'][0]['desc']} was measured; "
            f"{correct[0].lower()} was kept the same so it could not affect the results.")
    return _emit(rng, prompt, correct, distractors, subskill="identify_variables",
                 explanation=expl, qtype=QT_TABLE, est=55, tags=ED_TAGS + ["variables"],
                 stimulus=experiment_table(ds))


@_retry
def ed_control_purpose(rng, difficulty):
    ds = _ed_dataset(rng, difficulty, pred=lambda s: s["zero_ok"])
    if ds is None or ds["xs"][0] != 0:
        return None
    scen = ds["scen"]
    ser = scen["series"][0]
    xu = ds["xunit"]
    prompt = rng.choice([
        f"Why did the experimenters most likely include a trial {_xat(ds, '0')}?",
        f"The trial {_xat(ds, '0')} was most likely included in Experiment 1 in order to:",
    ])
    correct = (f"Serve as a control against which the other trials could be compared",
               "Correct. A zero trial shows what happens with none of the treatment, so the effect "
               "of each nonzero amount can be judged against it.")
    distractors = [
        (f"Produce the largest possible value of {ser['desc']} in the experiment",
         f"The {_vu('0', xu)} row is a baseline, not an attempt to obtain a maximum."),
        (f"Check that the instrument used to measure {ser['desc']} was properly calibrated",
         "Nothing in the procedure uses the zero trial to calibrate an instrument."),
        (f"Determine whether {scen['controlled'][0]} has any effect on {ser['desc']}",
         f"{_cap_first(scen['controlled'][0])} was held constant, so no trial can test its effect."),
    ]
    expl = (f"A trial with {scen['x_short']} of zero serves as the control: it establishes the "
            f"baseline value of {ser['desc']} against which the other trials are compared.")
    return _emit(rng, prompt, correct, distractors, subskill="control_purpose",
                 explanation=expl, qtype=QT_TABLE, est=55, tags=ED_TAGS + ["control"],
                 stimulus=experiment_table(ds))


@_retry
def ed_experiment_difference(rng, difficulty):
    ds = _ed_dataset(rng, difficulty, need_cond=True)
    if ds is None:
        return None
    scen, c = ds["scen"], ds["cond"]
    ser = scen["series"][0]
    prompt = rng.choice([
        "Experiment 2 differed from Experiment 1 in which of the following ways?",
        "Which of the following best describes how the procedure of Experiment 2 differed from that "
        "of Experiment 1?",
        "The only intentional difference between Experiments 1 and 2 was:",
    ])
    correct = (f"{_cap_first(c['var'])} was {c['labels'][0]} in Experiment 1 and "
               f"{c['labels'][1]} in Experiment 2",
               "Correct. The description of Experiment 2 says the procedure was repeated with only "
               "this condition changed.")
    distractors = [
        (f"{_cap_first(scen['x_desc'])} was held constant in Experiment 2 but varied in Experiment 1",
         f"Both experiments tested the same set of values of {scen['x_short']}."),
        (f"A different quantity was measured in Experiment 2 in place of {ser['desc']}",
         f"Both experiments measured {ser['desc']}."),
        (f"{_cap_first(scen['controlled'][0])} was varied in Experiment 2 but held constant in "
         f"Experiment 1",
         f"{_cap_first(scen['controlled'][0])} was kept the same in both experiments; only "
         f"{c['var']} changed."),
    ]
    expl = (f"Experiment 2 repeated Experiment 1 {c['phrases'][1]}; everything else, including the "
            f"values of {scen['x_short']} and the quantity measured, stayed the same.")
    return _emit(rng, prompt, correct, distractors, subskill="experiment_comparison",
                 explanation=expl, qtype=QT_TABLE, est=60, tags=ED_TAGS + ["comparison"],
                 stimulus=experiment_table(ds, two=True))


def _hypothesis_texts(scen, shape):
    x, y = scen["x_short"], scen["series"][0]["short"]
    return {
        "inc": f"Increasing {x} increases {y}.",
        "dec": f"Increasing {x} decreases {y}.",
        "peak": f"{_cap_first(y)} is greatest at an intermediate {x} and lower at both higher and "
                f"lower values.",
        "none": f"{_cap_first(x)} has no effect on {y}.",
    }


@_retry
def ed_hypothesis_support(rng, difficulty):
    ds = _ed_dataset(rng, difficulty)
    if ds is None:
        return None
    scen = ds["scen"]
    col = ds["cols"][0]
    shape = col["shape"]
    texts = _hypothesis_texts(scen, shape)
    prompt = rng.choice([
        "Which of the following hypotheses is best supported by the results of Experiment 1?",
        "The results of Experiment 1 are most consistent with which hypothesis?",
        "Based on Experiment 1, which conclusion is best supported?",
    ])
    correct = (texts[shape], "Correct. " + {
        "inc": "Every increase in the independent variable produced a larger measured value.",
        "dec": "Every increase in the independent variable produced a smaller measured value.",
        "peak": "The measured value rises to a maximum partway through the range and then falls.",
    }[shape])
    why = {
        "inc": "The results do not rise with every increase in the independent variable.",
        "dec": "The results do not fall with every increase in the independent variable.",
        "peak": "The results never reverse direction, so there is no intermediate maximum.",
        "none": "The measured values change clearly from trial to trial, so there is an effect.",
    }
    if shape == "peak":
        why["inc"] = "The results rise only over the first part of the range, then fall."
        why["dec"] = "The results fall only over the last part of the range, after rising."
    distractors = [(texts[k], why[k]) for k in texts if k != shape]
    ctrl = scen["controlled"][0]
    distractors.append((f"{_cap_first(ctrl)} determines {col['short']}.",
                        f"{_cap_first(ctrl)} was held constant, so the experiment says nothing "
                        f"about its effect."))
    rng.shuffle(distractors)
    expl = (f"Reading the results in order of {scen['x_short']}, {col['desc']} "
            f"{_direction_word(shape)}, which supports: \"{texts[shape]}\"")
    return _emit(rng, prompt, correct, distractors, subskill="hypothesis_support",
                 explanation=expl, qtype=QT_PASSAGE, est=70, tags=ED_TAGS + ["hypothesis"],
                 stimulus=experiment_passage(ds), verify=_spec("trend", col=1, expect=shape))


@_retry
def ed_replication_purpose(rng, difficulty):
    ds = _ed_dataset(rng, difficulty, pred=lambda s: "repeat" in s["method"] or "three" in s["method"]
                     or "average" in s["method"] or "triplicate" in s["method"] or "10 complete" in s["method"])
    if ds is None:
        return None
    scen = ds["scen"]
    ser = scen["series"][0]
    m = scen["method"]
    if "10 complete swings" in m:
        act = "timed 10 complete swings and divided by 10, rather than timing a single swing"
        base = "time 10 complete swings and divide by 10 rather than time a single swing"
    elif "triplicate" in m:
        act = "tested each condition in triplicate"
        base = "test each condition in triplicate"
    else:
        act = "repeated each measurement several times and recorded the average"
        base = "repeat each measurement several times and record the average"
    prompt = rng.choice([
        f"In Experiment 1, the experimenters {act}. The most likely reason was to:",
        f"Why did the experimenters most likely {base} in Experiment 1?",
    ])
    correct = ("Reduce the effect of random error in individual measurements",
               "Correct. Averaging repeated measurements cancels out much of the random variation "
               "in any single measurement.")
    distractors = [
        (f"Increase the range of {scen['x_short']} that could be tested",
         f"Repeating a measurement does not change which values of {scen['x_short']} are tested."),
        (f"Remove the need to keep {scen['controlled'][0]} the same",
         "Repetition does not substitute for controlling variables; controls are still needed."),
        (f"Make {ser['desc']} change more in response to {scen['x_short']}",
         "Repeating a measurement cannot change the size of the real effect."),
    ]
    expl = ("Any single measurement contains random error; repeating and averaging makes the "
            "recorded value more reliable.")
    return _emit(rng, prompt, correct, distractors, subskill="control_purpose",
                 explanation=expl, qtype=QT_PASSAGE, est=55, tags=ED_TAGS + ["method"],
                 stimulus=experiment_passage(ds))


@_retry
def ed_predict_trial(rng, difficulty):
    ds = _ed_dataset(rng, difficulty, pred=lambda s: s["shape"] != "peak" and s["x_short"] != "year")
    if ds is None:
        return None
    scen = ds["scen"]
    col = ds["cols"][0]
    n = len(ds["xs"])
    i = rng.randrange(n - 1)
    xa, xb = ds["xs"][i], ds["xs"][i + 1]
    xm = (xa + xb) / 2
    xm_s = _xstr(xm) if float(xm).is_integer() else f"{xm:g}"
    xu, yu = ds["xunit"], col["unit"]
    lo, hi = sorted([col["vals"][i], col["vals"][i + 1]])
    lo_s, hi_s = _fmt(lo, ds["dec"]), _fmt(hi, ds["dec"])
    prompt = rng.choice([
        f"Suppose the experimenters had run one more trial in Experiment 1 {_xat(ds, xm_s)}. "
        f"Based on the results, {col['desc']} in that trial would most likely have been:",
        f"If Experiment 1 were extended with a trial at {_vu(xm_s, xu)}, {col['desc']} would most "
        f"likely have been:",
    ])
    def between(a, b):
        return f"between {_vu(a, yu)} and {_vu(b, yu)}"
    correct = (between(lo_s, hi_s),
               f"Correct. {_vu(xm_s, xu)} is between the tested values {_vu(ds['xstrs'][i], xu)} and "
               f"{_vu(ds['xstrs'][i + 1], xu)}, whose results were {lo_s} and {hi_s}.")
    vmin, vmax = _fmt(min(col["vals"]), ds["dec"]), _fmt(max(col["vals"]), ds["dec"])
    distractors = [
        (f"below every result obtained, less than {_vu(vmin, yu)}",
         "This is below every result; the trend gives no reason to expect it."),
        (f"above every result obtained, greater than {_vu(vmax, yu)}",
         "This is above every result; the trend gives no reason to expect it."),
    ]
    if i + 2 < n:
        a2, b2 = sorted([col["vals"][i + 1], col["vals"][i + 2]])
        distractors.append((between(_fmt(a2, ds["dec"]), _fmt(b2, ds["dec"])),
                            f"This interval belongs to {scen['x_short']} between "
                            f"{_vu(ds['xstrs'][i + 1], xu)} and {_vu(ds['xstrs'][i + 2], xu)}."))
    else:
        a2, b2 = sorted([col["vals"][i - 1], col["vals"][i]])
        distractors.append((between(_fmt(a2, ds["dec"]), _fmt(b2, ds["dec"])),
                            f"This interval belongs to {scen['x_short']} between "
                            f"{_vu(ds['xstrs'][i - 1], xu)} and {_vu(ds['xstrs'][i], xu)}."))
    expl = (f"The results change steadily with {scen['x_short']}, so a trial at {_vu(xm_s, xu)} "
            f"should give a value between those of its neighbors, {lo_s} and {hi_s} {yu}.".strip())
    return _emit(rng, prompt, correct, distractors, subskill="predict_result",
                 explanation=expl, qtype=QT_PASSAGE, est=65, tags=ED_TAGS + ["predict"],
                 stimulus=experiment_passage(ds),
                 verify=_spec("interp_range", x=xm_s, col=1))


@_retry
def ed_design_change(rng, difficulty):
    ds = _ed_dataset(rng, difficulty)
    if ds is None:
        return None
    scen = ds["scen"]
    ser = scen["series"][0]
    k = rng.randrange(len(scen["controlled"]))
    ctrl = scen["controlled"][k]
    prompt = rng.choice([
        f"Suppose the experimenters wanted to test whether {ctrl} affects {ser['desc']}. Which "
        f"change to the procedure of Experiment 1 would best test this?",
        f"To determine whether {ctrl} influences {ser['desc']}, the experimenters should most "
        f"likely:",
        f"Which modification of Experiment 1 would allow the experimenters to test the effect of "
        f"{ctrl} on {ser['desc']}?",
    ])
    correct = (f"Vary {ctrl} while holding {scen['x_desc']} and all other conditions constant",
               "Correct. To test a new factor, change only that factor and hold everything else, "
               "including the original independent variable, constant.")
    distractors = [
        (f"Vary both {ctrl} and {scen['x_desc']} at the same time in each trial, measuring "
         f"{ser['desc']}",
         "Changing two factors at once makes it impossible to tell which one caused any change."),
        (f"Repeat Experiment 1 exactly as before, but with a larger number of values of "
         f"{scen['x_desc']}",
         f"This gives more detail about {scen['x_short']} but never changes {ctrl}."),
        (f"Measure {ctrl} in each trial of Experiment 1 instead of measuring {ser['desc']}",
         f"Measuring {ctrl} does not test its effect; it must be deliberately varied."),
    ]
    expl = (f"A fair test of {ctrl} changes it alone. {_cap_first(scen['x_desc'])}, which was the "
            f"variable in Experiment 1, must now be held fixed.")
    return _emit(rng, prompt, correct, distractors, subskill="design_change",
                 explanation=expl, qtype=QT_TABLE, est=75, tags=ED_TAGS + ["design"],
                 stimulus=experiment_table(ds))


@_retry
def ed_results_support_claim(rng, difficulty):
    use_null = rng.random() < 0.4
    ds = _ed_dataset(rng, difficulty, need_cond=True, cond="null" if use_null else "cond")
    if ds is None:
        return None
    scen, c = ds["scen"], ds["cond"]
    a, b = ds["cols"]
    shape = a["shape"]
    dirw = _direction_word(shape)
    prompt = rng.choice([
        f"A student claims that {c['var']} affects {a['desc']}. Do the results of Experiments 1 and 2 "
        f"support this claim?",
        f"Based on Experiments 1 and 2, is the claim that {c['var']} affects {a['desc']} supported?",
    ])
    if use_null:
        correct = (f"No; at every {scen['x_short']} tested, the two experiments gave the same "
                   f"{a['short']}",
                   "Correct. Changing the condition left every result unchanged, so the results "
                   "give no sign that it matters.")
        distractors = [
            (f"Yes; {a['desc']} {dirw} as {scen['x_short']} increased in both experiments",
             f"That trend concerns {scen['x_short']}, not {c['var']}, and appears identically in both "
             f"experiments."),
            (f"Yes; {a['desc']} was higher for {c['labels'][1]} than for {c['labels'][0]} at every "
             f"{scen['x_short']}",
             "The two columns are identical, so neither condition gave higher values."),
            (f"No; {a['desc']} did not change with {scen['x_short']} in either experiment",
             f"{_cap_first(a['desc'])} did change with {scen['x_short']}; the point is that the "
             f"condition made no difference."),
        ]
        expl = (f"Experiments 1 and 2 differ only in {c['var']}, and every value is the same in both, "
                f"so the results do not support the claim.")
        verify = _spec("cond_same")
    else:
        b_higher = all(vb > va for va, vb in zip(a["vals"], b["vals"]))
        a_higher = all(va > vb for va, vb in zip(a["vals"], b["vals"]))
        if not (b_higher or a_higher):
            return None
        hi_lab, lo_lab = (c["labels"][1], c["labels"][0]) if b_higher else (c["labels"][0], c["labels"][1])
        correct = (f"Yes; at every {scen['x_short']} tested, {a['desc']} was higher for {hi_lab} "
                   f"than for {lo_lab}",
                   "Correct. The two experiments differ only in this condition, and the results "
                   "differ consistently between them.")
        distractors = [
            (f"Yes; {a['desc']} {dirw} as {scen['x_short']} increased in both Experiment 1 and "
             f"Experiment 2",
             f"That trend concerns {scen['x_short']}, not {c['var']}; it would appear even if the "
             f"condition had no effect."),
            (f"No; {a['desc']} {dirw} as {scen['x_short']} increased in both experiments",
             f"A shared trend with {scen['x_short']} says nothing about whether {c['var']} matters; "
             f"the two columns differ at every row."),
            (f"No; the two experiments gave the same {a['short']} at every {scen['x_short']} tested",
             f"The columns differ at every {scen['x_short']}; compare them row by row."),
        ]
        expl = (f"Because the experiments differ only in {c['var']}, the consistent gap between the "
                f"two sets of results (higher for {hi_lab}) shows that the condition affects {a['desc']}.")
        verify = _spec("cond_all", higher=2 if b_higher else 1)
    return _emit(rng, prompt, correct, distractors, subskill="hypothesis_support",
                 explanation=expl, qtype=QT_TABLE, est=85, tags=ED_TAGS + ["comparison", "claim"],
                 stimulus=experiment_table(ds, two=True), verify=verify)


@_retry
def ed_which_experiments(rng, difficulty):
    ds = _ed_dataset(rng, difficulty, need_cond=True)
    if ds is None:
        return None
    scen, c = ds["scen"], ds["cond"]
    ser = scen["series"][0]
    prompt = rng.choice([
        f"Which experiment(s) provide the information needed to determine whether {c['var']} "
        f"affects {ser['desc']}?",
        f"To decide whether {c['var']} has an effect on {ser['desc']}, a student should compare the "
        f"results of:",
    ])
    correct = (f"Experiments 1 and 2 together, because they differ only in {c['var']}",
               "Correct. Only by comparing results obtained under the two conditions, with "
               "everything else the same, can the effect of that condition be isolated.")
    distractors = [
        (f"Experiment 1 alone, because it tested the full range of {scen['x_desc']} under one "
         f"condition",
         f"Experiment 1 used a single setting of {c['var']}, so by itself it cannot reveal its effect."),
        (f"Experiment 2 alone, because it was the only experiment performed {c['phrases'][1]}",
         f"Experiment 2 also used only one setting of {c['var']}; a comparison is required."),
        (f"Neither experiment, because {scen['x_desc']} was varied in both of them",
         f"Varying {scen['x_short']} in both experiments is what makes them comparable row by row; "
         f"the comparison across experiments is exactly what is needed."),
    ]
    expl = (f"Each experiment holds {c['var']} fixed at one setting; the two settings differ between "
            f"experiments, so comparing Experiments 1 and 2 isolates its effect.")
    return _emit(rng, prompt, correct, distractors, subskill="experiment_comparison",
                 explanation=expl, qtype=QT_PASSAGE, est=70, tags=ED_TAGS + ["comparison"],
                 stimulus=experiment_passage(ds, two=True))


@_retry
def ed_predict_between_conditions(rng, difficulty):
    ds = _ed_dataset(rng, difficulty, need_cond=True, pred=lambda s: s["cond"].get("numeric"))
    if ds is None:
        return None
    scen, c = ds["scen"], ds["cond"]
    a, b = ds["cols"]
    n = len(ds["xs"])
    i = rng.randrange(n)
    xu, yu = ds["xunit"], a["unit"]
    lo, hi = sorted([a["vals"][i], b["vals"][i]])
    dec = ds["dec"]
    lo_s, hi_s = _fmt(lo, dec), _fmt(hi, dec)
    x = _vu(ds["xstrs"][i], xu)
    prompt = rng.choice([
        f"Suppose Experiment 1 were repeated with {c['mid']}, a setting between those used in "
        f"Experiments 1 and 2. {_cap_first(_xat(ds, ds['xstrs'][i]))}, {a['desc']} would most "
        f"likely be:",
        f"If a third experiment used {c['mid']} and all other conditions of Experiments 1 and 2, "
        f"{a['desc']} at {x} would most likely be:",
    ])
    def between(p, q):
        return f"between {_vu(p, yu)} and {_vu(q, yu)}"
    correct = (between(lo_s, hi_s),
               f"Correct. At {x}, Experiment 1 gave {a['strs'][i]} and Experiment 2 gave {b['strs'][i]}; "
               f"an intermediate setting should give an intermediate result.")
    distractors = [
        (f"below both experiments' results, less than {_vu(lo_s, yu)}",
         "This is below both experiments' results at this row; an intermediate setting should "
         "not fall outside them."),
        (f"above both experiments' results, greater than {_vu(hi_s, yu)}",
         "This is above both experiments' results at this row; an intermediate setting should "
         "not fall outside them."),
    ]
    j = i + 1 if i + 1 < n else i - 1
    lo2, hi2 = sorted([a["vals"][j], b["vals"][j]])
    distractors.append((between(_fmt(lo2, dec), _fmt(hi2, dec)),
                        f"These are the results for {_vu(ds['xstrs'][j], xu)}, not {x}."))
    expl = (f"The two experiments bracket the new setting, so the result at {x} should lie between "
            f"{lo_s} and {hi_s} {yu}.".strip())
    return _emit(rng, prompt, correct, distractors, subskill="predict_result",
                 explanation=expl, qtype=QT_TABLE, est=85, tags=ED_TAGS + ["predict", "conditions"],
                 stimulus=experiment_table(ds, two=True),
                 verify=_spec("cond_between", x=ds["xstrs"][i]))


# --------------------------------------------------------------------------- #
# Conflicting viewpoints (authored; see VIEWPOINTS at the end of the file)
# --------------------------------------------------------------------------- #
CV_TAGS = ["science", "conflicting-viewpoints"]
CV_SLOTS = ("claim", "common", "evidence", "new_obs", "difference")
CV_SUBSKILL = {"claim": "scientist_claim", "common": "common_ground",
               "evidence": "supporting_evidence", "new_obs": "new_observation",
               "difference": "main_difference"}


def _text_complexity(text):
    words = text.split()
    sents = [s for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    avg_word = sum(len(w) for w in words) / max(1, len(words))
    avg_sent = sum(len(s.split()) for s in sents) / max(1, len(sents))
    return len(text) + 12 * avg_sent + 40 * avg_word


def _pair_complexity(pair):
    return _text_complexity(pair["text_a"]) + _text_complexity(pair["text_b"])


def viewpoint_tiers():
    """Pairs sorted simplest-first, split into overlapping easy/medium/hard windows
    so that each tier draws from at least 8 pairs while still ramping."""
    ordered = sorted(VIEWPOINTS, key=_pair_complexity)
    n = len(ordered)
    w = max(8, n - 4)
    return {
        "easy": ordered[:w],
        "medium": ordered[(n - w) // 2:(n - w) // 2 + w],
        "hard": ordered[n - w:],
    }


def _cv_question(rng, difficulty, slot):
    tiers = viewpoint_tiers()
    pair = rng.choice(tiers[difficulty])
    q = pair["questions"][slot]
    prompt, options, ci, rats, expl = q
    order = list(range(len(options)))
    rng.shuffle(order)
    opts = [options[i] for i in order]
    rat = [rats[i] for i in order]
    stim = {"type": "paired_passages", "title": pair["title"],
            "text": "Scientist 1\n" + pair["text_a"], "text_b": "Scientist 2\n" + pair["text_b"]}
    return mc(prompt, opts, order.index(ci), rat, subskill=CV_SUBSKILL[slot],
              qtype=QT_PASSAGE, explanation=expl, est=90, tags=CV_TAGS + [slot, "pair:" + pair["id"]],
              stimulus=stim)


def cv_scientist_claim(rng, difficulty):
    return _cv_question(rng, difficulty, "claim")


def cv_common_ground(rng, difficulty):
    return _cv_question(rng, difficulty, "common")


def cv_supporting_evidence(rng, difficulty):
    return _cv_question(rng, difficulty, "evidence")


def cv_new_observation(rng, difficulty):
    return _cv_question(rng, difficulty, "new_obs")


def cv_main_difference(rng, difficulty):
    return _cv_question(rng, difficulty, "difference")


for _fn in (cv_scientist_claim, cv_common_ground, cv_supporting_evidence,
            cv_new_observation, cv_main_difference,
            ed_control_purpose, ed_replication_purpose):
    _fn.small_space = True


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
FAMILIES = {
    "data_representation": {
        "easy": [dr_lookup_value, dr_direction, dr_extreme, dr_inverse_lookup, dr_figure_read],
        "medium": [dr_difference, dr_ratio, dr_consistent_statement, dr_condition_compare,
                   dr_count_above],
        "hard": [dr_condition_statement, dr_percent_change, dr_cross_condition_lookup,
                 dr_average, dr_figure_biggest_step],
    },
    "trends_extrapolation": {
        "easy": [tr_trend_shape, tr_interpolate_range, tr_beyond_direction, tr_figure_trend],
        "medium": [tr_interpolate_value, tr_x_for_target, tr_doubling, tr_biggest_step],
        "hard": [tr_extrapolate_value, tr_crossing, tr_reach_threshold,
                 tr_condition_trend_compare],
    },
    "experimental_design": {
        "easy": [ed_independent_variable, ed_dependent_variable, ed_controlled_variable,
                 ed_control_purpose],
        "medium": [ed_experiment_difference, ed_hypothesis_support, ed_replication_purpose,
                   ed_predict_trial],
        "hard": [ed_design_change, ed_results_support_claim, ed_which_experiments,
                 ed_predict_between_conditions],
    },
    "conflicting_viewpoints": {
        "easy": [cv_scientist_claim, cv_common_ground, cv_supporting_evidence,
                 cv_new_observation, cv_main_difference],
        "medium": [cv_scientist_claim, cv_common_ground, cv_supporting_evidence,
                   cv_new_observation, cv_main_difference],
        "hard": [cv_scientist_claim, cv_common_ground, cv_supporting_evidence,
                 cv_new_observation, cv_main_difference],
    },
}


# --------------------------------------------------------------------------- #
# Authored viewpoint pairs (original prose). Each question is
# (prompt, [opt0..opt3], correct_index, [rat0..rat3], explanation).
# --------------------------------------------------------------------------- #
VIEWPOINTS = [
    {
        "id": "extinction", "title": "The End of the Dinosaurs",
        "text_a": (
            "An asteroid about 10 km wide struck the Earth 66 million years ago. The impact "
            "threw enormous amounts of dust and sulfur into the air, which blocked sunlight "
            "for months. Plants died, and the animals that depended on them starved. The "
            "clearest evidence is a thin layer of clay found at sites around the world that "
            "is rich in iridium, an element rare in Earth's crust but common in asteroids. "
            "The layer sits exactly at the boundary where dinosaur fossils stop appearing. A "
            "crater of the right age and size has also been identified beneath the coast of "
            "Mexico. Because the layer and the crater are the same age, the impact must have "
            "been the main cause of the extinction."),
        "text_b": (
            "Massive volcanic eruptions in what is now India were the main cause. These "
            "eruptions released lava over an area larger than many countries and continued "
            "for hundreds of thousands of years. They poured carbon dioxide and sulfur gases "
            "into the atmosphere, causing rapid swings in climate and acid rain. Fossil "
            "records show that some groups of animals were already declining before the "
            "boundary layer formed, which an instant impact cannot explain. Iridium can also "
            "be carried up from deep within the Earth by such eruptions. An asteroid may have "
            "struck near the end, but it hit a world whose ecosystems were already collapsing "
            "from volcanic activity."),
        "questions": {
            "claim": (
                "Scientist 1 would most likely agree with which of the following statements?",
                ["The iridium in the boundary clay layer came from material outside the Earth.",
                 "The iridium in the boundary clay layer was carried up from deep inside the Earth.",
                 "Dinosaur populations declined gradually over hundreds of thousands of years.",
                 "The crater beneath the coast of Mexico formed long after the extinction."],
                0,
                ["Correct. Scientist 1 says iridium is rare in the crust but common in asteroids, pointing to an extraterrestrial source.",
                 "This is Scientist 2's explanation for the iridium, not Scientist 1's.",
                 "Scientist 1 describes a sudden event; gradual decline is Scientist 2's claim.",
                 "Scientist 1 stresses that the crater and the layer are the same age."],
                "Scientist 1 uses the iridium layer as evidence of an asteroid, so the iridium must come from outside the Earth."),
            "common": (
                "Both scientists would most likely agree that:",
                ["a clay layer rich in iridium marks the time of the extinction.",
                 "volcanic gases alone were enough to change the climate.",
                 "the asteroid struck before any groups of animals had begun to decline.",
                 "sunlight was blocked for only a few days after the impact."],
                0,
                ["Correct. Both refer to the iridium-rich boundary layer; they disagree only about where the iridium came from.",
                 "Only Scientist 2 attributes the climate change to volcanic gases.",
                 "Scientist 2 says some groups were already declining before the boundary formed.",
                 "Scientist 1 says sunlight was blocked for months; Scientist 2 does not discuss this."],
                "The existence of the iridium layer at the boundary is accepted by both; its origin is what they dispute."),
            "evidence": (
                "Which of the following findings, if true, would most strongly support Scientist 2's viewpoint?",
                ["Several dinosaur groups become steadily rarer in the rock layers just below the boundary.",
                 "The crater beneath the coast of Mexico is confirmed by new dating to be exactly 66 million years old.",
                 "Iridium concentrations are highest in boundary samples taken closest to the crater.",
                 "The volcanic lava flows in India turn out to cover a much smaller area than thought."],
                0,
                ["Correct. A gradual decline before the boundary fits prolonged volcanic stress and is hard to explain with a single instant impact.",
                 "A crater of exactly the right age strengthens Scientist 1's impact explanation.",
                 "Iridium concentrated near the crater points to the impact as the iridium source, supporting Scientist 1.",
                 "Smaller eruptions would weaken, not support, the volcanic explanation."],
                "Scientist 2's case rests on ecosystems collapsing before the boundary; evidence of pre-boundary decline supports it directly."),
            "new_obs": (
                "Suppose careful dating showed that the great majority of the lava in India erupted after the iridium layer formed. This finding would most likely:",
                ["weaken Scientist 2's view that volcanic eruptions caused the extinction.",
                 "weaken Scientist 1's view that the impact was the main cause of the extinction.",
                 "support Scientist 2's claim that animals were declining before the boundary formed.",
                 "show that the crater beneath Mexico is older than the iridium layer."],
                0,
                ["Correct. If most eruptions came after the extinction, they could not have been its main cause.",
                 "The timing of the lava says nothing against the impact; if anything it removes a rival explanation.",
                 "Eruptions that came later cannot explain declines that came earlier.",
                 "The finding concerns the lava, not the crater's age."],
                "Scientist 2 needs the eruptions to precede and overlap the extinction; eruptions mostly afterward undercut that."),
            "difference": (
                "The two viewpoints differ mainly on which of the following points?",
                ["Whether the extinction was caused by a sudden event or a prolonged process.",
                 "Whether the global climate was seriously disrupted at the time of the extinction.",
                 "Whether the clay layer at the boundary actually contains the element iridium.",
                 "Whether an asteroid struck the Earth at some point near the end of the period."],
                0,
                ["Correct. Scientist 1 describes a sudden impact; Scientist 2 describes eruptions lasting hundreds of thousands of years.",
                 "Both describe climate disruption; they differ on its cause.",
                 "Both accept the iridium layer and differ only on its source.",
                 "Scientist 2 allows that an asteroid may have struck; the dispute is about what mattered most."],
                "The core disagreement is sudden impact versus prolonged volcanism, not the existence of the layer or the climate change."),
        },
    },
    {
        "id": "lake", "title": "The Perch of Miller Lake",
        "text_a": (
            "The decline of perch in Miller Lake began soon after the farms upstream "
            "expanded. Fertilizer washed into the lake by rain feeds algae, which bloom "
            "across the surface each summer. When the algae die, bacteria decompose them and "
            "use up the oxygen dissolved in the water. Measurements taken in August show "
            "oxygen levels near the bottom of the lake that are too low for perch eggs and "
            "young fish to survive. Adult perch can move to shallower water, but their young "
            "cannot, so each year fewer fish reach adulthood. Reducing fertilizer runoff "
            "would allow the oxygen to recover and the perch population to rebuild."),
        "text_b": (
            "The perch decline is due to the arrival of the zander, a predatory fish first "
            "recorded in Miller Lake eight years ago, probably released by anglers. Zander "
            "feed heavily on young perch, and their numbers have grown each year while the "
            "perch count has fallen. Low oxygen alone cannot explain the pattern: the lake "
            "had algae blooms for decades before perch began to decline, and nearby lakes "
            "with similar farms and blooms still have healthy perch populations but no "
            "zander. Stomach samples from zander in the lake contain mostly young perch. "
            "Removing zander by netting would allow the perch to recover even if the "
            "fertilizer runoff continued."),
        "questions": {
            "claim": (
                "With which of the following statements would Scientist 2 most likely agree?",
                ["Algae blooms occurred in Miller Lake before the perch decline began.",
                 "Fertilizer runoff is the main reason the perch population has fallen.",
                 "Zander were present in Miller Lake for decades before the perch declined.",
                 "Nearby lakes that contain zander have healthy perch populations."],
                0,
                ["Correct. Scientist 2 states the lake had blooms for decades before the decline, which is why blooms cannot be the cause.",
                 "This is Scientist 1's position; Scientist 2 blames the zander.",
                 "Scientist 2 says zander were first recorded only eight years ago.",
                 "Scientist 2 says the healthy nearby lakes have no zander."],
                "Scientist 2 uses the long history of blooms to argue that blooms do not explain the recent decline."),
            "common": (
                "Scientist 1 and Scientist 2 would both most likely agree that:",
                ["fewer young perch are surviving to adulthood each year.",
                 "removing zander from the lake would restore the perch population.",
                 "oxygen near the bottom of the lake is too low for young perch to survive.",
                 "the perch decline began before the farms upstream expanded."],
                0,
                ["Correct. Scientist 1 blames low oxygen and Scientist 2 blames predation, but both say young perch are being lost.",
                 "Only Scientist 2 proposes removing zander.",
                 "Only Scientist 1 makes this claim about oxygen.",
                 "Scientist 1 says the decline began soon after the farms expanded; Scientist 2 ties it to the zander's arrival."],
                "The loss of young perch is the shared observation; the two explanations differ on what kills them."),
            "evidence": (
                "Which of the following observations, if confirmed, would provide the strongest support for Scientist 1's explanation?",
                ["Young perch caged near the lake bottom in August die within days, while those caged near the surface survive.",
                 "The number of zander in Miller Lake is found to have doubled over the past two years, while perch counts fell.",
                 "Oxygen levels near the lake bottom in August are found to be the same as they were thirty years ago, before the decline.",
                 "Perch populations in nearby lakes that have farms and blooms but no zander are found to be increasing."],
                0,
                ["Correct. This directly shows that bottom-water conditions kill young perch, the mechanism Scientist 1 proposes.",
                 "Growing zander numbers support Scientist 2's predation explanation.",
                 "Unchanged oxygen levels would undercut the idea that oxygen loss caused a recent decline.",
                 "Healthy perch where zander are absent supports Scientist 2."],
                "Scientist 1's mechanism is suffocation of young perch in low-oxygen bottom water; a cage experiment showing exactly that is the strongest support."),
            "new_obs": (
                "Suppose a lake with heavy fertilizer runoff and summer algae blooms but no zander were found to have a stable perch population. This finding would most likely:",
                ["weaken Scientist 1's explanation.",
                 "weaken Scientist 2's explanation.",
                 "support Scientist 1's explanation.",
                 "support both explanations equally."],
                0,
                ["Correct. If blooms and runoff occur without a decline, they are unlikely to be sufficient to cause one.",
                 "A lake with no zander and no decline is consistent with Scientist 2's view.",
                 "The finding shows runoff and blooms without a decline, the opposite of what Scientist 1 predicts.",
                 "The finding favors the predation explanation over the oxygen explanation."],
                "Scientist 1 predicts that runoff and blooms cause decline; a counterexample weakens that prediction."),
            "difference": (
                "The central disagreement between the two scientists concerns:",
                ["whether low oxygen or predation is responsible for the loss of young perch.",
                 "whether the number of perch in Miller Lake has actually fallen in recent years.",
                 "whether zander are actually present in the waters of Miller Lake.",
                 "whether algae blooms spread across the surface of the lake each summer."],
                0,
                ["Correct. Each proposes a different cause for the loss of young perch.",
                 "Both accept that the perch population has declined.",
                 "Scientist 1 does not deny the zander's presence; the dispute is about what matters.",
                 "Both acknowledge the summer blooms."],
                "The disagreement is about the cause of the decline, not about whether it is happening."),
        },
    },
    {
        "id": "atmosphere", "title": "Where an Atmosphere Comes From",
        "text_a": (
            "A rocky planet's atmosphere comes mainly from inside the planet. As the young "
            "planet's interior heated, volcanoes released water vapor, carbon dioxide, and "
            "nitrogen that had been trapped in its rocks. Over millions of years this "
            "outgassing built up a thick atmosphere. The mix of gases in such atmospheres "
            "closely matches the gases released by volcanoes today, and the ratio of certain "
            "forms of argon, called isotopes, points to a source within the planet rather "
            "than from space. Impacts by comets may have added small amounts of water, but "
            "the bulk of the atmosphere came from the planet's own interior."),
        "text_b": (
            "The atmosphere was delivered mostly by comets and icy asteroids that struck the "
            "planet during the first several hundred million years after it formed. The "
            "planet formed too hot to hold onto gases; any early atmosphere would have been "
            "lost to space. Comets contain large amounts of frozen water and other ices, and "
            "the cratering record shows that impacts were extremely frequent during that "
            "early period. The ratio of heavy hydrogen, called deuterium, to ordinary "
            "hydrogen in the planet's water is similar to that measured in some comets. "
            "Volcanoes have released gases since, but they recycle material that impacts "
            "delivered rather than creating a new atmosphere."),
        "questions": {
            "claim": (
                "Which of the following claims is most consistent with Scientist 2's viewpoint?",
                ["Any atmosphere the planet had soon after forming was lost to space.",
                 "Volcanic gases built most of the atmosphere over millions of years.",
                 "Comets contain very little frozen water.",
                 "The planet's argon isotope ratio points to a source inside the planet."],
                0,
                ["Correct. Scientist 2 says the planet formed too hot to hold gases, so an early atmosphere would have escaped.",
                 "This is Scientist 1's view; Scientist 2 says volcanoes only recycle delivered material.",
                 "Scientist 2 says comets contain large amounts of frozen water.",
                 "The argon argument belongs to Scientist 1."],
                "Scientist 2's reasoning begins with the loss of any original atmosphere, which is why delivery from space is needed."),
            "common": (
                "Despite their disagreement, both scientists would accept that:",
                ["volcanoes have released gases into the planet's atmosphere.",
                 "comets delivered most of the water now found on the planet.",
                 "the planet has never lost any of its gases to space.",
                 "impacts were rare during the planet's first few hundred million years."],
                0,
                ["Correct. Scientist 1 makes volcanoes the main source; Scientist 2 says volcanoes recycle delivered material. Both accept volcanic release.",
                 "Only Scientist 2 credits comets with most of the water.",
                 "Scientist 2 argues the early atmosphere was lost to space.",
                 "Scientist 2 says impacts were extremely frequent early on; Scientist 1 does not dispute this."],
                "Both passages describe volcanoes releasing gases; they differ on whether that gas was original or recycled."),
            "evidence": (
                "Suppose each of the following were discovered. Which one would most strengthen Scientist 1's position?",
                ["The planet's argon isotope ratio differs sharply from the ratio measured in comets.",
                 "The deuterium-to-hydrogen ratio of the planet's water matches that of several comets.",
                 "The cratering record shows impacts were even more frequent early on than previously thought.",
                 "The planet's crust contains almost no trapped water or carbon dioxide."],
                0,
                ["Correct. An argon signature unlike that of comets points away from delivery by comets and toward an internal source.",
                 "A match with comets supports Scientist 2's delivery explanation.",
                 "More frequent impacts strengthen Scientist 2's case.",
                 "Little trapped gas in the rocks would undercut outgassing as a source."],
                "Scientist 1 relies on isotope evidence of an internal source; isotopes that rule out comets strengthen that case."),
            "new_obs": (
                "Suppose a probe measured the deuterium-to-hydrogen ratio of the planet's water and found it very different from that of every comet sampled. This finding would most likely:",
                ["weaken Scientist 2's viewpoint.",
                 "weaken Scientist 1's viewpoint.",
                 "support Scientist 2's viewpoint.",
                 "support both viewpoints equally."],
                0,
                ["Correct. Scientist 2 cites the similarity of the planet's water to comet water; a mismatch removes that support.",
                 "Scientist 1 does not rely on hydrogen isotopes, so a mismatch with comets does not hurt that view.",
                 "A mismatch with comets argues against comets as the water source.",
                 "The finding bears on Scientist 2's evidence, not Scientist 1's."],
                "Scientist 2's argument uses the comet-like deuterium ratio; a clearly different ratio weakens it."),
            "difference": (
                "The two viewpoints differ mainly about:",
                ["whether the atmosphere came mainly from inside the planet or from space.",
                 "whether the planet has ever had active volcanoes releasing gases.",
                 "whether the atmosphere contains water vapor and carbon dioxide.",
                 "whether impacts by comets and asteroids occurred early in the planet's history."],
                0,
                ["Correct. Outgassing from inside versus delivery by impacts is the central dispute.",
                 "Both passages mention volcanoes.",
                 "Both passages treat water as part of the atmosphere.",
                 "Scientist 1 allows that comet impacts occurred; the dispute is about how much they contributed."],
                "Both accept volcanoes and impacts; they disagree about which supplied most of the atmosphere."),
        },
    },
    {
        "id": "bridge", "title": "The Swaying Footbridge",
        "text_a": (
            "The bridge swayed from side to side on its opening day because of the people "
            "walking on it. When a crowd walks across a flexible bridge, small sideways "
            "movements make people adjust their steps to keep their balance. Many walkers end "
            "up stepping in time with the sway, and their combined footsteps push the bridge "
            "at exactly the frequency at which it naturally rocks. The more the bridge moves, "
            "the more people fall into step, so the motion grows. The sway appeared only when "
            "the crowd was large and stopped within minutes when the crowd was cleared, and "
            "no sway has been measured on windy days when the bridge was empty."),
        "text_b": (
            "The sway was caused by wind. As wind flows past the bridge deck and cables, it "
            "sheds swirling eddies alternately from each side, producing a push that switches "
            "direction at a regular rate. If that rate matches a natural frequency of the "
            "bridge, the structure rocks in resonance. The opening day was breezy, and the "
            "deck's flat shape is well suited to shedding eddies. Pedestrians certainly felt "
            "the motion and reacted to it, but their steps were a response to the sway, not "
            "its cause. Adding fins to the deck to break up the eddies, rather than limiting "
            "the crowd, is the correct fix."),
        "questions": {
            "claim": (
                "Scientist 1 would most likely agree with which of the following statements?",
                ["The bridge's motion grew because walkers synchronized their steps with it.",
                 "The sway would occur on a windy day even with no one on the bridge.",
                 "Adding fins to the bridge deck would be the correct way to eliminate the sway.",
                 "The crowd's footsteps were a response to the sway rather than its cause."],
                0,
                ["Correct. Scientist 1 describes a feedback loop in which walkers fall into step with the motion and amplify it.",
                 "Scientist 1 notes that no sway has been measured on windy days when the bridge was empty.",
                 "Fins are Scientist 2's proposed fix for wind-driven motion.",
                 "This is Scientist 2's view of the footsteps."],
                "Scientist 1's explanation is that synchronized footsteps drive and amplify the sway."),
            "common": (
                "Both scientists would most likely agree that:",
                ["the bridge rocked at one of its natural frequencies.",
                 "the size of the crowd on the bridge had no effect on the sway.",
                 "the sway was strongest at times when the bridge was empty.",
                 "pedestrians caused the bridge to begin rocking in the first place."],
                0,
                ["Correct. Scientist 1 says footsteps matched the bridge's natural frequency; Scientist 2 describes resonance at a natural frequency.",
                 "Scientist 1 says the sway appeared only with a large crowd.",
                 "Neither scientist claims this; Scientist 1 says the opposite.",
                 "Scientist 2 says the pedestrians responded to the sway rather than causing it."],
                "Resonance at a natural frequency appears in both explanations; they differ on what supplied the push."),
            "evidence": (
                "Which of the following findings, if true, would most strongly support Scientist 2's viewpoint?",
                ["Wind-tunnel tests show the deck sheds eddies at the bridge's natural frequency in a light breeze.",
                 "Sensors show the sway grew only when more than 150 people were on the bridge at the same time, regardless of wind.",
                 "Video recordings show many of the walkers stepping in time with the sway of the deck.",
                 "The sway stopped within a minute of the bridge being cleared of all pedestrians."],
                0,
                ["Correct. This directly confirms the mechanism Scientist 2 proposes: eddies at the resonant frequency.",
                 "Dependence on crowd size supports the pedestrian explanation.",
                 "Both scientists expect walkers to step in time with the motion, so this does not favor Scientist 2.",
                 "Motion that stops when people leave points to the crowd as the cause."],
                "Scientist 2 needs eddies at the right frequency; a wind-tunnel confirmation of that is the most direct support."),
            "new_obs": (
                "Suppose the bridge swayed strongly one calm, windless evening while a large crowd crossed it. This observation would most likely:",
                ["support Scientist 1's viewpoint and weaken Scientist 2's.",
                 "support Scientist 2's viewpoint and weaken Scientist 1's.",
                 "support both viewpoints about equally.",
                 "weaken both viewpoints to the same degree."],
                0,
                ["Correct. Sway with a crowd but no wind fits the pedestrian explanation and contradicts the wind explanation.",
                 "Without wind, the eddy mechanism cannot operate.",
                 "The observation contradicts the wind explanation.",
                 "The observation is exactly what Scientist 1 predicts."],
                "No wind removes Scientist 2's cause, while a large crowd supplies Scientist 1's cause."),
            "difference": (
                "The scientists disagree mainly about:",
                ["whether the walkers' synchronized steps caused the sway or merely responded to it.",
                 "whether the bridge actually swayed from side to side on its opening day.",
                 "whether the bridge has a natural frequency at which it tends to rock back and forth.",
                 "whether people on the bridge adjusted their steps as the deck moved beneath them."],
                0,
                ["Correct. Scientist 1 says the steps drove the motion; Scientist 2 says they were a reaction to it.",
                 "Both accept that the sway occurred.",
                 "Both invoke the bridge's natural frequency.",
                 "Both agree that walkers reacted to the motion."],
                "Both accept the sway, the natural frequency and the walkers' reaction; they disagree on cause versus response."),
        },
    },
    {
        "id": "pebbles", "title": "The Pebble Layer",
        "text_a": (
            "The pebble layer exposed in the quarry wall was laid down by a fast-flowing "
            "river. The pebbles are well rounded, which happens when stones tumble against "
            "each other in moving water over long distances. They are sorted by size, with "
            "coarse pebbles at the bottom grading up to sand, exactly what a river deposits "
            "as its current slows. Many pebbles lie tilted in the same direction, the way a "
            "current stacks flat stones against the flow. The layer is also lens-shaped, "
            "thick in the middle and thinning to the sides, which matches the shape of a "
            "river channel cut into the older rock beneath it."),
        "text_b": (
            "The layer was deposited by a glacier and the meltwater streams that flowed from "
            "it. Beneath the pebbles is a bed of unsorted material containing clay, sand, and "
            "boulders mixed together, a mixture that only ice can carry and drop in one "
            "place. Several of the larger stones have flat faces with parallel scratches, "
            "which form when stones are dragged along beneath moving ice. The pebbles above "
            "could have been rounded in meltwater streams at the glacier's edge, where "
            "sorting and tilting also occur over short distances. The region's climate "
            "records show it was cold enough for ice at the time, while river deposits need "
            "no such conditions."),
        "questions": {
            "claim": (
                "With which of the following statements would Scientist 2 most likely agree?",
                ["Flat-faced stones with parallel scratches indicate transport beneath moving ice.",
                 "Pebbles become well rounded only after long-distance transport in a river.",
                 "The unsorted bed beneath the pebbles was deposited by a slow-moving river.",
                 "The climate at the time the layer formed was far too warm for any glacier to exist."],
                0,
                ["Correct. Scientist 2 cites the scratched, flat-faced stones as evidence of dragging beneath ice.",
                 "Scientist 2 says pebbles can be rounded in meltwater streams over short distances.",
                 "Scientist 2 says only ice can deposit such an unsorted mixture.",
                 "Scientist 2 says climate records show it was cold enough for ice."],
                "The scratched stones are one of Scientist 2's key pieces of evidence for ice."),
            "common": (
                "Scientist 1 and Scientist 2 would both most likely agree that:",
                ["the pebbles were rounded by moving water.",
                 "the layer beneath the pebbles is sorted by size.",
                 "ice was present in the region when the layer formed.",
                 "the pebbles were tilted by the movement of a glacier."],
                0,
                ["Correct. Scientist 1 cites a river; Scientist 2 cites meltwater streams. Both involve rounding by water.",
                 "Scientist 2 describes the lower bed as unsorted; Scientist 1 does not discuss it.",
                 "Only Scientist 2 argues for ice.",
                 "Scientist 2 attributes tilting to meltwater streams, and Scientist 1 to a river current."],
                "Rounding by water is common ground; the type of water flow is the disagreement."),
            "evidence": (
                "Which of the following observations, if confirmed, would provide the strongest support for Scientist 1's explanation?",
                ["The pebbles are made of rock types found only in mountains far upstream.",
                 "The scratches on the large stones are found to be parallel to one another on every face.",
                 "The clay beneath the pebbles contains pollen from plants that grow only in cold climates.",
                 "Most of the pebbles turn out to be angular and sharp-edged rather than well rounded."],
                0,
                ["Correct. Rock from far upstream implies long-distance river transport, which Scientist 1 proposes.",
                 "Parallel scratches are Scientist 2's evidence for dragging beneath ice.",
                 "Cold-climate pollen supports the glacial setting Scientist 2 describes.",
                 "Angular pebbles would argue against the long tumbling that Scientist 1 describes."],
                "Scientist 1's model requires long-distance transport by a river; distant source rock supports it."),
            "new_obs": (
                "Suppose the scratches on the large stones were found to run in many different directions, and laboratory tests showed that similar scratches form when stones grind together in a strong river current. This finding would most likely:",
                ["weaken Scientist 2's viewpoint.",
                 "weaken Scientist 1's viewpoint.",
                 "support Scientist 2's viewpoint.",
                 "support both viewpoints equally."],
                0,
                ["Correct. The scratches would no longer point specifically to ice, removing a key piece of Scientist 2's evidence.",
                 "Scratches explainable by river action are consistent with Scientist 1's view.",
                 "The finding undercuts rather than supports the ice interpretation.",
                 "The finding favors the river explanation."],
                "Scientist 2 uses the scratches as a sign of ice; if rivers produce them too, that evidence loses its force."),
            "difference": (
                "Which of the following best describes the main point on which the scientists disagree? They disagree about:",
                ["whether ice played any role in depositing the layer.",
                 "whether the pebbles in the layer have been rounded at all.",
                 "whether the pebbles in the layer are sorted by size from bottom to top.",
                 "whether moving water played any part in shaping the pebbles."],
                0,
                ["Correct. Scientist 1 needs only a river; Scientist 2 requires a glacier and its meltwater.",
                 "Both agree the pebbles are rounded.",
                 "Both agree the pebbles show sorting.",
                 "Both agree water rounded the pebbles."],
                "Rounding, sorting, and water are accepted by both; the role of ice is the dispute."),
        },
    },
    {
        "id": "bees", "title": "How Bees Find Their Way",
        "text_a": (
            "Honeybees find their way home using the sun. A forager keeps track of the angle "
            "between its flight path and the sun, and it can read the pattern of polarized "
            "light in the sky even when the sun itself is hidden by clouds. Bees kept in the "
            "dark for several hours and then released set off in a direction shifted by the "
            "amount the sun has moved, showing that they steer by a remembered sun position. "
            "On fully overcast days with no polarized light, foragers often fail to return. "
            "Bees are also known to communicate the direction of food relative to the sun, "
            "which would be pointless unless the sun were their compass."),
        "text_b": (
            "Bees rely mainly on Earth's magnetic field. Bees contain tiny grains of "
            "magnetite, an iron mineral that responds to magnetic fields, in their abdomens. "
            "In experiments, bees trained to find sugar water in one direction lost the "
            "ability when a small magnet was attached to them, and hives placed between "
            "strong electrical coils that disturbed the field produced disorganized combs. "
            "The sun is useful, but it moves across the sky and disappears at night and on "
            "cloudy days, so a fixed magnetic reference is needed. Bees that return home on "
            "overcast days are using the field, not the sky."),
        "questions": {
            "claim": (
                "Which of the following claims is most consistent with Scientist 1's viewpoint?",
                ["Bees can detect the direction of polarized light in the sky.",
                 "Magnetite grains in the abdomen guide bees back to the hive.",
                 "Bees navigate just as well in complete darkness as in daylight.",
                 "A fixed magnetic reference is needed because the sun moves."],
                0,
                ["Correct. Scientist 1 says bees read the pattern of polarized light even when the sun is hidden.",
                 "Magnetite is part of Scientist 2's explanation.",
                 "Scientist 1 says bees kept in the dark become misdirected, and overcast days cause failures.",
                 "This is Scientist 2's argument."],
                "Polarized-light detection is central to Scientist 1's sun-compass view."),
            "common": (
                "Despite their disagreement, both scientists would accept that:",
                ["the sun is not always visible to a flying bee.",
                 "bees cannot navigate on overcast days.",
                 "attaching a magnet to a bee changes the direction it flies.",
                 "bees use polarized light when the sun is hidden by clouds."],
                0,
                ["Correct. Scientist 1 mentions the sun being hidden by clouds; Scientist 2 says it disappears at night and on cloudy days.",
                 "Scientist 2 says bees do return on overcast days; Scientist 1 says they often fail.",
                 "Only Scientist 2 cites the magnet experiment.",
                 "Only Scientist 1 claims polarized-light navigation."],
                "Both acknowledge the sun is sometimes hidden; they disagree on what bees do about it."),
            "evidence": (
                "Suppose each of the following were discovered. Which one would most strengthen Scientist 2's position?",
                ["Bees trained in a windowless room still orient correctly after the only lamp is moved.",
                 "Bees released after hours in the dark fly off in a direction shifted by the sun's movement.",
                 "Foragers frequently fail to return to the hive on days that are fully overcast.",
                 "Bees fly directly home whenever the polarization pattern of the sky is visible."],
                0,
                ["Correct. Orientation that does not depend on the light source implies a non-visual cue such as the magnetic field.",
                 "This is Scientist 1's evidence for steering by a remembered sun position.",
                 "Failures without sky cues support the sun-compass view.",
                 "Reliance on polarization supports Scientist 1."],
                "Scientist 2 needs evidence that bees orient without sky cues; orientation unaffected by moving the lamp provides it."),
            "new_obs": (
                "Suppose researchers removed all magnetite from a group of bees and found that, on sunny days, these bees returned to the hive from unfamiliar locations just as well as untreated bees. This finding would most likely:",
                ["weaken Scientist 2's viewpoint.",
                 "weaken Scientist 1's viewpoint.",
                 "support Scientist 2's viewpoint.",
                 "support both viewpoints equally."],
                0,
                ["Correct. If bees navigate normally without magnetite, the magnetic sense cannot be their main guide, at least when the sun is available.",
                 "Normal navigation on sunny days is what the sun-compass view predicts.",
                 "Losing magnetite without losing navigation argues against the magnetic explanation.",
                 "The finding favors the sun-compass view."],
                "Scientist 2 makes magnetite the key sensor; bees that navigate without it undercut that claim."),
            "difference": (
                "The central disagreement between the two scientists concerns:",
                ["whether bees' main directional cue comes from the sky or from the magnetic field.",
                 "whether bees are able to find their way back to the hive from unfamiliar, distant places.",
                 "whether bees' bodies contain grains of the magnetic mineral magnetite.",
                 "whether the sun changes its position in the sky over the course of a day."],
                0,
                ["Correct. Sun and polarized light versus the magnetic field is the central dispute.",
                 "Both accept that bees navigate home successfully.",
                 "Scientist 1 does not dispute the presence of magnetite, only its importance.",
                 "Both accept that the sun moves; Scientist 1 even uses this to explain misdirected bees."],
                "The disagreement is about the main cue, not about whether bees navigate or whether magnetite exists."),
        },
    },
    {
        "id": "heat_island", "title": "The Warm City",
        "text_a": (
            "The city center is about 4°C warmer at night than the surrounding farmland "
            "because of what the city is made of. Asphalt, brick, and concrete absorb "
            "sunlight during the day and store the heat, releasing it slowly after sunset. "
            "These surfaces are also dark, so they reflect less sunlight than fields and "
            "forests do. Vegetation cools the air as water evaporates from leaves, but the "
            "city has replaced most plants with pavement. The temperature difference is "
            "largest on clear, calm summer nights, when stored heat is released most "
            "effectively, and smallest in winter, when the sun is weak. Painting roofs white "
            "and planting trees would reduce the difference."),
        "text_b": (
            "The warmth comes mainly from the energy people use. Every engine, air "
            "conditioner, furnace, and light releases heat into the city's air. In the dense "
            "center, this waste heat per square kilometer can rival the energy delivered by "
            "sunlight. The nighttime difference is large because the city keeps releasing "
            "heat after the sun sets, while the countryside does not. The difference also "
            "grows on weekdays, when traffic and business activity are heaviest, and shrinks "
            "on holidays, something that building materials alone cannot explain. Reducing "
            "energy use and improving the efficiency of vehicles and buildings would do more "
            "than changing roof colors."),
        "questions": {
            "claim": (
                "Scientist 1 would most likely agree with which of the following statements?",
                ["Replacing pavement with vegetation would lower nighttime temperatures in the city.",
                 "The temperature difference is greater on holidays than it is on busy weekdays.",
                 "Waste heat from vehicles and buildings is the main reason the city is warm at night.",
                 "The temperature difference is largest in winter, when heating systems run."],
                0,
                ["Correct. Scientist 1 says vegetation cools the air and recommends planting trees.",
                 "Scientist 2 says the difference shrinks on holidays; Scientist 1 does not discuss it.",
                 "This is Scientist 2's explanation.",
                 "Scientist 1 says the difference is smallest in winter."],
                "Scientist 1 attributes the warmth to materials and the loss of vegetation, so adding vegetation should help."),
            "common": (
                "Both scientists would most likely agree that:",
                ["the city center is warmer than the countryside at night.",
                 "the extra warmth comes from sunlight stored in building materials.",
                 "weekday traffic is what drives the temperature difference.",
                 "painting roofs white would be the most effective remedy."],
                0,
                ["Correct. Both passages set out to explain the same nighttime temperature difference.",
                 "Only Scientist 1 makes stored sunlight the cause.",
                 "Only Scientist 2 cites weekday traffic.",
                 "Scientist 2 explicitly says roof color changes would do less than reducing energy use."],
                "The observation being explained, a warmer city at night, is shared; the cause is disputed."),
            "evidence": (
                "Which of the following findings, if true, would most strongly support Scientist 2's viewpoint?",
                ["The nighttime temperature difference became much smaller during a week-long power outage.",
                 "The temperature difference is largest on clear, calm summer nights and smallest in winter.",
                 "Dark roofs are measured to be hotter than light-colored roofs at sunset.",
                 "Tree-lined streets are cooler at night than streets without trees."],
                0,
                ["Correct. Less energy use with the same buildings leading to a smaller difference points to waste heat as the cause.",
                 "This pattern is what Scientist 1 predicts from stored sunlight.",
                 "Hot dark roofs support the materials explanation.",
                 "Cooling by trees supports Scientist 1's emphasis on vegetation."],
                "Scientist 2's claim is that energy use drives the warmth; a drop in warmth when energy use drops supports it."),
            "new_obs": (
                "Suppose a city with very little industry or traffic, but built of the same materials, showed the same nighttime temperature difference as a busy city of similar size. This finding would most likely:",
                ["support Scientist 1's viewpoint and weaken Scientist 2's.",
                 "support Scientist 2's viewpoint and weaken Scientist 1's.",
                 "support both viewpoints about equally.",
                 "weaken both viewpoints to the same degree."],
                0,
                ["Correct. The same warmth with far less energy use suggests materials, not waste heat, are responsible.",
                 "Low energy use with the same warmth argues against waste heat as the cause.",
                 "The finding contradicts the waste-heat explanation.",
                 "The finding is consistent with the materials explanation."],
                "If energy use varies greatly but the warmth does not, materials are the better explanation."),
            "difference": (
                "The two viewpoints differ mainly about:",
                ["whether the extra warmth comes from stored sunlight or from energy use.",
                 "whether the city center is actually warmer than the surrounding countryside.",
                 "whether the temperature difference is larger at night than it is during the day.",
                 "whether the city center contains more pavement than the countryside around it."],
                0,
                ["Correct. Stored solar heat versus waste heat is the central disagreement.",
                 "Both accept the temperature difference.",
                 "Both discuss the nighttime difference without disputing it.",
                 "Neither disputes that the city is paved."],
                "The source of the heat is the dispute; the warmth itself is agreed."),
        },
    },
    {
        "id": "moon", "title": "The Origin of the Moon",
        "text_a": (
            "The Moon formed when a body about the size of Mars collided with the young "
            "Earth. The collision blasted molten rock from Earth's outer layers into orbit, "
            "where it quickly gathered into the Moon. This explains why the Moon's rocks "
            "match Earth's in the ratios of oxygen isotopes, which differ from one body to "
            "another in the solar system. It also explains why the Moon has a very small "
            "iron core: the impact stripped mostly rocky material from the outside of the "
            "Earth, leaving Earth's iron core behind. The Moon's rocks are also unusually "
            "dry, as expected if they were once heated enough to drive off their water."),
        "text_b": (
            "The Moon formed elsewhere in the solar system and was captured by Earth's "
            "gravity as it passed nearby. Capture explains why the Moon is so large compared "
            "with Earth; the impact scenario should have left a much smaller moon or none at "
            "all, as computer models of similar collisions often show. The matching oxygen "
            "isotopes could result from the Moon forming in the same region of the solar "
            "system as Earth, from the same raw material. A capture would have left the Moon "
            "in a tilted orbit, and the Moon's orbit is indeed tilted relative to Earth's "
            "equator. The small core could simply reflect the Moon's original composition."),
        "questions": {
            "claim": (
                "With which of the following statements would Scientist 1 most likely agree?",
                ["The Moon is made mostly of material that once belonged to Earth's outer layers.",
                 "The Moon formed far from Earth and was captured by Earth's gravity later on.",
                 "The matching oxygen isotopes are a coincidence of where the Moon formed.",
                 "The Moon's small core simply reflects the composition it had when it formed elsewhere."],
                0,
                ["Correct. Scientist 1 says the collision blasted rock from Earth's outer layers into orbit to form the Moon.",
                 "This is Scientist 2's capture view.",
                 "Scientist 2 offers this explanation; Scientist 1 attributes the match to a shared origin in the impact.",
                 "Scientist 1 explains the small core as a result of the impact stripping Earth's rocky exterior."],
                "Scientist 1's model builds the Moon out of Earth's outer material."),
            "common": (
                "Scientist 1 and Scientist 2 would both most likely agree that:",
                ["the Moon's rocks have oxygen isotope ratios similar to Earth's.",
                 "the Moon has an iron core as large, relative to its size, as Earth's.",
                 "the Moon formed from debris produced by a collision.",
                 "the Moon's orbit is not tilted relative to Earth's equator."],
                0,
                ["Correct. Both accept the isotope match and offer different explanations for it.",
                 "Both describe the Moon's core as small.",
                 "Only Scientist 1 proposes a collision.",
                 "Scientist 2 states the orbit is tilted; Scientist 1 does not dispute this."],
                "The isotope similarity is a shared fact; each scientist explains it differently."),
            "evidence": (
                "Which of the following observations, if confirmed, would provide the strongest support for Scientist 2's explanation?",
                ["Computer models show that captured bodies tend to end up in tilted orbits like the Moon's.",
                 "The Moon's rocks are found to contain almost no water, even deep below the surface.",
                 "Rocks from deep inside the Moon match the composition of Earth's mantle.",
                 "Models show that a Mars-sized impact can place enough material in orbit to form a Moon-sized body."],
                0,
                ["Correct. This links the observed tilted orbit specifically to capture, strengthening Scientist 2's argument.",
                 "Dry rocks fit Scientist 1's heated-debris explanation.",
                 "A match with Earth's mantle supports formation from Earth material.",
                 "This removes Scientist 2's objection that an impact could not make a large moon."],
                "Scientist 2 cites the tilted orbit as a sign of capture; models confirming that connection support the view."),
            "new_obs": (
                "Suppose precise measurements showed that other bodies that formed in the same region of the solar system as Earth have oxygen isotope ratios clearly different from Earth's. This finding would most likely:",
                ["weaken Scientist 2's viewpoint.",
                 "weaken Scientist 1's viewpoint.",
                 "support Scientist 2's viewpoint.",
                 "support both viewpoints equally."],
                0,
                ["Correct. Scientist 2 explains the isotope match by shared raw material in the same region; if neighbors differ, that explanation fails.",
                 "Scientist 1 explains the match by the Moon being made of Earth material, which the finding does not challenge.",
                 "The finding removes Scientist 2's explanation for the match.",
                 "The finding favors the impact explanation."],
                "Scientist 2's account of the isotope match depends on same-region bodies sharing ratios; the finding contradicts that."),
            "difference": (
                "The scientists disagree mainly about:",
                ["whether the Moon was built from Earth material or captured from elsewhere.",
                 "whether the Moon's iron core is small compared with the cores of other rocky bodies.",
                 "whether the Moon currently orbits the Earth in a tilted orbit.",
                 "whether the Earth itself has a large core made of iron."],
                0,
                ["Correct. Formation from Earth debris versus capture of a separate body is the central dispute.",
                 "Both describe a small core.",
                 "Both accept that the Moon orbits Earth.",
                 "Both passages take Earth's iron core for granted."],
                "The disagreement is about origin, not about the Moon's present features."),
        },
    },
    {
        "id": "ice_ages", "title": "What Drives the Ice Ages",
        "text_a": (
            "Ice ages are driven by slow, regular changes in Earth's orbit and tilt. Over "
            "tens of thousands of years, the shape of Earth's orbit, the tilt of its axis, "
            "and the direction the axis points all shift in predictable cycles. These cycles "
            "change how much summer sunlight reaches the far northern lands. When northern "
            "summers are cool, winter snow does not fully melt, ice sheets grow, and their "
            "bright surfaces reflect still more sunlight. Records from deep-sea sediments "
            "show that the timing of past ice ages matches the periods of the orbital "
            "cycles. The cycles are the pacemaker; everything else follows."),
        "text_b": (
            "Orbital cycles are too weak to produce ice ages on their own. The change in "
            "sunlight they cause is small, and it is spread across the year. The real driver "
            "is carbon dioxide. Air bubbles trapped in ancient ice show that carbon dioxide "
            "levels fell during every ice age and rose during every warm period, and carbon "
            "dioxide is far better than orbital changes at shifting the whole planet's "
            "temperature. The gas moves between the oceans and the atmosphere as ocean "
            "circulation changes, which can be triggered by many things. Orbital cycles may "
            "set the timing, but carbon dioxide does the work of cooling the globe."),
        "questions": {
            "claim": (
                "Which of the following claims is most consistent with Scientist 2's viewpoint?",
                ["Carbon dioxide levels were lower during ice ages than during warm periods.",
                 "Orbital changes alone are strong enough to cool the entire planet.",
                 "Deep-sea sediments show no link between ice ages and orbital cycles.",
                 "Carbon dioxide levels stayed essentially constant across ice ages and warm periods."],
                0,
                ["Correct. Scientist 2 cites ice-core bubbles showing carbon dioxide fell during every ice age.",
                 "Scientist 2 says orbital changes are too weak on their own.",
                 "Scientist 2 allows that orbital cycles may set the timing; the sediment evidence is not denied.",
                 "Scientist 2 says the levels rose and fell with the climate."],
                "The fall of carbon dioxide during ice ages is Scientist 2's central evidence."),
            "common": (
                "Despite their disagreement, both scientists would accept that:",
                ["orbital cycles are related to the timing of ice ages.",
                 "carbon dioxide is the main cause of the cooling during ice ages.",
                 "the changes in sunlight caused by orbital cycles are large.",
                 "ice sheets reflect less sunlight than open ground does."],
                0,
                ["Correct. Scientist 1 calls the cycles the pacemaker; Scientist 2 concedes they may set the timing.",
                 "Only Scientist 2 makes carbon dioxide the cause.",
                 "Scientist 2 says the sunlight changes are small.",
                 "Scientist 1 says ice sheets reflect more sunlight; Scientist 2 does not dispute this."],
                "Timing by orbital cycles is accepted by both; what actually does the cooling is disputed."),
            "evidence": (
                "Suppose each of the following were discovered. Which one would most strengthen Scientist 1's position?",
                ["Ice ages are found to begin only at minima of northern summer sunlight, whatever the carbon dioxide level.",
                 "Ice-core records show carbon dioxide levels beginning to fall well before global temperatures start to fall.",
                 "Ocean circulation is found to change sharply just before each ice age.",
                 "Climate models show that small changes in sunlight cannot, by themselves, grow large ice sheets."],
                0,
                ["Correct. Ice ages tied to sunlight minima independent of carbon dioxide make the orbital cycles the controlling factor.",
                 "Carbon dioxide falling first supports Scientist 2's view that it drives the cooling.",
                 "Circulation changes releasing or absorbing carbon dioxide fit Scientist 2's account.",
                 "This is Scientist 2's objection to the orbital explanation."],
                "Scientist 1 claims sunlight changes control ice ages; a finding that ice ages track sunlight minima regardless of carbon dioxide supports that."),
            "new_obs": (
                "Suppose ice-core data showed that during the past several ice ages, carbon dioxide levels began to fall only after the ice sheets had already started growing. This finding would most likely:",
                ["weaken Scientist 2's claim that carbon dioxide drives the cooling.",
                 "weaken Scientist 1's claim that orbital cycles are the pacemaker.",
                 "support Scientist 2's claim that carbon dioxide drives the cooling.",
                 "have no bearing on either viewpoint."],
                0,
                ["Correct. A cause should precede its effect; carbon dioxide falling after the ice grows suggests it responded to the cooling rather than driving it.",
                 "Ice growing before carbon dioxide falls is consistent with orbital cycles starting the process.",
                 "The order of events argues against carbon dioxide as the initial driver.",
                 "The timing of cause and effect bears directly on which factor drives the change."],
                "If carbon dioxide drops only after ice sheets grow, it is hard to credit it as the driver of that growth."),
            "difference": (
                "Which of the following best describes the main point on which the scientists disagree? They disagree about:",
                ["whether orbital cycles or carbon dioxide does most of the cooling during an ice age.",
                 "whether ice ages have actually occurred repeatedly in Earth's past.",
                 "whether carbon dioxide levels in the atmosphere changed between ice ages and warm periods.",
                 "whether Earth's orbit and the tilt of its axis change over time."],
                0,
                ["Correct. Each scientist names a different main cause of the cooling.",
                 "Both accept that ice ages occurred.",
                 "Scientist 1 does not dispute the carbon dioxide record, only its role.",
                 "Both accept the orbital cycles; Scientist 2 questions only their strength."],
                "The passages dispute the main cause of cooling, not the existence of ice ages or orbital cycles."),
        },
    },
    {
        "id": "migration", "title": "Why Songbirds Fly at Night",
        "text_a": (
            "Most small songbirds migrate at night because darkness protects them from "
            "predators. Hawks and falcons hunt by sight during the day, and a small bird "
            "crossing open country in daylight is an easy target. At night the hunters are "
            "roosting. Night flight also lets birds use the daylight hours to feed and "
            "rebuild the fat they burn in flight. Birds that migrate in flocks during the "
            "day, such as swallows, are fast fliers that can feed on insects while moving, "
            "so they can afford the risk. The timing of migration therefore reflects a "
            "trade-off between safety from predators and the need to eat."),
        "text_b": (
            "Small birds migrate at night because of the physical conditions of the night "
            "sky. Night air is cooler and calmer, so a flying bird loses heat more easily "
            "and does not overheat during hours of hard flapping. Cool air also slows the "
            "loss of water from a bird's breath, which matters on long flights with nowhere "
            "to drink. The atmosphere is usually less turbulent after sunset, which lowers "
            "the energy cost of flight. Songbirds also navigate using the stars, a cue "
            "available only at night. Predators influence where birds stop to rest, but the "
            "decision to fly after dark is set by the demands of the flight itself."),
        "questions": {
            "claim": (
                "Scientist 1 would most likely agree with which of the following statements?",
                ["Migrating in daylight would expose small songbirds to hunting hawks.",
                 "Cooler night air keeps songbirds from overheating during long flights.",
                 "Songbirds find their way mainly by the positions of the stars in the night sky.",
                 "Swallows migrate at night in order to avoid being hunted by hawks and falcons."],
                0,
                ["Correct. Scientist 1 says daytime predators make a small bird in open country an easy target.",
                 "Overheating is part of Scientist 2's explanation.",
                 "Star navigation is cited by Scientist 2.",
                 "Scientist 1 says swallows migrate by day and can afford the risk."],
                "Predator avoidance is Scientist 1's central reason for night migration."),
            "common": (
                "Both scientists would most likely agree that:",
                ["long migratory flights place heavy demands on a small bird's body.",
                 "predators have no influence at all on the behavior of migrating songbirds.",
                 "the night sky provides songbirds with navigational cues.",
                 "the atmosphere is more turbulent at night than during the day."],
                0,
                ["Correct. Scientist 1 mentions fat burned in flight; Scientist 2 describes hours of hard flapping and water loss.",
                 "Scientist 2 says predators influence where birds rest; Scientist 1 makes them central.",
                 "Only Scientist 2 mentions navigation by stars.",
                 "Scientist 2 says the night atmosphere is less turbulent."],
                "Both treat migration as physically demanding; they differ on what sets its timing."),
            "evidence": (
                "Which of the following findings, if true, would most strongly support Scientist 2's viewpoint?",
                ["In a wind tunnel, songbirds flying in cool night air lose less water per hour than in warm daytime air.",
                 "Hawk attacks on migrating songbirds are found to be rare after dark and common by day.",
                 "Migrating songbirds are observed to spend most of the daylight hours feeding in order to rebuild their fat.",
                 "Swallows are observed feeding on flying insects while migrating during the daytime, in flocks."],
                0,
                ["Correct. This directly supports the claim that cooler night air reduces water loss during flight.",
                 "Rare attacks at night support the predator-avoidance explanation.",
                 "Daytime feeding fits Scientist 1's account of the trade-off.",
                 "This is Scientist 1's explanation for why swallows can fly by day."],
                "Scientist 2's reasoning rests on the physical advantages of night flight; measured water savings are direct support."),
            "new_obs": (
                "Suppose that on an island with no hawks or falcons, the local songbirds were found to migrate during the day, even though nights there are cooler and calmer than days. This finding would most likely:",
                ["support Scientist 1's viewpoint and weaken Scientist 2's.",
                 "support Scientist 2's viewpoint and weaken Scientist 1's.",
                 "support both viewpoints about equally.",
                 "weaken both viewpoints to the same degree."],
                0,
                ["Correct. Without predators the birds abandon night flight despite favorable night conditions, so predators, not conditions, set the timing.",
                 "Favorable night conditions were available and not used, which contradicts Scientist 2.",
                 "The finding contradicts the physical-conditions explanation.",
                 "The finding is exactly what Scientist 1's view predicts."],
                "Removing predators changes the behavior while night conditions stay favorable, pointing to predators as the cause."),
            "difference": (
                "The central disagreement between the two scientists concerns:",
                ["whether night flight is chosen mainly to avoid predators or because of flight conditions.",
                 "whether most small songbirds actually migrate during the night rather than during the day.",
                 "whether hawks and falcons hunt mainly by sight during the daytime hours.",
                 "whether small birds burn their stored fat during long migratory flights."],
                0,
                ["Correct. Predator avoidance versus flight conditions is the central dispute.",
                 "Both accept that small songbirds migrate at night.",
                 "Scientist 2 does not dispute daytime hunting by predators.",
                 "Both treat migration as energetically costly."],
                "The passages agree on the behavior and disagree on its main cause."),
        },
    },
    {
        "id": "frogs", "title": "The Vanishing Frogs",
        "text_a": (
            "Frog populations in mountain streams across the region have crashed because of "
            "a fungus that infects amphibian skin. Frogs breathe and take in water partly "
            "through their skin, and the infection disrupts this exchange until the heart "
            "fails. The fungus has been found on dead frogs at every site where populations "
            "collapsed, and healthy populations remain only where the fungus is absent. "
            "Declines have spread from valley to valley in a wave, the way a contagious "
            "disease spreads, and have hit protected parks with clean water as hard as "
            "farmland. Frogs raised in captivity and exposed to the fungus die within weeks."),
        "text_b": (
            "The declines are the result of pesticides carried by wind and rain from farms "
            "into the mountains. Pesticide residues have been measured in stream water, in "
            "frog tissue, and even in snow at high elevations. These chemicals weaken the "
            "frogs' immune systems, which is why a fungus that frogs have lived with for a "
            "long time now kills them. The fungus is found on many healthy frogs in regions "
            "with little agriculture, so its presence alone does not cause collapse. "
            "Declines are also most severe at sites downwind of major farming areas. "
            "Reducing pesticide drift would let the frogs resist the fungus as they once did."),
        "questions": {
            "claim": (
                "With which of the following statements would Scientist 2 most likely agree?",
                ["The fungus kills frogs mainly because their immune defenses have been weakened.",
                 "The fungus is absent from every frog population that is still healthy.",
                 "Pesticides are unable to reach streams that lie inside protected parks.",
                 "Frogs exposed to the fungus in captivity always die within a few weeks of exposure."],
                0,
                ["Correct. Scientist 2 says pesticides weaken immunity, allowing a long-familiar fungus to become lethal.",
                 "Scientist 2 says the fungus is found on many healthy frogs.",
                 "Scientist 2 says pesticides travel by wind and rain, even into high-elevation snow.",
                 "This is Scientist 1's evidence, which Scientist 2 does not endorse."],
                "Weakened immunity is the heart of Scientist 2's explanation."),
            "common": (
                "Scientist 1 and Scientist 2 would both most likely agree that:",
                ["the fungus is involved in the deaths of frogs at the collapsed sites.",
                 "pesticide residues are present in the tissues of frogs from the collapsed sites.",
                 "the declines have spread from valley to valley in a wave.",
                 "healthy frog populations exist only where the fungus is absent."],
                0,
                ["Correct. Scientist 1 blames the fungus directly; Scientist 2 says the fungus kills frogs weakened by pesticides.",
                 "Only Scientist 2 cites pesticide residues.",
                 "Only Scientist 1 describes the wave-like spread.",
                 "Scientist 2 says many healthy frogs carry the fungus."],
                "Both accept that the fungus kills frogs; they differ on whether it does so alone."),
            "evidence": (
                "Which of the following observations, if confirmed, would provide the strongest support for Scientist 1's explanation?",
                ["Captive frogs never exposed to pesticides die when infected with the fungus.",
                 "Pesticide residues are detected in snow collected at high elevations in the mountains.",
                 "Frogs at sites downwind of farms decline faster than frogs upwind.",
                 "The fungus is found on healthy frogs in remote regions with no farming."],
                0,
                ["Correct. Death without any pesticide exposure shows the fungus can kill on its own, as Scientist 1 claims.",
                 "Residues in snow support Scientist 2's claim that pesticides reach the mountains.",
                 "A downwind pattern supports the pesticide explanation.",
                 "Healthy carriers are Scientist 2's evidence that the fungus alone is not enough."],
                "Scientist 1 claims the fungus alone is lethal; deaths of frogs with no pesticide exposure demonstrate exactly that."),
            "new_obs": (
                "Suppose frogs at sites with no detectable pesticide residue were found to collapse at the same rate as frogs at heavily contaminated sites once the fungus arrived. This finding would most likely:",
                ["weaken Scientist 2's viewpoint.",
                 "weaken Scientist 1's viewpoint.",
                 "support Scientist 2's viewpoint.",
                 "support both viewpoints equally."],
                0,
                ["Correct. If pesticide-free sites collapse just as fast, pesticides are not needed to explain the collapse.",
                 "Collapse wherever the fungus arrives is what Scientist 1 predicts.",
                 "Equal collapse without pesticides argues against the pesticide explanation.",
                 "The finding favors the fungus-alone explanation."],
                "Scientist 2 predicts that pesticide exposure is what makes the fungus lethal; equal collapse without pesticides contradicts that."),
            "difference": (
                "The two viewpoints differ mainly about:",
                ["whether the fungus by itself is enough to cause the population collapses.",
                 "whether frog populations in the region's mountain streams have actually declined.",
                 "whether the fungus infects the skin of frogs and disrupts breathing.",
                 "whether there are farms in the region that use pesticides."],
                0,
                ["Correct. Scientist 1 says the fungus alone is sufficient; Scientist 2 says pesticides are required to make it lethal.",
                 "Both accept the declines.",
                 "Neither disputes that the fungus infects frog skin.",
                 "Both passages mention farmland in the region."],
                "The dispute is about whether the fungus needs help from pesticides, not about the fungus or the decline."),
        },
    },
    {
        "id": "leaves", "title": "The Colors of Autumn",
        "text_a": (
            "The red and yellow colors of autumn leaves are simply revealed, not made. "
            "Throughout summer a leaf is packed with green chlorophyll, which hides yellow "
            "and orange pigments that are present all along and help capture light. As days "
            "shorten, the tree stops repairing chlorophyll and breaks it down to recover its "
            "nitrogen, and the green fades. The yellow pigments remain and finally show. Red "
            "colors come from the breakdown of sugars trapped in the leaf once the tree "
            "seals off the leaf stem. The display is a side effect of recycling, which is "
            "why a leaf's color has no clear benefit to the tree."),
        "text_b": (
            "Red autumn leaves are produced on purpose. The red pigments, called "
            "anthocyanins, are not present in summer; the leaf makes them fresh in autumn, "
            "using energy and sugar at a time when the tree is shutting down. Making them "
            "would be wasteful unless they did something useful. Anthocyanins absorb excess "
            "light and protect the leaf's cells while the tree pulls valuable nutrients out "
            "of the leaf before it drops. Leaves on the sunny side of a tree turn redder "
            "than shaded leaves, and trees growing in poor soil, which need to recover "
            "nutrients most, produce the reddest leaves. Yellow pigments may be unmasked, but "
            "red is manufactured."),
        "questions": {
            "claim": (
                "Which of the following claims is most consistent with Scientist 2's viewpoint?",
                ["Red pigments are newly made in the leaf during autumn.",
                 "Red pigments are present in leaves all summer but hidden by chlorophyll.",
                 "The red color of autumn leaves provides no benefit to the tree.",
                 "Shaded leaves turn redder than leaves on the sunny side of a tree."],
                0,
                ["Correct. Scientist 2 says anthocyanins are absent in summer and made fresh in autumn.",
                 "Scientist 2 explicitly denies that red pigments are present in summer.",
                 "Scientist 2 argues the red pigments protect cells during nutrient recovery.",
                 "Scientist 2 says sunny-side leaves turn redder."],
                "Fresh production of anthocyanins in autumn is Scientist 2's core claim."),
            "common": (
                "Despite their disagreement, both scientists would accept that:",
                ["yellow pigments are present in leaves before autumn begins.",
                 "red pigments protect the cells of a leaf from excess light.",
                 "the tree makes new pigments in its leaves as autumn begins.",
                 "a leaf's autumn color provides no benefit at all to the tree."],
                0,
                ["Correct. Scientist 1 says yellow pigments are present all along; Scientist 2 concedes yellow may be unmasked.",
                 "Only Scientist 2 makes this claim.",
                 "Scientist 1 says the colors are revealed, not made.",
                 "Scientist 2 argues that red color is beneficial."],
                "Both allow that yellow is unmasked; the dispute is over red."),
            "evidence": (
                "Suppose each of the following were discovered. Which one would most strengthen Scientist 2's position?",
                ["Shaded autumn leaves give back fewer nutrients to the tree than sunlit, red leaves do.",
                 "Yellow pigments are detected in green leaves throughout the summer growing season.",
                 "The breakdown of chlorophyll releases nitrogen that the tree stores for the following spring.",
                 "Red pigment appears in a leaf only after the tree has sealed off the leaf's stem."],
                0,
                ["Correct. A link between red, sunlit leaves and better nutrient recovery supports the protective role Scientist 2 proposes.",
                 "Both scientists accept that yellow pigments are present in summer.",
                 "Nitrogen recovery from chlorophyll is part of Scientist 1's account.",
                 "Scientist 1 ties red color to sugars trapped after the stem is sealed, so this fits Scientist 1."],
                "Scientist 2 claims red pigments protect nutrient recovery; evidence that sunlit red leaves yield more nutrients supports that."),
            "new_obs": (
                "Suppose chemical analysis found that the red pigment molecules of autumn leaves had been present at low levels in the same leaves throughout the summer, hidden by chlorophyll. This finding would most likely:",
                ["weaken Scientist 2's viewpoint.",
                 "weaken Scientist 1's viewpoint.",
                 "support Scientist 2's viewpoint.",
                 "support both viewpoints equally."],
                0,
                ["Correct. Scientist 2 insists the red pigments are absent in summer and made fresh; their presence all along contradicts that.",
                 "Hidden pigments revealed in autumn is consistent with Scientist 1's unmasking view.",
                 "The finding contradicts Scientist 2's claim of fresh production.",
                 "The finding favors the unmasking explanation."],
                "Scientist 2's argument depends on red pigments being newly made; finding them present in summer undercuts it."),
            "difference": (
                "The scientists disagree mainly about:",
                ["whether red autumn color is actively produced or merely revealed.",
                 "whether chlorophyll is the pigment that makes leaves green in summer.",
                 "whether the leaves of trees change color as autumn arrives.",
                 "whether yellow pigments exist in leaves during the summer."],
                0,
                ["Correct. Manufactured versus unmasked red pigment is the central dispute.",
                 "Neither disputes the color of chlorophyll.",
                 "Both accept that leaves change color.",
                 "Both accept that yellow pigments are present in summer."],
                "Yellow is common ground; the origin of red is the disagreement."),
        },
    },
    {
        "id": "sinkhole", "title": "The Collapse at Carver Road",
        "text_a": (
            "The sudden hole that opened beneath Carver Road formed because rainwater "
            "slowly dissolved the limestone beneath the surface. Limestone is made of a "
            "mineral that dissolves in slightly acidic water, and rain becomes acidic as it "
            "absorbs carbon dioxide from the air and soil. Over thousands of years, water "
            "seeping down through cracks widened them into a cavern. The roof of the cavern "
            "thinned until it could no longer hold up the road. Caves and springs are common "
            "in the surrounding countryside, and the hole has sheer walls of solid limestone, "
            "exactly as expected when a cavern roof gives way."),
        "text_b": (
            "The hole formed because a leaking water main washed away the soil beneath the "
            "road. The main, installed sixty years ago, runs directly under the collapse and "
            "was found to be cracked. Escaping water carried fine soil particles into a "
            "nearby storm drain, leaving a growing void just below the pavement. Limestone "
            "caverns take thousands of years to form, but the road showed no sign of "
            "sinking until two months before the collapse, soon after water pressure in the "
            "main was raised. The hole's walls are mostly loose soil, and the solid rock "
            "lies several meters deeper. Repairing the main is the key to preventing another "
            "collapse."),
        "questions": {
            "claim": (
                "Scientist 1 would most likely agree with which of the following statements?",
                ["The cavern beneath the road took thousands of years to form.",
                 "The leaking water main is the main reason the road collapsed.",
                 "The hole's walls consist mostly of loose soil.",
                 "The road showed signs of sinking only after the water pressure was raised."],
                0,
                ["Correct. Scientist 1 describes limestone dissolving over thousands of years.",
                 "The water main is Scientist 2's explanation.",
                 "Scientist 1 says the walls are solid limestone.",
                 "This observation is cited by Scientist 2."],
                "Slow dissolving of limestone over thousands of years is the basis of Scientist 1's view."),
            "common": (
                "Both scientists would most likely agree that:",
                ["material beneath the road was removed before the collapse occurred.",
                 "the collapse was caused by rainwater that had become slightly acidic.",
                 "the water main under the road is cracked.",
                 "the hole's walls are made of solid limestone."],
                0,
                ["Correct. Scientist 1 describes dissolved limestone and Scientist 2 describes washed-away soil, but both describe a void forming first.",
                 "Only Scientist 1 cites acidic rainwater.",
                 "Only Scientist 2 reports the cracked main.",
                 "Scientist 2 says the walls are mostly loose soil."],
                "Both views involve a void forming beneath the pavement; they differ on how it formed."),
            "evidence": (
                "Which of the following findings, if true, would most strongly support Scientist 2's viewpoint?",
                ["Soil matching that beneath the road began appearing in the storm drain two months before the collapse.",
                 "The groundwater beneath the area is found to be slightly acidic, as is typical for limestone country.",
                 "Several large caverns are discovered in the limestone a few kilometers from the road.",
                 "The water main beneath the road was found to have been shut off for the entire past year."],
                0,
                ["Correct. Soil from under the road appearing in the drain just before the collapse directly shows the washing-away Scientist 2 proposes.",
                 "Acidic groundwater supports the limestone-dissolving explanation.",
                 "Caverns nearby fit Scientist 1's view of the region.",
                 "A shut-off main could not have leaked, which weakens Scientist 2."],
                "Scientist 2 needs evidence that soil was washed into the drain recently; matching sediment with the right timing provides it."),
            "new_obs": (
                "Suppose drilling showed that the limestone beneath the road is solid, with no cavities, down to a depth of 30 meters. This finding would most likely:",
                ["weaken Scientist 1's viewpoint.",
                 "weaken Scientist 2's viewpoint.",
                 "support Scientist 1's viewpoint.",
                 "support both viewpoints equally."],
                0,
                ["Correct. Scientist 1's explanation requires a cavern in the limestone; solid rock with no cavities contradicts it.",
                 "Scientist 2 places the void in the soil above the rock, so solid rock below is consistent with that view.",
                 "The finding removes the cavern Scientist 1 relies on.",
                 "The finding favors the soil-washout explanation."],
                "No cavern in the limestone means no collapsing cavern roof, which is what Scientist 1 proposes."),
            "difference": (
                "Which of the following best describes the main point on which the scientists disagree? They disagree about:",
                ["whether the void beneath the road formed slowly in rock or quickly in soil.",
                 "whether a hole actually opened beneath the surface of Carver Road.",
                 "whether limestone can be dissolved by slightly acidic water over long periods.",
                 "whether a water main runs beneath the road at the site of the collapse."],
                0,
                ["Correct. Slow dissolving of limestone versus rapid washing of soil is the central dispute.",
                 "Both accept that the collapse occurred.",
                 "Scientist 2 does not dispute the chemistry, only its relevance here.",
                 "Scientist 1 does not deny the main exists; the dispute is about its role."],
                "The disagreement concerns the process and timescale that created the void."),
        },
    },
]
