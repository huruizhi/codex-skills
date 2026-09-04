# WeChat Article Layout Usage

## Commands

Preview/local HTML only:

```bash
python3 ~/.codex/skills/wechat-article-layout/scripts/layout_article.py article.md \
  --theme tech-blue \
  --layout wide \
  --out article.wechat.html
```

Create draft JSON after images are uploaded:

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

Layout modes:

- `--layout wide` is the default. Use it for final WeChat drafts; it keeps mobile content wide and avoids nested side margins.
- `--layout boxed` restores the older card-style layout with outer padding, border, rounded corners, and shadow.

Override metadata:

```bash
python3 ~/.codex/skills/wechat-article-layout/scripts/layout_article.py article.md \
  --title "公众号标题" \
  --author "RZ" \
  --digest "128 字以内摘要" \
  --source-url "https://example.com/source" \
  --out article.wechat.html
```

List available styles:

```bash
python3 ~/.codex/skills/wechat-article-layout/scripts/layout_article.py --list-themes
```

## Publishing Handoff

1. Upload cover:

```bash
md2wechat upload_image cover.png --json
```

2. Upload inline images:

```bash
md2wechat upload_image inline-1.png --json
md2wechat upload_image inline-2.png --json
```

3. Write `image-map.json` using each uploaded WeChat URL.
4. Run layout with `--draft-json`.
5. Create draft:

```bash
md2wechat create_draft article.draft.json --json
```

## Output Contract

The script writes:

- HTML file from `--out`
- optional draft JSON from `--draft-json`
- summary JSON to stdout with metadata, image count, reference count, and output paths
