from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict
import json
import os

# ----------------------------
# Transações e Histórico
# ----------------------------

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self) -> float:
        pass

    @abstractmethod
    def registrar(self, conta: 'Conta') -> bool:
        pass

class Historico:
    def __init__(self):
        self.transacoes: List[Dict[str, str | float]] = []

    def adicionar(self, transacao: Transacao):
        self.transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
        })

    def listar(self, tipo: Optional[str] = None) -> List[Dict]:
        if tipo:
            return [t for t in self.transacoes if t["tipo"] == tipo]
        return self.transacoes

# ----------------------------
# Conta e Cliente
# ----------------------------

class Conta:
    def __init__(self, numero: int, cliente: 'Cliente', agencia: str = "0001"):
        self.numero = numero
        self.agencia = agencia
        self.cliente = cliente
        self.saldo = 0.0
        self.historico = Historico()

    def sacar(self, valor: float) -> bool:
        if valor <= 0 or valor > self.saldo:
            return False
        self.saldo -= valor
        return True

    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            return False
        self.saldo += valor
        return True

    def transferir(self, valor: float, destino: 'Conta') -> bool:
        if self.sacar(valor):
            destino.depositar(valor)
            return True
        return False

class ContaCorrente(Conta):
    def __init__(self, numero: int, cliente: 'Cliente', limite: float = 500.0, limite_saques: int = 3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
        self.saques_realizados = 0

    def sacar(self, valor: float) -> bool:
        if self.saques_realizados >= self.limite_saques or valor > self.limite:
            return False
        if super().sacar(valor):
            self.saques_realizados += 1
            return True
        return False

class Cliente:
    def __init__(self, nome: str, cpf: str, senha: str, endereco: str):
        self.nome = nome
        self.cpf = cpf
        self.senha = senha
        self.endereco = endereco
        self.contas: List[Conta] = []

    def autenticar(self, senha: str) -> bool:
        return self.senha == senha

    def adicionar_conta(self, conta: Conta):
        self.contas.append(conta)

    def realizar_transacao(self, conta: Conta, transacao: Transacao) -> bool:
        if conta in self.contas:
            sucesso = transacao.registrar(conta)
            if sucesso:
                conta.historico.adicionar(transacao)
            return sucesso
        return False

# ----------------------------
# Transações concretas
# ----------------------------

class Deposito(Transacao):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: Conta) -> bool:
        return conta.depositar(self._valor)

class Saque(Transacao):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: Conta) -> bool:
        return conta.sacar(self._valor)

# ----------------------------
# Persistência de Dados
# ----------------------------

class Banco:
    def __init__(self, arquivo_dados: str = "banco_dados.json"):
        self.arquivo_dados = arquivo_dados
        self.clientes: Dict[str, Cliente] = {}
        self.contas: List[Conta] = []
        self.carregar_dados()

    def salvar_dados(self):
        dados = {
            "clientes": [vars(c) for c in self.clientes.values()]
        }
        with open(self.arquivo_dados, "w") as f:
            json.dump(dados, f, indent=4)

    def carregar_dados(self):
        if os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados) as f:
                dados = json.load(f)
                for c in dados["clientes"]:
                    cliente = Cliente(c['nome'], c['cpf'], c['senha'], c['endereco'])
                    self.clientes[c['cpf']] = cliente

    def cadastrar_cliente(self, nome: str, cpf: str, senha: str, endereco: str):
        if cpf in self.clientes:
            print("CPF já cadastrado.")
            return None
        cliente = Cliente(nome, cpf, senha, endereco)
        self.clientes[cpf] = cliente
        self.salvar_dados()
        return cliente

    def criar_conta_corrente(self, cpf: str) -> Optional[Conta]:
        cliente = self.clientes.get(cpf)
        if not cliente:
            print("Cliente não encontrado.")
            return None
        conta = ContaCorrente(numero=len(self.contas) + 1, cliente=cliente)
        cliente.adicionar_conta(conta)
        self.contas.append(conta)
        self.salvar_dados()
        return conta

    def autenticar_cliente(self, cpf: str, senha: str) -> Optional[Cliente]:
        cliente = self.clientes.get(cpf)
        if cliente and cliente.autenticar(senha):
            return cliente
        return None
