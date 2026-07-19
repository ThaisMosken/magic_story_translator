"""Orquestrador do processo completo: extração, tradução e publicação."""
from src.story_extractor import extract_story
from src.translation_prompts import build_translation_prompt, build_title_prompt
from src.notion_publisher import publish_story


def build_pipeline(gemini_client, notion_client, database_id, model_name, vocabulary, status_name):
    """Monta e devolve a função translate_and_publish(story_url, arc_name, tags,
    dry_run=False), já configurada com os clientes e parâmetros da sessão atual.

    Isso permite que o BLOCO 2 do notebook continue chamando
    translate_and_publish(...) exatamente como antes, sem precisar repassar
    clientes/configurações a cada conto.
    """

    def translate_and_publish(story_url: str, arc_name: str, tags: list, dry_run: bool = False) -> None:
        if not dry_run and not gemini_client:
            print("❌ Não é possível continuar: CHAVE_GEMINI ausente.")
            return
        if not database_id:
            print("❌ Não é possível continuar: NOTION_DATABASE_ID ausente.")
            return

        print(f"🔎 Extraindo conteúdo de: {story_url}")
        try:
            story = extract_story(story_url)
        except Exception as e:
            print(f"❌ Erro na extração: {e}")
            return

        print(f"📖 Título original: {story['title']}")
        print(f"✍️  Autor: {story['author']}")
        print(f"📅 Data: {story['date']}")
        print(f"📝 Tamanho do texto extraído: {len(story['text'])} caracteres")

        if dry_run:
            print("🧪 DRY RUN ativo: pulando chamadas ao Gemini, usando texto de teste no lugar da tradução.")
            translated_text = (
                f"# {story['title'] or 'Conto de teste'}\n\n"
                "Este é um **parágrafo de teste** em negrito, e este trecho está em *itálico*.\n\n"
                "> Esta é uma citação de teste, só para validar a formatação.\n\n"
                "- Primeiro item de lista\n"
                "- Segundo item de lista\n\n"
                "Parágrafo final de teste, sem depender do Gemini."
            )
            translated_title = f"[TESTE] {story['title']}" if story.get("title") else "[TESTE] Conto sem título"
        else:
            print("🌐 Traduzindo corpo do texto...")
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=build_translation_prompt(story["text"], vocabulary),
            )
            translated_text = response.text

            translated_title = None
            if story.get("title"):
                print("🌐 Traduzindo título...")
                title_response = gemini_client.models.generate_content(
                    model=model_name,
                    contents=build_title_prompt(story["title"], vocabulary),
                )
                translated_title = title_response.text.strip().strip('"').strip()
                print(f"📖 Título traduzido: {translated_title}")

        try:
            print("🚀 Publicando conto traduzido no Notion...")
            page_id = publish_story(
                notion_client,
                database_id,
                story,
                translated_text,
                story_url,
                arc=arc_name,
                tags=tags,
                status_name=status_name,
                translated_title=translated_title,
            )
            print(f"✅ Sucesso! Página criada: https://notion.so/{page_id.replace('-', '')}")
        except Exception as e:
            print(f"❌ Erro na integração com Notion: {e}")

    return translate_and_publish