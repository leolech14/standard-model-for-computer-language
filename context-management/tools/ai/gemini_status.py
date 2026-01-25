#!/usr/bin/env python3
"""
Gemini API Status & Diagnostics Tool

Real-time observability for Gemini API usage, quotas, and error diagnosis.

Usage:
    python gemini_status.py              # Show current status
    python gemini_status.py --diagnose   # Diagnose last error
    python gemini_status.py --watch      # Continuous monitoring
    python gemini_status.py --recommend  # Recommend optimal model
"""

import json
import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
SESSIONS_DIR = PROJECT_ROOT / "standard-model-of-code/docs/research/gemini/sessions"

# Quota limits (Free Tier - AI Studio)
QUOTAS = {
    "gemini-3-pro-preview": {
        "requests_per_min": 25,
        "requests_per_day": 250,
        "input_tokens_per_min": 1_000_000,
        "output_tokens_per_min": 100_000,
    },
    "gemini-3-pro": {
        "requests_per_min": 25,
        "requests_per_day": 250,
        "input_tokens_per_min": 1_000_000,
        "output_tokens_per_min": 100_000,
    },
    "gemini-2.5-flash": {
        "requests_per_min": 2000,
        "requests_per_day": 2_520_000,
        "input_tokens_per_min": 4_000_000,
        "output_tokens_per_min": 400_000,
    },
    "gemini-2.5-pro": {
        "requests_per_min": 360,
        "requests_per_day": 30_000,
        "input_tokens_per_min": 2_000_000,
        "output_tokens_per_min": 200_000,
    },
    "gemini-2.0-flash-001": {
        "requests_per_min": 1000,
        "requests_per_day": 2_520_000,
        "input_tokens_per_min": 4_000_000,
        "output_tokens_per_min": 400_000,
    },
}

# Error patterns and diagnoses
ERROR_PATTERNS = {
    "RESOURCE_EXHAUSTED": {
        "pattern": "RESOURCE_EXHAUSTED",
        "diagnosis": "Rate limit exceeded",
        "solutions": [
            "Wait for the retry delay specified in the error",
            "Use --model gemini-2.5-flash (higher limits)",
            "Reduce context size with smaller --set",
            "Space out requests (avoid rapid-fire queries)",
        ]
    },
    "quota_exceeded": {
        "pattern": "quota exceeded",
        "diagnosis": "Specific quota limit hit",
        "solutions": [
            "Check which quota: requests/min, tokens/min, or requests/day",
            "For token limits: use smaller context sets",
            "For request limits: wait or use different model",
        ]
    },
    "input_token_count": {
        "pattern": "input_token_count",
        "diagnosis": "Input token quota exceeded",
        "solutions": [
            "Your context is too large for current rate window",
            "Wait ~30-60 seconds for token quota to reset",
            "Use gemini-2.5-flash (4M tokens/min vs 1M)",
            "Use smaller --set (e.g., 'quick' instead of 'brain')",
        ]
    },
    "retry_delay": {
        "pattern": "retryDelay",
        "diagnosis": "Temporary rate limit - specific wait time given",
        "solutions": [
            "Wait the specified number of seconds",
            "The error message contains exact retry time",
        ]
    },
}


