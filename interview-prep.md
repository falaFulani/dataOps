# Interview Prep — MLOps Support Team Lead, CloudFactory

**For the introductory call next week.** This is your single review doc.
Read it the morning of the call. Fill in every `[bracket]` with real numbers/names
before then — specifics win interviews.

> Note: An introductory call is usually part culture-fit, part mutual discovery.
> It's rarely a deep technical grilling. Your job: sound credible, show genuine
> interest, ask sharp questions, and flag the ML gap honestly as a fast ramp.

---

## 1. Your 60-second opening pitch

Use when they say "tell me about yourself" or "why this role?"

> "I've spent the last [X] years in platform engineering at I&M Bank, owning the
> reliability of 24/7 systems in a heavily regulated environment. My core work has
> been the three things this role calls for: establishing SLOs and the alerting
> behind them, owning incidents end to end, and standardizing post-incident
> governance. I've also led cross-functional technical teams, so I'm comfortable
> being both the operational owner and the person developing the engineers around me.
>
> What draws me to CloudFactory is that the operational discipline is identical,
> but the domain is new and growing — moving from banking infrastructure to live
> ML pipelines. I see the ML-specific knowledge as a fast on-ramp on a strong
> reliability foundation, not a start from zero. And the mission of connecting
> people to meaningful work is something I'd genuinely want to support — especially
> leading a team that already spans Kenya, where I'm based."

---

## 2. The one thing to say about your gap

When ML experience comes up (it will), say this:

> "My reliability foundation transfers directly — SLOs, alerting, incident
> governance, on-call leadership — because operationally an ML pipeline is still a
> production system with latency, errors, and uptime to defend. What's new to me is
> the ML-specific failure layer: drift, data quality, and training-serving skew,
> and the fact that these fail *silently* rather than throwing errors. I've been
> studying that and even built out a learning plan. I see it as a focused ramp, not
> a rebuild. What I'd want to learn fast is the specific signals and thresholds your
> team uses today."

That last line turns the gap into a smart question.

---

## 3. ML cheat sheet (review right before the call)

**The core insight:** Traditional software fails *loudly* (errors, crashes).
ML systems fail *silently* — the pipeline runs green while predictions quietly
get worse. That's why ML monitoring is its own discipline.

**The pipeline:** data ingestion → validation/preprocessing → training →
evaluation → deployment/serving → monitoring → retraining (loop).

**The failure family (know these cold):**
- **Data drift** — live input data differs from training data.
- **Concept drift** — the real-world relationship changed (e.g., fraud patterns shift).
- **Prediction drift** — the model's output distribution shifts (often the first visible symptom).
- **Training-serving skew** — data processing in production differs from training.

**Two monitoring layers:**
- Operational (yours already): latency, throughput, error rate, uptime, resources.
- ML-specific (new): prediction accuracy over time, drift scores, data-quality checks, feature distributions.

**Vocabulary to use naturally:**
model registry · feature store · model rollback · shadow/canary deployment ·
ground truth/labels · retraining · inference (real-time vs batch).

