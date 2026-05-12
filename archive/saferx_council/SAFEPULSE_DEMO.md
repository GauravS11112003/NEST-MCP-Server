# SafePulse Demo Payload

Use this payload in a SafeRx Council prompt to demo wearable-aware medication
safety review. It is intentionally synthetic and designed for a hackathon demo;
do not treat it as real patient data.

## Demo Prompt

```text
Run a SafeRx Council review for the current patient. Include SafePulse wearable
analysis and connect any smartwatch trend signals to possible medication safety
risks. Do not diagnose; treat wearable data as a signal for clinician review.

Wearable payload:
{
  "device": "smartwatch_demo",
  "window_days": 6,
  "resting_hr": [68, 70, 72, 82, 85, 87],
  "steps": [6200, 5900, 5400, 3100, 2400, 1900],
  "sleep_hours": [7.1, 6.8, 6.5, 4.2, 3.9, 4.0],
  "spo2_min": [96, 96, 95, 91, 90, 89],
  "hrv_ms": [42, 40, 38, 31, 29, 28],
  "falls": 1,
  "dizziness": true,
  "med_changes": [
    "Started diphenhydramine 25 mg nightly 5 days ago for sleep"
  ]
}
```

## Expected Story

SafePulse should flag worsening sleep, declining activity, rising resting heart
rate, low nighttime SpO2, HRV drop, dizziness, and a fall event. The Wearable
Sentinel should correlate those signals with sedating or anticholinergic
medications when present in the FHIR medication list, while the rest of the
SafeRx Council still checks Beers Criteria, drug interactions, and renal dosing.

## Judge-Friendly Framing

Before SafePulse, the smartwatch shows noisy consumer data. After SafePulse, the
SafeRx Council turns that data into a medication safety question: could a recent
medication change be worsening sedation, falls, sleep disruption, oxygenation,
or dehydration risk?
