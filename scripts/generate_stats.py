import json
import urllib.request
from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = "sxmtryhard"

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "stats"

OUTPUT_FILE = OUTPUT_DIR / "overview.svg"


# ============================================================
# GITHUB API
# ============================================================

def github_request(url):

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "SXMTRYHARD-Profile-Stats"
        }
    )

    with urllib.request.urlopen(request) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


# ============================================================
# GET PROFILE
# ============================================================

def get_profile():

    return github_request(
        f"https://api.github.com/users/{USERNAME}"
    )


# ============================================================
# GET REPOSITORIES
# ============================================================

def get_repositories():

    return github_request(
        f"https://api.github.com/users/{USERNAME}/repos"
        "?per_page=100&sort=updated"
    )


# ============================================================
# ESCAPE SVG TEXT
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
# CALCULATE LANGUAGES
# ============================================================

def calculate_languages(repositories):

    languages = Counter()

    for repository in repositories:

        language = repository.get("language")

        if language:

            languages[language] += 1

    return languages


# ============================================================
# GENERATE LANGUAGE BARS
# ============================================================

def generate_language_bars(languages):

    if not languages:

        return """
        <text
            x="70"
            y="390"
            fill="#8b949e"
            font-size="14"
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

        percentage = (
            count / total
        )

        bar_width = int(
            percentage * 430
        )

        y = start_y + (
            index * 42
        )

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
# GENERATE SVG
# ============================================================

def generate_svg(
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

    repository_count = profile[
        "public_repos"
    ]

    followers = profile[
        "followers"
    ]

    language_bars = generate_language_bars(
        languages
    )

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="760"
    height="650"
    viewBox="0 0 760 650"
>

    <!-- ================================================= -->
    <!-- BACKGROUND                                        -->
    <!-- ================================================= -->

    <rect
        width="760"
        height="650"
        fill="transparent"
    />

    <!-- ================================================= -->
    <!-- HEADER                                            -->
    <!-- ================================================= -->

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


    <!-- ================================================= -->
    <!-- HEADER LINE                                       -->
    <!-- ================================================= -->

    <line
        x1="70"
        y1="170"
        x2="690"
        y2="170"
        stroke="#21262d"
        stroke-width="1"
    />


    <!-- ================================================= -->
    <!-- METRICS                                           -->
    <!-- ================================================= -->

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


    <!-- ================================================= -->
    <!-- DIVIDER                                           -->
    <!-- ================================================= -->

    <line
        x1="70"
        y1="275"
        x2="690"
        y2="275"
        stroke="#21262d"
        stroke-width="1"
    />


    <!-- ================================================= -->
    <!-- LANGUAGES                                         -->
    <!-- ================================================= -->

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


    <!-- ================================================= -->
    <!-- FOOTER                                            -->
    <!-- ================================================= -->

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
        PROFILE / {USERNAME.upper()}
    </text>

</svg>
'''

    return svg


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("========================================")
    print("      SXMTRYHARD SVG STAT GENERATOR")
    print("========================================")
    print()

    print("Connecting to GitHub...")

    profile = get_profile()

    repositories = get_repositories()

    print("✓ GitHub connection successful")
    print()

    print("Calculating statistics...")

    languages = calculate_languages(
        repositories
    )

    print("✓ Statistics calculated")
    print()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    svg = generate_svg(
        profile,
        repositories,
        languages
    )

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8"
    )

    print(
        f"✓ SVG generated: {OUTPUT_FILE}"
    )

    print()
    print("========================================")
    print("             COMPLETE")
    print("========================================")
    print()


if __name__ == "__main__":

    main()