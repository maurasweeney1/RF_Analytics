# RF Analytics— College Admissions Analysis

## Features

- **Pool Overview** — GPA, SAT, ACT, and AP distributions across all students
- **Outcome Stats** — Summary stats broken down by admitted / waitlisted / denied
- **Acceptance Rates** — Admit rates by GPA bracket, SAT range, and class rank percentile
- **Student Lookup** — Individual student profile with per-school comparison vs admitted medians
- **Reach / Match / Safety** — Classifies each school on a student's list
- **School Deep Dive** — Full applicant breakdown for a specific school, including regional patterns
- **Schedule Rigor** — Admit rates by AP/IB courseload, activities count, and activity type
- **Test Mode** — Enter a hypothetical student's stats to see pool comparisons and school predictions

## Setup

```bash
pip install pandas numpy plotext rich
```

## Data Files

| File                  | Description                                                             |
| --------------------- | ----------------------------------------------------------------------- |
| `student_stats.csv`   | One row per student — GPA, SAT, ACT, AP courses, class rank, activities |
| `admission_stats.csv` | One row per application — student ID, school, outcome, award            |

### student_stats.csv columns

`student_id, name, gpa, weighted, sat, act, ap_ib_college_taken, ap_Avg_score, class_rank, class_size, grad_year, activities_count, activity_types`

### admission_stats.csv columns

`student_id, school_name, school_tier, outcome, award, grad_year, committed`

Accepted outcome values: `Accepted`, `Rejected`, `Waitlist`, `Deferred`

## Usage

```bash
# Full report for the pool
python admissions_analysis.py

# Deep dive on a specific school
python admissions_analysis.py "TCU"

# Enter a hypothetical student and get predictions
python admissions_analysis.py test
```
