# Paper Quality And Metadata Rules

Use this reference for candidate screening, quality ranking, publication-status checks, and "含金量" explanations.

## Required Fields

Every candidate or deep-read paper must show:

- Publication date.
- Venue / journal / preprint status.
- Peer-review status.
- Quality judgment.
- Timeliness.
- Priority reason.
- Relation to the user's thesis section.
- Metadata source links.

## Priority Ranking

Use this quality order:

1. Top conference or authoritative journal.
2. Formal conference or journal paper.
3. Workshop, demo, short paper, or findings-style paper depending on venue context.
4. arXiv-only or technical report.

Default selection rule:

- Prefer recent formal papers from the last three years unless the user requests a historical or foundational review.
- Prefer papers directly related to the user's stated research topic and thesis section.
- Keep older papers only for classic theory, foundational scales, or key methods.

## Metadata Verification

Use official or primary sources when possible:

- Publisher or conference page.
- ACL Anthology.
- arXiv page for preprint version dates.
- DOI/Crossref/IEEE/ACM pages for final formal citation.

Never infer venue or peer-review status from the title alone. If status is unclear, label it as unverified and lower priority.

## Wording Rules

- For formal conference papers: say "正式会议论文" only after source verification.
- For arXiv-only papers: say "预印本，正式发表状态未核验" unless accepted status is verified.
- For user studies: distinguish perception, design insight, usability, and effectiveness evidence.
- For evaluator papers: distinguish LLM-as-judge, human benchmark, inter-annotator agreement, and gold standard.

## Public Default State

The public skill package does not ship a default candidate set. Candidate IDs, topics, and priority order must come from the user's vault, PDFs, or stated research topic. Use `check_paper_vault.py --profile author-demo` only when intentionally validating the original author demo vault.
