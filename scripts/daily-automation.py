"""Daily automation for OnlineCheckPrinter.com.

Discovers a new article topic, drafts it, gets it voted on by every
configured LLM provider, and auto-publishes on a 70%+ approval vote.

Fully autonomous per owner's explicit instruction (2026-08-23) — no human
review step. This intentionally supersedes CONTENT-GUIDE.md's "owner
reviews every article before publication" / "never publish AI-generated
content under these names without line-by-line review" rules for this
automated path; those rules still apply to anything written by hand.
Ported from RentByCard.com / PayrollByCreditCards.com's identical pipeline
(same override precedent), adapted for this site's niche (check-printing
services comparison, not credit cards) and its Derek Voss / Naomi Reyes
personas.

Usage:
    python scripts/daily-automation.py
    python scripts/daily-automation.py --dry-run   # skip git commit/push
"""
import sys
import os
import re
import json
import argparse
import subprocess
import datetime
from pathlib import Path

# LLM-generated titles/text can contain non-ASCII characters (smart quotes,
# non-breaking hyphens); Windows' cp1252 console encoding crashes on those in
# a plain print(), which would kill the whole run mid-loop instead of just
# skipping one attempt. Force UTF-8 + line buffering so output always flushes.
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

sys.path.insert(0, str(Path(__file__).parent))
from llm_router import call_llm, PROVIDERS  # noqa: E402

ROOT = Path(__file__).parent.parent
ARTICLES_DIR = ROOT / 'src' / 'content' / 'articles'
DATA_DIR = ROOT / 'data'
LOG_DIR = ROOT / 'logs'
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / 'topic-history.json'
LOG_FILE = LOG_DIR / f'automation-{datetime.date.today().isoformat()}.log'

ALL_PROVIDERS = list(PROVIDERS.keys())
VOTE_THRESHOLD_PCT = 70

# Brand-new site (launched 2026-08-23), no articles published yet -- initial
# roadmap from CONTENT-GUIDE.md.
ROADMAP = [
    "Checkeeper vs Deluxe vs QuickBooks Checks: Which Actually Costs Less at 100 Checks a Month?",
    "DIY Check Printing at Home: Blank Stock, Software, and the Real Per-Check Cost",
    "Check Fraud Is Still Common in 2026 — Here's What Actually Stops It",
    "What Is Positive Pay and Does Your Business Actually Need It?",
    "Can You Print Checks Directly From QuickBooks or Xero? The Real Integration Answer",
    "Mail Theft and Check Washing: How Common Is It Really, and How Do You Stop It?",
    "MICR Ink and Check Printers: What You Actually Need vs What Vendors Upsell",
    "When Should a Business Switch From Printing Its Own Checks to a Check-Printing Service?",
]

VOICE_NOTES = {
    'derek-voss': (
        "Derek Voss's voice: math-first, skeptical of hype, runs cost-per-check "
        "and break-even calculations in fenced code blocks, cites vendor "
        "pricing by name and date, uses 'I' for personal preference and 'we' "
        "for editorial policy, ends with a concrete do-this/don't-do-that "
        "checklist, never recommends a service without showing the break-even "
        "volume where it beats the alternative."
    ),
    'naomi-reyes': (
        "Naomi Reyes's voice: leads with concrete fraud/failure scenarios and "
        "specific dollar examples from realistic SMB operations, cautious, "
        "always names the security trade-off of the cheaper option, never "
        "absolute, ends with an 'if X goes wrong, here's what happens' "
        "warning, sentences get shorter and punchier in risk sections."
    ),
    'editorial-team': (
        "Editorial Team voice: neutral, comparison-oriented, balanced, used "
        "for news roundups, service comparisons, and multi-author deep dives."
    ),
}


def log(msg):
    line = f'[{datetime.datetime.now().isoformat(timespec="seconds")}] {msg}'
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def extract_json(text):
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*\n', '', text)
    text = re.sub(r'\n```\s*$', '', text)
    m = re.search(r'\{.*\}', text, re.S)
    return m.group(0) if m else text


def load_existing_articles():
    items = []
    for f in ARTICLES_DIR.glob('*.mdx'):
        text = f.read_text(encoding='utf-8')
        m = re.search(r'^title:\s*"(.+?)"', text, re.M)
        items.append({'slug': f.stem, 'title': m.group(1) if m else f.stem})
    return items


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding='utf-8'))
    return {'published': [], 'rejected': []}


def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding='utf-8')


def slugify(title):
    s = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return s[:80]


