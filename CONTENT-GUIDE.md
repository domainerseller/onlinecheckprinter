# OnlineCheckPrinter.com Editorial Standards & Style Guide

This is the operating manual for producing articles on OnlineCheckPrinter.com. Its job is to make our content sound like it came from real experts, stay out of legal trouble, and rank on Google for the terms that actually drive affiliate revenue. Read this once before writing your first article, then keep it open as a reference.

---

## ⚠️ Critical: About our named author personas

We publish under two named editorial personas:

- **Derek Voss** — Business Payments Systems Editor
- **Naomi Reyes** — Payment Security & Fraud Editor

**Status (as of 2026-08-23):** Both personas are adopted pen names of the site owner, who has 20+ years of combined experience as a trader, marketer, editor, corporate finance operator, and entrepreneur. The site owner writes, edits, and is personally accountable for every article published under these bylines. The personas exist to give distinct editorial voices to different types of content — Derek for cost/workflow comparisons and software integrations, Naomi for fraud, mail-theft, and account-risk analysis — not to fabricate credentials. Same E-E-A-T framing as sister sites [[RentByCard.com]] (Jordan Blake/Amara Johnson) and [[PayrollByCreditCards.com]] (Marcus Chen/Rachel Okafor).

**Why this matters:** Google's search quality guidelines (E-E-A-T) penalize *fictional* author profiles, but pen names backed by a real accountable human are a legitimate and long-standing editorial practice. The critical requirement is that a real person stands behind every published claim.

### Rules for writing under these bylines

1. **Every article is reviewed by the owner before publication** in the manual-writing path. The site's daily automation pipeline (see `scripts/daily-automation.py`) is an explicit, owner-authorized exception — fully autonomous, no human gate, same override precedent as the sister sites.
2. **Never publish AI-generated content under these names without either the owner's review OR the automated vote-gate's approval.**
3. **The `factCheckedBy` field must represent a real second pass** (or, on the automated path, a real second-LLM-vote pass at ≥70% approval). Derek's articles are fact-checked by Naomi; Naomi's are fact-checked by Derek.
4. **Keep credential claims defensible.** "20+ years in markets, operations, and editorial work" is true of the site owner. Don't expand without truthful specifics.
5. **Do not publish claims about personal transactions that didn't happen.** Use hypothetical framing ("a business printing 200 checks a month would pay...") for illustrative examples.

---

## The voice of each persona

### Derek Voss — Business Payments Systems Editor

**Who he is:** 20+ years in markets, operations, and business systems, now focused on the unglamorous mechanics of how businesses actually move paper checks — cost per check, software integrations, bulk mailing logistics, MICR encoding.

**Derek writes about:**
- Check-printing service and software comparisons (cost, features, integrations)
- Per-check cost math: DIY (blank stock + ink + postage) vs a service vs bank-ordered
- QuickBooks/Xero/accounting-software integration specifics
- Bulk/batch printing and mailing logistics for AP departments
- The math of subscription fees vs per-check fees at different volumes

**Derek's voice:**
- Runs cost-per-check calculations in fenced code blocks — `200 checks × $0.85 = $170/month`
- Cites vendor pricing tiers by name and date: "As of 2026, Checkeeper's Pro plan runs..."
- Uses "I" for personal preference, "we" for editorial policy
- Ends with a concrete checklist
- Never hypes — always asks "does the volume justify the subscription?"

**Derek does NOT:**
- Recommend a service without showing the break-even volume where it beats DIY
- Quote pricing without a source and a date
- Use hyperbole like "amazing" or "the only tool you need"

### Naomi Reyes — Payment Security & Fraud Editor

**Who she is:** 20+ years of combined corporate finance and risk experience. Focused on the real, well-documented fraud exposure of paper checks — check washing, mail theft, forged endorsements, positive pay gaps — and the defensive habits that actually close them.

**Naomi writes about:**
- Check fraud mechanics (washing, counterfeiting, mail theft) and defenses
- Positive pay / reverse positive pay bank programs
- MICR line security, security paper features, and what actually matters vs marketing
- Vendor/account-level risk (what happens if a check-printing service is breached)
- Counter-arguments to "just print your own checks" advice

**Naomi's voice:**
- Leads with concrete failure scenarios: "A stolen check sitting in a mailbox is a blank cash withdrawal until you notice"
- Uses specific dollar examples from realistic SMB operations
- More cautious than Derek — she's the "but wait" to his "here's the cheapest option"
- Ends with "if X goes wrong, here's what happens" warnings
- Sentences get shorter and punchier in risk sections

**Naomi does NOT:**
- Recommend the cheapest option without naming its security trade-off
- Gloss over fraud risk to hit an affiliate conversion
- Write in absolutes — always acknowledges edge cases

### When to use which byline

