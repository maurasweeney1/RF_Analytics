"""
College Admissions Analytics — Terminal Output
================================================
Replace STUDENTS and OUTCOMES at the bottom with your real data,
or load from CSV by calling load_from_csv() instead.
"""

import pandas as pd
import numpy as np
import plotext as plt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule

console = Console()

# ── LOAD FROM CSV  ─────────────────────────────────────────────────
def load_from_csv(students_csv, outcomes_csv):
    """
    Call this instead of using the hardcoded data above.
    students_csv  columns: id, name, gpa, sat, act, ap_taken, ap_avg, class_rank, class_size
    outcomes_csv  columns: sid, school, tier, outcome
    """
    students_df = pd.read_csv(students_csv, skipinitialspace=True)
    outcomes_df = pd.read_csv(outcomes_csv, skipinitialspace=True)
    return students_df.to_dict("records"), outcomes_df.to_dict("records")


# ── SETUP DATAFRAMES ─────────────────────────────────────────────────────────
def build_dfs(students, outcomes):
    s = pd.DataFrame(students)
    s = s.rename(columns={"student_id": "id", "ap_ib_college_taken": "ap_taken", "ap_Avg_score": "ap_avg"})
    s["percentile"] = (s["class_rank"] / s["class_size"]) * 100
    for col in ("ap_ib_senior_year", "activities_count", "activity_types"):
        if col not in s.columns:
            s[col] = np.nan
    o = pd.DataFrame(outcomes)
    o = o.rename(columns={"student_id": "sid", "school_name": "school", "school_tier": "tier"})
    outcome_map = {"Accepted": "admitted", "Rejected": "denied", "Waitlist": "waitlisted", "Deferred": "waitlisted"}
    o["outcome"] = o["outcome"].map(lambda x: outcome_map.get(x, x.lower()))
    joined = o.merge(s, left_on="sid", right_on="id")
    return s, o, joined


# ── HELPERS ──────────────────────────────────────────────────────────────────
def section(title):
    console.print()
    console.rule(f"[bold yellow]{title}[/bold yellow]")
    console.print()

def bar_chart_plotext(labels, values, title, xlabel="", color="green", width=60):
    plt.clf()
    plt.bar(labels, values, color=color, width=0.5)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.plotsize(width, 15)
    plt.theme("dark")
    plt.show()

def outcome_color(outcome):
    return {"admitted": "green", "waitlisted": "yellow", "denied": "red"}.get(outcome, "white")


# ══════════════════════════════════════════════════════════════════════════════
# 1. POOL OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def pool_overview(s):
    section("1 · POOL OVERVIEW — All Students")

    # Summary stats table
    t = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
    t.add_column("Metric", style="dim")
    t.add_column("Mean",   justify="right")
    t.add_column("Median", justify="right")
    t.add_column("Min",    justify="right")
    t.add_column("Max",    justify="right")
    t.add_column("Std Dev",justify="right")

    for col, label in [("gpa","GPA"), ("sat","SAT"), ("act","ACT"), ("ap_taken","AP Exams"), ("ap_avg","AP Avg Score")]:
        t.add_row(
            label,
            f"{s[col].mean():.2f}",
            f"{s[col].median():.2f}",
            f"{s[col].min():.2f}",
            f"{s[col].max():.2f}",
            f"{s[col].std():.2f}",
        )
    console.print(t)

    # GPA histogram
    bins   = [3.3, 3.5, 3.6, 3.7, 3.8, 3.9, 4.01]
    labels = ["<3.5","3.5-3.6","3.6-3.7","3.7-3.8","3.8-3.9","3.9-4.0"]
    counts = pd.cut(s["gpa"], bins=bins, labels=labels, right=False).value_counts().reindex(labels).fillna(0).tolist()
    bar_chart_plotext(labels, counts, "GPA Distribution", "GPA Range", color="cyan")

    # SAT histogram
    sbins   = [1200, 1300, 1350, 1400, 1450, 1500, 1600]
    slabels = ["<1300","1300-1350","1350-1400","1400-1450","1450-1500","1500+"]
    scounts = pd.cut(s["sat"], bins=sbins, labels=slabels, right=False).value_counts().reindex(slabels).fillna(0).tolist()
    bar_chart_plotext(slabels, scounts, "SAT Distribution", "SAT Range", color="magenta+")

    # AP histogram
    abins   = [0, 2, 4, 6, 8, 10]
    alabels = ["1-2","3-4","5-6","7-8","9+"]
    acounts = pd.cut(s["ap_taken"], bins=abins, labels=alabels, right=True).value_counts().reindex(alabels).fillna(0).tolist()
    bar_chart_plotext(alabels, acounts, "AP Exams Taken", "# Exams", color="yellow")


# ══════════════════════════════════════════════════════════════════════════════
# 2. SUMMARY STATS BY OUTCOME TIER
# ══════════════════════════════════════════════════════════════════════════════
def outcome_stats(s, joined):
    section("2 · SUMMARY STATS BY OUTCOME TIER")

    t = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan")
    t.add_column("Outcome",    style="bold")
    t.add_column("Students",   justify="right")
    t.add_column("GPA avg",    justify="right")
    t.add_column("GPA med",    justify="right")
    t.add_column("GPA range",  justify="right")
    t.add_column("SAT avg",    justify="right")
    t.add_column("SAT med",    justify="right")
    t.add_column("SAT range",  justify="right")
    t.add_column("Rank %tile", justify="right")

    for outcome in ["admitted","waitlisted","denied"]:
        sids = joined[joined["outcome"]==outcome]["sid"].unique()
        pool = s[s["id"].isin(sids)]
        color = outcome_color(outcome)
        t.add_row(
            f"[{color}]{outcome}[/{color}]",
            str(len(sids)),
            f"{pool['gpa'].mean():.2f}",
            f"{pool['gpa'].median():.2f}",
            f"{pool['gpa'].min():.2f}–{pool['gpa'].max():.2f}",
            f"{pool['sat'].mean():.0f}",
            f"{pool['sat'].median():.0f}",
            f"{pool['sat'].min():.0f}–{pool['sat'].max():.0f}",
            f"{pool['percentile'].mean():.1f}%",
        )
    console.print(t)

    # Side-by-side GPA avg bar chart
    outcomes  = ["admitted","waitlisted","denied"]
    gpa_avgs  = [s[s["id"].isin(joined[joined["outcome"]==o]["sid"].unique())]["gpa"].mean() for o in outcomes]
    sat_avgs  = [s[s["id"].isin(joined[joined["outcome"]==o]["sid"].unique())]["sat"].mean() for o in outcomes]

    plt.clf()
    plt.multiple_bar(outcomes, [gpa_avgs, [x/100 for x in sat_avgs]], labels=["GPA", "SAT÷100"])
    plt.title("Avg GPA and SAT (÷100) by Outcome")
    plt.plotsize(60, 15)
    plt.theme("dark")
    plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# 3. ACCEPTANCE RATES BY BRACKET
