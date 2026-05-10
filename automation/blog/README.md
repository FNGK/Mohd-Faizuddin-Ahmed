# Blog Automation (Approval Gate)

This pipeline generates SEO blog drafts twice per week and requires manual approval before publication.

## Pipeline Stages

1. `trend_collector.py`
   - Collects trend headlines from trusted SEO feeds.
   - Writes `automation/blog/data/trends.json`.

2. `keyword_planner.py`
   - Converts trend signals into keyword and topic ideas.
   - Writes `automation/blog/data/keyword_plan.json`.

3. `draft_generator.py`
   - Generates markdown drafts in `blog/drafts/`.
   - Every draft is created with `approved: false`.

4. `publish_validator.py`
   - Validates editorial and SEO quality rules.
   - With `--publish`, converts approved drafts into HTML in `blog/posts/` and updates `blog/index.html`.

## Quality Checks Enforced

- Required metadata and frontmatter fields.
- At least 2 external sources.
- At least 3 internal links.
- At least 3 H2 sections.
- Minimum content length threshold.
- Manual approval (`approved: true`) required for publishing.

## Local Run

```bash
python -m pip install -r automation/blog/requirements.txt
python automation/blog/trend_collector.py
python automation/blog/keyword_planner.py
python automation/blog/draft_generator.py
python automation/blog/publish_validator.py
```

Publish approved drafts:

```bash
python automation/blog/publish_validator.py --publish
```

## Approval Workflow

1. Open a file in `blog/drafts/`.
2. Review and improve content quality.
3. Set `approved: true`.
4. Run publish validator with `--publish`.
5. Confirm post appears in `blog/posts/` and is listed on `blog/index.html`.
