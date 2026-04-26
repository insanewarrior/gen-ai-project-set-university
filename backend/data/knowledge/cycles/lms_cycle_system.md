# LMS Self-Calculating Cycles (SRC) System

## Origin and Authorship

The Self-Calculating Cycles (SRC) are a body of programmable training spreadsheets developed by Dmitry Bondarenko, Vadim Myakotin, Andrey Barskov, and the LastManStanding (lastman.org) coaching team. The system is rooted in Soviet weightlifting science — Vorobyev's load periodization, Chernyak's relative intensity formulas, Funtikov's intensity calculation, and Bondarenko's session-time model — and translated into Excel workbooks that recalculate every weight, set, and rep when an athlete enters their current 1RM, target 1RM, and start date.

The cycles are distributed openly through `last-man.org` and `lms-plans.site`. They represent one of the most algorithmic and well-documented frameworks for non-Western strength programming.

## Core Methodological Vocabulary

A working understanding of the SRC system requires the following terms — they recur in every cycle file and are not standard Western terminology.

Total rep count is the count of barbell lifts in a microcycle, equivalent to the Western concept of repetition volume but counted at the lift level rather than the set level. Tonnage is computed by multiplying total rep count by average bar weight. Average bar weight equals total tonnage divided by total rep count and serves as the input for relative intensity calculations.

Relative intensity by Chernyak is a per-session intensity index derived from the ratio of average bar weight to the athlete's 1RM, weighted by exercise type. Funtikov's intensity is a related but corrected variant. Bondarenko's session-time model estimates how long a workout will last given prescribed volume and intensity.

PM is the predicted maximum used by the calculator at any given microcycle; it is not necessarily the athlete's true tested 1RM. The system explicitly notes that PM is a calculation input that drives load prescription, and athletes should re-test their actual 1RM 3–5 days after the cycle completes.

## Macrocycle and Microcycle Structure

A typical SRC macrocycle spans 12 to 16 microcycles (weeks). Each microcycle contains 2 to 4 training sessions depending on the cycle variant. The volume curve has a configurable shape: a number of descending steps followed by a number of ascending steps, with explicit step sizes (e.g., descending step 0.19, ascending step 0.22) and a starting rep count (e.g., 230). This produces a wave loading pattern where volume drops, then rises, peaking late in the macrocycle to coincide with intensity peaks.

The layout is the prescribed sets-by-reps scheme such as 4×4, 5×3, 6×2. Each microcycle assigns one layout to each main exercise, and the layout shifts across the macrocycle to manage stimulus and fatigue.

Within a microcycle, training days are classified by load: heavy, medium, and light. The same exercise may appear on multiple days at different intensity classes — e.g., a heavy bench session on day 1 and a light bench session on day 3 — to maintain frequency without overreaching.

## Exercise Coding and Group Tags

Cycles use compact two- or three-letter group tags to classify each exercise. The squat-group tag marks squat-pattern movements such as back squat, front squat, and wide-stance squat. The bench-group tag marks bench-pattern movements: flat bench press, incline press, close-grip bench, dumbbell bench, and floor press. The deadlift-group tag marks deadlift-pattern movements: conventional deadlift, Romanian deadlift, good mornings. The general-fitness tag marks general physical preparation work: standing press, French press, barbell curl, dumbbell tricep extension. Some cycles use a separate tag to distinguish a primary press lift from accessory presses.

Each exercise also carries a coefficient reflecting its impact on the body — multi-joint lifts get higher values (1.0 to 1.4) while single-joint accessories get lower values (0.3 to 0.5). The coefficient feeds the relative intensity calculation so that heavy squat work counts more than equivalent volume of bicep curls.

## Cycle Catalog and Specialization

The published SRC catalog covers a deliberate range of athletes and goals, with selection driven by discipline, training period, athlete level, and body weight.

SRC1 is a basic powerlifting strength cycle for beginners (II rank through Candidate to Master of Sport, Candidate to Master of Sport) with three training days, body weight 80kg or more. SRC2 is the four-day intermediate counterpart for Candidate to Master of Sport through Master of Sport. SRC14 is a three-day mixed-period powerlifting cycle that scales from II rank up to Master of Sport, accepting body weights from 60kg, designed for beginners and advanced lifters returning after layoffs. SRC7 is a peak-output powerlifting cycle for high-level athletes (Master of Sport through International Master of Sport), with body weight from 70kg.

SRC4 is a strength cycle for arm wrestling at the II rank to Candidate to Master of Sport level, authored by Andrey Barskov, oriented toward top-roll style. Its exercises differ sharply from powerlifting cycles: top imitation, side press, supination of strength bands, wrist with strength bands, shoulder adduction, and pull-down on the cable.

SRC5 and SRC6 are strength bench-press cycles for beginner and intermediate levels respectively. SRC10 and SRC11 are bench-press strength endurance cycles for Candidate to Master of Sport through Master of Sport and Master of Sport to International Master of Sport. SRC13 is a combined strength bench cycle for Candidate to Master of Sport to International Master of Sport with no body weight restriction; its annotation notes that it has zero load on back and legs and includes an optional cool-down sequence (lateral and front raises for shoulders, leg extensions or curls, hyperextensions, light bench machine and cable crossover for chest, rotator cuff finishers).

SRC8 is a bodybuilding mass-gain cycle for intermediate athletes (3+ years of training, body weight 80kg+, focused on lean mass). SRC9 and SRC12 are deadlift-and-bench focused cycles for elite levels. SRC15 and SRC16 are bench cycles for the 60kg+ body weight class — peak output and strength endurance respectively.

## When Not to Use a Cycle

The SRC documentation is explicit about contraindications. A cycle should not be applied if the athlete has a markedly low body-weight-to-height ratio (visible underweight or insufficient muscle mass), if there are obvious technical flaws in the cycle's exercises, if there are injuries or chronic pain in the involved muscles or tendons, if the athlete is under regular psychological or physical stress at work, or if there is insufficient sleep and recovery. The system assumes a baseline of technical competence, recovery capacity, and hormonal health.

## Adaptation for Natural Athletes

The cycles were originally written assuming pharmacological assistance (steroid-using powerlifting context). For drug-free athletes, the documentation prescribes a correction percentage of -0.4 to 0.1, applied as a downward shift to all calculated weights. For oral steroid use the correction is 0.2 to 0.5, for two-drug stacks 0.4 to 0.7, and for larger stacks 0.6 to 1.1. Natural athletes are advised to use the lower 0.5–1% correction range and individualize further based on subjective recovery.

## Practical Selection Heuristics

For a beginner powerlifter at 80kg+ training three days per week, SRC1 is the starting point. For an intermediate (Candidate to Master of Sport level), SRC2 with four sessions per week. For arm wrestlers entering structured training, SRC4. For lighter lifters under 80kg, SRC14 (powerlifting) or SRC15/16 (bench). For peaking into competition, SRC7 or block cycles. The cycle selector at lms-plans.site/selector formalizes this matrix as a decision tool.

## Why The System Works in Practice

The SRC system's strength is not any single mathematical innovation but the integration of three things: a fixed periodization shape (total rep count wave) that prevents the athlete from accumulating fatigue indefinitely, exercise-specific impact coefficients that prevent over-counting accessory volume, and explicit body-weight and rank thresholds that match training stimulus to recovery capacity. The result is a programming framework that produces non-trivial intensity prescription from a small set of athlete inputs, similar in spirit to Western percentage-based templates (Sheiko, Smolov, Juggernaut) but with denser frequency and a Soviet-flavored emphasis on tonnage and relative intensity rather than e1RM and RPE.