# ══════════════════════════════════════════════════════════════════════════════
def acceptance_rates(joined):
    section("3 · ACCEPTANCE RATES BY BRACKET")

    def admit_rate(df): return len(df[df["outcome"]=="admitted"]) / len(df) if len(df) else 0

    # GPA brackets
    gpa_bins   = [0, 3.5, 3.6, 3.7, 3.8, 3.9, 4.01]
    gpa_labels = ["<3.5","3.5-3.6","3.6-3.7","3.7-3.8","3.8-3.9","3.9-4.0"]
    joined["gpa_bracket"] = pd.cut(joined["gpa"], bins=gpa_bins, labels=gpa_labels, right=False)
    gpa_rates = [admit_rate(joined[joined["gpa_bracket"]==l]) * 100 for l in gpa_labels]

    t = Table(title="Admit Rate by GPA Bracket", box=box.SIMPLE_HEAVY, header_style="bold cyan")
    t.add_column("GPA Bracket"); t.add_column("Apps", justify="right"); t.add_column("Admitted", justify="right"); t.add_column("Admit Rate", justify="right")
    for label, rate in zip(gpa_labels, gpa_rates):
        grp = joined[joined["gpa_bracket"]==label]
        n, adm = len(grp), len(grp[grp["outcome"]=="admitted"])
        color = "green" if rate >= 60 else "yellow" if rate >= 35 else "red"
        t.add_row(label, str(n), str(adm), f"[{color}]{rate:.0f}%[/{color}]")
    console.print(t)
    bar_chart_plotext(gpa_labels, gpa_rates, "Admit Rate by GPA Bracket (%)", "GPA", color="green")

    # SAT brackets
    sat_bins   = [0, 1300, 1350, 1400, 1450, 1500, 1600]
    sat_labels = ["<1300","1300-1350","1350-1400","1400-1450","1450-1500","1500+"]
    joined["sat_bracket"] = pd.cut(joined["sat"], bins=sat_bins, labels=sat_labels, right=False)
    sat_rates = [admit_rate(joined[joined["sat_bracket"]==l]) * 100 for l in sat_labels]

    t2 = Table(title="Admit Rate by SAT Range", box=box.SIMPLE_HEAVY, header_style="bold cyan")
    t2.add_column("SAT Range"); t2.add_column("Apps", justify="right"); t2.add_column("Admitted", justify="right"); t2.add_column("Admit Rate", justify="right")
    for label, rate in zip(sat_labels, sat_rates):
        grp = joined[joined["sat_bracket"]==label]
        n, adm = len(grp), len(grp[grp["outcome"]=="admitted"])
        color = "green" if rate >= 60 else "yellow" if rate >= 35 else "red"
        t2.add_row(label, str(n), str(adm), f"[{color}]{rate:.0f}%[/{color}]")
    console.print(t2)
    bar_chart_plotext(sat_labels, sat_rates, "Admit Rate by SAT Range (%)", "SAT", color="magenta+")

    # Rank percentile bands
    rank_bins   = [0, 5, 10, 25, 50, 100]
    rank_labels = ["Top 5%","5-10%","10-25%","25-50%","50%+"]
    joined["rank_band"] = pd.cut(joined["percentile"], bins=rank_bins, labels=rank_labels, right=True)
    rank_rates = [admit_rate(joined[joined["rank_band"]==l]) * 100 for l in rank_labels]

    t3 = Table(title="Admit Rate by Class Rank Percentile", box=box.SIMPLE_HEAVY, header_style="bold cyan")
    t3.add_column("Rank Band"); t3.add_column("Apps", justify="right"); t3.add_column("Admitted", justify="right"); t3.add_column("Admit Rate", justify="right")
    for label, rate in zip(rank_labels, rank_rates):
        grp = joined[joined["rank_band"]==label]
        n, adm = len(grp), len(grp[grp["outcome"]=="admitted"])
        color = "green" if rate >= 60 else "yellow" if rate >= 35 else "red"
        t3.add_row(label, str(n), str(adm), f"[{color}]{rate:.0f}%[/{color}]")
    console.print(t3)
    bar_chart_plotext(rank_labels, rank_rates, "Admit Rate by Class Rank (%)", "Rank Band", color="yellow")



# ══════════════════════════════════════════════════════════════════════════════
# 5. STUDENT LOOKUP
# ══════════════════════════════════════════════════════════════════════════════
def student_lookup(s, joined, student_id="S004"):
    section(f"5 · STUDENT LOOKUP — {student_id}")

    student = s[s["id"]==student_id].iloc[0]
    console.print(Panel(
        f"[bold]{student['name']}[/bold]   GPA [cyan]{student['gpa']:.2f}[/cyan]  "
        f"SAT [cyan]{student['sat']}[/cyan]  ACT [cyan]{student['act']}[/cyan]  "
        f"AP Exams [cyan]{student['ap_taken']}[/cyan]  AP Avg [cyan]{student['ap_avg']:.1f}[/cyan]  "
        f"Rank [cyan]{student['class_rank']}/{student['class_size']}[/cyan] "
        f"([cyan]{student['percentile']:.1f}%ile[/cyan])",
        title="Student Profile", border_style="cyan"
    ))

    apps = joined[joined["sid"]==student_id]

    t = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan")
    for col in ["School","Outcome","Their SAT","Adm Median SAT","SAT %tile","Their GPA","Adm Median GPA","GPA %tile"]:
        t.add_column(col, justify="right" if col not in ["School","Outcome"] else "left")

    for _, app in apps.iterrows():
        adm_pool = joined[(joined["school"]==app["school"]) & (joined["outcome"]=="admitted")]
        sat_med = adm_pool["sat"].median() if len(adm_pool) else float("nan")
        gpa_med = adm_pool["gpa"].median() if len(adm_pool) else float("nan")
        sat_pct = (adm_pool["sat"] <= student["sat"]).mean() * 100 if len(adm_pool) else float("nan")
        gpa_pct = (adm_pool["gpa"] <= student["gpa"]).mean() * 100 if len(adm_pool) else float("nan")
        oc = outcome_color(app["outcome"])
        sc = "green" if sat_pct >= 50 else "red"
        gc = "green" if gpa_pct >= 50 else "red"
        t.add_row(
            app["school"],
            f"[{oc}]{app['outcome']}[/{oc}]",
            str(student["sat"]), f"{sat_med:.0f}" if not np.isnan(sat_med) else "—",
            f"[{sc}]{sat_pct:.0f}%[/{sc}]" if not np.isnan(sat_pct) else "—",
            f"{student['gpa']:.2f}", f"{gpa_med:.2f}" if not np.isnan(gpa_med) else "—",
            f"[{gc}]{gpa_pct:.0f}%[/{gc}]" if not np.isnan(gpa_pct) else "—",
        )
    console.print(t)


