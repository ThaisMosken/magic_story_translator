"""Conversão de Markdown traduzido para blocos do Notion."""
import re

IMAGE_RE = re.compile(r'^!\[(.*?)\]\((.*?)\)\s*$')
HEADING_RE = re.compile(r'^(#{1,3})\s+(.*)$')
BULLET_RE = re.compile(r'^[-*]\s+(.*)$')
NUMBERED_RE = re.compile(r'^\d+\.\s+(.*)$')


def parse_inline_markdown(text: str) -> list:
    """Converte **negrito** e *itálico* em rich_text do Notion.
    Cada segmento também respeita o limite de 2000 caracteres do Notion."""
    tokens = re.split(r'(\*\*.+?\*\*|\*.+?\*)', text)
    rich_text = []
    for token in tokens:
        if not token:
            continue
        if token.startswith('**') and token.endswith('**'):
            content, annotations = token[2:-2], {"bold": True}
        elif token.startswith('*') and token.endswith('*'):
            content, annotations = token[1:-1], {"italic": True}
        else:
            content, annotations = token, {}
        for i in range(0, len(content), 2000):
            piece = {"type": "text", "text": {"content": content[i:i + 2000]}}
            if annotations:
                piece["annotations"] = annotations
            rich_text.append(piece)
    return rich_text or [{"type": "text", "text": {"content": ""}}]


def chunk_plain_text(text: str, max_len: int = 2000) -> list:
    """Rede de segurança: garante que nenhum parágrafo isolado passe de 2000
    caracteres, mesmo depois do parsing de Markdown (quebra por frases)."""
    if len(text) <= max_len:
        return [text]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 1 > max_len:
            if current:
                chunks.append(current)
            if len(s) > max_len:
                for i in range(0, len(s), max_len):
                    chunks.append(s[i:i + max_len])
                current = ""
            else:
                current = s
        else:
            current = f"{current} {s}" if current else s
    if current:
        chunks.append(current)
    return chunks


def markdown_to_notion_blocks(markdown_text: str) -> list:
    """Converte o Markdown traduzido em uma lista de blocos do Notion
    (heading_1/2/3, quote, bulleted/numbered list, image, paragraph)."""
    blocks = []
    lines = markdown_text.split('\n')
    paragraph_buffer = []

    def flush_paragraph():
        if not paragraph_buffer:
            return
        paragraph = ' '.join(paragraph_buffer).strip()
        paragraph_buffer.clear()
        if not paragraph:
            return
        for chunk in chunk_plain_text(paragraph):
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": parse_inline_markdown(chunk)},
            })

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            i += 1
            continue

        img_match = IMAGE_RE.match(stripped)
        if img_match:
            flush_paragraph()
            _, url = img_match.group(1), img_match.group(2)
            blocks.append({
                "object": "block",
                "type": "image",
                "image": {"type": "external", "external": {"url": url}},
            })
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('*') and lines[i + 1].strip().endswith('*'):
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": parse_inline_markdown(lines[i + 1].strip())},
                })
                i += 1
            i += 1
            continue

        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            flush_paragraph()
            heading_type = f"heading_{len(heading_match.group(1))}"
            blocks.append({
                "object": "block",
                "type": heading_type,
                heading_type: {"rich_text": parse_inline_markdown(heading_match.group(2))},
            })
            i += 1
            continue

        if stripped.startswith('>'):
            flush_paragraph()
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_lines.append(lines[i].strip().lstrip('>').strip())
                i += 1
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {"rich_text": parse_inline_markdown(' '.join(quote_lines))},
            })
            continue

        bullet_match = BULLET_RE.match(stripped)
        if bullet_match:
            flush_paragraph()
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": parse_inline_markdown(bullet_match.group(1))},
            })
            i += 1
            continue

        numbered_match = NUMBERED_RE.match(stripped)
        if numbered_match:
            flush_paragraph()
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": parse_inline_markdown(numbered_match.group(1))},
            })
            i += 1
            continue

        paragraph_buffer.append(stripped)
        i += 1

    flush_paragraph()
    return blocks