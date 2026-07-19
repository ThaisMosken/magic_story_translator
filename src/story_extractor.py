"""Extração de contos do site Magic Story (magic.wizards.com)."""
from datetime import datetime
import trafilatura


def extract_story(url: str) -> dict:
    """Baixa e extrai o conteúdo principal de uma página do Magic Story.

    Retorna um dicionário com:
      - title: título original (em inglês)
      - author: autor extraído da página
      - date: data de publicação normalizada em ISO (YYYY-MM-DD), quando possível
      - text: corpo do texto em Markdown, incluindo tags de imagem (![alt](url))
        na posição em que aparecem no original
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        raise RuntimeError(f"Não foi possível baixar a página: {url}")

    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=False,
        include_images=True,
        favor_precision=True,
    )
    metadata = trafilatura.extract_metadata(downloaded)

    if not text or len(text) < 500:
        raise RuntimeError(
            "Texto extraído parece incompleto — verifique manualmente a página "
            "(pode ser que essa página em específico use outra estrutura)."
        )

    # trafilatura geralmente já retorna a data em formato ISO (YYYY-MM-DD),
    # mas caso venha em outro formato, tentamos normalizar aqui.
    raw_date = metadata.date if metadata else None
    release_date_iso = None
    if raw_date:
        try:
            release_date_iso = datetime.fromisoformat(raw_date).date().isoformat()
        except ValueError:
            release_date_iso = raw_date  # mantém como veio; ajuste manual se necessário

    return {
        "title": metadata.title if metadata else None,
        "author": metadata.author if metadata else None,
        "date": release_date_iso,
        "text": text,
    }