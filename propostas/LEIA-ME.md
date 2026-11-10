# Propostas comerciais ClipCar (PDF)

Gera a proposta de um prestador a partir de uma lista de valores, no modelo da cartilha da Lava Lento
(com o logo e as cores do prestador) mais as páginas comerciais: resumo, Módulo Plus, preço do ClipCar,
taxas da Asaas (página separada), exemplos e próximos passos.

    python3 propostas/gerar.py propostas/clientes/<arquivo>.json

O PDF sai em `propostas/saida/<Nome>/`. Precisa de Python 3, Node e Playwright (Chromium).
Recursos do painel do prestador (7 páginas, com o mesmo JSON; o selo PLUS some se `modulo_plus` for `nao`):

    python3 propostas/painel.py propostas/clientes/<arquivo>.json

Sai em `propostas/saida/<Nome>/painel/`.
No Claude Code, é só pedir: "gere a proposta para ..." (agente `proposta-comercial`).

## Valores

Obrigatórios

| Valor | O que é | Exemplo |
|---|---|---|
| `categoria` | `estetica`, `mecanica` ou `funilaria` | `estetica` |
| `nome` | Nome curto do prestador (até ~22 letras) | `Ateliê do Automóvel` |
| `artigo` | `o` ou `a` (o Ateliê, a Oficina) | `o` |
| `validade` | Até quando a proposta vale, DD/MM/AAAA | `13/11/2026` |

Proposta (se faltar, vale o padrão)

| Valor | Padrão | O que é |
|---|---|---|
| `taxa_clipcar_pct` | `2` | Taxa do ClipCar sobre o serviço pago pelo app |
| `mensalidade` | `a combinar` | Valor fixo por mês (número) ou `a combinar` |
| `modulo_plus` | `incluso_ate_validade` | `incluso_ate_validade`, `incluso` ou `nao` |
| `condicao_especial` | (vazio) | Texto livre da condição especial; `condicao_titulo` muda o título |
| `clipcar_paga_abertura` | `true` | Se o ClipCar paga a abertura da conta na Asaas |
| `exemplo_valor` | `200` | Valor do serviço usado na página "Quanto você recebe" |
| `data`, `cidade` | hoje, `Ubatuba` | Data e cidade no fim da proposta |
| `apelido` | igual ao nome | Como chamar no meio do texto (`Ateliê`) |

Identidade e telas do app (se faltar, vale o padrão da categoria)

`nome_completo`, `logo` (arquivo PNG/JPG ao lado do .json; vazio = selo com as iniciais), `logo_fundo`,
`cor_principal`, `cor_escura`, `cor_frase` (#RRGGBB), `frase`, `titulo_capa`, `codigo_qr`,
`servico_1` a `servico_5`, `nota_servicos`.
Só estética: `servico_destaque`, `inclui_1` a `inclui_7`, `inclui_mais`, `preco_pequeno`, `preco_medio`, `preco_grande`.
Só mecânica e funilaria: `foto_1` a `foto_3`.
Mande `-` para esconder um item. Detalhes em `templates/variaveis-<categoria>.json`.

## Taxas da Asaas

Ficam em `asaas.json` (conferidas em 10/11/2026 no app Asaas do ClipCar). Mudou a taxa? Atualize ali e
todas as próximas propostas saem com o valor novo. Para um prestador com taxa diferente, coloque um bloco
`"asaas": {...}` no arquivo dele só com o que muda.

## Ainda não cobre

Lojista (revenda de veículos): a apresentação é outra e ainda não virou modelo.
