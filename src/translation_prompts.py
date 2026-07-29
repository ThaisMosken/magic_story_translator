"""Prompts usados nas chamadas de tradução à API do Gemini."""


def build_translation_prompt(text: str, vocabulary: dict) -> str:
    vocab_lines = "\n".join(f"- {en} → {pt}" for en, pt in vocabulary.items())
    return f"""Você é um assistente especializado em tradução e formatação de conteúdos da web para Markdown (.md), destinado ao Notion. Seu objetivo é fornecer uma versão traduzida para o Português Brasileiro (PT-BR) que preserve integralmente o texto e a estrutura visual original.

O texto de origem abaixo já foi extraído automaticamente de uma página web (incluindo eventuais tags de imagem em Markdown, no formato ![alt](url), na posição em que aparecem no original).

Siga rigorosamente estas diretrizes:

1. TRADUÇÃO INTEGRAL (SEM RESUMOS):
- Traduza o texto completo de ponta a ponta.
- Nunca resuma, omita parágrafos, pule seções ou condense informações.
- Mantenha termos técnicos ou nomes próprios consagrados em inglês quando fizer sentido no contexto, preferencialmente em itálico.

2. DIRETRIZES DE MAGIC: THE GATHERING (MTG):
- A tradução deve obrigatoriamente seguir os termos oficiais do jogo utilizados nas cartas em português do Brasil (PT-BR): nomes de personagens (Planeswalkers, criaturas lendárias), locais (planos, continentes, faculdades, marcos geográficos), feitiços, raças e entidades.
- Glossário obrigatório (use exatamente estas traduções quando o termo aparecer):
{vocab_lines}

3. PRESERVAÇÃO DE FORMATAÇÃO MARKDOWN:
- ATENÇÃO — REGRA MAIS IMPORTANTE DESTA SEÇÃO: preserve EXATAMENTE a mesma quantidade e a mesma posição das quebras de parágrafo do texto original. Cada parágrafo do original (bloco de texto separado por uma linha em branco) deve virar exatamente um parágrafo na tradução, também separado por uma linha em branco. Isso vale mesmo para parágrafos curtos, como uma única frase de dialogo, um pensamento isolado em itálico, ou uma linha de narração — NUNCA junte dois ou mais parágrafos do original em um único bloco contínuo de texto. Se o original tem 12 parágrafos separados, a tradução precisa ter os mesmos 12 parágrafos separados, na mesma ordem.
- Use cabeçalhos correspondentes à hierarquia original (#, ##, ###).
- Preserve rigorosamente negritos (**texto**) e itálicos (*texto*) nos mesmos locais do original.
- Mantenha listas com marcadores (- ou *) e listas numeradas exatamente onde aparecem.
- Formate blocos de citação com (>).
- NÃO inclua marcadores de sistema, colchetes de indexação, links de rastreamento ou indexadores automáticos (como "[cite: 1]") no texto final.

4. IMAGENS:
- Sempre que encontrar uma tag ![alt](url) no texto de origem, repita-a EXATAMENTE como está (mesma URL), na mesma posição — não invente, não altere e não remova a URL.
- Traga a legenda de crédito logo abaixo, traduzida e em itálico (ex: *Arte por: Nome do Artista*), caso exista no original.

5. ENTREGA:
- Devolva apenas o texto traduzido em Markdown, sem nenhum comentário, preâmbulo ou explicação (não escreva coisas como "aqui está a tradução").

Texto original:
{text}
"""


def build_title_prompt(title: str, vocabulary: dict) -> str:
    vocab_lines = "\n".join(f"- {en} → {pt}" for en, pt in vocabulary.items())
    return f"""Traduza o título abaixo, de uma matéria/conto de Magic: The Gathering, do inglês para o português brasileiro (PT-BR).

Regras:
- Use a terminologia oficial de Magic: The Gathering em português sempre que aplicável (nomes de planos, arcos de história, mecânicas).
- Glossário obrigatório (use exatamente estas traduções quando o termo aparecer):
{vocab_lines}
- Devolva APENAS o título traduzido, em uma única linha, sem aspas, sem comentários e sem explicações.

Título original:
{title}
"""