# ══════════════════════════════════════════════════════════════════════════════
# 6. REACH / MATCH / SAFETY
# ══════════════════════════════════════════════════════════════════════════════
def reach_match_safety(s, joined, student_id="S004"):
    section(f"6 · REACH / MATCH / SAFETY — {student_id}")

    student = s[s["id"]==student_id].iloc[0]
    schools = joined[joined["sid"]==student_id]["school"].unique()
    rows = []

    for school in schools:
        adm = joined[(joined["school"]==school) & (joined["outcome"]=="admitted")]
        if len(adm) < 2: continue
        sat_med = adm["sat"].median()
        gpa_med = adm["gpa"].median()
        sat_ok  = student["sat"] >= sat_med
        gpa_ok  = student["gpa"] >= gpa_med
        sat_close = adm["sat"].min() <= student["sat"] < sat_med
        gpa_close = adm["gpa"].min() <= student["gpa"] < gpa_med
        if sat_ok and gpa_ok:                           cat = "Safety"
        elif sat_ok or gpa_ok or (sat_close and gpa_close): cat = "Match"
        else:                                           cat = "Reach"
        outcome = joined[(joined["sid"]==student_id) & (joined["school"]==school)].iloc[0]["outcome"]
        rows.append({"school": school, "cat": cat, "sat_med": sat_med, "gpa_med": gpa_med, "outcome": outcome})

    order = {"Safety":0,"Match":1,"Reach":2}
    rows.sort(key=lambda r: order[r["cat"]])

    counts = {k: sum(1 for r in rows if r["cat"]==k) for k in ["Safety","Match","Reach"]}
    console.print(Columns([
        Panel(f"[green]{counts['Safety']}[/green] schools", title="[green]Safety[/green]", width=20),
        Panel(f"[yellow]{counts['Match']}[/yellow] schools",  title="[yellow]Match[/yellow]",  width=20),
        Panel(f"[red]{counts['Reach']}[/red] schools",    title="[red]Reach[/red]",    width=20),
    ]))

    t = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan")
    for col in ["School","Classification","Adm Median SAT","Adm Median GPA","Outcome"]:
        t.add_column(col, justify="right" if col not in ["School","Classification","Outcome"] else "left")

    cat_colors = {"Safety":"green","Match":"yellow","Reach":"red"}
    for r in rows:
        cc = cat_colors[r["cat"]]
        oc = outcome_color(r["outcome"]) if r["outcome"] != "not applied" else "dim"
        t.add_row(
            r["school"],
            f"[{cc}]{r['cat']}[/{cc}]",
            f"{r['sat_med']:.0f}", f"{r['gpa_med']:.2f}",
            f"[{oc}]{r['outcome']}[/{oc}]",
        )
    console.print(t)

    cats   = ["Safety","Match","Reach"]
    colors = ["green","yellow","red"]
    for cat, color in zip(cats, colors):
        bar = "█" * counts[cat]
        console.print(f"  [{color}]{cat:10}[/{color}]  [{color}]{bar}[/{color}] {counts[cat]}")


