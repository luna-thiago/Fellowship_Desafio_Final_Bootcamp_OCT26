# Como usei IA neste desafio

* **Ferramenta utilizada:** Gemini (assistente de IA).
* **Papel adotado:** Conforme as regras da versão consolidada v3 do desafio — **par com escopo limitado** nas etapas de construção do ETL e testes (definindo o escopo de cada parte, executando, validando e explicando o código) e **tutora** nas consultas SQL.
* **Segurança e privacidade:** Nenhuma senha do banco de dados PostgreSQL foi compartilhada com a IA ou versionada no repositório. Todos os dados manipulados são 100% sintéticos (gerados com a `seed 2026`).

---

## Sugestões aceitas

### 1. Consolidação da Errata v3 (18/11) e escolha do esquema de banco de dados (Fase 0)

* **O que foi pedido à IA:** Ler o documento original (v1 de 03/11) e a errata consolidada (v3 de 18/11), resumir o que mudou e orientar a preparação inicial do ambiente em linguagem acessível.
* **O que a IA propôs:** Seguir o **Caminho A (PostgreSQL instalado localmente)** e utilizar exclusivamente o arquivo `insumos/schema.sql` para criar as tabelas, ignorando o `schema_sqlite.sql` (voltado apenas para o Caminho C com SQLite e incompatível com PostgreSQL).
* **Justificativa da decisão:** Aceita porque o Caminho A é o recomendado na errata v3 e o uso do arquivo SQL correto evita erros de sintaxe na criação das tabelas.
* **Como foi validado:** Conferi manualmente os cabeçalhos dos arquivos `schema.sql` e `schema_sqlite.sql` e executei a criação do banco e das tabelas via CMD:
  ```bash
  psql -U postgres -c "CREATE DATABASE verdejar;"
  psql -U postgres -d verdejar -f insumos/schema.sql
  ```
  Ambos os comandos finalizaram com sucesso no PostgreSQL local.

### 2. Diagnóstico e correção de ambiente no Windows (`psql` no PATH e instalação do Python) (Fase 0)

* **O que foi pedido à IA:** Solução para dois erros encontrados no terminal do Windows durante a preparação: o comando `psql` não era reconhecido e, em seguida, o comando `python` não foi encontrado.
* **O que a IA propôs:**
  1. Adicionar a pasta `bin` da instalação do PostgreSQL na variável de ambiente `PATH` do Windows e reiniciar o terminal.
  2. Instalar o Python 3 marcando a opção `Add python.exe to PATH` e reiniciar o terminal.
* **Justificativa da decisão:** Aceita porque configurar o `PATH` permite rodar tanto o `psql` quanto o `python` diretamente de qualquer pasta no CMD, destravando todas as etapas seguintes.
* **Como foi validado:** Após configurar o `PATH` do PostgreSQL, criei o banco `verdejar` e apliquei o `schema.sql`. Após instalar o Python 3, subi a API local e validei a rota `/saude`:
  ```bash
  python insumos/api_verdejar.py --dados insumos/dados
  curl "http://127.0.0.1:8000/saude"
  ```
  Resposta obtida no terminal: `{"status": "ok"}`.

### 3. Implementação da extração paginada da API e leitura do CSV (`etl/extracao.py`) (Fase 1)

* **O que foi pedido à IA:** Uma proposta modular para a Parte 1 (`etl/extracao.py`) capaz de percorrer todas as páginas das rotas `/clientes` e `/pedidos`, verificar o código de status HTTP, tratar erros de conexão e página inexistente (`404`) com mensagens claras, ler `insumos/dados/produtos.csv` com o módulo padrão `csv` e gravar os dados brutos na pasta `brutos/`.
* **O que a IA propôs:** Dividir a extração em quatro funções pequenas (`extrair_rota_paginada`, `ler_produtos_csv`, `salvar_bruto_json` e `executar_extracao`) usando apenas a biblioteca padrão do Python (`urllib`, `json`, `csv`, `os`) e imprimindo os contadores em texto simples.
* **Justificativa da decisão:** Aceita por atender a todos os critérios da dimensão D1 (extração completa, tratamento de erros, preservação dos dados brutos e saída acessível sem cores), sem exigir dependências externas nesta fase e com código fácil de acompanhar linha a linha.
* **Como foi validado:** Executei os três cenários diretamente no CMD e obtive as seguintes saídas reais:
  1. **Erro de conexão (API desligada):**
     ```text
     erro: falha de conexao com http://127.0.0.1:8000 ([WinError 10061] Nenhuma conexão pôde ser feita porque a máquina de destino as recusou ativamente). Verifique se a API esta rodando.
     ```
  2. **Extração completa (API ligada):**
     ```text
     extracao: clientes paginas=20 registros=1000
     extracao: pedidos paginas=102 registros_brutos=5100
     extracao: produtos registros=12
     ```
  3. **Página inexistente (HTTP 404 na página 9999):**
     ```text
     erro: pagina 9999 ou rota /clientes inexistente (HTTP 404).
     ```

---

## Sugestões rejeitadas

> **[Em andamento — a preencher nas próximas etapas]**
> *Regra obrigatória da Parte 5: registrar no mínimo **2 sugestões rejeitadas**, informando em cada uma o trecho pedido, o que a IA propôs, por que foi inadequada (justificativa) e o que foi feito no lugar com validação.*

---

## Falhas e retrabalho

> **[Em andamento — a preencher nas próximas etapas]**
> *Regra obrigatória da Parte 5: registrar ao menos **1 falha encontrada em código proposto pela IA**, descrevendo o erro observado na execução ou nos testes e o retrabalho feito para corrigi-lo.*