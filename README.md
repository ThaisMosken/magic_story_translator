# Magic Story Translator

Script para Google Colab que extrai contos e matérias do site [Magic Story](https://magic.wizards.com/en/news/magic-story), traduz para Português Brasileiro usando a API do Gemini com glossário de termos de Magic: The Gathering e publica o resultado, já formatado, como um novo registro em uma database do Notion.

## Visão geral do fluxo

1. **Extração**: o texto do artigo é extraído diretamente do HTML da página (via `trafilatura`), incluindo as imagens na posição correta — sem precisar imprimir a página como PDF.
2. **Tradução**: o texto (e o título, separadamente) são enviados à API do Gemini, com um prompt que exige tradução integral, terminologia oficial de MTG e preservação da formatação em Markdown.
3. **Conversão**: o Markdown traduzido é convertido nos blocos reais do Notion (títulos, negrito, itálico, citações, listas, imagens).
4. **Publicação**: um novo registro é criado na database do Notion configurada, preenchendo todas as propriedades e o conteúdo da página.

O notebook é dividido em dois blocos de código, pensados para o seguinte fluxo de trabalho:

- **BLOCO 1** — configuração geral (instalação de dependências, leitura dos secrets, criação dos clientes de API, carregamento do glossário e definição de todas as funções). Roda **uma vez por sessão** do Colab.
- **BLOCO 2** — variáveis do conto a ser traduzido no momento, seguidas da chamada que executa o processo inteiro. Roda **uma vez para cada conto**, podendo ser editado e reexecutado quantas vezes for preciso, sem precisar rodar o BLOCO 1 de novo.

## Pré-requisitos

### Secrets do Colab

Configurados no ícone de chave 🔑 na barra lateral do Colab:

| Secret | Descrição |
|---|---|
| `GEMINI_API_KEY` | Chave da API do Gemini, usada para as traduções |
| `NOTION_TOKEN_MTG_TRANSLATOR` | Token da integração do Notion dedicada a este projeto |
| `NOTION_DATABASE_ID_MTG_TRANSLATOR` | ID da database do Notion onde os contos traduzidos são publicados |

> A integração do Notion precisa ter sido conectada manualmente à database (**••• → Connections**, na página da database), além de ter o token gerado em [notion.so/my-integrations](https://notion.so/my-integrations).

### Estrutura esperada da database no Notion

| Propriedade | Tipo | Preenchida com |
|---|---|---|
| `Name` | Title | Título traduzido do conto |
| `Author` | Text | Autor extraído da página original |
| `Arc` | Select | Valor de `ARC_NAME` (ver abaixo) — **precisa já existir como opção** |
| `Tags` | Multi-select | Valores de `TAGS` (ver abaixo) |
| `Status` | Status | Sempre `"Not started"` na publicação inicial |
| `Original URL` | URL | Valor de `STORY_URL` (ver abaixo) |
| `Release Date` | Date | Data de publicação extraída da página original (quando disponível) |

### Glossário de MTG

O vocabulário usado para orientar a tradução (nomes de planos, colégios, raças, mecânicas etc.) não fica no código — ele é lido do arquivo [`glossary_mtg.md`](https://github.com/ThaisMosken/magic_story_translator/blob/main/glossary_mtg.md), no repositório GitHub deste projeto.

Formato de cada linha do glossário:

```markdown
- termo em inglês → tradução oficial em PT-BR
```

Cabeçalhos (`#`, `##`), linhas em branco e comentários HTML (`<!-- ... -->`) são ignorados pelo script — servem só para organizar o arquivo em seções, visualmente, para quem for editá-lo.

Para atualizar o glossário: edite e commite `glossary_mtg.md` no repositório e, no BLOCO 1, defina `FORCE_UPDATE_GLOSSARY = True` antes de rodar (isso faz um `git pull` do repositório antes de carregar o vocabulário).

## Variáveis do BLOCO 2

Estas são as únicas variáveis que precisam ser editadas a cada novo conto traduzido:

### `STORY_URL`
A URL completa da página do Magic Story que será traduzida (o link do artigo/conto original, em inglês). É a partir dela que o script extrai o texto, o título, o autor e a data de publicação.

```python
STORY_URL = "https://magic.wizards.com/en/news/magic-story/nome-do-conto"
```

### `ARC_NAME`
O nome do arco/temporada da história ao qual este conto pertence (ex.: `"Secrets of Strixhaven"`). Esse valor é enviado para a propriedade **Arc** no Notion, que é do tipo *select* — **o valor precisa já existir como uma opção configurada nessa coluna da database**, ou a criação da página falha.

```python
ARC_NAME = "Secrets of Strixhaven"
```

### `TAGS`
Uma lista de tags que serão aplicadas à propriedade **Tags** (multi-select) no Notion. Podem ser tags já existentes na database ou novas — o Notion cria automaticamente qualquer tag nova que ainda não exista na coluna.

```python
TAGS = ["MTG", "Strixhaven"]
```

### A chamada de execução

Depois de preencher as três variáveis acima, a última linha do bloco dispara o processo inteiro (extração → tradução → publicação):

```python
translate_and_publish(STORY_URL, ARC_NAME, TAGS)
```

Existe também um modo de teste, que pula as chamadas ao Gemini (útil quando a cota diária da API se esgota) e publica no Notion um conteúdo de exemplo, prefixado com `[TESTE]` no título, só para validar que a extração e a integração com o Notion continuam funcionando:

```python
translate_and_publish(STORY_URL, ARC_NAME, TAGS, dry_run=True)
```

> `STATUS_NAME` não é uma variável do BLOCO 2 — ela é uma constante fixa (`"Not started"`), definida no BLOCO 1, já que todo conto recém-publicado começa com esse status.

## Limitações conhecidas

- A extração depende da estrutura HTML da página do Magic Story; se a Wizards mudar o layout do site, a extração via `trafilatura` pode parar de funcionar corretamente.
- A qualidade da tradução depende do modelo do Gemini escolhido em `MODELO_ESCOLHIDO` (BLOCO 1) — modelos mais robustos tendem a seguir melhor as instruções de terminologia e formatação, ao custo de mais tempo/cota.
- Histórias muito longas (mais de 100 blocos no Notion) são publicadas em múltiplas requisições automaticamente — isso é tratado pelo script, mas pode deixar a publicação um pouco mais lenta.

## Histórico de versões

- **v1** — primeira versão funcional, com blocos separados por etapa (extração, tradução, publicação).
- **v2** — reestruturação em 2 blocos: setup (uma vez por sessão) + variáveis e execução (por conto).
- **v3** — glossário de MTG migrado do código para um arquivo `.md` versionado no GitHub.
- **v4** — ajustes finais de estabilização.