# ══════════════════════════════════════════════════════════════════════════════
# 7. SCHOOL DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
def school_deep_dive(s, o, joined, school_name):
    matches = joined[joined["school"].str.contains(school_name, case=False, na=False)]
    if matches.empty:
        console.print(f"[red]No applicants found for '[bold]{school_name}[/bold]'[/red]")
        return

    full_name = matches.iloc[0]["school"]
    section(f"7 · SCHOOL DEEP DIVE — {full_name}")

    def fmt(val, kind=None):
        if val is None or (isinstance(val, float) and np.isnan(val)) or str(val).strip() == "":
            return "—"
        try:
            v = float(val)
            if kind == "int":   return str(int(v))
            if kind == "money": return f"${v:,.0f}"
            if kind == "gpa":   return f"{v:.2f}"
        except (ValueError, TypeError):
            pass
        return str(val)

    outcome_order = {"admitted": 0, "waitlisted": 1, "denied": 2}
    rows = matches.sort_values("outcome", key=lambda col: col.map(lambda x: outcome_order.get(x, 9)))

    t = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan")
    for col in ["Student", "Outcome", "Award", "GPA", "W?", "SAT", "ACT", "AP Taken", "AP Avg", "Rank"]:
        t.add_column(col, justify="right" if col not in ["Student", "Outcome", "W?"] else "left")

    for _, row in rows.iterrows():
        oc = outcome_color(row["outcome"])
        cr = fmt(row.get("class_rank"), "int")
        cs = fmt(row.get("class_size"), "int")
        rank = f"{cr}/{cs}" if cr != "—" and cs != "—" else "—"
        weighted_flag = "W" if str(row.get("weighted", "")).lower() == "yes" else ""
        t.add_row(
            row["name"],
            f"[{oc}]{row['outcome']}[/{oc}]",
            fmt(row.get("award"), "money"),
            fmt(row.get("gpa"), "gpa"),
            f"[dim]{weighted_flag}[/dim]",
            fmt(row.get("sat"), "int"),
            fmt(row.get("act"), "int"),
            fmt(row.get("ap_taken"), "int"),
            fmt(row.get("ap_avg")),
            rank,
        )
    console.print(t)

    # Summary by outcome
    console.print()
    for outcome in ["admitted", "waitlisted", "denied"]:
        pool = rows[rows["outcome"] == outcome]
        if pool.empty:
            continue
        color = outcome_color(outcome)
        gpas = pool["gpa"].dropna()
        sats = pool["sat"].dropna()
        acts = pool["act"].dropna()
        gpa_str = f"GPA {gpas.mean():.2f} avg ({gpas.min():.2f}–{gpas.max():.2f})" if not gpas.empty else "GPA —"
        sat_str = f"SAT {sats.mean():.0f} avg ({int(sats.min())}–{int(sats.max())})" if not sats.empty else "SAT —"
        act_str = f"ACT {acts.mean():.1f} avg" if not acts.empty else "ACT —"
        console.print(f"  [{color}]{outcome.upper():12}[/{color}]  {len(pool)} student{'s' if len(pool)>1 else ''}  ·  {gpa_str}  ·  {sat_str}  ·  {act_str}")

    # Other schools each applicant applied to
    console.print()
    console.print("[bold cyan]Other Schools Each Applicant Applied To[/bold cyan]")
    for _, row in rows.iterrows():
        oc = outcome_color(row["outcome"])
        others = o[(o["sid"] == row["sid"]) & (~o["school"].str.contains(school_name, case=False, na=False))]
        console.print(f"\n  [{oc}]{row['name']} ({row['outcome']})[/{oc}]")
        if others.empty:
            console.print("    [dim]none[/dim]")
        for _, r in others.iterrows():
            rc = outcome_color(r["outcome"])
            console.print(f"    [{rc}]{'●'}[/{rc}] {r['school']}  [{rc}]{r['outcome']}[/{rc}]")

    # Regional patterns
    REGION_MAP = {
        "Northeast":  ["Massachusetts", "Connecticut", "Rhode Island", "Vermont", "New Hampshire",
                       "Maine", "New York", "New Jersey", "Pennsylvania", "Boston", "Harvard",
                       "Yale", "Princeton", "Cornell", "Columbia", "Dartmouth", "Brown",
                       "Northeastern", "Tufts", "Fordham", "Villanova", "Georgetown", "American",
                       "George Washington", "Lehigh", "Bucknell", "Lafayette", "Colgate"],
        "Southeast":  ["Florida", "Georgia", "Alabama", "Tennessee", "South Carolina",
                       "North Carolina", "Virginia", "Mississippi", "Louisiana", "Kentucky",
                       "Auburn", "Clemson", "Vanderbilt", "Duke", "Wake Forest", "Tulane",
                       "Ole Miss", "Mississippi State"],
        "Midwest":    ["Ohio", "Indiana", "Michigan", "Illinois", "Wisconsin", "Minnesota",
                       "Iowa", "Missouri", "Kansas", "Nebraska", "Notre Dame", "Purdue",
                       "Northwestern", "Washington University", "Creighton", "Marquette",
                       "DePaul", "Loyola Chicago", "Ball State", "Carroll", "Butler"],
        "Southwest":  ["Texas", "Oklahoma", "Arkansas", "Arizona", "New Mexico", "TCU",
                       "Baylor", "SMU", "Rice", "Texas A&M", "Texas Tech", "Tulsa"],
        "West":       ["California", "Oregon", "Washington", "Colorado", "Utah", "Nevada",
                       "Idaho", "Montana", "Wyoming", "USC", "UCLA", "Stanford", "Pepperdine",
                       "Gonzaga", "Santa Clara", "San Diego", "Chapman"],
    }

    def get_region(school_str):
        for region, keywords in REGION_MAP.items():
            if any(kw.lower() in school_str.lower() for kw in keywords):
                return region
        return "Other"

    console.print()
    console.print("[bold cyan]Regional Patterns — Where These Students Also Applied[/bold cyan]")
    console.print(f"[dim](all schools from applicants who applied to {full_name})[/dim]\n")

    all_apps = o[o["sid"].isin(rows["sid"])].copy()
    all_apps["region"] = all_apps["school"].map(get_region)

    region_order = ["Northeast", "Southeast", "Midwest", "Southwest", "West", "Other"]
    reg_t = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan")
    reg_t.add_column("Region")
    reg_t.add_column("Schools Applied", justify="right")
    reg_t.add_column("Accepted", justify="right")
    reg_t.add_column("Waitlisted", justify="right")
    reg_t.add_column("Denied", justify="right")
    reg_t.add_column("Admit Rate", justify="right")

    for region in region_order:
        grp = all_apps[all_apps["region"] == region]
        if grp.empty:
            continue
        n        = len(grp)
        adm      = (grp["outcome"] == "admitted").sum()
        wl       = (grp["outcome"] == "waitlisted").sum()
        den      = (grp["outcome"] == "denied").sum()
        rate     = adm / n * 100
        rate_col = "green" if rate >= 60 else "yellow" if rate >= 35 else "red"
        reg_t.add_row(
            region, str(n), f"[green]{adm}[/green]",
            f"[yellow]{wl}[/yellow]", f"[red]{den}[/red]",
            f"[{rate_col}]{rate:.0f}%[/{rate_col}]",
        )
    console.print(reg_t)

    # Per-student region breakdown
    console.print("[bold cyan]Per-Student Regional Spread[/bold cyan]\n")
    for _, row in rows.iterrows():
        oc = outcome_color(row["outcome"])
        student_apps = all_apps[all_apps["sid"] == row["sid"]]
        by_region = student_apps.groupby("region")["outcome"].apply(list)
        region_strs = []
        for region in region_order:
            if region not in by_region:
                continue
            outcomes = by_region[region]
            adm = outcomes.count("admitted")
            wl  = outcomes.count("waitlisted")
            den = outcomes.count("denied")
            parts = []
            if adm: parts.append(f"[green]{adm}✓[/green]")
            if wl:  parts.append(f"[yellow]{wl}~[/yellow]")
            if den: parts.append(f"[red]{den}✗[/red]")
            region_strs.append(f"{region}({'/'.join(parts)})")
        console.print(f"  [{oc}]{row['name']:20}[/{oc}]  " + "  ".join(region_strs))


