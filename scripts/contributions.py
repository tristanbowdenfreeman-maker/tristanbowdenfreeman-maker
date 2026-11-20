"""Draw the last year of GitHub contributions as an SVG in GitHub's dark style."""
import datetime, json, os, sys, urllib.request

USER = "tristanbowdenfreeman-maker"
OUT = sys.argv[1] if len(sys.argv) > 1 else "media/contributions.svg"
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount contributionLevel weekday}}}}}}"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
    headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
)
cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]

COLOURS = {"NONE": "#151b23", "FIRST_QUARTILE": "#033a16", "SECOND_QUARTILE": "#196c2e",
           "THIRD_QUARTILE": "#2ea043", "FOURTH_QUARTILE": "#56d364"}
FONT = 'font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif"'
CELL, STEP, LEFT, TOP = 11, 15, 56, 76
weeks = cal["weeks"]
W = LEFT + len(weeks) * STEP + 24
H = TOP + 7 * STEP + 52

parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" {FONT}>',
         f'<text x="0" y="20" font-size="20" fill="#f0f6fc">{cal["totalContributions"]:,} contributions in the last year</text>',
         f'<rect x="0.5" y="38.5" width="{W - 1}" height="{H - 39}" rx="6" fill="#0d1117" stroke="#3d444d"/>']
for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
    parts.append(f'<text x="18" y="{TOP + row * STEP + 10}" font-size="12" fill="#f0f6fc">{label}</text>')
last_month = None
for i, week in enumerate(weeks):
    x = LEFT + i * STEP
    first = datetime.date.fromisoformat(week["contributionDays"][0]["date"])
    if first.month != last_month and i < len(weeks) - 2:
        if last_month is not None or first.day <= 7:
            parts.append(f'<text x="{x}" y="{TOP - 10}" font-size="12" fill="#f0f6fc">{first.strftime("%b")}</text>')
        last_month = first.month
    for day in week["contributionDays"]:
        y = TOP + day["weekday"] * STEP
        tip = f'{day["contributionCount"]} contributions on {day["date"]}'
        parts.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{COLOURS[day["contributionLevel"]]}"><title>{tip}</title></rect>')
ly = TOP + 7 * STEP + 18
lx = W - 24 - 5 * STEP - 40
parts.append(f'<text x="{lx - 8}" y="{ly + 10}" font-size="12" fill="#9198a1" text-anchor="end">Less</text>')
for j, c in enumerate(COLOURS.values()):
    parts.append(f'<rect x="{lx + j * STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
parts.append(f'<text x="{lx + 5 * STEP + 4}" y="{ly + 10}" font-size="12" fill="#9198a1">More</text>')
parts.append("</svg>\n")
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
open(OUT, "w").write("".join(parts))
print(f"Wrote {OUT}: {cal['totalContributions']} contributions")
