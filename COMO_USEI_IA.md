# Como usei IA neste desafio

- **Ferramenta utilizada:** Gemini (assistente de IA).
- **Papel adotado:** Uso conforme as regras do desafio — **par com escopo limitado** nas etapas do ETL (pedindo orientações e funções pontuais dentro de um escopo definido, executando e validando cada passo) e **tutora** nas consultas SQL.
- **Boas práticas de segurança:** Nenhuma senha de banco de dados ou credencial sensível foi compartilhada com a IA. Apenas os insumos sintéticos do desafio e mensagens de erro genéricas de ambiente foram utilizados.

---

## Sugestões aceitas

### 1. Preparação do ambiente, escolha do banco e diagnóstico de terminal (Parte 0)

- **Trecho / tarefa pedida:** Pedi um passo a passo sem termos técnicos soltos a partir da errata v3 (18/11), os comandos para criar o banco de dados `verdejar` no PostgreSQL, aplicar o esquema de tabelas, subir a API local e resolver os erros de comando não reconhecido (`psql` e `python`) no Windows.
- **Justificativa da decisão:** Aceitei seguir o **Caminho A (PostgreSQL local)**, recomendado pela errata, aplicando exclusivamente o arquivo `insumos/schema.sql` (e descartando o `schema_sqlite.sql`, incompatível com PostgreSQL). Também segui as orientações de adicionar a pasta `bin` do PostgreSQL na variável de ambiente `PATH` e instalar o Python 3 para destravar o terminal.
- **Como validei:**
  - Após ajustar o `PATH`, executei `psql -U postgres -c "CREATE DATABASE verdejar;"` e `psql -U postgres -d verdejar -f insumos/schema.sql`, criando o banco e as tabelas sem erros.
  - Após instalar o Python, iniciei a API com `python insumos/api_verdejar.py --dados insumos/dados` e testei com `curl "http://127.0.0.1:8000/saude"`, obtendo exatamente `{"status": "ok"}`.
  - Registrei a estrutura inicial no branch `desafio-final-verdejar` com o primeiro commit.

### 2. Implementação da extração paginada e leitura do CSV (`etl/extracao.py`) (Parte 1)

- **Trecho / tarefa pedida:** Pedi uma proposta de funções para o módulo `etl/extracao.py` capazes de consumir as rotas paginadas `/clientes` e `/pedidos`, validar status HTTP, tratar erros de conexão e página inexistente (`404`), ler `insumos/dados/produtos.csv` com o módulo padrão `csv` e salvar cópias brutas na pasta `brutos/`.
- **Justificativa da decisão:** Aceitei a estrutura modular dividida em funções pequenas (`extrair_rota_paginada`, `ler_produtos_csv`, `salvar_bruto_json` e `executar_extracao`) usando apenas a biblioteca padrão do Python (`urllib`, `json`, `csv`, `os`), pois cumpre todos os requisitos da Parte 1 sem exigir instalação de pacotes extras nesta etapa e facilita explicar o fluxo na defesa oral.
- **Como validei:**
  - **Teste 1 (API desligada):** executei `python etl/extracao.py` com o servidor parado e confirmei a mensagem amigável de erro de conexão (`[WinError 10061]`).
  - **Teste 2 (API ligada):** executei `python etl/extracao.py` com a API ativa e confirmei a gravação dos arquivos em `brutos/` e os contadores (`clientes paginas=20 registros=1000`, `pedidos paginas=102 registros_brutos=5100`, `produtos registros=12`).
  - **Teste 3 (página inexistente):** chamei `extrair_rota_paginada` na página `9999` e confirmei o tratamento limpo do erro `HTTP 404`.

### 3. Estrutura do `CONTRATO_DE_DADOS.md` e funções puras de limpeza (`etl/transformacao.py`) (Parte 2)

