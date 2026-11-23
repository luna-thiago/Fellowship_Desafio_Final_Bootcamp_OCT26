# Como usei IA neste desafio

* **Ferramenta utilizada:** Gemini (assistente de IA usado no papel de apoio à documentação/ambiente na Fase 0 e, nas próximas etapas, como **tutora** nas consultas SQL e **par com escopo limitado** na construção do ETL e dos testes, conforme a versão consolidada v3 do desafio).
* **Segurança e privacidade:** Nenhuma senha do banco de dados PostgreSQL foi compartilhada com a IA ou versionada no repositório. Todos os dados manipulados são 100% sintéticos (gerados com a `seed 2026`).

---

## Sugestões aceitas

### 1. Consolidação da Errata v3 (18/11) e escolha do esquema de banco de dados (Fase 0)
* **O que foi pedido à IA:** Ler o documento original (v1 de 03/11) e a errata consolidada (v3 de 18/11), resumir o que mudou e orientar a preparação inicial do ambiente em linguagem acessível.
* **O que a IA propôs:** Seguir o **Caminho A (PostgreSQL instalado localmente)** e utilizar exclusivamente o arquivo `insumos/schema.sql` para criar as tabelas, ignorando o `schema_sqlite.sql` (que é voltado apenas para o Caminho C com SQLite e utiliza comandos incompatíveis com PostgreSQL, como `PRAGMA`).
* **Justificativa da decisão:** Aceita porque o Caminho A é o caminho recomendado na errata v3 e o uso do arquivo SQL correto evita erros de sintaxe logo na criação das tabelas.
* **Como foi validado:** Conferi manualmente os cabeçalhos dos arquivos `schema.sql` e `schema_sqlite.sql` recebidos nos insumos e executei a criação do banco e das tabelas via CMD:
  ```bash
  psql -U postgres -c "CREATE DATABASE verdejar;"
  psql -U postgres -d verdejar -f insumos/schema.sql
  ```
  Ambos os comandos finalizaram com sucesso no PostgreSQL local.

### 2. Diagnóstico e correção de ambiente no Windows (`psql` no PATH e instalação do Python) (Fase 0)
* **O que foi pedido à IA:** Solução para dois erros encontrados no terminal do Windows durante a preparação: o comando `psql` não era reconhecido e, em seguida, o comando `python` não foi encontrado.
* **O que a IA propôs:**
  1. Adicionar a pasta `bin` da instalação do PostgreSQL na variável de ambiente `PATH` do Windows e reiniciar o terminal.
  2. Instalar o Python 3 marcando a opção `Add python.exe to PATH` (verificando também possíveis conflitos de aliases no Windows) e reiniciar o terminal.
* **Justificativa da decisão:** Aceita porque configurar o `PATH` permite rodar tanto o `psql` quanto o `python` diretamente de qualquer pasta no CMD, facilitando todas as próximas etapas do ETL e dos testes.
* **Como foi validado:** Após configurar a variável `PATH` do PostgreSQL, os comandos de criação do banco `verdejar` e aplicação do `insumos/schema.sql` rodaram normalmente. Após instalar o Python 3, subi o servidor local da API e validei a rota de saúde:
  ```bash
  python insumos/api_verdejar.py --dados insumos/dados
  curl "http://127.0.0.1:8000/saude"
  ```
  Resposta obtida no terminal: `{"status": "ok"}`.

### 3. Estrutura inicial do repositório, `.gitignore` e organização da documentação (Fase 0)
* **O que foi pedido à IA:** Sugestão de estrutura de pastas, modelo inicial do `README.md` e lista de proteção para o arquivo `.gitignore` seguindo as regras do desafio.
* **O que a IA propôs:** Organizar o projeto em `insumos/`, `etl/`, `tests/` e `brutos/`, configurar um `branch` separado do `main` e adicionar `brutos/`, `.env` e `.venv/` ao `.gitignore`.
* **Justificativa da decisão:** Aceita por estar totalmente alinhada à Seção 7 (Sugestão de organização) e à Seção 9 (Regras de segurança para nunca versionar senhas nem dados brutos).
* **Como foi validado:** Conferi o texto do documento v3 e verifiquei com `git status` antes do primeiro *commit* que apenas os arquivos permitidos estavam preparados para envio ao GitHub.

---

## Sugestões rejeitadas

> **[Em andamento — a preencher nas Partes 1 a 4]**
> *Regra da Parte 5: registrar no mínimo **2 sugestões rejeitadas**, informando em cada uma o trecho pedido, o que a IA propôs, por que foi inadequada (justificativa) e o que foi feito no lugar com validação.*

<!-- Modelo para preenchimento nas próximas fases:
### 1. [Título curto da sugestão rejeitada] (Parte X)
* **O que foi pedido à IA:**
* **O que a IA propôs:**
* **Justificativa da rejeição:**
* **O que fiz no lugar e como validei:**
-->

---

## Falhas e retrabalho

> **[Em andamento — a preencher nas Partes 1 a 4]**
> *Regra da Parte 5: registrar ao menos **1 falha encontrada em código proposto pela IA**, descrevendo o erro observado na execução ou nos testes e o retrabalho feito para corrigi-lo.*

<!-- Modelo para preenchimento nas próximas fases:
### 1. [Título curto da falha encontrada] (Parte X)
* **Contexto / código proposto pela IA:**
* **Falha observada (erro ou comportamento incorreto):**
* **Retrabalho realizado e validação:**
-->