# ══════════════════════════════════════════════════════════════════════════════
# 8. SCHEDULE RIGOR vs ACCEPTANCE RATES
# ══════════════════════════════════════════════════════════════════════════════
def schedule_rigor(s, joined):
    section("8 · SCHEDULE RIGOR vs ACCEPTANCE RATES")

    def admit_rate(df): return len(df[df["outcome"] == "admitted"]) / len(df) if len(df) else 0

    # ── AP/IB senior year count ──────────────────────────────────────────────
    senior_col = "ap_ib_senior_year"
    has_senior = joined[senior_col].notna().any()
    if has_senior:
        sr_bins   = [-0.5, 0.5, 2.5, 4.5, 6.5, 99]
        sr_labels = ["0", "1–2", "3–4", "5–6", "7+"]
        joined["sr_band"] = pd.cut(joined[senior_col], bins=sr_bins, labels=sr_labels, right=True)

        t = Table(title="Admit Rate by AP/IB Classes Taken Senior Year", box=box.SIMPLE_HEAVY, header_style="bold cyan")
        t.add_column("AP/IB Senior Year"); t.add_column("Apps", justify="right")
        t.add_column("Admitted", justify="right"); t.add_column("Admit Rate", justify="right")
        sr_rates = []
        for label in sr_labels:
            grp = joined[joined["sr_band"] == label]
            if grp.empty:
                continue
            n, adm = len(grp), len(grp[grp["outcome"] == "admitted"])
            rate = adm / n * 100
            sr_rates.append((label, rate))
            color = "green" if rate >= 60 else "yellow" if rate >= 35 else "red"
            t.add_row(label, str(n), str(adm), f"[{color}]{rate:.0f}%[/{color}]")
        console.print(t)
        if sr_rates:
            bar_chart_plotext([r[0] for r in sr_rates], [r[1] for r in sr_rates],
                              "Admit Rate by AP/IB Senior Year Count (%)", "Classes", color="cyan")
    else:
        console.print("[dim]No AP/IB senior year data yet — fill in ap_ib_senior_year in student_stats.csv[/dim]\n")

    # ── Activities count ─────────────────────────────────────────────────────
    act_col = "activities_count"
    has_act = joined[act_col].notna().any()
    if has_act:
        act_bins   = [0, 2, 4, 6, 8, 99]
        act_labels = ["1–2", "3–4", "5–6", "7–8", "9+"]
        joined["act_band"] = pd.cut(joined[act_col], bins=act_bins, labels=act_labels, right=True)

        t2 = Table(title="Admit Rate by Number of Activities", box=box.SIMPLE_HEAVY, header_style="bold cyan")
        t2.add_column("Activities"); t2.add_column("Apps", justify="right")
        t2.add_column("Admitted", justify="right"); t2.add_column("Admit Rate", justify="right")
        act_rates = []
        for label in act_labels:
            grp = joined[joined["act_band"] == label]
            if grp.empty:
                continue
            n, adm = len(grp), len(grp[grp["outcome"] == "admitted"])
            rate = adm / n * 100
            act_rates.append((label, rate))
            color = "green" if rate >= 60 else "yellow" if rate >= 35 else "red"
            t2.add_row(label, str(n), str(adm), f"[{color}]{rate:.0f}%[/{color}]")
        console.print(t2)
        if act_rates:
            bar_chart_plotext([r[0] for r in act_rates], [r[1] for r in act_rates],
                              "Admit Rate by Number of Activities (%)", "# Activities", color="yellow")
    else:
        console.print("[dim]No activities data yet — fill in activities_count in student_stats.csv[/dim]\n")

    # ── Activity types breakdown ─────────────────────────────────────────────
    type_col = "activity_types"
    has_types = joined[type_col].notna().any()
    if has_types:
        exploded = joined.dropna(subset=[type_col]).copy()
        exploded[type_col] = exploded[type_col].str.split(",")
        exploded = exploded.explode(type_col)
        exploded[type_col] = exploded[type_col].str.strip().str.title()

        all_types = exploded[type_col].dropna().unique()
        rows_type = []
        for atype in sorted(all_types):
            grp = exploded[exploded[type_col] == atype]
            n   = len(grp)
            adm = len(grp[grp["outcome"] == "admitted"])
            rate = adm / n * 100 if n else 0
            rows_type.append((atype, n, adm, rate))
        rows_type.sort(key=lambda r: r[3], reverse=True)

        t3 = Table(title="Admit Rate by Activity Type", box=box.SIMPLE_HEAVY, header_style="bold cyan")
        t3.add_column("Activity Type"); t3.add_column("Apps", justify="right")
        t3.add_column("Admitted", justify="right"); t3.add_column("Admit Rate", justify="right")
        for atype, n, adm, rate in rows_type:
            color = "green" if rate >= 60 else "yellow" if rate >= 35 else "red"
            t3.add_row(atype, str(n), str(adm), f"[{color}]{rate:.0f}%[/{color}]")
        console.print(t3)
    else:
        console.print("[dim]No activity type data yet — fill in activity_types in student_stats.csv (comma-separated, e.g. 'Sport,Club,Leadership')[/dim]\n")

    # ── Rigor index: AP/IB senior + AP/IB total vs admit rate ───────────────
    has_both = joined["ap_taken"].notna().any() and has_senior
    if has_both:
        joined["rigor_index"] = joined["ap_taken"].fillna(0) + joined[senior_col].fillna(0)
        ri_bins   = [0, 2, 5, 8, 12, 99]
        ri_labels = ["0–2", "3–5", "6–8", "9–12", "13+"]
        joined["ri_band"] = pd.cut(joined["rigor_index"], bins=ri_bins, labels=ri_labels, right=True)

        t4 = Table(title="Admit Rate by Courseload Rigor (Total AP/IB + Senior AP/IB)", box=box.SIMPLE_HEAVY, header_style="bold cyan")
        t4.add_column("Rigor Index"); t4.add_column("Apps", justify="right")
        t4.add_column("Admitted", justify="right"); t4.add_column("Admit Rate", justify="right")
        ri_rates = []
        for label in ri_labels:
            grp = joined[joined["ri_band"] == label]
            if grp.empty:
                continue
            n, adm = len(grp), len(grp[grp["outcome"] == "admitted"])
            rate = adm / n * 100
            ri_rates.append((label, rate))
            color = "green" if rate >= 60 else "yellow" if rate >= 35 else "red"
            t4.add_row(label, str(n), str(adm), f"[{color}]{rate:.0f}%[/{color}]")
        console.print(t4)
        if ri_rates:
            bar_chart_plotext([r[0] for r in ri_rates], [r[1] for r in ri_rates],
                              "Admit Rate by Courseload Rigor (%)", "Index", color="magenta+")


# ══════════════════════════════════════════════════════════════════════════════
# TEST MODE — interactive student entry
# ══════════════════════════════════════════════════════════════════════════════
def prompt_test_student():
    """Interactively collect a student's stats from stdin."""
    console.print(Panel.fit(
        "[bold yellow]Test Student Entry[/bold yellow]\n"
        "[dim]Enter stats to see how this student compares against the existing pool.[/dim]",
        border_style="yellow"
    ))
    console.print()

    def ask(label, hint, cast=str, optional=False, default=None):
        prompt_str = f"  [bold cyan]{label}[/bold cyan] [dim]({hint})[/dim]"
        if default is not None:
            prompt_str += f" [dim][{default}][/dim]"
        prompt_str += ": "
        while True:
            raw = console.input(prompt_str).strip()
            if not raw and default is not None:
                return cast(default) if cast is not str else default
            if not raw and optional:
                return None
            if not raw:
                console.print("    [red]This field is required.[/red]")
                continue
            try:
                return cast(raw)
            except (ValueError, TypeError):
                console.print(f"    [red]Expected {hint} — try again.[/red]")

    gpa      = ask("GPA",                                        "0.00 – 4.00",                          float, optional=True)
    weighted = ask("Weighted GPA?", "yes / no", str, optional=False, default="no") if gpa is not None else None
    sat      = ask("SAT",                                        "400 – 1600  (skip if not taken)",      int,   optional=True)
    act      = ask("ACT",                                        "1 – 36      (skip if not taken)",      int,   optional=True)
    ap_ib    = ask("AP, IB, and College Level Classes Taken",    "integer",                              int,   optional=True)
    ap_avg   = ask("AP Average Score",                           "1.0 – 5.0   (skip if none)",           float, optional=True)
    c_rank   = ask("Class Rank",                                 "integer (1 = top of class)",           int,   optional=True)
    c_size   = ask("Class Size",                                 "integer",                              int,   optional=True)
    grad_yr  = ask("Graduation Year",                            "e.g. 2026",                            int,   optional=True)
    act_cnt  = ask("Activities Count",                           "integer",                              int,   optional=True)
    act_types= ask("Activity Types",                             "comma-separated: Sport,Club,...",      str,   optional=True)

    return {
        "gpa": gpa,
        "weighted": weighted,
        "sat": sat,
        "act": act,
        "ap_ib_college_taken": ap_ib,
        "ap_Avg_score": ap_avg,
        "class_rank": c_rank,
        "class_size": c_size,
        "grad_year": grad_yr,
        "activities_count": act_cnt,
        "activity_types": act_types,
    }


