from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List

# Interface Transacao
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self) -> float:
        pass
    
    @abstractmethod
    def registrar(self, conta) -> bool:
        pass

# Classe Historico
class Historico:
    def __init__(self):
        self._transacoes: List[dict] = []
    
    def adicionar_transacao(self, transacao: Transacao) -> None:
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
        )
    
    def gerar_relatorio(self) -> List[dict]:
        return self._transacoes

# Classe Conta
class Conta:
    def __init__(self, cliente, numero: int, agencia: str = "0001"):
        self._saldo: float = 0.0
        self._numero: int = numero
        self._agencia: str = agencia
        self._cliente = cliente
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls, cliente, numero: int) -> 'Conta':
        return cls(cliente, numero)
    
    @property
    def saldo(self) -> float:
        return self._saldo
    
    @property
    def numero(self) -> int:
        return self._numero
    
    @property
    def agencia(self) -> str:
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self) -> Historico:
        return self._historico
    
    def sacar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
        
        if self._saldo < valor:
            print("\n@@@ Operação falhou! Saldo insuficiente. @@@")
            return False
        
        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True
    
    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
        
        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True

# Classe ContaCorrente
class ContaCorrente(Conta):
    def __init__(self, cliente, numero: int, limite: float = 500.0, limite_saques: int = 3):
        super().__init__(cliente, numero)
        self._limite: float = limite
        self._limite_saques: int = limite_saques
        self._saques_realizados: int = 0
    
    def sacar(self, valor: float) -> bool:
        if self._saques_realizados >= self._limite_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
            return False
        
        if valor > self._limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False
        
        if super().sacar(valor):
            self._saques_realizados += 1
            return True
        
        return False

# Classe Deposito
class Deposito(Transacao):
    def __init__(self, valor: float):
        self._valor = valor
    
    @property
    def valor(self) -> float:
        return self._valor
    
    def registrar(self, conta) -> bool:
        sucesso = conta.depositar(self.valor)
        
        if sucesso:
            conta.historico.adicionar_transacao(self)
        
        return sucesso

# Classe Saque
class Saque(Transacao):
    def __init__(self, valor: float):
        self._valor = valor
    
    @property
    def valor(self) -> float:
        return self._valor
    
    def registrar(self, conta) -> bool:
        sucesso = conta.sacar(self.valor)
        
        if sucesso:
            conta.historico.adicionar_transacao(self)
        
        return sucesso

# Classe Cliente
class Cliente:
    def __init__(self, endereco: str):
        self._endereco: str = endereco
        self._contas: List[Conta] = []
    
    def realizar_transacao(self, conta: Conta, transacao: Transacao) -> bool:
        if conta not in self._contas:
            print("\n@@@ Operação falhou! Conta não pertence ao cliente. @@@")
            return False
        
        return transacao.registrar(conta)
    
    def adicionar_conta(self, conta: Conta) -> None:
        self._contas.append(conta)
    
    @property
    def contas(self) -> List[Conta]:
        return self._contas
    
    @property
    def endereco(self) -> str:
        return self._endereco

# Classe PessoaFisica
class PessoaFisica(Cliente):
    def __init__(self, cpf: str, nome: str, data_nascimento: date, endereco: str):
        super().__init__(endereco)
        self._cpf: str = cpf
        self._nome: str = nome
        self._data_nascimento: date = data_nascimento
    
    @property
    def cpf(self) -> str:
        return self._cpf
    
    @property
    def nome(self) -> str:
        return self._nome
    
    @property
    def data_nascimento(self) -> date:
        return self._data_nascimento

# Sistema Bancário
class Banco:
    def __init__(self):
        self._clientes: List[Cliente] = []
        self._contas: List[Conta] = []
    
    def criar_cliente(self, cpf: str, nome: str, data_nascimento: date, endereco: str) -> PessoaFisica:
        cliente = PessoaFisica(cpf, nome, data_nascimento, endereco)
        self._clientes.append(cliente)
        return cliente
    
    def criar_conta_corrente(self, cliente: Cliente, numero: int) -> ContaCorrente:
        conta = ContaCorrente(cliente, numero)
        cliente.adicionar_conta(conta)
        self._contas.append(conta)
        return conta
    
    def listar_contas(self) -> List[Conta]:
        return self._contas
    
    def listar_clientes(self) -> List[Cliente]:
        return self._clientes 
