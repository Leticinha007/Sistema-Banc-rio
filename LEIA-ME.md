# 🪙 Sistema Bancário Python: Controle Financeiro Simplificado

## ✍🏻 Descrição 

Este projeto é um sistema bancário robusto, orientado a objetos, desenvolvido com foco em aprendizado prático e estruturação profissional de código Python. Ele simula com fidelidade operações bancárias reais, permitindo a manipulação de contas, transações e histórico de forma segura, modular e escalável.

## ⚙️ Funcionalidades Principais

- **Operações Financeiras:**

✔️ Depósitos com rastreabilidade completa (data/hora)

✔️ Saques com controle de limite diário e por valor

✔️ Histórico detalhado de transações com filtragem por tipo

✔️ Suporte a múltiplas contas por cliente

✔️ Modelo de transações orientado por interface (Transacao)

- **Gerencia de Contas:**

✔️ Conta Corrente com regras específicas de saque

✔️ Criação de contas com método fábrica

✔️ Cliente pode possuir várias contas vinculadas

✔️ Vinculação de cliente com autenticação de titularidade

- **Histórico e Relatórios:**

✔️ Armazenamento interno de transações via classe Historico

✔️ Geração de relatórios filtráveis por tipo de transação

✔️ Registro de transações usando padrão de projeto command-like

---

## 💾 Tecnologias Integradas

- **Boas Práticas de Programação:**

Uso de @property para encapsulamento de atributos

Polimorfismo com classes abstratas (ABC)

Separação de responsabilidades entre entidades (Cliente, Conta, Transação)

- **Gerenciamento de Tempo:**

Marcação precisa de data/hora de cada operação com datetime

Formatação uniforme de dados para relatórios e extratos

---

## 🪄 Próximas Melhorias
-  Implementação de transferências entre contas
- Adição de sistema de autenticação com senha e perfil
- Persistência de dados com SQLite ou JSON
- Geração de extratos e relatórios analíticos em PDF
- Interface de administração com painel de controle
