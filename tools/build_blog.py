#!/usr/bin/env python3
"""Builds the Duerr Imports blog from Markdown files.

Write a post:  content/blog/my-post-slug.md  (front matter at the top, see the starter posts)
Then run, from the site folder:  python3 tools/build_blog.py

It writes:
  blog/index.html                 the list of posts
  blog/<slug>/index.html          one page per post
  blog/feed.xml                   RSS feed
  and refreshes the "From the blog" list on the homepage (index.html).

Posts with `draft: true` are skipped. No installs needed (standard Python 3 only).
"""
import datetime as dt
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "blog")
OUT = os.path.join(ROOT, "blog")
SITE = "https://www.duerrimports.com"
e = html.escape


# ---------------------------------------------------------------- Markdown
def inline(t):
    t = e(t, quote=False)
    t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1" loading="lazy">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}"'
               + (' rel="noopener"' if m.group(2).startswith("http") else "") + f">{m.group(1)}</a>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def markdown(src):
    out, para, lst = [], [], None

    def flush():
        nonlocal para, lst
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            lst = None

    for raw in src.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush(); continue
        m = re.match(r"^(#{2,4})\s+(.*)", line)
        if m:
            flush()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            continue
        m = re.match(r"^\s*([-*]|\d+\.)\s+(.*)", line)
        if m:
            if para:
                flush()
            tag = "ol" if m.group(1)[0].isdigit() else "ul"
            if not lst or lst[0] != tag:
                flush(); lst = (tag, [])
            lst[1].append(m.group(2)); continue
        if line.startswith(">"):
            flush(); out.append(f"<blockquote><p>{inline(line.lstrip('> '))}</p></blockquote>"); continue
        if lst:
            flush()
        para.append(line.strip())
    flush()
    return "\n".join(out)


def read_post(path):
    text = open(path, encoding="utf-8").read()
    meta, body = {}, text
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if m:
        for ln in m.group(1).splitlines():
            if ":" in ln:
                k, v = ln.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        body = m.group(2)
    slug = os.path.splitext(os.path.basename(path))[0]
    date = dt.date.fromisoformat(meta.get("date", dt.date.today().isoformat()))
    words = len(re.findall(r"\w+", body))
    return {
        "slug": slug, "title": meta.get("title", slug), "date": date,
        "summary": meta.get("summary", ""), "author": meta.get("author", "Duerr Imports"),
        "tag": meta.get("tag", ""), "draft": meta.get("draft", "false").lower() == "true",
        "html": markdown(body), "minutes": max(1, round(words / 220)),
    }


def nice(d):
    return d.strftime("%B %-d, %Y")


