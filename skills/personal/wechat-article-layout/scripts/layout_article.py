#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Iterable


THEMES = {
    "tech-blue": {
        "label": "科技蓝",
        "best_for": "AI、云计算、开发者工具、技术商业分析",
        "page_bg": "#f6f9fc",
        "card_bg": "#ffffff",
        "text": "#263241",
        "muted": "#728194",
        "accent": "#2f6fb2",
        "accent_soft": "#eaf3fb",
        "border": "#dbe6f2",
        "shadow": "rgba(28, 51, 84, 0.06)",
        "h2_style": "bar",
    },
    "clean-news": {
        "label": "清爽新闻",
        "best_for": "快讯、资讯汇总、客观新闻稿",
        "page_bg": "#fafafa",
        "card_bg": "#ffffff",
        "text": "#2b2b2b",
        "muted": "#767676",
        "accent": "#4a5568",
        "accent_soft": "#f1f3f5",
        "border": "#e5e7eb",
        "shadow": "rgba(17, 24, 39, 0.04)",
        "h2_style": "underline",
    },
    "deep-analysis": {
        "label": "深度分析",
        "best_for": "长文、行业判断、商业分析、趋势复盘",
        "page_bg": "#f7f6f2",
        "card_bg": "#fffdf8",
        "text": "#27313c",
        "muted": "#7a7368",
        "accent": "#8a5a2b",
        "accent_soft": "#f5ecdf",
        "border": "#eadfcc",
        "shadow": "rgba(91, 66, 32, 0.07)",
        "h2_style": "block",
    },
    "product-review": {
        "label": "产品评测",
        "best_for": "工具推荐、产品体验、App/开发者工具介绍",
        "page_bg": "#f7faf7",
        "card_bg": "#ffffff",
        "text": "#24312b",
        "muted": "#728078",
        "accent": "#2d7d5f",
        "accent_soft": "#eaf6f1",
        "border": "#d9ebe2",
        "shadow": "rgba(18, 79, 56, 0.06)",
        "h2_style": "pill",
    },
    "ai-dark": {
        "label": "AI 暗色",
        "best_for": "大模型、Agent、前沿技术、发布会解读",
        "page_bg": "#07111f",
        "card_bg": "#0d1b2e",
        "text": "#e6edf7",
        "muted": "#9fb0c5",
        "accent": "#38bdf8",
        "accent_soft": "#102a43",
        "border": "#1f3b57",
        "shadow": "rgba(0, 0, 0, 0.24)",
        "h2_style": "block",
    },
    "business-gold": {
        "label": "商业金",
        "best_for": "融资、财报、资本、云厂商、商业模式分析",
        "page_bg": "#f8f5ee",
        "card_bg": "#fffdf7",
        "text": "#2d2a24",
        "muted": "#80776a",
        "accent": "#b7791f",
        "accent_soft": "#f5ead2",
        "border": "#eadcc3",
        "shadow": "rgba(91, 66, 32, 0.07)",
        "h2_style": "underline",
    },
    "startup-orange": {
        "label": "创业橙",
        "best_for": "Product Hunt、创业产品、增长、工具新品",
        "page_bg": "#fff7ed",
        "card_bg": "#ffffff",
        "text": "#30261f",
        "muted": "#836b5c",
        "accent": "#f97316",
        "accent_soft": "#ffedd5",
        "border": "#fed7aa",
        "shadow": "rgba(154, 71, 18, 0.08)",
        "h2_style": "pill",
    },
    "knowledge-green": {
        "label": "知识绿",
        "best_for": "教程、方法论、知识科普、工作流拆解",
        "page_bg": "#f4fbf7",
        "card_bg": "#ffffff",
        "text": "#23312b",
        "muted": "#6f8177",
        "accent": "#16825d",
        "accent_soft": "#e8f6ef",
        "border": "#d4eadf",
        "shadow": "rgba(20, 91, 63, 0.06)",
        "h2_style": "bar",
    },
    "minimal-gray": {
        "label": "极简灰",
        "best_for": "短评、工程笔记、低装饰技术文章",
        "page_bg": "#ffffff",
        "card_bg": "#ffffff",
        "text": "#242424",
        "muted": "#737373",
        "accent": "#111827",
        "accent_soft": "#f5f5f5",
        "border": "#e5e5e5",
        "shadow": "rgba(0, 0, 0, 0.00)",
        "h2_style": "minimal",
    },
    "magazine-red": {
        "label": "杂志红",
        "best_for": "评论、批判、观点稿、风险和安全话题",
        "page_bg": "#fff7f7",
        "card_bg": "#ffffff",
        "text": "#2f2525",
        "muted": "#816d6d",
        "accent": "#b91c1c",
        "accent_soft": "#fee2e2",
        "border": "#fecaca",
        "shadow": "rgba(127, 29, 29, 0.06)",
        "h2_style": "block",
    },
}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip()
    body = text[end + 5 :].lstrip()
    meta: dict[str, str] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            current_key = key.strip()
            meta[current_key] = value.strip().strip("\"'")
        elif current_key:
            meta[current_key] += "\n" + line.strip()
    return meta, body


