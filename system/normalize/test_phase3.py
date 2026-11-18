# system/normalize/test_phase3.py
import sys
from pathlib import Path

# Ensure project root (kykloi/) is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system.normalize.graph import (
    compute_relative_link,
    heal_markdown_links,
    parse_markdown_links,
    split_target_url,
)


def run_tests():
    print("[1/4] Testing URL splitting and stem extraction...")
    p1, s1 = split_target_url("../notes/matrix.md#eigenvalues")
    assert p1 == "../notes/matrix.md"
    assert s1 == "#eigenvalues"

    p2, s2 = split_target_url("image.png?raw=true")
    assert p2 == "image.png"
    assert s2 == "?raw=true"
    print("  -> URL splitting verified.")

    print("[2/4] Testing relative path mathematics...")
    # Same directory
    assert compute_relative_link("notes/intro.md", "notes/math.md") == "math.md"
    # Root to subfolder
    assert compute_relative_link("intro.md", "notes/math.md") == "notes/math.md"
    # Subfolder to root
    assert compute_relative_link("notes/math.md", "intro.md") == "../intro.md"
    # Deep cross-folder navigation
    assert (
        compute_relative_link("math/advanced/calculus.md", "media/diagrams/chart.svg")
        == "../../media/diagrams/chart.svg"
    )
    print("  -> Relative path calculations verified.")

    print("[3/4] Testing Markdown link extraction with code block isolation...")
    # Using \x60 escape sequence for backticks avoids markdown parser collisions
    fence = "\x60\x60\x60"
    sample_md = (
        "# Sample Document\n"
        "Here is a [Valid Link](../physics/energy.md) and an image ![Chart](../media/chart.png).\n"
        "\n"
        f"{fence}python\n"
        "# Link inside code block should be completely ignored\n"
        "[Ignored Code Link](ignored.md)\n"
        f"{fence}\n"
        "\n"
        "And an `inline [Ignored Link](ignored.md)` in backticks.\n"
        'Another [Valid Anchor Link](../chemistry/atom.md#protons "Atom Details").\n'
    )

    links = parse_markdown_links(sample_md, source_stem="sample-doc")
    assert len(links) == 3

    assert links[0].target_stem == "energy"
    assert links[0].line_number == 2
    assert links[0].is_image is False

    assert links[1].target_stem == "chart"
    assert links[1].line_number == 2
    assert links[1].is_image is True

    assert links[2].target_stem == "atom"
    assert links[2].line_number == 10
    assert links[2].suffix == "#protons"
    print("  -> Link extraction & code isolation verified.")

    print("[4/4] Testing content link healing across moves and renames...")
    sample_content = (
        "Check [Energy Conservation](../physics/energy.md#law) and "
        '![Diagram](../media/chart.png "Flow Diagram").'
    )

    # Scenario:
    # 1. 'energy' moved from 'physics/energy.md' to 'science/energy-conservation.md'
    # 2. 'chart' moved from 'media/chart.png' to 'assets/chart.png'
    stem_to_new_rel_path = {
        "energy": "science/energy-conservation.md",
        "chart": "assets/chart.png",
    }

    source_doc_path = "notes/overview.md"
    healed, count = heal_markdown_links(
        sample_content, source_doc_path, stem_to_new_rel_path
    )

    assert count == 2
    assert "../science/energy-conservation.md#law" in healed
    assert "../assets/chart.png" in healed
    assert '"Flow Diagram"' in healed  # Preserves title
    print("  -> Link healing and formatting preservation verified.")

    print("[SUCCESS] All Phase 3 graph and link healing tests verified.")


if __name__ == "__main__":
    run_tests()
