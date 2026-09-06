#!/usr/bin/env python3
"""Build the portfolio and blogs/*/main.typ into _site using Typst."""

import hashlib
import html
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"


def version(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def typst(*args):
    return subprocess.run(
        ["typst", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout


def post_row(post, number):
    title = html.escape(post["title"])
    published = html.escape(post["date"])
    description = html.escape(post["description"])
    summary = f"\n              <p>{description}</p>" if description else ""
    return f'''          <li class="post" data-reveal>
            <span class="post-number" aria-hidden="true">{number:02d}</span>
            <article>
              <div class="post-meta"><time datetime="{published}">{published}</time></div>
              <h3><a href="blogs/{post['slug']}/">{title}</a></h3>{summary}
            </article>
          </li>'''


def build():
    if not shutil.which("typst"):
        raise ValueError("Typst is required. Install Typst 0.14.2, then run this command again.")

    source = (ROOT / "index.html").read_text()
    marker = "          <!-- BLOG_POSTS -->"
    if source.count(marker) != 1:
        raise ValueError("index.html must contain exactly one BLOG_POSTS marker")

    style_version = version(ROOT / "style.css")
    common = ["--features", "html", "--root", str(ROOT), "--input", f"style-version={style_version}"]

    # Keep the previous preview intact if any article fails to compile.
    with tempfile.TemporaryDirectory(prefix=".site-build-", dir=ROOT) as temporary:
        site = Path(temporary) / "site"
        site.mkdir()
        posts = []
        for main in sorted((ROOT / "blogs").glob("*/main.typ")):
            slug = main.parent.name
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
                raise ValueError(f"Invalid blog folder {slug!r}; use lowercase letters, numbers, and hyphens")
            post = json.loads(typst("query", *common, "--target", "html", str(main),
                                    "<blog-post>", "--field", "value", "--one"))
            if not isinstance(post, dict) or any(
                not isinstance(post.get(key), str) for key in ("title", "date", "description")
            ):
                raise ValueError(f"{main.relative_to(ROOT)}: title, date, and description must be strings")
            if not post["title"].strip():
                raise ValueError(f"{main.relative_to(ROOT)}: title cannot be empty")
            if date.fromisoformat(post["date"]).isoformat() != post["date"]:
                raise ValueError(f"{main.relative_to(ROOT)}: use YYYY-MM-DD for the date")
            post["slug"] = slug
            destination = site / "blogs" / slug / "index.html"
            destination.parent.mkdir(parents=True)
            typst("compile", *common, str(main), str(destination))
            posts.append(post)

        posts.sort(key=lambda post: post["date"], reverse=True)
        source = source.replace(marker, "\n".join(post_row(post, n) for n, post in enumerate(posts, 1)))
        for asset in ("style.css", "script.js"):
            source = re.sub(
                re.escape(asset) + r"(?:\?v=[a-f0-9]+)?(?=\")",
                f"{asset}?v={version(ROOT / asset)}", source,
            )
            shutil.copy2(ROOT / asset, site / asset)
        (site / "index.html").write_text(source)
        shutil.copytree(ROOT / "assets", site / "assets")
        (site / ".nojekyll").touch()

        if OUTPUT.exists():
            shutil.rmtree(OUTPUT)
        shutil.move(str(site), OUTPUT)

    print(f"Built {len(posts)} post(s) → {OUTPUT}")
    print(f"Open the generated page: {OUTPUT / 'index.html'}")
    print("The root index.html is a template; this command only builds the site.")
    print("To preview over HTTP, run:")
    print(f"  python3 -m http.server 8001 --bind 127.0.0.1 --directory {shlex.quote(str(OUTPUT))}")
    print("Then open http://127.0.0.1:8001/#blog (or refresh it if already running).")


if __name__ == "__main__":
    try:
        build()
    except subprocess.CalledProcessError as error:
        sys.exit(error.stderr.strip() or "Typst compilation failed")
    except (ValueError, OSError) as error:
        sys.exit(str(error))
