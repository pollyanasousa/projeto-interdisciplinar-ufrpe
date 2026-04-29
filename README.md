<div align="center">

<img src="https://img.shields.io/badge/Python-3.x-2E7D32?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Status-Release%201-4CAF50?style=for-the-badge"/>
<img src="https://img.shields.io/badge/UFRPE-PISI1-795548?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Agronomia-Agrobook-8D6E63?style=for-the-badge"/>

```
------------------------------------------------------------------
|*************************** AGROBOOK ***************************|
|                                                                |
| Organizando a produção rural para gerar dados e oportunidades. |
|                                                                |
|****************************************************************|
------------------------------------------------------------------
```

</div>

---

## 📌 Sobre o projeto

O **AGROBOOK** é um caderno digital desenvolvido para auxiliar agricultores no registro e organização da produção rural. O sistema permite cadastrar áreas de plantio, registrar plantios, colheitas e gastos, além de gerar um relatório completo da safra em HTML.

Projeto desenvolvido para a disciplina **PISI1 — Projeto Interdisciplinar para Sistemas de Informação 1** da **UFRPE**, 2026.

---

## 👨‍💻 Desenvolvedores

| Nome | GitHub |
|------|--------|
| Gabriel Soares | [@GS-bit](https://github.com/GS-bit) |
| Pollyana Cassia | [@pollyanasousa](https://github.com/pollyanasousa) |

**Professor:** Cleyton Vanut

---

## 🚀 Como executar

```bash
# Clone o repositório
git clone https://github.com/pollyanasousa/projeto-interdisciplinar-ufrpe.git

# Entre na pasta do projeto
cd projeto-interdisciplinar-ufrpe

# Execute o sistema
python3 main.py
```

> A pasta `data/` e os arquivos JSON são criados automaticamente na primeira execução.

---

## ✅ Funcionalidades — Release 1

| Requisito | Descrição | Status |
|-----------|-----------|--------|
| RF001 | Cadastro do agricultor com validação de CPF, telefone, cidade e estado | ✅ Pronta |
| RF002 | Gerenciamento de áreas de plantio (CRUD completo) | ✅ Pronta |
| RF003 | Registro de plantios (CRUD completo) | ✅ Pronta |
| RF004 | Colheita e gastos (CRUD completo) | ✅ Pronta |
| RF005 | Geração de relatório de safra em HTML | ✅ Pronta |

## 🔜 Funcionalidades — Release 2

| Requisito | Descrição | Status |
|-----------|-----------|--------|
| RF006 | Gamificação | 🔄 A fazer |
| RF007 | Interface por voz | 🔄 A fazer |

---

## 🗂️ Estrutura do projeto

```
├── main.py               ← porta de entrada do sistema
├── model/
│   ├── farmer.py         ← classe do agricultor (centro do sistema)
│   ├── area.py           ← classe das áreas de plantio
│   ├── planting.py       ← classe dos plantios
│   ├── harvest.py        ← classe das colheitas
│   ├── expense.py        ← classe dos gastos
│   └── report.py         ← classe do relatório de safra
├── utils/
│   ├── validators.py     ← validação de CPF, telefone, datas e nomes
│   ├── menu.py           ← função de exibição de menus
│   ├── textprocessor.py  ← capitalização de texto respeitando preposições
│   └── io.py             ← função de entrada de números inteiros
├── data/                 ← criada automaticamente ao rodar o sistema
└── doc/
    └── planilha_funcionalidades_agrobook.xlsx
```

---

## 🛠️ Bibliotecas utilizadas

Todas as bibliotecas utilizadas são **nativas do Python** — não é necessário instalar nenhuma dependência externa.

| Biblioteca | Arquivo | Objetivo |
|------------|---------|----------|
| `json` | farmer.py, area.py, planting.py, harvest.py, expense.py | Leitura e escrita dos dados nos arquivos JSON |
| `re` | validators.py | Validação de CPF, telefone e datas com expressões regulares |
| `datetime` | validators.py | Verificação se a data existe no calendário |
| `string` | textprocessor.py | Capitalização de nomes com `capwords` |
| `os` | main.py | Criação automática da pasta `data/` na primeira execução |
| `webbrowser` | report.py | Abertura do relatório HTML no navegador |
| `sys` | main.py | Encerramento seguro do programa |

---

## 🔍 Destaques do projeto

### Validação de CPF matemática
O sistema valida o CPF calculando os **dígitos verificadores** — a mesma lógica usada pela Receita Federal. CPFs inventados são rejeitados.

```python
# validators.py
_sum = 0
for i, weight in enumerate(range(10, 1, -1)):
    _sum += int(cpf[i]) * weight
remainder = (_sum * 10) % 11
first_digit = remainder if remainder < 10 else 0
```

### Proteção de dados entre módulos
A área não pode ser removida se estiver em uso por um plantio. Isso é garantido pela conexão entre os objetos via `link_to_planting`.

```python
# area.py
for planting in self.planting.list_of_planting:
    if planting["area"] == self.list_of_area[_id]["name"]:
        print("Não é possível remover a área: ela já está em uso por um plantio.")
        return
```

### Relatório de safra em HTML
O sistema gera automaticamente um relatório completo em HTML com todos os dados cadastrados, que pode ser aberto direto no navegador.

---

<div align="center">
  <sub>Feito com 💚 por Gabriel Soares e Pollyana Cassia — UFRPE 2026</sub>
</div>