def test_student_report(s, o, joined, data):
    """Display pool-comparison analytics for a manually entered student."""
    gpa      = data.get("gpa")
    sat      = data.get("sat")
    act      = data.get("act")
    ap_taken = data.get("ap_ib_college_taken")
    ap_avg   = data.get("ap_Avg_score")
    rank     = data.get("class_rank")
    size     = data.get("class_size")
    pct      = (rank / size) * 100 if (rank is not None and size) else float("nan")
    weighted_flag = "(W)" if str(data.get("weighted", "")).lower() == "yes" else ""

    def fv(val, fmt_fn=None):
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return "—"
        return fmt_fn(val) if fmt_fn else str(val)

    # ── Profile panel ─────────────────────────────────────────────────────────
    console.print()
    console.print(Panel(
        f"{weighted_flag}  "
        f"GPA [cyan]{fv(gpa, lambda v: f'{v:.2f}')}[/cyan]   "
        f"SAT [cyan]{fv(sat, lambda v: str(int(v)))}[/cyan]   "
        f"ACT [cyan]{fv(act, lambda v: str(int(v)))}[/cyan]   "
        f"AP [cyan]{fv(ap_taken, lambda v: str(int(v)))}[/cyan]   AP Avg [cyan]{fv(ap_avg, lambda v: f'{v:.1f}')}[/cyan]\n"
        f"Rank [cyan]{fv(rank, str)}/{fv(size, str)}[/cyan] ([cyan]{fv(pct, lambda v: f'{v:.1f}%')}ile[/cyan])   "
        f"Grad [cyan]{fv(data.get('grad_year'))}[/cyan]   "
        f"Activities [cyan]{fv(data.get('activities_count'))}[/cyan]"
        + (f"  ({data['activity_types']})" if data.get("activity_types") else ""),
        title="[bold yellow]Test Student[/bold yellow]",
        border_style="yellow"
    ))

    # ── 1. Where they rank in the pool ────────────────────────────────────────
    section("POOL PERCENTILE RANKINGS")

    all_metrics = [
        ("GPA",      "gpa",      gpa,      lambda v: f"{v:.2f}"),
        ("SAT",      "sat",      sat,      lambda v: f"{int(v)}"),
        ("ACT",      "act",      act,      lambda v: f"{int(v)}"),
        ("AP Exams", "ap_taken", ap_taken, lambda v: f"{int(v)}"),
        ("AP Avg",   "ap_avg",   ap_avg,   lambda v: f"{v:.1f}"),
    ]
    metrics = [(lbl, col, val, fmt) for lbl, col, val, fmt in all_metrics if val is not None]

    t = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan",
              title="Student vs Pool — Where They Stand")
    for col in ["Metric", "Student", "Pool Median", "Pool Range", "Pool %ile"]:
        t.add_column(col, justify="right" if col not in ["Metric"] else "left")

    for label, col, val, fmt in metrics:
        med = s[col].median()
        lo  = s[col].min()
        hi  = s[col].max()
        percentile_rank = (s[col] <= val).mean() * 100
        color = "green" if percentile_rank >= 50 else "yellow" if percentile_rank >= 25 else "red"
        t.add_row(
            label,
            fmt(val),
            fmt(med),
            f"{fmt(lo)}–{fmt(hi)}",
            f"[{color}]{percentile_rank:.0f}th[/{color}]",
        )

    if not np.isnan(pct):
        rank_pct_med = s["percentile"].median()
        t.add_row(
            "Class Rank %ile",
            f"{pct:.1f}%",
            f"{rank_pct_med:.1f}%",
            f"{s['percentile'].min():.1f}%–{s['percentile'].max():.1f}%",
            "[dim]N/A[/dim]",
        )
    console.print(t)

    # ── 2. Bracket admission rates ────────────────────────────────────────────
    section("BRACKET ADMISSION RATES")
    console.print("[dim]Admit rates for students in the same brackets as this student.[/dim]\n")

    def admit_rate(df):
        return len(df[df["outcome"] == "admitted"]) / len(df) * 100 if len(df) else 0

    gpa_bins    = [0, 3.5, 3.6, 3.7, 3.8, 3.9, 4.01]
    gpa_labels  = ["<3.5","3.5-3.6","3.6-3.7","3.7-3.8","3.8-3.9","3.9-4.0"]
    sat_bins    = [0, 1300, 1350, 1400, 1450, 1500, 1600]
    sat_labels  = ["<1300","1300-1350","1350-1400","1400-1450","1450-1500","1500+"]
    rank_bins   = [0, 5, 10, 25, 50, 100]
    rank_labels = ["Top 5%","5-10%","10-25%","25-50%","50%+"]

    joined["gpa_bracket"] = pd.cut(joined["gpa"],        bins=gpa_bins,  labels=gpa_labels,  right=False)
    joined["sat_bracket"] = pd.cut(joined["sat"],        bins=sat_bins,  labels=sat_labels,  right=False)
    joined["rank_band"]   = pd.cut(joined["percentile"], bins=rank_bins, labels=rank_labels, right=True)

    student_gpa_bracket = pd.cut([gpa], bins=gpa_bins,  labels=gpa_labels,  right=False)[0] if gpa is not None else None
    student_sat_bracket = pd.cut([sat], bins=sat_bins,  labels=sat_labels,  right=False)[0] if sat is not None else None
    student_rank_band   = pd.cut([pct], bins=rank_bins, labels=rank_labels, right=True)[0]  if not np.isnan(pct) else None

    bt = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan")
    for col in ["Dimension", "Bracket", "Apps in Bracket", "Admitted", "Admit Rate"]:
        t2_align = "right" if col not in ["Dimension", "Bracket"] else "left"
        bt.add_column(col, justify=t2_align)

    for dim, bracket, col in [
        ("GPA",        student_gpa_bracket, "gpa_bracket"),
        ("SAT",        student_sat_bracket, "sat_bracket"),
        ("Class Rank", student_rank_band,   "rank_band"),
    ]:
        if bracket is None or str(bracket) == "nan":
            bt.add_row(dim, "[dim]not provided[/dim]", "—", "—", "—")
            continue
        grp = joined[joined[col] == bracket]
        n   = len(grp)
        adm = len(grp[grp["outcome"] == "admitted"])
        rate = adm / n * 100 if n else 0
        color = "green" if rate >= 60 else "yellow" if rate >= 35 else "red"
        bt.add_row(dim, str(bracket), str(n), str(adm), f"[{color}]{rate:.0f}%[/{color}]")

    console.print(bt)

    # ── 3. vs admitted / waitlisted / denied averages ─────────────────────────
    section("VS OUTCOME GROUP AVERAGES")

    avgs = {}
    for outcome in ["admitted", "waitlisted", "denied"]:
        sids = joined[joined["outcome"] == outcome]["sid"].unique()
        pool = s[s["id"].isin(sids)]
        avgs[outcome] = {col: pool[col].mean() for _, col, _, _ in metrics}

    ct = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan",
               title="Student vs Admitted / Waitlisted / Denied Averages")
    ct.add_column("Metric")
    ct.add_column("This Student",         justify="right")
    ct.add_column("[green]Admitted Avg[/green]",    justify="right")
    ct.add_column("[yellow]Waitlisted Avg[/yellow]", justify="right")
    ct.add_column("[red]Denied Avg[/red]",       justify="right")

    for label, col, val, fmt in metrics:
        adm_avg = avgs["admitted"].get(col, float("nan"))
        color = "green" if not np.isnan(adm_avg) and val >= adm_avg else "red"
        ct.add_row(
            label,
            f"[{color}]{fmt(val)}[/{color}]",
            fmt(adm_avg)                                   if not np.isnan(avgs["admitted"].get(col, float("nan")))   else "—",
            fmt(avgs["waitlisted"].get(col, float("nan"))) if not np.isnan(avgs["waitlisted"].get(col, float("nan"))) else "—",
            fmt(avgs["denied"].get(col, float("nan")))     if not np.isnan(avgs["denied"].get(col, float("nan")))     else "—",
        )
    console.print(ct)