# ---------------------------------------------------------------- Page shell
def shell(title, desc, path, body, extra_head=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/img/logo-large.jpg">
<meta name="theme-color" content="#111111">
<link rel="icon" href="/assets/img/favicon.png" type="image/png">
<link rel="alternate" type="application/rss+xml" title="Duerr Imports blog" href="/blog/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
<link rel="stylesheet" href="/blog.css">
{extra_head}
</head>
<body class="blog-page">
<a class="skip" href="#main">Skip to content</a>
<header class="bar" data-field="night">
  <a class="mark" href="/" aria-label="Duerr Imports, home">
    <img class="mark-logo" src="/assets/img/logo.jpg" alt="" width="48" height="46">
    <span class="mark-word">Duerr <span>Imports</span></span>
  </a>
  <nav aria-label="Main">
    <a href="/#real-estate">Real estate</a>
    <a href="/#health">Health</a>
    <a href="/#imports">Imports</a>
    <a href="/blog/"{' aria-current="page"' if path == '/blog/' else ''}>Blog</a>
  </nav>
  <a class="btn btn-small" href="/#contact">Contact</a>
</header>
<main id="main">
{body}
</main>
<footer class="field night foot blog-foot">
  <div class="wrap foot-row">
    <p>© {dt.date.today().year} Duerr Imports, LLC · 3315 W. McKay Ave., Tampa, FL 33609</p>
    <p><a href="/blog/feed.xml">RSS feed</a> · <a href="mailto:contact@duerrimports.com">contact@duerrimports.com</a></p>
  </div>
</footer>
</body>
</html>
"""


def build():
    posts = [read_post(os.path.join(SRC, f)) for f in sorted(os.listdir(SRC)) if f.endswith(".md")]
    posts = sorted([p for p in posts if not p["draft"]], key=lambda p: p["date"], reverse=True)
    os.makedirs(OUT, exist_ok=True)

    # Index
    rows = "\n".join(f"""    <li class="post-row">
      <a href="/blog/{p['slug']}/">
        <span class="post-meta"><time datetime="{p['date']}">{nice(p['date'])}</time>{' · ' + e(p['tag']) if p['tag'] else ''}</span>
        <span class="post-title">{e(p['title'])}</span>
        <span class="post-sum">{e(p['summary'])}</span>
      </a>
    </li>""" for p in posts) or '    <li class="post-row"><p>No posts yet.</p></li>'
    body = f"""<section class="field night blog-head" aria-labelledby="blog-h">
  <div class="wrap blog-head-grid">
    <h1 id="blog-h">Blog</h1>
    <p class="intro">News and notes from Duerr Imports and the companies in the group.</p>
  </div>
</section>
<section class="blog-list" aria-label="Posts">
  <ul class="wrap posts">
{rows}
  </ul>
</section>"""
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
        shell("Blog | Duerr Imports", "News and notes from Duerr Imports, a US holding group, and its companies.", "/blog/", body))

    # Posts
    for i, p in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        nav = ""
        if older or newer:
            nav = '<nav class="post-nav" aria-label="More posts">' + \
                (f'<a class="prev" href="/blog/{older["slug"]}/"><span>Older</span>{e(older["title"])}</a>' if older else "<span></span>") + \
                (f'<a class="next" href="/blog/{newer["slug"]}/"><span>Newer</span>{e(newer["title"])}</a>' if newer else "") + "</nav>"
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["summary"],
              "datePublished": p["date"].isoformat(), "author": {"@type": "Organization", "name": p["author"]},
              "publisher": {"@type": "Organization", "name": "Duerr Imports, LLC",
                            "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/logo-large.jpg"}},
              "mainEntityOfPage": f"{SITE}/blog/{p['slug']}/"}
        body = f"""<article class="post">
  <header class="post-head">
    <div class="wrap">
      <p class="crumbs"><a href="/blog/">Blog</a></p>
      <h1>{e(p['title'])}</h1>
      <p class="post-standfirst">{e(p['summary'])}</p>
      <p class="post-meta"><time datetime="{p['date']}">{nice(p['date'])}</time> · {e(p['author'])} · {p['minutes']} min read</p>
    </div>
  </header>
  <div class="wrap post-body">
{p['html']}
  </div>
  <div class="wrap">{nav}</div>
</article>"""
        d = os.path.join(OUT, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
            shell(f"{p['title']} | Duerr Imports", p["summary"], f"/blog/{p['slug']}/", body,
                  f'<meta property="og:type" content="article">\n<script type="application/ld+json">{json.dumps(ld)}</script>'))

    # RSS
    items = "".join(f"""
  <item>
    <title>{e(p['title'])}</title>
    <link>{SITE}/blog/{p['slug']}/</link>
    <guid>{SITE}/blog/{p['slug']}/</guid>
    <pubDate>{dt.datetime.combine(p['date'], dt.time(12)).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
    <description>{e(p['summary'])}</description>
  </item>""" for p in posts)
    open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8").write(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Duerr Imports blog</title>
  <link>{SITE}/blog/</link>
  <description>News and notes from Duerr Imports and the companies in the group.</description>{items}
</channel>
</rss>
""")

    # Sitemap: homepage, blog index and every post
    urls = [(SITE + "/", dt.date.today()), (SITE + "/blog/", posts[0]["date"] if posts else dt.date.today())]
    urls += [(f"{SITE}/blog/{p['slug']}/", p["date"]) for p in posts]
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{d.isoformat()}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")

    # Homepage teaser: replace whatever sits between the markers
    home = os.path.join(ROOT, "index.html")
    s = open(home, encoding="utf-8").read()
    latest = "\n".join(f"""        <li class="post-row" data-rise>
          <a href="/blog/{p['slug']}/">
            <span class="post-meta"><time datetime="{p['date']}">{nice(p['date'])}</time></span>
            <span class="post-title">{e(p['title'])}</span>
            <span class="post-sum">{e(p['summary'])}</span>
          </a>
        </li>""" for p in posts[:3])
    s = re.sub(r"(<!-- blog:latest -->).*?(<!-- /blog:latest -->)", lambda m: m.group(1) + "\n" + latest + "\n        " + m.group(2), s, flags=re.S)
    open(home, "w", encoding="utf-8").write(s)
    print(f"Built {len(posts)} post(s).")


if __name__ == "__main__":
    build()