def propose_topic(existing, history):
    existing_titles = '\n'.join(f'- {a["title"]}' for a in existing)
    rejected = '\n'.join(
        f'- {r["title"]}: {r["reason"]}' for r in history['rejected'][-20:]
    )
    roadmap_text = '\n'.join(f'{i+1}. "{t}"' for i, t in enumerate(ROADMAP))
    prompt = f"""You are a content strategist for OnlineCheckPrinter.com, a site comparing check-printing services and software for businesses (Checkeeper, Deluxe, Checks Unlimited, Harland Clarke, Costco Checks, QuickBooks Checks, Bill.com's printed-check feature, VersaCheck).

Existing articles already published (do NOT propose a duplicate or near-duplicate of any of these):
{existing_titles if existing_titles else '(none yet — this is a brand-new site)'}

Previously rejected topic ideas (avoid repeating these unless the reason no longer applies):
{rejected if rejected else '(none yet)'}

Content roadmap, in priority order — prefer one of these if not yet covered:
{roadmap_text}

Propose exactly ONE new article topic for today that is genuinely useful, not a duplicate, and fits this site's check-printing-services niche. Reply as strict JSON only, no markdown fences:
{{"title": "...", "angle": "1-2 sentence description of the specific angle/argument", "byline": "derek-voss|naomi-reyes|editorial-team", "tags": ["Guide", "..."]}}
"""
    r = call_llm(prompt, task='gen', json_mode=True, temperature=0.6, max_tokens=500)
    return json.loads(extract_json(r.text)), r.provider


def draft_article(topic, has_existing_articles):
    byline = topic.get('byline', 'editorial-team')
    if byline not in VOICE_NOTES:
        byline = 'editorial-team'
    fact_checker = {
        'derek-voss': 'naomi-reyes',
        'naomi-reyes': 'derek-voss',
        'editorial-team': 'derek-voss',
    }[byline]

    internal_links_rule = (
        "- Include 2-3 internal links to existing articles where genuinely relevant, using relative paths like /articles/<slug>."
        if has_existing_articles else
        "- This is one of the first articles on the site — there is nothing to internally link to yet. Do NOT invent or guess a slug for an internal link; skip internal linking entirely rather than link to something that doesn't exist."
    )

    prompt = f"""Write a full article for OnlineCheckPrinter.com in MDX format.

Topic: {topic['title']}
Angle: {topic.get('angle', '')}
Byline: {byline}
{VOICE_NOTES[byline]}

Follow this EXACT structure (from our CONTENT-GUIDE.md):
1. Opening (150-250 words) - state the question, identify the audience (e.g. "businesses printing 50-500 checks a month"), preview the answer, establish credibility in the first paragraph
2. Context (300-500 words) - why it matters, what's new about the 2026 landscape
3. Substance (1200-2200 words) - headers every 200-400 words, at least one table or code block per 500 words, specific numbers and named products, at least one worked cost-per-check calculation
4. Counter-arguments (300-500 words) - "when this does NOT work" section, mandatory, specific failure scenarios
5. Action checklist (100-200 words) - 4-6 concrete things to do, "before you start, confirm..." bullets
6. Bottom line (100-200 words) - summarize the core answer, name the next article to read

Target total length: 2000-3000 words.

Rules:
- Name real competitors directly where relevant: Checkeeper, Deluxe, Checks Unlimited, Harland Clarke, Costco Checks, QuickBooks Checks (Intuit), Bill.com, VersaCheck. This niche is small and readers know these names.
- Every price/fee/term claim must be sourced or hedged ("as of [date]," "per [provider]'s pricing page") — never invent precise numbers you're not confident about.
- Run the cost math publicly in at least one fenced code block, e.g.:
```
200 checks/month x $0.85 (service) = $170/month
200 checks/month x $0.06 (DIY stock+ink) + $29 software = $41/month
Break-even volume favors DIY until mailing/handling time is worth more than $129/month to you
```
- Include a "this doesn't work if..." failure-mode section — mandatory on every article.
- Never give direct tax or legal advice — use "consult your accountant/attorney" whenever those come up.
- Use hypothetical framing ("a business printing 200 checks a month would pay...") — never claim a personal transaction that didn't happen.
- No hyperbole ("amazing," "incredible deal," "can't-miss").
{internal_links_rule}
- Include one affiliate-disclosure sentence mid-article where a specific product is recommended: "This section contains affiliate links. If you apply through one, we may earn a commission. Our rankings are not affected by commission rates."
- Never write a bare `<` or `>` symbol in prose (e.g. "<20% APR" or ">$50"). MDX parses `<` as the start of a JSX tag and this breaks the build. Always spell comparisons out: "below 20% APR", "above $50".
- This article's pubDate is {datetime.date.today().isoformat()} — the current year is {datetime.date.today().year}. Any phrase describing "the current/today's/this year's landscape" must mean {datetime.date.today().year}, matching pubDate exactly. Do not write things like "as of 2024" or "in {datetime.date.today().year - 2}'s landscape" to describe the present — that contradicts pubDate and reads as a factual error. It's fine to name a specific PAST year for a real historical fact, just never use a past year to describe the present.
- The article MUST end with all 6 structure sections present, including a final "## Bottom Line" (or "## The Bottom Line") heading, and the last sentence must be a complete, properly punctuated sentence. Do not stop partway through a section.

Output ONLY the full MDX file content, starting with this exact frontmatter block (fill in title/description, keep the rest as given):
---
title: "..."
description: "..."
pubDate: {datetime.date.today().isoformat()}
author: "{byline}"
factCheckedBy: "{fact_checker}"
tags: {json.dumps(topic.get('tags', ['Guide']))}
---

(then the article body in Markdown)
"""
    r = call_llm(prompt, task='gen', temperature=0.5, max_tokens=10000)
    return r.text.strip(), r.provider