**Tools to recognize (don't need depth):**
MLflow / W&B (tracking + registry) · Kubeflow (pipelines on k8s) ·
Evidently / Arize / WhyLabs (drift monitoring) · Seldon / KServe (serving) ·
Prometheus + Grafana (operational metrics).

---

## 4. Questions THEY may ask + how to answer

**"Tell me about yourself / why this role?"**
→ Use the opening pitch (Section 1).

**"You don't have ML experience — how would you handle that?"**
→ Use the gap statement (Section 2).

**"Walk me through a major incident you owned."**
→ STAR Story 1 below.

**"How have you established SLOs / reduced alert noise?"**
→ STAR Story 2.

**"How do you standardize process across a team?"**
→ STAR Story 3.

**"How do you lead a distributed / remote team?"**
→ STAR Story 4. Emphasize timezones, clear on-call rotations, removing single points of knowledge failure.

**"Why are you leaving banking / I&M?"**
→ Keep it positive and forward-looking: growth into a fast-moving domain, global
remote team, mission-driven work. Never criticize your current employer.

**"What do you know about CloudFactory?"**
→ Mission: "connect one million people to meaningful work." Impact-sourcing /
distributed workforce model. Be ready to say one genuine sentence on why that resonates.

**"Where do you see yourself / what's your next career step?"**
→ Operational leadership in a growing technical domain; building and developing a
team; deepening ML/platform expertise.

---

## 5. Your STAR stories (fill in the brackets)

### Story 1 — Owning a major incident
- **S:** [System] started failing [how], affecting [customer impact].
- **T:** As [role], accountable for restoring service + preventing recurrence, with regulatory reporting in play.
- **A:** Led triage, root-caused to [cause], applied mitigation, drove permanent fix, ran blameless postmortem, added [missing alert/control].
- **R:** Restored in [X min]; recurrence of that failure class → zero; postmortem became a team template. MTTR [X→Y].

### Story 2 — Establishing SLOs / cutting alert noise
- **S:** [Alerting on every spike → noise, on-call fatigue, missed real issues.]
- **T:** Define meaningful SLOs; rebuild alerts around user-impacting symptoms.
- **A:** Defined availability/latency targets + error budgets; retuned alerts to SLO burn-rate; built [Grafana] dashboards.
- **R:** Alert volume down [X%]; faster detection of real degradations; pages [X→Y per week].

### Story 3 — Standardizing post-incident governance
- **S:** [Inconsistent incident reviews; audit risk.]
- **T:** Standardize governance to satisfy internal + regulatory audit.
- **A:** Created postmortem template + RCA process + severity scheme; made reviews blameless; tracked action items to closure.
- **R:** [100% of Sev-1/2 documented]; action-item closure [X%]; passed [audit] cleanly.

### Story 4 — Leading a distributed/cross-functional team
- **S:** [Team size/mix; challenge — hero-dependence, uneven load, unclear ownership.]
- **T:** Improve coordination; remove single points of failure.
- **A:** Set on-call rotations, escalation paths, knowledge-sharing; mentored [junior eng].
- **R:** Even incident handling; faster response; [junior grew into owning X].

> Practice each out loud once. Target 60–90 seconds each.

---

## 6. Scenario questions (they may test your thinking)

**"A model's prediction accuracy dropped overnight. Walk me through your response."**
Model answer structure:
1. **Triage scope** — Is it operational (latency/errors) or quality (accuracy/drift)? Check dashboards for both layers.
2. **Stabilize** — If a recent model deploy caused it, roll back to the last good model version (registry). Stabilize before investigating.
3. **Investigate root cause** — Check for data drift (did input data change?), a broken upstream data source, or training-serving skew. Look at when the drop started and what changed around then.
4. **Decide the fix** — Rollback vs retrain on fresh data vs fix the data pipeline. Don't retrain blindly if the cause is bad input data.
5. **Communicate** — Update stakeholders/client per severity; track in incident channel.
6. **Post-incident** — Blameless postmortem, add the missing alert (e.g., drift threshold), close action items.
→ Punchline: "The structure mirrors any production incident — stabilize, root-cause, fix, learn — but with ML-specific suspects like drift and data quality added to the checklist."

**"Your on-call engineer in Nepal escalates an issue, but the owning expert is asleep in Colombia. How do you handle it?"**
→ Clear escalation paths defined in advance; runbooks so first responder can act without the expert; severity-based decision on whether to wake someone; follow-the-sun handoff notes. Emphasize *removing single points of knowledge failure* so no incident depends on one person being awake.

**"How would you reduce alert fatigue on the team?"**
→ Alert on symptoms/SLO burn-rate not raw metrics; tune thresholds; group/deduplicate; route by severity; regularly review which alerts fired and were ignored, and delete the noise. Tie to your real Story 2.

**"How do you decide when to retrain a model?"**
→ When drift/accuracy crosses a defined threshold AND the cause is genuine data/concept change (not a pipeline bug). Tie retraining to SLOs/error budgets, not gut feel. Acknowledge ground-truth/label delay makes live accuracy hard to measure, so drift proxies matter.

---

## 7. Questions YOU ask them

Pick 4–5. Asking good questions is half of an intro call.

**Role & team**
- What's the biggest operational pain point you want this lead to fix in the first 90 days?
- What does the current on-call rotation and escalation path look like across the three regions?
- Is this role hands-on, pure people leadership, or a blend? What's the split?

**Stack & scope**
- How mature is the current alerting/observability stack? What tools are in place?
- What kinds of ML pipelines does the team monitor — training, inference, data pipelines, or all?
- What ML-specific signals do you monitor today (drift, data quality, latency, accuracy)?
- What does a typical "client escalation" involve, and who owns the client relationship?

**Success & growth**
- How will you measure success for this role at 90 days and one year?
- Why is this role open now — new position or backfill?

**Culture & mission**
- How does the MLOps team connect day-to-day to the "meaningful work" mission?
- What's the team's tenure and how do you support growth for remote engineers?

---

## 8. Logistics checklist (day of call)

- [ ] Test camera, mic, and internet; have a backup (phone hotspot)
- [ ] Quiet, well-lit space; neutral background
- [ ] This doc open on a second screen/printed
- [ ] One genuine sentence ready on why CloudFactory's mission resonates
- [ ] 2–3 brackets-filled metrics memorized (your strongest numbers)
- [ ] Confirm timezone of the call (you're EAT; recruiter may be elsewhere)
- [ ] Have your own questions visible so you don't forget to ask
- [ ] Send a short thank-you note within 24 hrs afterward

---

## TL;DR for the call
1. Lead with reliability + governance + leadership — that's your match.
2. Own the ML gap honestly, framed as a fast ramp (you even built a learning plan).
3. Know the drift family and the "fails silently" insight cold.
4. Ask sharp questions about their stack, pain points, and success measures.
5. Tie everything back to their mission.