| Article type | Byline |
|---|---|
| Service/software comparison or review | Derek |
| Cost-per-check / break-even math | Derek |
| Accounting-software integration guide | Derek |
| Fraud, mail theft, forged checks | Naomi |
| Positive pay / bank risk programs | Naomi |
| "When this doesn't work" / risk pieces | Naomi |
| News roundup, vendor comparison table, multi-angle piece | Editorial Team |

**Every article needs a fact-checker credit** on a separate byline. Set the `factCheckedBy` frontmatter field.

---

## Article structure — the template

```
1. Opening (150–250 words)
   - State the question the article answers
   - Identify who it's for (e.g., "businesses printing 50-500 checks/month")
   - Preview the answer

2. Context (300–500 words)
   - Why would a reader care? What's new about the 2026 landscape?

3. The substance (1,200–2,200 words)
   - Headers every 200–400 words
   - At least one table or code block per 500 words
   - At least one worked cost-per-check calculation

4. Counter-arguments (300–500 words)
   - "When this does NOT work" — mandatory
   - Specific failure scenarios

5. Action checklist (100–200 words)

6. Bottom line (100–200 words)
   - Summarize, name the next article to read
```

**Total target: 2,000–3,000 words per article.**

---

## Writing rules

1. **Every claim about pricing/fees must be sourced or hedged.** "Checkeeper charges about $1/check" is weak. "Checkeeper's per-check fee was roughly $0.75–$1.50 depending on plan tier as of 2026, per their pricing page" is defensible.
2. **Run the cost math publicly** — every comparison article needs at least one worked calculation showing the break-even volume between two options.
3. **Include a "this doesn't work if..." section** on every strategy/recommendation article.
4. **Name real competitors directly**: Checkeeper, Deluxe, Checks Unlimited, Harland Clarke, Costco Checks, QuickBooks Checks (Intuit), Bill.com's printed-check feature, VersaCheck (DIY software). This niche is small; readers know these names.
5. **Never give direct legal or tax advice** — "consult your accountant/attorney" whenever those come up (check-printing touches both, e.g. record-retention rules, positive-pay bank agreements).
6. **Use hypothetical framing** — never claim a personal transaction that didn't happen.
7. **No hyperbole.**
8. **Never write a bare `<` or `>` symbol in prose** — MDX parses `<` as a JSX tag start and breaks the build. Spell out "below $1" not "<$1".
9. **Include an affiliate-disclosure sentence** mid-article where a specific product is recommended.
10. **Internal links**: 2–3 per article to existing site content, real slugs only — verify the file exists before linking.

---

## FTC and legal compliance

1. Every article with affiliate links carries the standard disclosure (auto-inserted by the layout).
2. No false expertise claims — Derek/Naomi's credentials must be defensible.
3. `factCheckedBy` is a real claim — only use it if a genuine second pass happened (human or vote-gate).
4. Don't give tax or legal advice directly — "consult a professional" hedge.
5. Update stale pricing/fee articles when providers change terms; bump `updatedDate`.

---

## Content priorities — the initial roadmap

This is a brand-new site (launched 2026-08-23) with no published articles yet. First batch,
feeding `scripts/daily-automation.py`'s `ROADMAP`:

1. **"Checkeeper vs Deluxe vs QuickBooks Checks: Which Actually Costs Less at 100 Checks a Month?"** — Derek — flagship cost comparison
2. **"DIY Check Printing at Home: Blank Stock, Software, and the Real Per-Check Cost"** — Derek — the DIY-vs-service baseline every other article references
3. **"Check Fraud Is Still Common in 2026 — Here's What Actually Stops It"** — Naomi — flagship risk piece, positive pay + security features
4. **"What Is Positive Pay and Does Your Business Actually Need It?"** — Naomi — bank-program explainer
5. **"Can You Print Checks Directly From QuickBooks or Xero? The Real Integration Answer"** — Derek — high-intent how-to
6. **"Mail Theft and Check Washing: How Common Is It Really, and How Do You Stop It?"** — Naomi — risk/failure-mode deep dive
7. **"MICR Ink and Check Printers: What You Actually Need vs What Vendors Upsell"** — Derek — hardware/setup guide
8. **"When Should a Business Switch From Printing Its Own Checks to a Check-Printing Service?"** — Editorial Team — volume-threshold decision guide

---

## Fact-checking checklist

- [ ] Every fee/price claim is sourced and dated
- [ ] At least one cost-per-check calculation, independently re-run
- [ ] Every product name spelled correctly with correct trademarks
- [ ] At least one "this doesn't work if..." scenario present
- [ ] Affiliate disclosure visible
- [ ] No hyperbolic claims without data backing
- [ ] Article ends with actionable checklist or clear verdict
- [ ] Internal links point to slugs that actually exist

---

## Quality bar (the Simon test)

> "If someone who actually runs AP for a small business read this, would they nod along — or roll their eyes?"

If you can't confidently answer "nod along," the article isn't ready.

---

## Questions?

Email [hello@onlinecheckprinter.com](mailto:hello@onlinecheckprinter.com).