def clean_mdx(text):
    text = re.sub(r'^```(?:mdx|markdown)?\s*\n', '', text.strip())
    text = re.sub(r'\n```\s*$', '', text)
    text = text.strip() + '\n'
    # MDX parses a bare '<' as the start of a JSX tag - "<4%" or "<$50" in
    # prose breaks the build. These articles never use real JSX components,
    # so any '<' immediately followed by a digit or '$' is always prose that
    # needs escaping, never a real tag (which is always followed by a letter).
    text = re.sub(r'<(?=[\d$])', '&lt;', text)
    return text


def truncation_reason(mdx_text):
    """Cheap structural check for a cut-off draft (hit the token cap mid-article)
    -- catches it before spending a full vote round on something obviously
    incomplete. Returns a reason string if truncated, None if it looks whole."""
    if not re.search(r'^#{1,3}\s*(the\s+)?bottom line', mdx_text, re.I | re.M):
        return 'missing final "Bottom Line" section'
    tail = mdx_text.rstrip()
    if not re.search(r'[.!?"\')\]]\s*$', tail):
        return 'last line does not end in a complete sentence'
    return None


def vote_on_article(mdx_text):
    prompt = f"""You are an editorial reviewer for OnlineCheckPrinter.com, a site for small business owners comparing check-printing services and software. Review this DRAFT article and decide whether it's ready to publish as-is.

Reject if: it contains fabricated/suspiciously precise pricing numbers without hedging or a stated source, hyperbolic language, factual claims that seem wrong, missing a "when this does NOT work" failure-mode section, missing a worked cost-per-check calculation, direct tax/legal advice instead of "consult your accountant/attorney," poor structure, an internal link to an article that doesn't plausibly exist yet on a brand-new site, or is materially thin/generic.

Approve if: it's factually careful (hedged/sourced figures), matches the site's math-first/cautious tone, names real competitors (Checkeeper/Deluxe/Checks Unlimited/Harland Clarke/QuickBooks Checks/Bill.com) where relevant, has real structure including the failure-mode section and a cost example, and would not embarrass someone who actually runs AP for a small business (the "Simon test").

DRAFT ARTICLE:
---
{mdx_text[:6000]}
---

Reply as strict JSON only, no markdown fences: {{"publish": true or false, "reason": "one sentence"}}
"""
    votes = []
    for provider in ALL_PROVIDERS:
        if not os.environ.get(PROVIDERS[provider]['env_key']):
            continue
        try:
            r = call_llm(prompt, task='audit', prefer=[provider], json_mode=True,
                         temperature=0.0, max_tokens=800)
            verdict = json.loads(extract_json(r.text))
            votes.append({
                'provider': provider,
                'publish': bool(verdict.get('publish')),
                'reason': verdict.get('reason', ''),
            })
        except Exception as e:
            log(f'  vote skipped ({provider}): {e}')
    return votes


MAX_ATTEMPTS = 5  # retry with a fresh topic until one passes, capped to bound API spend


