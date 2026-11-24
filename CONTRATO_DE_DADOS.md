# Contrato de Dados — ETL da Verdejar

Este documento define a estrutura das tabelas de destino no banco de dados **PostgreSQL** (conforme `insumos/schema.sql`), os tipos de dados esperados, a obrigatoriedade de preenchimento e as regras de transformação aplicadas para tratar as armadilhas `A1` a `A6`.

---

## 1. Tabela `clientes`

Armazena o cadastro único dos clientes da loja Verdejar.

| Coluna | Tipo no PostgreSQL | Admite nulo? | Regra de origem e transformação |
|---|---|---|---|
| `id` | `INTEGER` (Chave Primária) | Não | Identificador numérico único do cliente vindo da rota `/clientes`. Convertido para inteiro (`int`). |
| `nome` | `TEXT` | Não | Nome completo do cliente, texto limpo sem espaços sobrando nas pontas. |
| `email` | `TEXT` | **Sim** | **Armadilha A1:** parte dos clientes vem sem e-mail (`null` ou vazio). O cliente é mantido e o campo é gravado como nulo (`None` / `NULL`), contabilizando a ocorrência. |
| `cidade` | `TEXT` | Não | Nome da cidade do cliente, texto limpo. |
| `estado` | `CHAR(2)` | Não | **Armadilha A2:** sigla do estado (UF) com 2 letras. Padronizada sempre para letras maiúsculas (ex.: `"rs"` → `"RS"`). |
| `cadastro_em` | `DATE` | Não | Data de cadastro no formato ISO (`AAAA-MM-DD`), convertida para o tipo `DATE` do PostgreSQL. |

---

## 2. Tabela `produtos`

Armazena o catálogo de produtos comercializados, extraído da planilha `insumos/dados/produtos.csv`.

| Coluna | Tipo no PostgreSQL | Admite nulo? | Regra de origem e transformação |
|---|---|---|---|
| `produto_id` | `INTEGER` (Chave Primária) | Não | Código numérico único do produto, convertido para inteiro (`int`). |
| `nome` | `TEXT` | Não | Nome do produto hortifrúti. |
| `categoria` | `TEXT` | Não | Categoria do produto (`folhas`, `legumes`, `frutas`). |
| `preco_base` | `NUMERIC(10,2)` | Não | Preço unitário de referência do catálogo, convertido para número decimal com 2 casas decimais. |

---

## 3. Tabela `pedidos`

Armazena o cabeçalho de cada pedido único realizado na loja.

| Coluna | Tipo no PostgreSQL | Admite nulo? | Regra de origem e transformação |
|---|---|---|---|
| `id` | `INTEGER` (Chave Primária) | Não | **Armadilha A5:** identificador único do pedido. Pedidos repetidos (mesmo `id`) entre páginas da API são descartados, mantendo apenas a primeira ocorrência. |
| `cliente_id` | `INTEGER` (Chave Estrangeira) | Não | Referência ao `id` da tabela `clientes`. Convertido para inteiro (`int`). |
| `data_pedido` | `DATE` | Não | **Armadilha A3:** data do pedido recebida nos formatos `AAAA-MM-DD` ou `DD/MM/AAAA`. Ambos são convertidos para o tipo `DATE` do PostgreSQL. |
| `status` | `TEXT` | Não | Situação atual do pedido (`entregue`, `cancelado`, `em_transporte`). |
| `valor_total` | `NUMERIC(12,2)` | Não | **Armadilha A4:** valor total informado pela API, que vem ora como número, ora como texto com vírgula (ex.: `"125,84"`). Convertido para número decimal com 2 casas decimais (`125.84`). |
| `valor_itens` | `NUMERIC(12,2)` | Não | **Armadilha A6:** soma calculada a partir dos itens do pedido (`quantidade × preco_unitario`), arredondada para 2 casas decimais. |
| `divergente` | `BOOLEAN` | Não | **Armadilha A6:** valor lógico (`True` ou `False`, padrão `False`). Marcado como `True` quando a diferença absoluta entre `valor_total` e `valor_itens` for maior que `0.01` (1 centavo). |

---

## 4. Tabela `itens_pedido`

Armazena cada item comprado dentro de um pedido (relação de 1 pedido para vários itens).

| Coluna | Tipo no PostgreSQL | Admite nulo? | Regra de origem e transformação |
|---|---|---|---|
| `pedido_id` | `INTEGER` (Chave Primária / Estrangeira) | Não | Referência ao `id` da tabela `pedidos`. |
| `linha` | `INTEGER` (Chave Primária) | Não | Número sequencial do item dentro do mesmo pedido (`1, 2, 3...`), gerado na transformação para compor a chave primária `(pedido_id, linha)`. |
| `produto_id` | `INTEGER` (Chave Estrangeira) | Não | Referência ao `produto_id` da tabela `produtos`. |
| `quantidade` | `INTEGER` | Não | Quantidade de unidades compradas daquele produto, convertida para inteiro (`int`). |
| `preco_unitario` | `NUMERIC(10,2)` | Não | Preço unitário praticado no item, convertido para número decimal com 2 casas decimais. |

---

## Resumo das 6 armadilhas tratadas

- **A1:** E-mails ausentes mantidos como `NULL` e contabilizados (`emails_nulos`).
- **A2:** Siglas de estado padronizadas para maiúsculas e contabilizadas (`estados_padronizados`).
- **A3:** Datas em `DD/MM/AAAA` e `AAAA-MM-DD` unificadas para `DATE` e contabilizadas (`datas_convertidas`).
- **A4:** Valores totais em texto com vírgula convertidos para número decimal com 2 casas e contabilizados (`valores_convertidos`).
- **A5:** Pedidos duplicados removidos pelo `id` mantendo a primeira ocorrência (`pedidos_unicos` e `repetidos_descartados`).
- **A6:** Cálculo de `valor_itens` e marcação de `divergente = True` quando `|valor_total - valor_itens| > 0.01` (`divergentes`).