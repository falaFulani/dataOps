#!/usr/bin/env python3
"""
ML Error Budget Calculator
==========================

Calculates remaining error budget for an ML model SLO and shows how drift
events and quality degradations consume that budget.

This is the same error budget math you already know, applied to ML signals:
- Instead of "minutes of downtime", think "hours of degraded accuracy"
- Instead of "deploy risk", think "drift event risk"
- Same policy: budget exhausted → stop shipping features, focus on reliability

Usage:
    python error-budget-calculator.py
    python error-budget-calculator.py --slo-target 0.95 --window-days 7
    python error-budget-calculator.py --slo-target 0.90 --window-days 30 --current-value 0.87 --breach-hours 18
"""

import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# =============================================================================
# ANSI Colors for terminal output
# =============================================================================
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def colored(text: str, color: str) -> str:
    return f"{color}{text}{Colors.END}"


# =============================================================================
# Error Budget Calculation
# =============================================================================
def calculate_error_budget(
    slo_target: float,
    window_days: int,
    current_value: Optional[float] = None,
    breach_hours: float = 0.0,
) -> Dict:
    """
    Calculate ML error budget status.

    Args:
        slo_target: The SLO objective (e.g., 0.90 for 90% accuracy)
        window_days: The SLO measurement window in days
        current_value: Current metric value (e.g., current accuracy)
        breach_hours: Hours spent below the SLO target in this window

    Returns:
        Dictionary with budget calculations
    """
    total_hours = window_days * 24

    # Error budget = allowed hours below target
    # If SLO says "90% of the time above target", then 10% is your budget
    # For simplicity: budget_fraction = 1 - slo_target (when target is a ratio)
    # For accuracy SLOs: budget is the % of time you can be below accuracy target
    budget_fraction = 1 - slo_target
    total_budget_hours = total_hours * budget_fraction

    # Budget consumed
    budget_consumed_hours = breach_hours
    budget_remaining_hours = max(0, total_budget_hours - budget_consumed_hours)
    budget_consumed_pct = (
        (budget_consumed_hours / total_budget_hours * 100) if total_budget_hours > 0 else 0
    )
    budget_remaining_pct = 100 - budget_consumed_pct

    # Burn rate: how fast are we consuming budget?
    # If we've been in the window for some time, calculate current burn rate
    # burn_rate = 1.0 means "on pace to exactly exhaust budget"
    if breach_hours > 0 and total_budget_hours > 0:
        # Assume breaches are recent — calculate as if they happened continuously
        burn_rate = budget_consumed_hours / total_budget_hours * (total_hours / max(breach_hours, 1))
    else:
        burn_rate = 0.0

    # Time to exhaustion at current burn rate
    if burn_rate > 0:
        hours_to_exhaustion = budget_remaining_hours / (burn_rate * budget_fraction)
    else:
        hours_to_exhaustion = float("inf")

    # Policy recommendation
    if budget_remaining_pct > 50:
        policy = "GREEN: Ship features, experiment with model changes"
        policy_color = Colors.GREEN
    elif budget_remaining_pct > 25:
        policy = "YELLOW: Investigate drift, prioritize reliability improvements"
        policy_color = Colors.YELLOW
    elif budget_remaining_pct > 0:
        policy = "RED: Stop experiments. Focus on model reliability: retrain, rollback, or fix data"
        policy_color = Colors.RED
    else:
        policy = "EXHAUSTED: Incident. Rollback to last-known-good model. Postmortem required."
        policy_color = Colors.RED

    return {
        "slo_target": slo_target,
        "window_days": window_days,
        "total_hours": total_hours,
        "total_budget_hours": total_budget_hours,
        "budget_consumed_hours": budget_consumed_hours,
        "budget_remaining_hours": budget_remaining_hours,
        "budget_consumed_pct": budget_consumed_pct,
        "budget_remaining_pct": budget_remaining_pct,
        "burn_rate": burn_rate,
        "hours_to_exhaustion": hours_to_exhaustion,
        "current_value": current_value,
        "policy": policy,
        "policy_color": policy_color,
    }


