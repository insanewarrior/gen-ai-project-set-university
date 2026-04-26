# LMS-Plans.site Cycle Repository

## Site Purpose

lms-plans.site is the primary distribution point for the LMS Self-Calculating Cycles (SRC, Russian: Self-Calculating Cycle). The site is organized as a programming reference rather than a coaching service: athletes select a cycle by discipline and level, download the Excel workbook, enter their inputs, and follow the prescribed weights and reps.

The navigation structure has four main sections: "Before You Start" (orientation and prerequisite reading), "Choose Your Cycle" (the selector tool), "Questions and Answers" (FAQ), and "About the Site / About the Author / Support the Author" (credits and sustainability).

## Selecting a Cycle

The cycle selector at lms-plans.site/selector organizes the catalog by specialization and athlete profile. Programs are categorized into Bench Press Cycles, Standing Press Cycles, Bicep Curl Cycles, Powerlifting Cycles, and Miscellaneous Cycles (hybrid and supplementary approaches).

Each cycle specifies its experience level (from II rank through Master of Sport — MSMK), its training period type (strength, endurance, peak, mass-gain, mixed), the minimum body weight for which the cycle is calibrated, and any additional constraints. The selector matches athlete profile to cycle in a structured way that prevents common mismatches such as a beginner picking an International Master of Sport-level peaking cycle.

## The Self-Calculating Concept

The phrase "self-calculating" refers to the Excel-based macros and formulas that recalculate every prescribed weight when the athlete enters their current 1RM, target 1RM, and start date. The athlete does not manually compute percentages or wave loads — the spreadsheet does. This frees the athlete to focus on execution and recovery rather than programming arithmetic.

The site notes explicitly that "two training sessions per week are extremely limited for achieving strength gains, so training becomes voluminous and conducted at high intensity percentages" — this is the rationale for cycles offering 2× per week schedules: they compensate for low frequency with higher per-session intensity and volume.

## Frequently Asked Questions Distilled

For an athlete at Candidate to Master of Sport level new to the system: read the cycle's instructions and the "Before You Begin" article, then choose by discipline and current training period. The site is structured so the homepage and selector page lead the athlete through the decision.

On training without anabolic steroids: programs accommodate athletes regardless of pharmacology. Where steroid use is assumed, the cycle's documentation flags this. Natural athletes apply a 0.5–1% downward correction percentage or adjust further based on individual experience.

On overtraining concern: load parameters (tonnage and volume) are calculated systematically. Following instructions correctly prevents overload. Multiple identical lifts within a week appear at different intensity classes (light, medium, heavy) and no maximum-effort work appears in any single session.

On intensity feeling too light: the cycle's effectiveness comes from the combined tonnage and intensity across all light, medium, and heavy work. The plan does not depend on any single heavy exercise. For 90% of users, the integrated stimulus across the full microcycle is adequate.

On missing exercises (lats, calves, biceps, traps, abs): cycles deliberately include only core lifts with calculated loads. Supplementary general-development exercises should be added independently at light or medium intensity as recommended in the cycle's text.

On post-cycle 1RM testing: re-test the actual 1RM after 3–5 days of recovery via either a max attempt or a heavy single. The PM value used by the calculator throughout the cycle is the prescribed input load, not the athlete's current true maximum.

## How the Calculator Works at the Spreadsheet Level

The cycle workbook contains several sheets. The Reference sheet holds athlete inputs: starting PM, target PM, start date, microcycle count, volume wave parameters (descending steps, ascending steps, step sizes, starting rep count). The 1-per-day sheet (1 per day) shows calculated weights for athletes training one workout per day; the 2-per-day sheet (2 per day) is for two-a-day splits.

The F sheet contains polynomial fits and lookup tables that drive intensity calculations — these are mathematical machinery the athlete does not interact with directly. The Reports sheet summarizes per-microcycle tonnage, total rep count, average relative intensity (Chernyak's method), Funtikov's intensity, and Bondarenko's session-time estimate.

To use the cycle: enter your input values in the reference sheet, save, and read the prescribed work from the 1-per-day or 2-per-day sheet. Keyboard shortcuts (Ctrl+J/T/I in newer cycles, Ctrl+Q/Y/U in older ones) clear microcycle data, isolate per-exercise output, and hide rest days. Excel macro support must be enabled, and background error detection should be disabled (File → Options → Formulas → Error Checking) because some intentional cells produce values Excel flags as suspicious.

## Block Cycles and Embedded Cycles

Beyond the standard SRC catalog, the site offers two additional formats. Block cycles are 4-week peak programs for bench press and powerlifting, used for short-term peaking into competition rather than as standalone training. Embedded cycles are supplementary programs (overhead press, strict biceps curl) that can be inserted into a base cycle without disrupting its main lift programming.
