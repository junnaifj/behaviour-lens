---
name: behaviour-lens
description: Analyse a daily observation of human behaviour as a hypothesis, research it, save a five-minute brief to an Obsidian vault, or create weekly/monthly/quarterly meta-pattern reviews of accumulated observation notes.
---

# Behaviour Lens

## Route the request

- If the user supplies an observation, run the **daily observation** workflow. Minimal input is a product principle: do not ask follow-ups unless the text cannot reasonably be interpreted as an observation.
- If the user asks for a weekly, monthly, or quarterly review, run the **pattern review** workflow.
- If the user asks to find or revisit notes, use `search_observations` or `get_observations_by_period`.

## Daily observation workflow

1. Preserve the raw observation. Restate it as a testable or inspectable hypothesis and note important ambiguity.
2. Research before writing. Browse for time-sensitive AI, policy, platform, social, and current-affairs claims. Prefer peer-reviewed research and primary or official sources; use strong reporting for current affairs. Never invent a citation. Say when evidence is thin.
3. Assign one evidence status: `supported`, `partly-supported`, `uncertain`, or `potentially-misleading`. This describes the proposition, not the observer.
4. Select 2–4 strongest mechanisms. Separate research findings from plausible interpretation and extrapolation.
5. Give credible competing explanations, including selection effects, setting effects, cultural or geographic variation, and evidence that could change the assessment.
6. Include AI and society only when meaningful. Say “No strong AI connection identified” rather than forcing one.
7. Include compact current-affairs updates that directly illuminate the observation. Verify them at execution time and date them where useful.
8. Finish with a broader synthesis and 4–8 traceable linked sources. Target 800–1,100 words and no more than five minutes. Prefer clarity over filling the range.
9. Call `save_observation` with the raw observation, complete Markdown brief, metadata, and sources. Use concise controlled tags and a short slug. Report the saved path.

Use these headings: `Observation as hypothesis`, `Evidence status`, `Strongest explanations`, `Credible alternatives and limits`, `AI and society now`, `Current-affairs signals`, `Why it matters`, and `Sources`.

Do not imply causation from correlation. Do not treat an anecdote as prevalence evidence. Never diagnose the user or observed people.

## Pattern review workflow

1. Resolve the period precisely: ISO Monday–Sunday weeks, calendar months, and calendar quarters unless specified otherwise.
2. Call `get_observations_by_period`. Base every claim on returned notes. State note count and coverage gaps.
3. Analyse attention (settings, actors, domains, behaviours), framing (descriptive, causal, comparative, evaluative, moral, technological, institutional), analytical scale (individual through societal), defensible changes over time, and recurring themes.
4. Discuss apparent blind spots strictly as absences or underrepresentation in the recorded notes. The archive is a selective sample. “Not recorded” is not “not perceived,” “not valued,” or “psychologically avoided.” Do not infer personality, mental state, motives, pathology, or diagnosis.
5. Include counter-readings and uncertainty. Suggest 2–4 gentle observation prompts for the next period as experiments, not corrections.
6. Call `save_pattern_review` with type, dates, note IDs, and Markdown review. Report the saved path.

Read `../../schemas/observation.schema.json` and `../../schemas/pattern-review.schema.json` when constructing inputs. Use ISO 8601 dates. Do not put sensitive inferred traits into YAML.
