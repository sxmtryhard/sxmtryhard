import json
import os
import urllib.request
from pathlib import Path
from collections import Counter
from datetime import datetime, date


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = "sxmtryhard"

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "stats"

OVERVIEW_FILE = OUTPUT_DIR / "overview.svg"
ACTIVITY_FILE = OUTPUT_DIR / "activity.svg"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

CURRENT_YEAR = datetime.now().year
TODAY = date.today()


# ============================================================
# GITHUB REST API
# ============================================================

def github_request(url):

    headers = {
        "User-Agent": "SXMTRYHARD-Profile-Stats",
        "Accept": "application/vnd.github+json"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    request = urllib.request.Request(
        url,
        headers=headers
    )

    with urllib.request.urlopen(request) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


# ============================================================
# GITHUB GRAPHQL API
# ============================================================

def github_graphql(query):

    if not GITHUB_TOKEN:

        raise RuntimeError(
            "GITHUB_TOKEN is required."
        )

    data = json.dumps({
        "query": query
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=data,
        headers={
            "User-Agent": "SXMTRYHARD-Profile-Stats",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:

        result = json.loads(
            response.read().decode("utf-8")
        )

    if "errors" in result:

        raise RuntimeError(
            json.dumps(
                result["errors"],
                indent=2
            )
        )

    return result["data"]


# ============================================================
# PROFILE
# ============================================================

def get_profile():

    return github_request(
        f"https://api.github.com/users/{USERNAME}"
    )


# ============================================================
# REPOSITORIES
# ============================================================

def get_repositories():

    return github_request(
        f"https://api.github.com/users/{USERNAME}/repos"
        "?per_page=100&sort=updated"
    )


# ============================================================
# CONTRIBUTION CALENDAR
# ============================================================

def get_contributions():

    query = f"""
    query {{
      user(login: "{USERNAME}") {{
        contributionsCollection(
          from: "{CURRENT_YEAR}-01-01T00:00:00Z"
          to: "{TODAY.isoformat()}T23:59:59Z"
        ) {{
          contributionCalendar {{
            totalContributions

            weeks {{
              contributionDays {{
                date
                contributionCount
                contributionLevel
              }}
            }}
          }}
        }}
      }}
    }}
    """

    data = github_graphql(query)

    return (
        data["user"]
        ["contributionsCollection"]
        ["contributionCalendar"]
    )


# ============================================================
# SVG ESCAPE
# ============================================================

def escape_svg(text):

    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


# ============================================================
# LANGUAGES
# ============================================================

def calculate_languages(repositories):

    languages = Counter()

    for repository in repositories:

        language = repository.get("language")

        if language:

            languages[language] += 1

    return languages


# ============================================================
# LANGUAGE BARS
# ============================================================

def generate_language_bars(languages):

    if not languages:

        return """
        <text
            x="70"
            y="390"
            fill="#8b949e"
            font-size="14"
            font-family="monospace"
        >
            No language data available
        </text>
        """

    sorted_languages = languages.most_common(5)

    total = sum(
        count
        for _, count in sorted_languages
    )

    output = []

    start_y = 390

    for index, (language, count) in enumerate(
        sorted_languages
    ):

        percentage = count / total

        bar_width = int(
            percentage * 430
        )

        y = start_y + index * 42

        output.append(
            f"""
            <text
                x="70"
                y="{y}"
                fill="#c9d1d9"
                font-size="13"
                font-family="monospace"
            >
                {escape_svg(language)}
            </text>

            <rect
                x="180"
                y="{y - 11}"
                width="430"
                height="5"
                rx="2.5"
                fill="#21262d"
            />

            <rect
                x="180"
                y="{y - 11}"
                width="{bar_width}"
                height="5"
                rx="2.5"
                fill="#f0f6fc"
            />

            <text
                x="635"
                y="{y}"
                fill="#8b949e"
                font-size="12"
                font-family="monospace"
            >
                {percentage * 100:.0f}%
            </text>
            """
        )

    return "\n".join(output)


# ============================================================
# OVERVIEW SVG
# ============================================================

def generate_overview_svg(
    profile,
    repositories,
    languages
):

    total_stars = sum(
        repository["stargazers_count"]
        for repository in repositories
    )

    total_forks = sum(
        repository["forks_count"]
        for repository in repositories
    )

    repository_count = profile["public_repos"]

    followers = profile["followers"]

    language_bars = generate_language_bars(
        languages
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="760"
    height="650"
    viewBox="0 0 760 650"
>

    <rect
        width="760"
        height="650"
        fill="transparent"
    />

    <text
        x="70"
        y="70"
        fill="#8b949e"
        font-size="12"
        font-family="monospace"
        letter-spacing="2"
    >
        GITHUB / OVERVIEW
    </text>

    <text
        x="70"
        y="112"
        fill="#f0f6fc"
        font-size="27"
        font-family="monospace"
        font-weight="600"
    >
        SXMTRYHARD
    </text>

    <text
        x="70"
        y="138"
        fill="#8b949e"
        font-size="13"
        font-family="monospace"
    >
        Software Engineer · Backend &amp; Full Stack
    </text>

    <line
        x1="70"
        y1="170"
        x2="690"
        y2="170"
        stroke="#21262d"
        stroke-width="1"
    />

    <text
        x="70"
        y="215"
        fill="#f0f6fc"
        font-size="28"
        font-family="monospace"
    >
        {repository_count}
    </text>

    <text
        x="70"
        y="238"
        fill="#8b949e"
        font-size="10"
        font-family="monospace"
        letter-spacing="1"
    >
        REPOSITORIES
    </text>

    <text
        x="250"
        y="215"
        fill="#f0f6fc"
        font-size="28"
        font-family="monospace"
    >
        {followers}
    </text>

    <text
        x="250"
        y="238"
        fill="#8b949e"
        font-size="10"
        font-family="monospace"
        letter-spacing="1"
    >
        FOLLOWERS
    </text>

    <text
        x="430"
        y="215"
        fill="#f0f6fc"
        font-size="28"
        font-family="monospace"
    >
        {total_stars}
    </text>

    <text
        x="430"
        y="238"
        fill="#8b949e"
        font-size="10"
        font-family="monospace"
        letter-spacing="1"
    >
        STARS
    </text>

    <text
        x="590"
        y="215"
        fill="#f0f6fc"
        font-size="28"
        font-family="monospace"
    >
        {total_forks}
    </text>

    <text
        x="590"
        y="238"
        fill="#8b949e"
        font-size="10"
        font-family="monospace"
        letter-spacing="1"
    >
        FORKS
    </text>

    <line
        x1="70"
        y1="275"
        x2="690"
        y2="275"
        stroke="#21262d"
        stroke-width="1"
    />

    <text
        x="70"
        y="320"
        fill="#8b949e"
        font-size="11"
        font-family="monospace"
        letter-spacing="2"
    >
        PRIMARY LANGUAGES
    </text>

    {language_bars}

    <line
        x1="70"
        y1="570"
        x2="690"
        y2="570"
        stroke="#21262d"
        stroke-width="1"
    />

    <text
        x="70"
        y="605"
        fill="#8b949e"
        font-size="11"
        font-family="monospace"
    >
        github.com/sxmtryhard
    </text>

    <text
        x="690"
        y="605"
        fill="#484f58"
        font-size="11"
        font-family="monospace"
        text-anchor="end"
    >
        PROFILE / SXMTRYHARD
    </text>

</svg>
'''


# ============================================================
# CONTRIBUTION OPACITY
# ============================================================

def get_cell_opacity(level):

    levels = {

        "NONE":
            0.08,

        "FIRST_QUARTILE":
            0.25,

        "SECOND_QUARTILE":
            0.45,

        "THIRD_QUARTILE":
            0.70,

        "FOURTH_QUARTILE":
            1.0

    }

    return levels.get(
        level,
        0.08
    )


# ============================================================
# ACTIVITY SVG
# ============================================================

def generate_activity_svg(calendar):

    weeks = calendar["weeks"]

    # --------------------------------------------------------
    # FILTER CURRENT YEAR
    # --------------------------------------------------------

    year_days = []

    for week in weeks:

        for day in week[
            "contributionDays"
        ]:

            day_date = datetime.strptime(
                day["date"],
                "%Y-%m-%d"
            ).date()

            if (
                day_date.year == CURRENT_YEAR
                and day_date <= TODAY
            ):

                year_days.append(day)

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    total_contributions = sum(
        day["contributionCount"]
        for day in year_days
    )

    # --------------------------------------------------------
    # ACTIVE DAYS
    # --------------------------------------------------------

    active_days = sum(
        1
        for day in year_days
        if day["contributionCount"] > 0
    )

    # --------------------------------------------------------
    # LONGEST STREAK
    # --------------------------------------------------------

    longest_streak = 0
    current_streak = 0

    previous_date = None

    for day in year_days:

        current_date = datetime.strptime(
            day["date"],
            "%Y-%m-%d"
        ).date()

        contributions = day[
            "contributionCount"
        ]

        if (
            contributions > 0
            and previous_date is not None
            and (
                current_date
                - previous_date
            ).days == 1
        ):

            current_streak += 1

        elif contributions > 0:

            current_streak = 1

        else:

            current_streak = 0

        longest_streak = max(
            longest_streak,
            current_streak
        )

        previous_date = current_date

    # --------------------------------------------------------
    # DIMENSIONS
    # --------------------------------------------------------

    width = 900
    height = 390

    cell_size = 13
    gap = 4

    start_x = 70
    start_y = 170

    output = []

    output.append(
        f'''<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}"
>

<rect
    width="{width}"
    height="{height}"
    fill="transparent"
/>

<!-- HEADER -->

<text
    x="70"
    y="40"
    fill="#8b949e"
    font-size="11"
    font-family="monospace"
    letter-spacing="2"
>
    GITHUB / ACTIVITY
</text>

<text
    x="70"
    y="72"
    fill="#f0f6fc"
    font-size="23"
    font-family="monospace"
    font-weight="600"
>
    {CURRENT_YEAR} CONTRIBUTION HISTORY
</text>

<!-- TOTAL -->

<text
    x="70"
    y="115"
    fill="#f0f6fc"
    font-size="25"
    font-family="monospace"
>
    {total_contributions}
</text>

<text
    x="70"
    y="135"
    fill="#8b949e"
    font-size="9"
    font-family="monospace"
    letter-spacing="1"
>
    CONTRIBUTIONS
</text>

<!-- ACTIVE DAYS -->

<text
    x="245"
    y="115"
    fill="#f0f6fc"
    font-size="25"
    font-family="monospace"
>
    {active_days}
</text>

<text
    x="245"
    y="135"
    fill="#8b949e"
    font-size="9"
    font-family="monospace"
    letter-spacing="1"
>
    ACTIVE DAYS
</text>

<!-- STREAK -->

<text
    x="420"
    y="115"
    fill="#f0f6fc"
    font-size="25"
    font-family="monospace"
>
    {longest_streak}
</text>

<text
    x="420"
    y="135"
    fill="#8b949e"
    font-size="9"
    font-family="monospace"
    letter-spacing="1"
>
    BEST STREAK
</text>

<line
    x1="70"
    y1="150"
    x2="830"
    y2="150"
    stroke="#21262d"
    stroke-width="1"
/>
'''
    )

    # --------------------------------------------------------
    # MONTHS + GRID
    # --------------------------------------------------------

    first_year_date = date(
        CURRENT_YEAR,
        1,
        1
    )

    # Find the first Sunday before
    # January 1st so the grid aligns
    # with GitHub's weekly layout.

    grid_start = first_year_date

    while grid_start.weekday() != 6:

        from datetime import timedelta

        grid_start -= timedelta(
            days=1
        )

    # Build all days from grid start
    # through today.

    from datetime import timedelta

    grid_days = []

    current = grid_start

    while current <= TODAY:

        grid_days.append(current)

        current += timedelta(
            days=1
        )

    # --------------------------------------------------------
    # CONTRIBUTION LOOKUP
    # --------------------------------------------------------

    contribution_lookup = {
        day["date"]: day
        for day in year_days
    }

    # --------------------------------------------------------
    # MONTH LABELS
    # --------------------------------------------------------

    shown_months = set()

    for current in grid_days:

        if current.month in shown_months:

            continue

        shown_months.add(
            current.month
        )

        days_from_start = (
            current - grid_start
        ).days

        week_index = (
            days_from_start // 7
        )

        x = (
            start_x
            + week_index
            * (
                cell_size + gap
            )
        )

        month_name = current.strftime(
            "%b"
        )

        output.append(
            f'''
            <text
                x="{x}"
                y="163"
                fill="#8b949e"
                font-size="9"
                font-family="monospace"
            >
                {month_name}
            </text>
            '''
        )

    # --------------------------------------------------------
    # DAY LABELS
    # --------------------------------------------------------

    labels = [
        ("Mon", 1),
        ("Wed", 3),
        ("Fri", 5)
    ]

    for label, row in labels:

        y = (
            start_y
            + row
            * (
                cell_size + gap
            )
            + 10
        )

        output.append(
            f'''
            <text
                x="18"
                y="{y}"
                fill="#8b949e"
                font-size="9"
                font-family="monospace"
            >
                {label}
            </text>
            '''
        )

    # --------------------------------------------------------
    # GRID
    # --------------------------------------------------------

    for current in grid_days:

        days_from_start = (
            current - grid_start
        ).days

        week_index = (
            days_from_start // 7
        )

        weekday = (
            days_from_start % 7
        )

        x = (
            start_x
            + week_index
            * (
                cell_size + gap
            )
        )

        y = (
            start_y
            + weekday
            * (
                cell_size + gap
            )
        )

        date_string = (
            current.isoformat()
        )

        day = contribution_lookup.get(
            date_string
        )

        if day:

            count = day[
                "contributionCount"
            ]

            opacity = get_cell_opacity(
                day[
                    "contributionLevel"
                ]
            )

        else:

            count = 0
            opacity = 0.08

        output.append(
            f'''
            <rect
                x="{x}"
                y="{y}"
                width="{cell_size}"
                height="{cell_size}"
                rx="3"
                fill="#f0f6fc"
                opacity="{opacity}"
            >
                <title>
                    {escape_svg(date_string)}
                    ·
                    {count}
                    contributions
                </title>
            </rect>
            '''
        )

    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    output.append(
        '''
        <line
            x1="70"
            y1="275"
            x2="830"
            y2="275"
            stroke="#21262d"
            stroke-width="1"
        />

        <text
            x="70"
            y="304"
            fill="#8b949e"
            font-size="9"
            font-family="monospace"
        >
            LESS
        </text>

        <rect
            x="110"
            y="294"
            width="12"
            height="12"
            rx="3"
            fill="#f0f6fc"
            opacity="0.08"
        />

        <rect
            x="130"
            y="294"
            width="12"
            height="12"
            rx="3"
            fill="#f0f6fc"
            opacity="0.25"
        />

        <rect
            x="150"
            y="294"
            width="12"
            height="12"
            rx="3"
            fill="#f0f6fc"
            opacity="0.45"
        />

        <rect
            x="170"
            y="294"
            width="12"
            height="12"
            rx="3"
            fill="#f0f6fc"
            opacity="0.70"
        />

        <rect
            x="190"
            y="294"
            width="12"
            height="12"
            rx="3"
            fill="#f0f6fc"
            opacity="1"
        />

        <text
            x="214"
            y="304"
            fill="#8b949e"
            font-size="9"
            font-family="monospace"
        >
            MORE
        </text>

        <text
            x="830"
            y="304"
            fill="#484f58"
            font-size="9"
            font-family="monospace"
            text-anchor="end"
        >
            github.com/sxmtryhard
        </text>

        </svg>
        '''
    )

    return "\n".join(output)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("========================================")
    print("     SXMTRYHARD PROFILE GENERATOR")
    print("========================================")
    print()

    print("Connecting to GitHub...")

    profile = get_profile()

    repositories = get_repositories()

    print("✓ GitHub connection successful")

    print()
    print("Calculating languages...")

    languages = calculate_languages(
        repositories
    )

    print("✓ Languages calculated")

    print()
    print(
        f"Fetching {CURRENT_YEAR} contributions..."
    )

    calendar = get_contributions()

    print("✓ Contribution data received")

    print()
    print("Generating SVG files...")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    overview_svg = generate_overview_svg(
        profile,
        repositories,
        languages
    )

    activity_svg = generate_activity_svg(
        calendar
    )

    OVERVIEW_FILE.write_text(
        overview_svg,
        encoding="utf-8"
    )

    ACTIVITY_FILE.write_text(
        activity_svg,
        encoding="utf-8"
    )

    print()
    print(
        f"✓ Generated: {OVERVIEW_FILE}"
    )

    print(
        f"✓ Generated: {ACTIVITY_FILE}"
    )

    print()
    print("========================================")
    print("              COMPLETE")
    print("========================================")
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()