---
name: wechat-article-layout
description: Locally typeset Markdown articles into WeChat Official Account compatible HTML and optional draft JSON content. Use when the user asks for 微信排版, 公众号排版, local WeChat HTML layout, article preview HTML, reusable公众号模板, or wants to avoid remote md2wechat conversion APIs while still publishing through md2wechat upload_image/create_draft.
---

# WeChat Article Layout

Use this skill to convert a Markdown article into local WeChat-compatible HTML. It does **not** upload or publish by itself; use `md2wechat upload_image` and `md2wechat create_draft` after layout when publishing is needed.

## Quick Start

Run the bundled script:

```bash
python3 ~/.codex/skills/wechat-article-layout/scripts/layout_article.py article.md \
  --theme tech-blue \
  --layout wide \
  --out article.wechat.html
```

To also create a WeChat draft JSON after image upload:

```bash
python3 ~/.codex/skills/wechat-article-layout/scripts/layout_article.py article.md \
  --theme tech-blue \
  --layout wide \
  --out article.wechat.html \
  --draft-json article.draft.json \
  --thumb-media-id "$COVER_MEDIA_ID" \
  --cover-url "$COVER_URL" \
  --image-map image-map.json
```

`image-map.json` maps Markdown image paths to uploaded WeChat URLs:

```json
{
  "imgs/inline-1.png": "http://mmbiz.qpic.cn/...",
  "/absolute/path/inline-2.png": "http://mmbiz.qpic.cn/..."
}
```

## Workflow

1. Prepare the article Markdown with frontmatter when possible:
   - `title`
   - `author`
   - `digest` or `summary`
   - `source_url`
2. Generate cover and inline illustrations before layout.
3. Run `layout_article.py` locally.
4. Inspect the output HTML for image count, title, digest, and references.
5. For publishing, upload images with `md2wechat upload_image`, rerun layout with `--image-map`, then call `md2wechat create_draft`.

## Theme Choice

List themes:

```bash
python3 ~/.codex/skills/wechat-article-layout/scripts/layout_article.py --list-themes
```

Supported themes:

- `tech-blue`: default for AI, developer tools, cloud, infra, business tech.
- `clean-news`: neutral news article with restrained typography.
- `deep-analysis`: denser analytical article with stronger section styling.
- `product-review`: product/tool recommendation article.
- `ai-dark`: dark AI/frontier look for model launches and Agent topics.
- `business-gold`: capital, cloud, investment, business-model analysis.
- `startup-orange`: startup/product-launch style.
- `knowledge-green`: explainers, tutorials, and methodology.
- `minimal-gray`: low-decoration engineering notes.
- `magazine-red`: opinion, critique, risk, and security.

Default to `tech-blue` for technology公众号文章.
Use `business-gold` for financing/capital/cloud-contract analysis.
Use `ai-dark` only when a darker visual identity is clearly desired.

## Rules

- Keep the skill local-first. Do not call remote conversion APIs from this skill.
- Keep publishing separate. This skill creates HTML/draft JSON only; `md2wechat` handles uploads and drafts.
- Default to `--layout wide` for mobile WeChat reading. `wide` removes the outer card/border/padding because the WeChat editor already adds its own mobile margins.
- Use `--layout boxed` only for previews, desktop screenshots, or when the user explicitly wants a card-style article body.
- Prefer frontmatter metadata over inferred metadata.
- If Markdown links point to external sources, convert them to numbered references by default and append a `参考来源` section.
- Preserve local image paths in preview HTML; replace them only when `--image-map` is provided.
- Use `--no-link-references` only when the user explicitly wants inline links preserved.

## Script Reference

See [references/usage.md](references/usage.md) for supported arguments and publishing handoff examples.
See [references/themes.md](references/themes.md) for theme selection guidance.