# ══════════════════════════════════════════════════════════════════════════════
# SCHOOL ADMISSION PREDICTIONS (test mode)
# ══════════════════════════════════════════════════════════════════════════════
def prompt_schools_of_interest():
    console.print()
    console.rule("[bold yellow]School Predictions[/bold yellow]")
    console.print()
    console.print("[dim]Enter schools you're interested in (one per line). Press Enter with no input when done.[/dim]\n")
    schools = []
    while True:
        raw = console.input("  [bold cyan]School[/bold cyan] [dim](or press Enter to finish)[/dim]: ").strip()
        if not raw:
            break
        schools.append(raw)
    return schools


def school_admission_prediction(s, o, joined, student_data, schools):
    if not schools:
        return

    gpa      = student_data.get("gpa")
    sat      = student_data.get("sat")
    act      = student_data.get("act")
    ap_taken = student_data.get("ap_ib_college_taken")
    ap_avg   = student_data.get("ap_Avg_score")
    rank     = student_data.get("class_rank")
    size     = student_data.get("class_size")
    pct      = (rank / size) * 100 if (rank is not None and size) else float("nan")

    def fv(val, fmt_fn=None):
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return "—"
        return fmt_fn(val) if fmt_fn else str(val)

    def prediction_label(score):
        if score >= 0.75:   return "Strong Admit", "green"
        elif score >= 0.55: return "Likely Admit", "cyan"
        elif score >= 0.40: return "Borderline",   "yellow"
        elif score >= 0.25: return "Reach",         "red"
        else:               return "Unlikely",      "bold red"

    def score_vs_pool(admitted_pool):
        """Weighted score: how many of student's metrics are >= admitted medians."""
        points, weights = [], []
        for col, val, w in [("gpa", gpa, 3.0), ("sat", sat, 2.5), ("act", act, 1.5),
                             ("ap_taken", ap_taken, 1.0), ("ap_avg", ap_avg, 0.8)]:
            if val is None:
                continue
            adm_vals = admitted_pool[col].dropna()
            if adm_vals.empty:
                continue
            adm_med = adm_vals.median()
            adm_min = adm_vals.min()
            if val >= adm_med:
                pt = 1.0
            elif val >= adm_min:
                pt = 0.1 + 0.4 * (val - adm_min) / (adm_med - adm_min) if adm_med > adm_min else 0.3
            else:
                pt = 0.0
            points.append(pt)
            weights.append(w)
        if not points:
            return None
        return sum(p * w for p, w in zip(points, weights)) / sum(weights)

    section("SCHOOL ADMISSION PREDICTIONS")

    for school_query in schools:
        matches = joined[joined["school"].str.contains(school_query, case=False, na=False)]
        console.print()

        # ── No historical data: estimate from bracket rates ───────────────────
        if matches.empty:
            console.print(Panel(
                "[dim]No historical applicants found. Estimating from overall pool bracket rates.[/dim]",
                title=f"[bold]{school_query}[/bold]  [dim](no data)[/dim]",
                border_style="dim"
            ))
            gpa_bins   = [0, 3.5, 3.6, 3.7, 3.8, 3.9, 4.01]
            gpa_labels = ["<3.5","3.5-3.6","3.6-3.7","3.7-3.8","3.8-3.9","3.9-4.0"]
            sat_bins   = [0, 1300, 1350, 1400, 1450, 1500, 1600]
            sat_labels = ["<1300","1300-1350","1350-1400","1400-1450","1450-1500","1500+"]
            rank_bins  = [0, 5, 10, 25, 50, 100]
            rank_labels= ["Top 5%","5-10%","10-25%","25-50%","50%+"]
            joined["gpa_bracket"] = pd.cut(joined["gpa"],        bins=gpa_bins,  labels=gpa_labels,  right=False)
            joined["sat_bracket"] = pd.cut(joined["sat"],        bins=sat_bins,  labels=sat_labels,  right=False)
            joined["rank_band"]   = pd.cut(joined["percentile"], bins=rank_bins, labels=rank_labels, right=True)
            rates = []
            if gpa is not None:
                gb = pd.cut([gpa], bins=gpa_bins, labels=gpa_labels, right=False)[0]
                g = joined[joined["gpa_bracket"] == gb]
                if len(g): rates.append(len(g[g["outcome"]=="admitted"]) / len(g))
            if sat is not None:
                sb = pd.cut([sat], bins=sat_bins, labels=sat_labels, right=False)[0]
                g = joined[joined["sat_bracket"] == sb]
                if len(g): rates.append(len(g[g["outcome"]=="admitted"]) / len(g))
            if not np.isnan(pct):
                rb = pd.cut([pct], bins=rank_bins, labels=rank_labels, right=True)[0]
                g = joined[joined["rank_band"] == rb]
                if len(g): rates.append(len(g[g["outcome"]=="admitted"]) / len(g))
            if rates:
                avg = sum(rates) / len(rates)
                lbl, color = prediction_label(avg)
                bar = "█" * int(avg * 20) + "░" * (20 - int(avg * 20))
                console.print(f"\n  Prediction:  [{color}]{lbl}[/{color}]  [dim](pool estimate)[/dim]")
                console.print(f"  [{color}]{bar}[/{color}] [dim]{avg*100:.0f}%[/dim]")
            else:
                console.print("  [dim]Not enough data to estimate — provide GPA, SAT, or class rank.[/dim]")
            continue

        # ── School has historical data ────────────────────────────────────────
        full_name  = matches.iloc[0]["school"]
        admitted   = matches[matches["outcome"] == "admitted"]
        waitlisted = matches[matches["outcome"] == "waitlisted"]
        denied     = matches[matches["outcome"] == "denied"]
        total      = len(matches)
        hist_rate  = len(admitted) / total * 100 if total else 0

        adm_gpa_med = admitted["gpa"].dropna().median() if not admitted["gpa"].dropna().empty else float("nan")
        adm_sat_med = admitted["sat"].dropna().median() if not admitted["sat"].dropna().empty else float("nan")
        adm_act_med = admitted["act"].dropna().median() if not admitted["act"].dropna().empty else float("nan")

        console.print(Panel(
            f"[green]{len(admitted)} admitted[/green]  [yellow]{len(waitlisted)} waitlisted[/yellow]  [red]{len(denied)} denied[/red]  "
            f"[dim]({total} applicants · {hist_rate:.0f}% admit rate in this dataset)[/dim]\n"
            f"Admitted medians:  GPA [cyan]{fv(adm_gpa_med, lambda v: f'{v:.2f}')}[/cyan]  "
            f"SAT [cyan]{fv(adm_sat_med, lambda v: str(int(v)))}[/cyan]  "
            f"ACT [cyan]{fv(adm_act_med, lambda v: f'{v:.1f}')}[/cyan]",
            title=f"[bold]{full_name}[/bold]",
            border_style="cyan"
        ))

        score = score_vs_pool(admitted) if len(admitted) >= 1 else None

        if score is not None:
            lbl, color = prediction_label(score)
            low_note = "  [dim](small sample — limited confidence)[/dim]" if len(admitted) < 3 else ""
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            console.print(f"\n  Prediction:  [{color}]{lbl}[/{color}]{low_note}")
            console.print(f"  [{color}]{bar}[/{color}] [dim]{score*100:.0f}%[/dim]")
        else:
            console.print("\n  [dim]No admitted students on record — cannot compute prediction.[/dim]")

        # Per-metric breakdown vs admitted pool
        mt = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan",
                   title="Your Stats vs This School's Admitted Students")
        mt.add_column("Metric")
        mt.add_column("You",           justify="right")
        mt.add_column("Adm Median",    justify="right")
        mt.add_column("Adm Range",     justify="right")
        mt.add_column("%ile (of adm)", justify="right")

        for col, metric_lbl, val, fmt in [
            ("gpa",      "GPA",      gpa,      lambda v: f"{v:.2f}"),
            ("sat",      "SAT",      sat,      lambda v: str(int(v))),
            ("act",      "ACT",      act,      lambda v: f"{v:.1f}"),
            ("ap_taken", "AP Exams", ap_taken, lambda v: str(int(v))),
            ("ap_avg",   "AP Avg",   ap_avg,   lambda v: f"{v:.1f}"),
        ]:
            adm_col = admitted[col].dropna()
            if adm_col.empty:
                continue
            adm_med = adm_col.median()
            adm_min = adm_col.min()
            adm_max = adm_col.max()
            if val is not None:
                pct_rank  = (adm_col <= val).mean() * 100
                pct_color = "green" if pct_rank >= 50 else "yellow" if pct_rank >= 25 else "red"
                val_color = "green" if val >= adm_med else "yellow" if val >= adm_min else "red"
                your_str  = f"[{val_color}]{fmt(val)}[/{val_color}]"
                pct_str   = f"[{pct_color}]{pct_rank:.0f}th[/{pct_color}]"
            else:
                your_str = "[dim]—[/dim]"
                pct_str  = "[dim]—[/dim]"
            mt.add_row(metric_lbl, your_str, fmt(adm_med),
                       f"{fmt(adm_min)}–{fmt(adm_max)}", pct_str)
        console.print(mt)

        # Reach / Match / Safety classification
        if len(admitted) >= 2:
            adm_sat = admitted["sat"].dropna()
            adm_gpa = admitted["gpa"].dropna()
            sat_ok    = sat is not None and not adm_sat.empty and sat >= adm_sat.median()
            gpa_ok    = gpa is not None and not adm_gpa.empty and gpa >= adm_gpa.median()
            sat_close = sat is not None and not adm_sat.empty and adm_sat.min() <= sat < adm_sat.median()
            gpa_close = gpa is not None and not adm_gpa.empty and adm_gpa.min() <= gpa < adm_gpa.median()
            if sat_ok and gpa_ok:                                cat, cc = "Safety", "green"
            elif sat_ok or gpa_ok or (sat_close and gpa_close): cat, cc = "Match",  "yellow"
            else:                                                cat, cc = "Reach",  "red"
            console.print(f"\n  Classification: [{cc}]{cat}[/{cc}]")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys

    STUDENTS, OUTCOMES = load_from_csv("student_stats.csv", "admission_stats.csv")
    s, o, joined = build_dfs(STUDENTS, OUTCOMES)

    # Usage: python admissions_analysis.py test
    if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
        student_data = prompt_test_student()
        test_student_report(s, o, joined, student_data)
        schools = prompt_schools_of_interest()
        school_admission_prediction(s, o, joined, student_data, schools)
        console.print()
        console.rule("[dim]end of report[/dim]")
        sys.exit(0)

    # Usage: python admissions_analysis.py "TCU"
    if len(sys.argv) > 1:
        school_deep_dive(s, o, joined, " ".join(sys.argv[1:]))
        console.print()
        console.rule("[dim]end of report[/dim]")
        sys.exit(0)

    LOOKUP_STUDENT = "S18"   # for sections 5 & 6

    console.print(Panel.fit(
        "[bold yellow]College Admissions Analytics[/bold yellow]\n"
        f"[dim]{len(s)} students · {len(o)} applications · {o['school'].nunique()} schools[/dim]",
        border_style="yellow"
    ))

    pool_overview(s)
    outcome_stats(s, joined)
    acceptance_rates(joined)
    student_lookup(s, joined, LOOKUP_STUDENT)
    reach_match_safety(s, joined, LOOKUP_STUDENT)
    schedule_rigor(s, joined)

    console.print()
    console.rule("[dim]end of report[/dim]")