def simulate_drift_event(
    budget: Dict,
    drift_duration_hours: float,
    drift_description: str = "drift event",
) -> Dict:
    """
    Simulate the impact of a drift event on the error budget.

    A drift event is a period where the model operates below SLO target.
    This shows how much budget a single event consumes.
    """
    new_consumed = budget["budget_consumed_hours"] + drift_duration_hours
    new_remaining = max(0, budget["total_budget_hours"] - new_consumed)
    new_consumed_pct = (
        (new_consumed / budget["total_budget_hours"] * 100)
        if budget["total_budget_hours"] > 0
        else 0
    )

    return {
        "event_description": drift_description,
        "event_duration_hours": drift_duration_hours,
        "budget_consumed_by_event_pct": (
            drift_duration_hours / budget["total_budget_hours"] * 100
            if budget["total_budget_hours"] > 0
            else 0
        ),
        "new_total_consumed_hours": new_consumed,
        "new_total_consumed_pct": new_consumed_pct,
        "new_remaining_hours": new_remaining,
        "new_remaining_pct": 100 - new_consumed_pct,
    }


# =============================================================================
# Display Functions
# =============================================================================
def print_header():
    print()
    print(colored("=" * 70, Colors.BOLD))
    print(colored("  ML Error Budget Calculator", Colors.BOLD))
    print(colored("  'Same math, new signals'", Colors.BLUE))
    print(colored("=" * 70, Colors.BOLD))
    print()


def print_budget_report(budget: dict):
    print(colored("─" * 70, Colors.BLUE))
    print(colored("  SLO CONFIGURATION", Colors.BOLD))
    print(colored("─" * 70, Colors.BLUE))
    print(f"  SLO Target:        {budget['slo_target']:.1%}")
    print(f"  Window:            {budget['window_days']} days ({budget['total_hours']} hours)")
    print(f"  Total Budget:      {budget['total_budget_hours']:.1f} hours of allowed degradation")
    if budget["current_value"] is not None:
        status = "✓ MEETING SLO" if budget["current_value"] >= budget["slo_target"] else "✗ BELOW SLO"
        color = Colors.GREEN if budget["current_value"] >= budget["slo_target"] else Colors.RED
        print(f"  Current Value:     {budget['current_value']:.3f} ({colored(status, color)})")
    print()

    print(colored("─" * 70, Colors.BLUE))
    print(colored("  BUDGET STATUS", Colors.BOLD))
    print(colored("─" * 70, Colors.BLUE))

    # Budget bar visualization
    bar_width = 40
    consumed_blocks = int(budget["budget_consumed_pct"] / 100 * bar_width)
    remaining_blocks = bar_width - consumed_blocks
    bar = colored("█" * consumed_blocks, Colors.RED) + colored("█" * remaining_blocks, Colors.GREEN)
    print(f"  [{bar}]")
    print(f"  Consumed: {budget['budget_consumed_hours']:.1f}h ({budget['budget_consumed_pct']:.1f}%) | "
          f"Remaining: {budget['budget_remaining_hours']:.1f}h ({budget['budget_remaining_pct']:.1f}%)")
    print()

    if budget["burn_rate"] > 0:
        print(f"  Current Burn Rate: {budget['burn_rate']:.1f}x")
        if budget["hours_to_exhaustion"] < float("inf"):
            print(f"  Time to Exhaustion: {budget['hours_to_exhaustion']:.1f} hours "
                  f"({budget['hours_to_exhaustion']/24:.1f} days) at current rate")
        print()

    print(colored("─" * 70, Colors.BLUE))
    print(colored("  ERROR BUDGET POLICY", Colors.BOLD))
    print(colored("─" * 70, Colors.BLUE))
    print(f"  {colored(budget['policy'], budget['policy_color'])}")
    print()


def print_drift_impact(events: List[Dict]):
    print(colored("─" * 70, Colors.BLUE))
    print(colored("  DRIFT EVENT IMPACT ANALYSIS", Colors.BOLD))
    print(colored("─" * 70, Colors.BLUE))
    print()
    print("  How much budget does each type of event consume?")
    print()
    print(f"  {'Event':<35} {'Duration':<12} {'Budget Cost':<15} {'Remaining'}")
    print(f"  {'─'*35} {'─'*12} {'─'*15} {'─'*12}")

    for event in events:
        remaining_color = (
            Colors.GREEN if event["new_remaining_pct"] > 50
            else Colors.YELLOW if event["new_remaining_pct"] > 25
            else Colors.RED
        )
        remaining_str = f"{event['new_remaining_pct']:.1f}%"
        print(
            f"  {event['event_description']:<35} "
            f"{event['event_duration_hours']:<12.1f} "
            f"{event['budget_consumed_by_event_pct']:<15.1f}% "
            f"{colored(remaining_str, remaining_color)}"
        )
    print()