def attempt_one(existing, history, args, attempt_no):
    """One propose->draft->vote->publish cycle. Returns True if published."""
    try:
        topic, topic_provider = propose_topic(existing, history)
    except Exception as e:
        log(f'Topic proposal failed: {e}. Skipping attempt.')
        return False
    log(f'Proposed topic ({topic_provider}): {topic["title"]}')

    slug = slugify(topic['title'])
    dest = ARTICLES_DIR / f'{slug}.mdx'
    if dest.exists():
        log(f'Slug collision with existing file {dest.name}. Skipping attempt.')
        history['rejected'].append({
            'title': topic['title'], 'reason': 'slug collision with existing article',
            'date': datetime.date.today().isoformat(),
        })
        return False

    try:
        mdx_raw, draft_provider = draft_article(topic, bool(existing))
    except Exception as e:
        log(f'Drafting failed: {e}. Skipping attempt.')
        return False
    mdx_text = clean_mdx(mdx_raw)
    log(f'Drafted article via {draft_provider}, {len(mdx_text.split())} words')

    trunc_reason = truncation_reason(mdx_text)
    if trunc_reason:
        log(f'Draft looks truncated ({trunc_reason}) — skipping vote, not publishing.')
        drafts_dir = DATA_DIR / 'rejected-drafts'
        drafts_dir.mkdir(exist_ok=True)
        (drafts_dir / f'{slug}.mdx').write_text(mdx_text, encoding='utf-8')
        history['rejected'].append({
            'title': topic['title'], 'reason': f'truncated: {trunc_reason}',
            'date': datetime.date.today().isoformat(),
        })
        return False

    votes = vote_on_article(mdx_text)
    yes = sum(1 for v in votes if v['publish'])
    total = len(votes)
    pct = (yes / total * 100) if total else 0
    vote_summary = ', '.join(f"{v['provider']}:{'Y' if v['publish'] else 'N'}" for v in votes)
    log(f'Votes: {yes}/{total} publish ({pct:.0f}%) — {vote_summary}')

    if total == 0:
        log('No providers responded to vote. Skipping attempt.')
        return False

    if pct < VOTE_THRESHOLD_PCT:
        log(f'Vote failed threshold (needed {VOTE_THRESHOLD_PCT}%, got {pct:.0f}%) — not publishing.')
        drafts_dir = DATA_DIR / 'rejected-drafts'
        drafts_dir.mkdir(exist_ok=True)
        (drafts_dir / f'{slug}.mdx').write_text(mdx_text, encoding='utf-8')
        reasons = '; '.join(v['reason'] for v in votes if not v['publish'])[:300]
        history['rejected'].append({
            'title': topic['title'], 'reason': f'{yes}/{total} votes, {reasons}',
            'date': datetime.date.today().isoformat(),
        })
        return False

    dest.write_text(mdx_text, encoding='utf-8')
    log(f'Wrote {dest.relative_to(ROOT)}')

    build = subprocess.run('npm run build', cwd=ROOT, shell=True,
                           capture_output=True, text=True)
    if build.returncode != 0:
        log('Build FAILED after adding article — reverting, trying a different topic.')
        log((build.stdout[-2000:] + build.stderr[-2000:]))
        dest.unlink(missing_ok=True)
        history['rejected'].append({
            'title': topic['title'], 'reason': 'build failed',
            'date': datetime.date.today().isoformat(),
        })
        return False

    if args.dry_run:
        log('Dry run: build passed, skipping commit/push, removing test file.')
        dest.unlink(missing_ok=True)
    else:
        rel = str(dest.relative_to(ROOT))
        subprocess.run(['git', 'add', rel], cwd=ROOT, check=True)
        commit_msg = (
            f"content: add \"{topic['title']}\" (auto, {yes}/{total} LLM votes, attempt {attempt_no})\n\n"
            "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
        )
        subprocess.run(['git', 'commit', '-m', commit_msg], cwd=ROOT, check=True)
        subprocess.run(['git', 'push'], cwd=ROOT, check=True)
        log(f'Published and pushed: {topic["title"]}')

    history['published'].append({
        'title': topic['title'], 'slug': slug,
        'date': datetime.date.today().isoformat(), 'votes': f'{yes}/{total}',
        'dry_run': args.dry_run,
    })
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='skip git commit/push')
    args = ap.parse_args()

    log('=== Daily automation run start ===')
    existing = load_existing_articles()
    history = load_history()

    published = False
    for attempt_no in range(1, MAX_ATTEMPTS + 1):
        log(f'--- Attempt {attempt_no}/{MAX_ATTEMPTS} ---')
        published = attempt_one(existing, history, args, attempt_no)
        save_history(history)  # persist after every attempt, not just at the end
        if published:
            log(f'Published on attempt {attempt_no}/{MAX_ATTEMPTS}.')
            break

    if not published:
        log(f'Exhausted {MAX_ATTEMPTS} attempts without a passing article today. No publish.')

    log('=== Run complete ===')


if __name__ == '__main__':
    main()
