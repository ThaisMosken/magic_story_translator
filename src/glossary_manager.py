"""Carregamento do glossário de termos de MTG a partir de um arquivo Markdown."""


def load_glossary(md_path: str) -> dict:
    """Lê um glossário em Markdown no formato '- termo em inglês → tradução'
    e retorna um dicionário. Cabeçalhos (#, ##), linhas em branco e
    comentários HTML (<!-- ... -->) são ignorados — servem só para
    organização visual do arquivo."""
    vocabulary = {}
    in_comment = False
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("<!--"):
                in_comment = True
            if in_comment:
                if "-->" in line:
                    in_comment = False
                continue
            if line.startswith("#"):
                continue
            line = line.lstrip("-*").strip()
            if "→" in line:
                en, pt = line.split("→", 1)
                vocabulary[en.strip()] = pt.strip()
    return vocabulary