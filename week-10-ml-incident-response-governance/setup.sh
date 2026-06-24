#!/bin/bash
# Week 10 — ML Incident Response & Governance Setup
# This week is primarily documentation and process work.
# Minimal tooling setup — just markdown viewing and validation.

set -e

echo "=== Setting up Week 10: ML Incident Response & Governance ==="
echo ""
echo "This week is different. You're not writing code — you're writing"
echo "operational artifacts: runbooks, postmortem templates, governance"
echo "checklists, and decision trees."
echo ""
echo "These are portfolio pieces. They demonstrate the operational maturity"
echo "that most ML teams are missing."
echo ""

# Create output directory for your customized artifacts
if [ ! -d "my-artifacts" ]; then
    mkdir -p my-artifacts
    echo "✓ Created 'my-artifacts/' directory for your customized versions"
else
    echo "✓ 'my-artifacts/' directory already exists"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Week 10 Files:"
echo ""
echo "    📖 README.md                    — Concepts guide"
echo "    📋 ml-incident-runbook.md       — Complete incident response runbook"
echo "    📝 ml-postmortem-template.md    — Blameless postmortem template (ML-extended)"
echo "    ✅ model-governance-checklist.md — Deployment governance checklist"
echo "    🌳 retraining-decision-tree.md  — When to retrain vs rollback vs wait"
echo ""
echo "  Your tasks:"
echo ""
echo "    1. Read each document thoroughly"
echo "    2. Customize for your context (copy to my-artifacts/ and edit)"
echo "    3. Write a mock postmortem for the fraud model scenario"
echo "    4. Walk through the decision tree with practice scenarios"
echo "    5. Draft a 1-page governance proposal for CloudFactory"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  💡 KEY MESSAGE:"
echo ""
echo "  This is where your banking/regulatory background becomes a"
echo "  DIFFERENTIATOR, not a gap. You already know incident governance,"
echo "  compliance, and audit. Now you're extending those frameworks to"
echo "  cover ML-specific failure modes."
echo ""
echo "  These artifacts are portfolio pieces you could pitch to use"
echo "  at CloudFactory."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Optional: Install a markdown viewer for better reading experience"
echo ""
echo "    brew install glow        # Terminal markdown renderer"
echo "    glow README.md           # Read with formatting"
echo ""
echo "  Or just use VS Code's built-in markdown preview (Cmd+Shift+V)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