def get_doppler_key():
    """Get API key from Doppler."""
    try:
        result = subprocess.run(
            ['doppler', 'secrets', 'get', 'GEMINI_API_KEY', '--plain'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def load_sessions(date_filter=None):
    """Load session files, optionally filtered by date."""
    sessions = []
    if not SESSIONS_DIR.exists():
        return sessions

    date_str = date_filter or datetime.now().strftime("%Y%m%d")

    for f in SESSIONS_DIR.glob("*.json"):
        if date_str in f.name:
            try:
                data = json.loads(f.read_text())
                data['_filename'] = f.name
                data['_filepath'] = str(f)
                sessions.append(data)
            except Exception:
                pass

    return sorted(sessions, key=lambda x: x.get('session_start', ''))


def analyze_usage(sessions):
    """Analyze usage from session data."""
    stats = {
        'total_calls': 0,
        'successful': 0,
        'failed': 0,
        'total_input_tokens': 0,
        'total_output_tokens': 0,
        'by_model': defaultdict(lambda: {
            'calls': 0, 'success': 0, 'failed': 0,
            'input_tokens': 0, 'output_tokens': 0
        }),
        'last_hour_calls': defaultdict(int),
        'last_minute_calls': defaultdict(int),
    }

    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    one_minute_ago = now - timedelta(minutes=1)

    for session in sessions:
        model = session.get('model', 'unknown')
        stats['total_calls'] += 1
        stats['by_model'][model]['calls'] += 1

        # Token counts (try both formats)
        inp = session.get('total_tokens_in', 0) or 0
        out = session.get('total_tokens_out', 0) or 0

        if inp > 0 or out > 0:
            stats['successful'] += 1
            stats['by_model'][model]['success'] += 1
        else:
            stats['failed'] += 1
            stats['by_model'][model]['failed'] += 1

        stats['total_input_tokens'] += inp
        stats['total_output_tokens'] += out
        stats['by_model'][model]['input_tokens'] += inp
        stats['by_model'][model]['output_tokens'] += out

        # Time-based analysis
        try:
            session_time = datetime.strptime(
                session.get('session_start', ''),
                "%Y-%m-%d %H:%M:%S"
            )
            if session_time > one_hour_ago:
                stats['last_hour_calls'][model] += 1
            if session_time > one_minute_ago:
                stats['last_minute_calls'][model] += 1
        except Exception:
            pass

    return stats


def diagnose_error(error_text):
    """Diagnose an error message and provide solutions."""
    diagnoses = []

    for name, pattern_info in ERROR_PATTERNS.items():
        if pattern_info['pattern'].lower() in error_text.lower():
            diagnoses.append({
                'type': name,
                'diagnosis': pattern_info['diagnosis'],
                'solutions': pattern_info['solutions']
            })

    # Extract specific details from error
    details = {}

    # Extract retry delay
    if 'retry' in error_text.lower():
        import re
        match = re.search(r'retry.*?(\d+\.?\d*)\s*s', error_text, re.IGNORECASE)
        if match:
            details['retry_seconds'] = float(match.group(1))

    # Extract quota metric
    if 'quotaMetric' in error_text:
        import re
        match = re.search(r'quotaMetric["\s:]+([^"]+)', error_text)
        if match:
            details['quota_metric'] = match.group(1)

    # Extract quota limit
    if 'limit:' in error_text:
        import re
        match = re.search(r'limit:\s*(\d+)', error_text)
        if match:
            details['quota_limit'] = int(match.group(1))

    return diagnoses, details


def recommend_model(stats):
    """Recommend optimal model based on current usage."""
    recommendations = []

    # Check gemini-3-pro usage
    pro_stats = stats['by_model'].get('gemini-3-pro-preview', {})
    pro_calls = pro_stats.get('calls', 0)
    pro_daily_limit = QUOTAS.get('gemini-3-pro-preview', {}).get('requests_per_day', 250)

    if pro_calls > pro_daily_limit * 0.8:
        recommendations.append({
            'urgency': 'HIGH',
            'message': f"gemini-3-pro at {pro_calls}/{pro_daily_limit} daily quota (>80%)",
            'action': "Switch to gemini-2.5-flash for remaining work"
        })

    # Check recent rate
    last_min_pro = stats['last_minute_calls'].get('gemini-3-pro-preview', 0)
    if last_min_pro > 20:
        recommendations.append({
            'urgency': 'HIGH',
            'message': f"{last_min_pro} requests in last minute (limit: 25/min)",
            'action': "Slow down or switch to flash model"
        })

    # General recommendation
    if not recommendations:
        recommendations.append({
            'urgency': 'LOW',
            'message': "Usage within normal limits",
            'action': "Continue with current model"
        })

    return recommendations


def print_status(stats, verbose=False):
    """Print formatted status report."""
    today = datetime.now().strftime("%Y-%m-%d")

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║               GEMINI API STATUS - {today}                ║
╠══════════════════════════════════════════════════════════════╣
║  Total Calls:         {stats['total_calls']:>8}                              ║
║  Successful:          {stats['successful']:>8}                              ║
║  Failed (429/errors): {stats['failed']:>8}                              ║
║  Input Tokens:        {stats['total_input_tokens']:>12,}                      ║
║  Output Tokens:       {stats['total_output_tokens']:>12,}                      ║
╠══════════════════════════════════════════════════════════════╣
║  MODEL BREAKDOWN:                                            ║""")

    for model, model_stats in sorted(stats['by_model'].items(), key=lambda x: -x[1]['calls']):
        quota = QUOTAS.get(model, {})
        daily_limit = quota.get('requests_per_day', '?')
        calls = model_stats['calls']
        success = model_stats['success']

        # Calculate percentage if we know the limit
        pct = ""
        if isinstance(daily_limit, int):
            pct = f" ({calls*100//daily_limit}%)"

        print(f"║    {model[:28]:<28} {success:>3}/{calls:<3} {pct:>6}    ║")

    print(f"""╠══════════════════════════════════════════════════════════════╣
║  RATE STATUS (Last Minute):                                  ║""")

    for model, count in stats['last_minute_calls'].items():
        limit = QUOTAS.get(model, {}).get('requests_per_min', '?')
        status = "⚠️ HIGH" if isinstance(limit, int) and count > limit * 0.8 else "✓ OK"
        print(f"║    {model[:24]:<24} {count:>3}/{limit:<5} {status:<8}    ║")

    if not stats['last_minute_calls']:
        print(f"║    No requests in last minute                                ║")

    print(f"╚══════════════════════════════════════════════════════════════╝")


def print_diagnosis(diagnoses, details):
    """Print error diagnosis."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    ERROR DIAGNOSIS                           ║
╠══════════════════════════════════════════════════════════════╣""")

    if details.get('retry_seconds'):
        print(f"║  ⏱️  Retry in: {details['retry_seconds']:.1f} seconds                              ║")

    if details.get('quota_metric'):
        metric = details['quota_metric'].split('/')[-1][:40]
        print(f"║  📊 Quota: {metric:<45} ║")

    if details.get('quota_limit'):
        print(f"║  🎯 Limit: {details['quota_limit']:,}                                          ║")

    for d in diagnoses:
        print(f"╠══════════════════════════════════════════════════════════════╣")
        print(f"║  🔍 {d['diagnosis']:<54} ║")
        print(f"║  Solutions:                                                  ║")
        for sol in d['solutions'][:3]:
            print(f"║    • {sol[:52]:<52} ║")

    print(f"╚══════════════════════════════════════════════════════════════╝")


def print_recommendations(recommendations):
    """Print model recommendations."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    RECOMMENDATIONS                           ║
╠══════════════════════════════════════════════════════════════╣""")

    for rec in recommendations:
        icon = "🔴" if rec['urgency'] == 'HIGH' else "🟡" if rec['urgency'] == 'MEDIUM' else "🟢"
        print(f"║  {icon} {rec['message'][:54]:<54} ║")
        print(f"║     → {rec['action'][:52]:<52} ║")

    print(f"╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Gemini API Status & Diagnostics")
    parser.add_argument('--diagnose', '-d', action='store_true',
                        help="Diagnose last error")
    parser.add_argument('--error', '-e', type=str,
                        help="Diagnose specific error text")
    parser.add_argument('--watch', '-w', action='store_true',
                        help="Continuous monitoring (refresh every 10s)")
    parser.add_argument('--recommend', '-r', action='store_true',
                        help="Show model recommendations")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Show detailed output")
    parser.add_argument('--date', type=str,
                        help="Check specific date (YYYYMMDD)")

    args = parser.parse_args()

    # Check API key
    if not get_doppler_key():
        print("⚠️  Warning: GEMINI_API_KEY not found in Doppler")

    if args.error:
        # Diagnose provided error
        diagnoses, details = diagnose_error(args.error)
        print_diagnosis(diagnoses, details)
        return

    if args.watch:
        # Continuous monitoring
        try:
            while True:
                print("\033[2J\033[H")  # Clear screen
                sessions = load_sessions(args.date)
                stats = analyze_usage(sessions)
                print_status(stats, args.verbose)

                recommendations = recommend_model(stats)
                if any(r['urgency'] == 'HIGH' for r in recommendations):
                    print_recommendations(recommendations)

                print(f"\n  [Refreshing in 10s... Ctrl+C to exit]")
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n  Stopped.")
            return

    # Load and analyze sessions
    sessions = load_sessions(args.date)
    stats = analyze_usage(sessions)

    # Print status
    print_status(stats, args.verbose)

    # Diagnose last error if requested
    if args.diagnose:
        # Find last failed session
        failed_sessions = [s for s in sessions
                          if s.get('total_tokens_in', 0) == 0
                          and s.get('total_tokens_out', 0) == 0]
        if failed_sessions:
            last_failed = failed_sessions[-1]
            print(f"\n  Last failed session: {last_failed.get('_filename', 'unknown')}")
            # Try to read error from file or show generic diagnosis
            diagnoses, details = diagnose_error("RESOURCE_EXHAUSTED quota exceeded")
            print_diagnosis(diagnoses, details)
        else:
            print("\n  ✓ No failed sessions found today")

    # Show recommendations
    if args.recommend or True:  # Always show
        recommendations = recommend_model(stats)
        print_recommendations(recommendations)


if __name__ == "__main__":
    main()