- **Trecho / tarefa pedida:** Pedi a estrutura do contrato de dados alinhada ao `insumos/schema.sql` e funções pequenas e puras para tratar cada uma das seis armadilhas (`A1` a `A6`), incluindo a geração sequencial da coluna `linha` para a tabela `itens_pedido`.
- **Justificativa da decisão:** Aceitei a divisão em funções puras e isoladas (`tratar_email`, `padronizar_estado`, `converter_data`, `converter_valor`, `remover_pedidos_repetidos` e `calcular_e_verificar_itens`) e a numeração automática da coluna `linha` via `enumerate(..., start=1)`, pois permite testar cada armadilha separadamente no `pytest` e respeita a chave primária composta `(pedido_id, linha)` do PostgreSQL.
- **Como validei:**
  - Executei `python etl/transformacao.py` sobre os dados brutos extraídos e conferi todos os contadores gerados (`pedidos_unicos=5000`, `repetidos_descartados=100`, `emails_nulos=81`, `estados_padronizados=151`, `datas_convertidas=1037`, `valores_convertidos=1255`, `divergentes=238`).

### 4. Carga transacional idempotente e orquestração (`etl/carga.py` e `etl/main.py`) (Parte 3)

- **Trecho / tarefa pedida:** Pedi uma proposta para carregar os dados limpos no PostgreSQL usando `psycopg`, respeitando a ordem das chaves estrangeiras, garantindo idempotência, usando consultas parametrizadas e lendo a senha de um arquivo `.env` local fora do Git.
- **Justificativa da decisão:** Aceitei o uso de `TRUNCATE TABLE itens_pedido, pedidos, clientes, produtos;` dentro de uma única transação (`with conn:`) seguido de `cur.executemany` com marcadores `%s` na ordem `produtos` → `clientes` → `pedidos` → `itens_pedido`. Essa abordagem garante atomicidade (tudo ou nada) e protege a senha do banco ao mantê-la apenas no `.env` listado no `.gitignore`.
- **Como validei:**
  - Executei `python -m etl.main` duas vezes seguidas e confirmei que ambas as execuções produziram exatamente as mesmas contagens (`clientes=1000 produtos=12 pedidos=5000 itens=12455`) e reconciliação zerada (`soma_valor_itens_origem=311228.75 soma_valor_itens_destino=311228.75 diferenca=0.00`).

---

## Sugestões rejeitadas

### 1. Adoção de prefixos em inglês (`chore:`, `feat:`) nas mensagens de commit (Parte 1)

- **Trecho / sugestão proposta pela IA:** A IA sugeriu padronizar as mensagens de commit do Git usando prefixos em inglês do padrão *Conventional Commits* (como `chore:` e `feat:`).
- **Justificativa da rejeição:** O documento do desafio exige apenas que os commits tenham mensagens descritivas explicando o que foi feito, sem obrigar o uso de prefixos em inglês. Usar frases diretas em português deixa o histórico do repositório mais claro, natural e fácil de revisar.
- **O que foi feito no lugar e como validei:** Escrevi as mensagens de commit diretamente em português descritivo e confirmei no histórico do Git (`git log`) e no GitHub que o registro ficou claro e objetivo.

### 2. Uso de `float` e `round()` para valores monetários na transformação (Parte 2)

- **Trecho / sugestão proposta pela IA:** Na primeira versão proposta para `etl/transformacao.py`, a IA sugeriu converter os valores financeiros (`valor_total`, `preco_unitario` e `preco_base`) usando `round(float(texto), 2)`.
- **Justificativa da rejeição:** Números do tipo `float` usam representação binária e podem causar imprecisões de arredondamento em operações financeiras, além de o `round()` padrão do Python usar arredondamento bancário (para o par mais próximo). Como o esquema do PostgreSQL (`insumos/schema.sql`) define essas colunas como `NUMERIC(10,2)` e `NUMERIC(12,2)`, o tipo adequado em Python é o `Decimal`.
- **O que foi feito no lugar e como validei:** Substituí `float` e `round()` pelo módulo padrão `decimal` (`Decimal` com `.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`), convertendo sempre a partir de `str(valor)` para evitar ruído binário, e validei os cálculos executando `python etl/transformacao.py` antes e depois da alteração.

---

## Falhas e retrabalho

> *Meta obrigatória até a Parte 5: registrar no mínimo **1 falha encontrada em código proposto pela IA** e o retrabalho feito para corrigi-la.*

### 1. [A preencher ao identificar e corrigir uma falha em código proposto pela IA]

- **O que a IA propôs:** *(trecho ou lógica original)*
- **Qual foi a falha encontrada:** *(erro de execução, teste que falhou ou comportamento incorreto)*
- **Retrabalho feito e validação:** *(como você corrigiu e provou que passou a funcionar)*