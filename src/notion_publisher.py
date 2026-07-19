"""Publicação de contos traduzidos como registros em uma database do Notion."""
from src.notion_formatter import markdown_to_notion_blocks


def publish_story(
    notion_client,
    database_id: str,
    story_meta: dict,
    translated_text: str,
    original_url: str,
    arc: str,
    tags: list,
    status_name: str,
    translated_title: str = None,
) -> str:
    all_blocks = markdown_to_notion_blocks(translated_text)

    # A API do Notion aceita no máximo 100 blocos filhos por requisição
    # (tanto na criação da página quanto em blocks.children.append)
    first_batch, remaining_batches = all_blocks[:100], all_blocks[100:]

    page_title = translated_title or story_meta["title"] or "Conto sem título"

    properties = {
        "Name": {"title": [{"text": {"content": page_title}}]},
        "Author": {"rich_text": [{"text": {"content": story_meta["author"] or ""}}]},
        "Arc": {"select": {"name": arc}},
        "Tags": {"multi_select": [{"name": t} for t in tags]},
        "Status": {"status": {"name": status_name}},
        "Original URL": {"url": original_url},
    }

    # "Release Date" só é enviado se conseguimos extrair/normalizar a data
    if story_meta.get("date"):
        properties["Release Date"] = {"date": {"start": story_meta["date"]}}

    page = notion_client.pages.create(
        parent={"database_id": database_id},
        properties=properties,
        children=first_batch,
    )

    for i in range(0, len(remaining_batches), 100):
        notion_client.blocks.children.append(
            block_id=page["id"],
            children=remaining_batches[i:i + 100],
        )

    return page["id"]