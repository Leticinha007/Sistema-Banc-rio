import json
from datetime import datetime
from getpass import getpass
import hashlib
import os

class Banco:
    def __init__(self):
        self.contas = {}
        self.arquivo_dados = 'contas.json'
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega os dados do arquivo JSON ou cria um novo se não existir"""
        try:
            if os.path.exists(self.arquivo_dados):
                with open(self.arquivo_dados, 'r') as f:
                    self.contas = json.load(f)
            else:
                self.criar_conta_admin()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.criar_conta_admin()
    
    def criar_conta_admin(self):
        """Cria uma conta admin padrão"""
        senha_hash = self._hash_password('admin123')
        self.contas = {
            'admin': {
                'nome': 'Administrador',
                'senha': senha_hash,
                'saldo': 1000.0,
                'extrato': [],
                'tipo': 'admin'
            }
        }
        self.salvar_dados()
    
    def _hash_password(self, senha):
        """Gera hash SHA-256 da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def salvar_dados(self):
        """Salva os dados no arquivo JSON"""
        try:
            with open(self.arquivo_dados, 'w') as f:
                json.dump(self.contas, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
    
    def login(self):
        """Realiza o login do usuário"""
        print("\n--- Login ---")
        usuario = input("Usuário: ").strip()
        senha = getpass("Senha: ").strip()
        
        if usuario in self.contas:
            senha_hash = self._hash_password(senha)
            if self.contas[usuario]['senha'] == senha_hash:
                print(f"\nBem-vindo(a), {self.contas[usuario]['nome']}!")
                return usuario
        
        print("\nUsuário ou senha inválidos!")
        return None
    
    def criar_conta(self):
        """Cria uma nova conta de usuário"""
        print("\n--- Criar Nova Conta ---")
        usuario = input("Escolha um nome de usuário: ").strip()
        
        if usuario in self.contas:
            print("Este nome de usuário já está em uso!")
            return
        
        nome = input("Seu nome completo: ").strip()
        
        while True:
            senha = getpass("Crie uma senha: ").strip()
            if len(senha) < 6:
                print("A senha deve ter pelo menos 6 caracteres!")
                continue
                
            confirmacao = getpass("Confirme a senha: ").strip()
            if senha == confirmacao:
                break
            print("As senhas não coincidem!")
        
        senha_hash = self._hash_password(senha)
        self.contas[usuario] = {
            'nome': nome,
            'senha': senha_hash,
            'saldo': 0.0,
            'extrato': [],
            'tipo': 'cliente'
        }
        self.salvar_dados()
        print("\nConta criada com sucesso!")
    
    def menu_principal(self, usuario):
        """Menu principal do sistema bancário"""
        while True:
            saldo = self.contas[usuario]['saldo']
            print(f"\n--- Menu Principal ---")
            print(f"Saldo atual: R$ {saldo:.2f}")
            print("1 - Depósito")
            print("2 - Saque")
            print("3 - Extrato")
            print("4 - Transferência")
            print("5 - Sair")
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == '1':
                self.deposito(usuario)
            elif opcao == '2':
                self.saque(usuario)
            elif opcao == '3':
                self.extrato(usuario)
            elif opcao == '4':
                self.transferencia(usuario)
            elif opcao == '5':
                print("\nObrigado por usar nosso sistema bancário!")
                break
            else:
                print("\nOpção inválida!")
    
    def deposito(self, usuario):
        """Realiza um depósito na conta"""
        print("\n--- Depósito ---")
        try:
            valor = float(input("Valor do depósito: R$ "))
            if valor <= 0:
                print("\nO valor deve ser positivo!")
                return
                
            self.contas[usuario]['saldo'] += valor
            self.registrar_operacao(usuario, 'DEPÓSITO', valor)
            print(f"\nDepósito de R$ {valor:.2f} realizado com sucesso!")
            print(f"Novo saldo: R$ {self.contas[usuario]['saldo']:.2f}")
            self.salvar_dados()
        except ValueError:
            print("\nValor inválido! Use apenas números.")
    
    def saque(self, usuario):
        """Realiza um saque da conta"""
        print("\n--- Saque ---")
        try:
            valor = float(input("Valor do saque: R$ "))
            if valor <= 0:
                print("\nO valor deve ser positivo!")
                return
                
            if valor > self.contas[usuario]['saldo']:
                print("\nSaldo insuficiente!")
                return
                
            self.contas[usuario]['saldo'] -= valor
            self.registrar_operacao(usuario, 'SAQUE', -valor)
            print(f"\nSaque de R$ {valor:.2f} realizado com sucesso!")
            print(f"Novo saldo: R$ {self.contas[usuario]['saldo']:.2f}")
            self.salvar_dados()
        except ValueError:
            print("\nValor inválido! Use apenas números.")
    
    def transferencia(self, origem):
        """Realiza transferência entre contas"""
        print("\n--- Transferência ---")
        try:
            destino = input("Nome de usuário do destinatário: ").strip()
            if destino not in self.contas:
                print("\nConta destinatária não encontrada!")
                return
                
            if destino == origem:
                print("\nVocê não pode transferir para si mesmo!")
                return
                
            valor = float(input("Valor da transferência: R$ "))
            if valor <= 0:
                print("\nO valor deve ser positivo!")
                return
                
            if valor > self.contas[origem]['saldo']:
                print("\nSaldo insuficiente!")
                return
                
            # Realiza a transferência
            self.contas[origem]['saldo'] -= valor
            self.contas[destino]['saldo'] += valor
            
            # Registra nas duas contas
            self.registrar_operacao(origem, f'TRANSF. PARA {destino}', -valor)
            self.registrar_operacao(destino, f'TRANSF. DE {origem}', valor)
            
            print(f"\nTransferência de R$ {valor:.2f} para {destino} realizada!")
            print(f"Novo saldo: R$ {self.contas[origem]['saldo']:.2f}")
            self.salvar_dados()
        except ValueError:
            print("\nValor inválido! Use apenas números.")
    
    def extrato(self, usuario):
        """Exibe o extrato da conta"""
        print(f"\n--- Extrato Bancário ---")
        print(f"Cliente: {self.contas[usuario]['nome']}")
        print(f"Saldo atual: R$ {self.contas[usuario]['saldo']:.2f}")
        print("\nÚltimas operações:")
        print("-" * 50)
        print(f"{'Data':<20} {'Operação':<25} {'Valor':>10}")
        print("-" * 50)
        
        for op in reversed(self.contas[usuario]['extrato'][-10:]):  # Mostra as 10 últimas
            valor_formatado = f"R$ {abs(op['valor']):.2f}"
            if op['valor'] < 0:
                valor_formatado = f"-{valor_formatado}"
            else:
                valor_formatado = f"+{valor_formatado}"
            
            print(f"{op['data']:<20} {op['operacao']:<25} {valor_formatado:>10}")
        
        print("-" * 50)
    
    def registrar_operacao(self, usuario, operacao, valor):
        """Registra uma operação no extrato"""
        self.contas[usuario]['extrato'].append({
            'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'operacao': operacao,
            'valor': valor
        })

# Programa principal
if __name__ == "__main__":
    banco = Banco()
    
    while True:
        print("\n=== Sistema Bancário ===")
        print("1 - Login")
        print("2 - Criar nova conta")
        print("3 - Sair")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            usuario = banco.login()
            if usuario:
                banco.menu_principal(usuario)
        elif opcao == '2':
            banco.criar_conta()
        elif opcao == '3':
            print("\nObrigado por usar nosso sistema!")
            break
        else:
            print("\nOpção inválida!")