def split_blocks(markdown: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    in_fence = False
    for line in markdown.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            current.append(line)
            continue
        if not in_fence and not line.strip():
            if current:
                blocks.append("\n".join(current).strip())
                current = []
            continue
        current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    return blocks


class LinkCollector:
    def __init__(self, enabled: bool = True, accent: str = "#2f6fb2") -> None:
        self.enabled = enabled
        self.accent = accent
        self.refs: list[tuple[str, str]] = []
        self.index: dict[str, int] = {}

    def render(self, text: str) -> str:
        escaped = html.escape(text.strip())
        escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
        escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
        return re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", self._replace_link, escaped)

    def _replace_link(self, match: re.Match[str]) -> str:
        label, url = match.groups()
        if not self.enabled:
            return f'<a href="{html.escape(url)}">{label}</a>'
        idx = self.index.get(url)
        if idx is None:
            self.refs.append((label, url))
            idx = len(self.refs)
            self.index[url] = idx
        return f'{label}<sup style="color:{self.accent};">[{idx}]</sup>'


def list_themes() -> None:
    payload = [
        {
            "name": name,
            "label": theme["label"],
            "best_for": theme["best_for"],
            "h2_style": theme["h2_style"],
        }
        for name, theme in sorted(THEMES.items())
    ]
    print(json.dumps({"success": True, "themes": payload}, ensure_ascii=False, indent=2))


def h2_html(text: str, theme: dict[str, str], link_collector: LinkCollector) -> str:
    rendered = link_collector.render(text)
    style = theme.get("h2_style", "bar")
    if style == "pill":
        return (
            f'<h2 style="font-size:19px;line-height:1.45;margin:34px 0 14px;'
            f'padding:10px 14px;border-radius:8px;background:{theme["accent_soft"]};'
            f'color:{theme["text"]};font-weight:750;">{rendered}</h2>'
        )
    if style == "underline":
        return (
            f'<section style="margin:34px 0 18px;padding:0;clear:both;">'
            f'<h2 style="display:block;font-size:19px;line-height:1.55;margin:0 0 10px;'
            f'padding:0;color:{theme["text"]};font-weight:750;">{rendered}</h2>'
            f'<section style="display:block;height:3px;width:100%;background:{theme["border"]};'
            f'margin:0;border-radius:3px;line-height:0;font-size:0;overflow:hidden;">'
            f'<section style="display:block;height:3px;width:18%;background:{theme["accent"]};'
            f'margin:0;border-radius:3px;line-height:0;font-size:0;"></section></section></section>'
        )
    if style == "block":
        return (
            f'<h2 style="font-size:19px;line-height:1.45;margin:34px 0 14px;'
            f'padding:12px 14px;border-left:4px solid {theme["accent"]};'
            f'background:{theme["accent_soft"]};border-radius:8px;color:{theme["text"]};'
            f'font-weight:750;">{rendered}</h2>'
        )
    if style == "minimal":
        return (
            f'<h2 style="font-size:19px;line-height:1.45;margin:34px 0 14px;'
            f'color:{theme["text"]};font-weight:750;">{rendered}</h2>'
            f'<section style="width:42px;height:3px;background:{theme["accent"]};'
            f'margin:-6px 0 16px;border-radius:3px;"></section>'
        )
    return (
        f'<h2 style="font-size:19px;line-height:1.45;margin:34px 0 14px;'
        f'padding-left:12px;border-left:4px solid {theme["accent"]};'
        f'color:{theme["text"]};font-weight:700;">{rendered}</h2>'
    )


def normalize_image_src(src: str, article_path: Path, image_map: dict[str, str]) -> str:
    if src in image_map:
        return image_map[src]
    candidate = (article_path.parent / src).resolve()
    if str(candidate) in image_map:
        return image_map[str(candidate)]
    return src


def image_block(src: str, alt: str, theme: dict[str, str], link_collector: LinkCollector) -> str:
    caption = link_collector.render(alt) if alt else ""
    caption_html = (
        f'<p style="margin:8px 2px 0;color:{theme["muted"]};font-size:13px;'
        f'line-height:1.6;text-align:center;">{caption}</p>'
        if caption
        else ""
    )
    return (
        '<section style="margin:30px 0;">'
        f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" '
        'style="display:block;width:100%;max-width:100%;border-radius:10px;'
        f'box-shadow:0 10px 28px {theme["shadow"]};" />'
        f"{caption_html}</section>"
    )



def is_markdown_table(block: str) -> bool:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if len(lines) < 2:
        return False
    if not all(line.startswith("|") and line.endswith("|") for line in lines[:2]):
        return False
    cells = [cell.strip() for cell in lines[1].strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def table_html(block: str, theme: dict[str, str], link_collector: LinkCollector) -> str:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    headers = parse_table_row(lines[0])
    rows = [parse_table_row(line) for line in lines[2:]]
    col_count = len(headers)
    parts = [
        f'<section style="margin:18px 0 24px;overflow-x:auto;-webkit-overflow-scrolling:touch;">',
        f'<table style="width:100%;border-collapse:collapse;table-layout:auto;font-size:14px;line-height:1.55;color:{theme["text"]};">',
        '<thead><tr>',
    ]
    for header in headers:
        parts.append(
            f'<th style="padding:9px 8px;border:1px solid {theme["border"]};'
            f'background:{theme["accent_soft"]};color:{theme["text"]};font-weight:700;text-align:left;vertical-align:top;">'
            f'{link_collector.render(header)}</th>'
        )
    parts.append('</tr></thead><tbody>')
    for row in rows:
        padded = row + [""] * max(0, col_count - len(row))
        parts.append('<tr>')
        for cell in padded[:col_count]:
            parts.append(
                f'<td style="padding:9px 8px;border:1px solid {theme["border"]};'
                f'background:{theme["card_bg"]};vertical-align:top;word-break:break-word;">'
                f'{link_collector.render(cell)}</td>'
            )
        parts.append('</tr>')
    parts.append('</tbody></table></section>')
    return "\n".join(parts)

def parse_unordered_items(block: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for line in block.splitlines():
        if line.startswith("- "):
            if current:
                items.append(" ".join(current).strip())
            current = [line[2:].strip()]
        elif current and line.strip():
            current.append(line.strip())
    if current:
        items.append(" ".join(current).strip())
    return items


def parse_ordered_items(block: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for line in block.splitlines():
        match = re.match(r"^\d+\. (.+)$", line)
        if match:
            if current:
                items.append(" ".join(current).strip())
            current = [match.group(1).strip()]
        elif current and line.strip():
            current.append(line.strip())
    if current:
        items.append(" ".join(current).strip())
    return items


def text_list_html(
    items: list[str],
    theme: dict[str, str],
    link_collector: LinkCollector,
    ordered: bool = False,
) -> str:
    parts = [f'<section style="margin:4px 0 22px;color:{theme["text"]};">']
    for idx, item in enumerate(items, 1):
        marker = f"{idx}." if ordered else "&bull;"
        parts.append(
            f'<p style="margin:0 0 10px;padding-left:22px;text-indent:-22px;'
            f'color:{theme["text"]};line-height:1.78;">'
            f'<span style="color:{theme["accent"]};font-weight:700;">{marker}</span> '
            f'{link_collector.render(item)}</p>'
        )
    parts.append("</section>")
    return "\n".join(parts)


def parse_reference_link(item: str) -> tuple[str, str] | None:
    match = re.fullmatch(r"\[(.+?)\]\((https?://[^)]+)\)", item.strip())
    if match:
        return match.group(1), match.group(2)
    match = re.search(r"(https?://\S+)", item.strip())
    if match:
        url = match.group(1)
        label = item.replace(url, "").strip(" -:：")
        return label or url, url
    return None


def reference_list_html(items: list[str], theme: dict[str, str]) -> str:
    parts = [f'<section style="margin:4px 0 24px;color:{theme["text"]};">']
    for idx, item in enumerate(items, 1):
        parsed = parse_reference_link(item)
        if parsed:
            label, url = parsed
            title_html = (
                f'<a href="{html.escape(url)}" style="color:{theme["accent"]};'
                f'text-decoration:none;border-bottom:1px solid {theme["accent"]};">'
                f'{html.escape(label)}</a>'
            )
        else:
            title_html = html.escape(item)
        parts.append(
            f'<section style="margin:0 0 14px;padding:0;">'
            f'<p style="margin:0;color:{theme["text"]};font-size:15px;line-height:1.65;">'
            f'<span style="color:{theme["accent"]};font-weight:700;">[{idx}]</span> '
            f'{title_html}</p></section>'
        )
    parts.append("</section>")
    return "\n".join(parts)


def render_blocks(
    body: str,
    article_path: Path,
    theme: dict[str, str],
    image_map: dict[str, str],
    link_collector: LinkCollector,
) -> tuple[str, int]:
    parts: list[str] = []
    image_count = 0
    reference_mode = False

    for block in split_blocks(body):
        if block == "---":
            parts.append(f'<section style="height:1px;background:{theme["border"]};margin:30px 0;"></section>')
            continue
        if block.strip() in {"参考来源：", "参考来源:"}:
            reference_mode = True
            parts.append(
                f'<p style="margin:0 0 14px;color:{theme["text"]};font-weight:700;">'
                f'{html.escape(block.strip())}</p>'
            )
            continue
        if block.startswith("# "):
            parts.append(
                f'<h1 style="font-size:24px;line-height:1.35;margin:0 0 18px;'
                f'color:{theme["text"]};font-weight:750;">{link_collector.render(block[2:])}</h1>'
            )
            continue
        if block.startswith("## "):
            parts.append(h2_html(block[3:], theme, link_collector))
            continue
        if block.startswith("### "):
            parts.append(
                f'<h3 style="font-size:17px;line-height:1.45;margin:26px 0 12px;'
                f'color:{theme["accent"]};font-weight:700;">{link_collector.render(block[4:])}</h3>'
            )
            continue
        if block.startswith("```"):
            code = "\n".join(block.splitlines()[1:-1])
            parts.append(
                f'<pre style="margin:18px 0;padding:14px 16px;background:#111827;color:#e5e7eb;'
                f'border-radius:8px;overflow-x:auto;font-size:13px;line-height:1.65;">'
                f'<code>{html.escape(code)}</code></pre>'
            )
            continue
        if is_markdown_table(block):
            parts.append(table_html(block, theme, link_collector))
            continue
        if block.startswith("> "):
            quote = "<br>".join(link_collector.render(line[2:].strip()) for line in block.splitlines() if line.startswith("> "))
            parts.append(
                f'<blockquote style="margin:20px 0;padding:14px 16px;background:{theme["accent_soft"]};'
                f'border-left:4px solid {theme["accent"]};border-radius:8px;color:{theme["text"]};">'
                f'<p style="margin:0;">{quote}</p></blockquote>'
            )
            continue
        if re.match(r"^!\[.*?\]\(.*?\)$", block):
            alt, src = re.match(r"^!\[(.*?)\]\((.*?)\)$", block).groups()
            image_count += 1
            parts.append(image_block(normalize_image_src(src, article_path, image_map), alt, theme, link_collector))
            continue
        if block.startswith("- "):
            items = parse_unordered_items(block)
            if reference_mode:
                parts.append(reference_list_html(items, theme))
                reference_mode = False
            else:
                parts.append(text_list_html(items, theme, link_collector))
            continue
        if re.match(r"^\d+\. ", block):
            items = parse_ordered_items(block)
            if reference_mode:
                parts.append(reference_list_html(items, theme))
                reference_mode = False
            else:
                parts.append(text_list_html(items, theme, link_collector, ordered=True))
            continue

        paragraph = "<br>".join(link_collector.render(line) for line in block.splitlines())
        parts.append(f'<p style="margin:0 0 18px;color:{theme["text"]};">{paragraph}</p>')

    return "\n".join(parts), image_count


def references_section(refs: Iterable[tuple[str, str]], theme: dict[str, str]) -> str:
    refs = list(refs)
    if not refs:
        return ""
    items = []
    for idx, (label, url) in enumerate(refs, 1):
        items.append(
            f'<p style="margin:0 0 8px;color:{theme["muted"]};font-size:13px;line-height:1.65;">'
            f'[{idx}] {html.escape(label)}：{html.escape(url)}</p>'
        )
    return (
        f'<section style="height:1px;background:{theme["border"]};margin:32px 0 20px;"></section>'
        f'<h2 style="font-size:16px;margin:0 0 12px;color:{theme["text"]};">参考来源</h2>'
        + "\n".join(items)
    )


def build_html(
    article_path: Path,
    body: str,
    theme_name: str,
    image_map: dict[str, str],
    link_references: bool,
    layout: str,
) -> tuple[str, int, int]:
    theme = THEMES[theme_name]
    link_collector = LinkCollector(enabled=link_references, accent=theme["accent"])
    content, image_count = render_blocks(body, article_path, theme, image_map, link_collector)
    refs_html = references_section(link_collector.refs, theme)
    if layout == "boxed":
        outer_style = (
            f'max-width:760px;margin:0 auto;padding:28px 18px;'
            f'background-color:{theme["page_bg"]};color:{theme["text"]};'
        )
        inner_style = (
            f'background-color:{theme["card_bg"]};border:1px solid {theme["border"]};'
            f'border-radius:12px;padding:26px 22px;box-shadow:0 8px 22px {theme["shadow"]};'
        )
    else:
        # WeChat already wraps article content with mobile margins. Keep this layer wide.
        outer_style = (
            f'width:100%;max-width:100%;margin:0;padding:0;box-sizing:border-box;'
            f'background-color:{theme["card_bg"]};color:{theme["text"]};'
        )
        inner_style = (
            f'width:100%;max-width:100%;margin:0;padding:0 2px;box-sizing:border-box;'
            f'background-color:{theme["card_bg"]};border:none;border-radius:0;box-shadow:none;'
        )
    html_out = (
        f'<section style="{outer_style}font-family:-apple-system,'
        f"BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;"
        f'line-height:1.86;font-size:16px;">'
        f'<section style="{inner_style}">'
        f"{content}{refs_html}</section></section>"
    )
    return html_out, image_count, len(link_collector.refs)


def load_image_map(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def first_heading(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Typeset Markdown into WeChat-compatible local HTML.")
    parser.add_argument("article", type=Path, nargs="?")
    parser.add_argument("--theme", choices=sorted(THEMES), default="tech-blue")
    parser.add_argument("--layout", choices=["wide", "boxed"], default="wide")
    parser.add_argument("--list-themes", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--draft-json", type=Path)
    parser.add_argument("--image-map")
    parser.add_argument("--title")
    parser.add_argument("--author")
    parser.add_argument("--digest")
    parser.add_argument("--source-url")
    parser.add_argument("--thumb-media-id")
    parser.add_argument("--cover-url")
    parser.add_argument("--no-link-references", action="store_true")
    args = parser.parse_args()

    if args.list_themes:
        list_themes()
        return
    if args.article is None:
        raise SystemExit("article is required unless --list-themes is used")

    text = args.article.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    title = args.title or meta.get("title") or first_heading(body) or "未命名文章"
    author = args.author or meta.get("author", "")
    digest = args.digest or meta.get("digest") or meta.get("summary") or meta.get("description", "")
    source_url = args.source_url or meta.get("source_url", "")
    image_map = load_image_map(args.image_map)

    html_out, image_count, ref_count = build_html(
        args.article,
        body,
        args.theme,
        image_map,
        link_references=not args.no_link_references,
        layout=args.layout,
    )

    out = args.out or args.article.with_suffix(".wechat.html")
    out.write_text(html_out, encoding="utf-8")

    draft_path = None
    if args.draft_json:
        if not args.thumb_media_id:
            raise SystemExit("--thumb-media-id is required with --draft-json")
        draft = {
            "articles": [
                {
                    "title": title[:32],
                    "author": author[:16],
                    "digest": digest[:120],
                    "content": html_out,
                    "content_source_url": source_url,
                    "thumb_media_id": args.thumb_media_id,
                    "show_cover_pic": 1,
                    "need_open_comment": 0,
                    "only_fans_can_comment": 0,
                }
            ]
        }
        if args.cover_url:
            draft["articles"][0]["cover_url"] = args.cover_url
        args.draft_json.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
        draft_path = str(args.draft_json)

    print(
        json.dumps(
            {
                "success": True,
                "article": str(args.article),
                "html": str(out),
                "draft_json": draft_path,
                "theme": args.theme,
                "layout": args.layout,
                "title": title[:32],
                "author": author[:16],
                "digest_chars": len(digest[:120]),
                "images": image_count,
                "references": ref_count,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