def print_comparison_table():
    """Print a comparison of traditional vs ML error budget concepts."""
    print(colored("─" * 70, Colors.BLUE))
    print(colored("  TRANSLATION TABLE: Traditional → ML Error Budgets", Colors.BOLD))
    print(colored("─" * 70, Colors.BLUE))
    print()
    comparisons = [
        ("Minutes of downtime", "Hours below accuracy target"),
        ("Deploy caused errors", "Model deploy caused accuracy drop"),
        ("Traffic spike overwhelmed service", "Data drift overwhelmed model"),
        ("Budget consumed by maintenance", "Budget consumed by retraining gap"),
        ("Freeze deploys", "Freeze experiments, focus on retrain"),
        ("Rollback deployment", "Rollback to previous model version"),
        ("SLA penalty to customer", "Incorrect predictions → business loss"),
    ]
    print(f"  {'Traditional (you know this)':<38} {'ML Equivalent (new signal, same math)'}")
    print(f"  {'─'*38} {'─'*38}")
    for trad, ml in comparisons:
        print(f"  {trad:<38} {ml}")
    print()


# =============================================================================
# Main
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="ML Error Budget Calculator — same math, new signals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --slo-target 0.95 --window-days 7
  %(prog)s --slo-target 0.90 --window-days 30 --current-value 0.87 --breach-hours 18
  %(prog)s --slo-target 0.999 --window-days 30 --breach-hours 2
        """,
    )
    parser.add_argument(
        "--slo-target",
        type=float,
        default=0.90,
        help="SLO target as a decimal (default: 0.90 for 90%% accuracy)",
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=30,
        help="SLO measurement window in days (default: 30)",
    )
    parser.add_argument(
        "--current-value",
        type=float,
        default=None,
        help="Current metric value (e.g., current accuracy). Optional.",
    )
    parser.add_argument(
        "--breach-hours",
        type=float,
        default=0.0,
        help="Hours spent below SLO target in this window (default: 0)",
    )
    args = parser.parse_args()

    print_header()

    # Calculate base budget
    budget = calculate_error_budget(
        slo_target=args.slo_target,
        window_days=args.window_days,
        current_value=args.current_value,
        breach_hours=args.breach_hours,
    )

    print_budget_report(budget)

    # Simulate common drift events and their budget impact
    events = [
        simulate_drift_event(budget, 4.0, "Minor drift (4h below target)"),
        simulate_drift_event(budget, 12.0, "Moderate drift (12h below target)"),
        simulate_drift_event(budget, 24.0, "Significant drift (24h, 1 day)"),
        simulate_drift_event(budget, 48.0, "Major incident (48h, 2 days)"),
        simulate_drift_event(budget, 72.0, "Severe (72h, full budget at 90%)"),
    ]

    print_drift_impact(events)
    print_comparison_table()

    # Summary recommendation
    print(colored("─" * 70, Colors.BLUE))
    print(colored("  RECOMMENDATION", Colors.BOLD))
    print(colored("─" * 70, Colors.BLUE))
    print()

    if budget["budget_remaining_pct"] > 75:
        print("  Your error budget is healthy. You can afford to:")
        print("  • Experiment with new model architectures")
        print("  • Run A/B tests on model variants")
        print("  • Ship new features that depend on model predictions")
        print("  • Accept minor drift without immediate retraining")
    elif budget["budget_remaining_pct"] > 50:
        print("  Your error budget is adequate but worth monitoring. Consider:")
        print("  • Reviewing drift trends — is budget consumption accelerating?")
        print("  • Scheduling proactive retraining before budget gets tight")
        print("  • Reducing risky model experiments until budget recovers")
    elif budget["budget_remaining_pct"] > 25:
        print("  ⚠️  Your error budget is getting tight. Actions:")
        print("  • Investigate what's consuming budget (drift? staleness? data issues?)")
        print("  • Prioritize retraining pipeline reliability")
        print("  • Pause non-critical model experiments")
        print("  • Set up burn-rate alerts if not already active")
    elif budget["budget_remaining_pct"] > 0:
        print("  🚨 Your error budget is nearly exhausted. Immediate actions:")
        print("  • STOP all model experiments and feature work")
        print("  • Focus exclusively on model reliability")
        print("  • Trigger retraining if not already in progress")
        print("  • Prepare rollback to last-known-good model version")
        print("  • Alert team lead and stakeholders")
    else:
        print("  🔥 ERROR BUDGET EXHAUSTED — This is an incident.")
        print("  • Rollback to last-known-good model immediately")
        print("  • Declare incident, assign incident commander")
        print("  • All work stops until model is back within SLO")
        print("  • Postmortem required")
        print("  • Notify business stakeholders of impact window")

    print()
    print(colored("─" * 70, Colors.BLUE))
    print()


if __name__ == "__main__":
    main()
