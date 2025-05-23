import json
from datetime import datetime
from getpass import getpass
import hashlib
import os
import re

class Banco:
    def __init__(self):
        self.usuarios = []
        self.contas = []
        self.arquivo_dados = 'banco_dados.json'
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega os dados do arquivo JSON ou cria um novo se não existir"""
        try:
            if os.path.exists(self.arquivo_dados):
                with open(self.arquivo_dados, 'r') as f:
                    dados = json.load(f)
                    self.usuarios = dados.get('usuarios', [])
                    self.contas = dados.get('contas', [])
            else:
                self.criar_admin_padrao()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.criar_admin_padrao()
    
    def criar_admin_padrao(self):
        """Cria um usuário admin padrão"""
        senha_hash = self._hash_password('admin123')
        admin = {
            'nome': 'Administrador',
            'login': 'admin',
            'senha': senha_hash,
            'tipo': 'admin',
            'cpf': '00000000000',
            'data_nascimento': '01/01/1900',
            'endereco': 'Admin, 0 - Sistema - Virtual/XX'
        }
        self.usuarios.append(admin)
        self.salvar_dados()
    
    def _hash_password(self, senha):
        """Gera hash SHA-256 da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def _validar_cpf(self, cpf):
        """Valida e formata o CPF para armazenar apenas números"""
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) != 11 or not cpf.isdigit():
            return None
        return cpf
    
    def _verificar_cpf_existente(self, cpf):
        """Verifica se já existe um usuário com o CPF informado"""
        return any(usuario['cpf'] == cpf for usuario in self.usuarios)
    
    def salvar_dados(self):
        """Salva os dados no arquivo JSON"""
        try:
            with open(self.arquivo_dados, 'w') as f:
                json.dump({
                    'usuarios': self.usuarios,
                    'contas': self.contas
                }, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")

    # Funções para usuários
    def criar_usuario(self):
        """Cria um novo usuário (cliente) com todos os dados solicitados"""
        print("\n--- Cadastro de Novo Usuário ---")
        
        # Dados pessoais
        nome = input("Nome completo: ").strip()
        
        while True:
            cpf = input("CPF (apenas números): ").strip()
            cpf = self._validar_cpf(cpf)
            if not cpf:
                print("CPF inválido! Deve conter 11 dígitos numéricos.")
                continue
            if self._verificar_cpf_existente(cpf):
                print("Já existe um usuário cadastrado com este CPF!")
                continue
            break
        
        data_nascimento = input("Data de nascimento (DD/MM/AAAA): ").strip()
        
        # Construção do endereço
        print("\nEndereço:")
        logradouro = input("Logradouro (Rua/Av.): ").strip()
        numero = input("Número: ").strip()
        bairro = input("Bairro: ").strip()
        cidade = input("Cidade: ").strip()
        estado = input("Sigla do Estado (XX): ").strip().upper()
        endereco = f"{logradouro}, {numero} - {bairro} - {cidade}/{estado}"
        
        # Dados de login
        login = input("\nNome de usuário para login: ").strip()
        if any(usuario['login'] == login for usuario in self.usuarios):
            print("Este nome de usuário já está em uso!")
            return
        
        while True:
            senha = getpass("Senha (mínimo 6 caracteres): ").strip()
            if len(senha) < 6:
                print("A senha deve ter pelo menos 6 caracteres!")
                continue
                
            confirmacao = getpass("Confirme a senha: ").strip()
            if senha == confirmacao:
                break
            print("As senhas não coincidem!")
        
        novo_usuario = {
            'nome': nome,
            'login': login,
            'senha': self._hash_password(senha),
            'tipo': 'cliente',
            'cpf': cpf,
            'data_nascimento': data_nascimento,
            'endereco': endereco
        }
        
        self.usuarios.append(novo_usuario)
        self.salvar_dados()
        
        # Cria uma conta corrente automaticamente para o novo usuário
        self.criar_conta(cpf)
        
        print("\nUsuário cadastrado com sucesso!")
        print("Uma conta corrente foi criada automaticamente.")
    
    # Funções para contas
    def criar_conta(self, cpf_usuario, tipo='corrente', saldo_inicial=0.0):
        """Cria uma nova conta bancária vinculada ao CPF do usuário"""
        numero_conta = str(datetime.now().timestamp()).replace('.', '')[-6:]
        agencia = '0001'
        
        nova_conta = {
            'agencia': agencia,
            'numero': numero_conta,
            'cpf_usuario': cpf_usuario,
            'tipo': tipo,
            'saldo': saldo_inicial,
            'extrato': []
        }
        
        self.contas.append(nova_conta)
        self.salvar_dados()
        return numero_conta
    
    def encontrar_contas_por_cpf(self, cpf):
        """Retorna todas as contas vinculadas a um CPF"""
        return [conta for conta in self.contas if conta['cpf_usuario'] == cpf]
    
    def encontrar_usuario_por_login(self, login):
        """Retorna um usuário pelo login"""
        for usuario in self.usuarios:
            if usuario['login'] == login:
                return usuario
        return None
    
    def selecionar_conta(self, cpf):
        """Permite ao usuário selecionar uma de suas contas"""
        contas_usuario = self.encontrar_contas_por_cpf(cpf)
        
        if not contas_usuario:
            print("Você não tem contas cadastradas!")
            return None
            
        if len(contas_usuario) == 1:
            return contas_usuario[0]
            
        print("\nSuas contas:")
        for i, conta in enumerate(contas_usuario, 1):
            print(f"{i} - {conta['tipo'].upper()} (Ag: {conta['agencia']} C/C: {conta['numero']}) - Saldo: R$ {conta['saldo']:.2f}")
        
        try:
            opcao = int(input("Selecione a conta: ")) - 1
            return contas_usuario[opcao]
        except (ValueError, IndexError):
            print("Opção inválida!")
            return None

    # Operações bancárias (mantidas conforme especificado anteriormente)
    def depositar(self, conta_num, valor, /):  # Positional only
        """Realiza um depósito na conta especificada"""
        for conta in self.contas:
            if conta['numero'] == conta_num:
                try:
                    if valor <= 0:
                        print("\nO valor deve ser positivo!")
                        return False
                        
                    conta['saldo'] += valor
                    self.registrar_operacao(conta_num, 'DEPÓSITO', valor)
                    print(f"\nDepósito de R$ {valor:.2f} realizado com sucesso!")
                    print(f"Novo saldo: R$ {conta['saldo']:.2f}")
                    self.salvar_dados()
                    return True
                except ValueError:
                    print("\nValor inválido!")
                    return False
        print("\nConta não encontrada!")
        return False

    def sacar(self, *, conta_num, valor):  # Keyword only
        """Realiza um saque da conta especificada"""
        for conta in self.contas:
            if conta['numero'] == conta_num:
                try:
                    if valor <= 0:
                        print("\nO valor deve ser positivo!")
                        return False
                        
                    if valor > conta['saldo']:
                        print("\nSaldo insuficiente!")
                        return False
                        
                    conta['saldo'] -= valor
                    self.registrar_operacao(conta_num, 'SAQUE', -valor)
                    print(f"\nSaque de R$ {valor:.2f} realizado com sucesso!")
                    print(f"Novo saldo: R$ {conta['saldo']:.2f}")
                    self.salvar_dados()
                    return True
                except ValueError:
                    print("\nValor inválido!")
                    return False
        print("\nConta não encontrada!")
        return False

    def visualizar_extrato(self, conta_num, /, *, detalhado=False):  # Misto
        """Exibe o extrato da conta especificada"""
        conta = None
        for c in self.contas:
            if c['numero'] == conta_num:
                conta = c
                break
                
        if not conta:
            print("\nConta não encontrada!")
            return
            
        usuario = None
        for u in self.usuarios:
            if u['cpf'] == conta['cpf_usuario']:
                usuario = u
                break
        
        print(f"\n--- Extrato da Conta {conta_num} ---")
        print(f"Agência: {conta['agencia']} | Conta: {conta['numero']}")
        print(f"Tipo: {conta['tipo'].upper()}")
        
        if detalhado and usuario:
            print(f"\nCliente: {usuario['nome']}")
            print(f"CPF: {usuario['cpf']}")
            print(f"Endereço: {usuario['endereco']}")
            print(f"Data/hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        print(f"\nSaldo atual: R$ {conta['saldo']:.2f}")
        print("\nHistórico de operações:")
        print("-" * 60)
        print(f"{'Data':<20} {'Operação':<25} {'Valor':>12}")
        print("-" * 60)
        
        for op in conta['extrato']:
            valor_formatado = f"R$ {abs(op['valor']):.2f}"
            valor_formatado = f"-{valor_formatado}" if op['valor'] < 0 else f"+{valor_formatado}"
            print(f"{op['data']:<20} {op['operacao']:<25} {valor_formatado:>12}")
        
        print("-" * 60)
    
    def registrar_operacao(self, conta_num, operacao, valor):
        """Registra uma operação no extrato da conta"""
        for conta in self.contas:
            if conta['numero'] == conta_num:
                conta['extrato'].append({
                    'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'operacao': operacao,
                    'valor': valor
                })
                break

    # Interface principal
    def login(self):
        """Realiza o login do usuário"""
        print("\n--- Login ---")
        login = input("Usuário: ").strip()
        senha = getpass("Senha: ").strip()
        
        usuario = self.encontrar_usuario_por_login(login)
        if usuario and usuario['senha'] == self._hash_password(senha):
            print(f"\nBem-vindo(a), {usuario['nome']}!")
            return usuario
        
        print("\nUsuário ou senha inválidos!")
        return None
    
    def menu_principal(self, usuario):
        """Menu principal do sistema bancário"""
        while True:
            print("\n--- Menu Principal ---")
            print(f"Cliente: {usuario['nome']}")
            print("1 - Operações Bancárias")
            print("2 - Criar Nova Conta")
            print("3 - Sair")
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == '1':
                self.menu_operacoes(usuario)
            elif opcao == '2':
                self.criar_conta(usuario['cpf'])
                print("Nova conta corrente criada com sucesso!")
            elif opcao == '3':
                print("\nObrigado por usar nosso sistema bancário!")
                break
            else:
                print("\nOpção inválida!")
    
    def menu_operacoes(self, usuario):
        """Menu de operações bancárias"""
        conta = self.selecionar_conta(usuario['cpf'])
        if not conta:
            return
            
        while True:
            print(f"\n--- Operações Bancárias ---")
            print(f"Ag: {conta['agencia']} C/C: {conta['numero']} | Saldo: R$ {conta['saldo']:.2f}")
            print("1 - Depósito")
            print("2 - Saque")
            print("3 - Extrato simples")
            print("4 - Extrato detalhado")
            print("5 - Voltar")
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == '1':
                try:
                    valor = float(input("Valor do depósito: R$ "))
                    self.depositar(conta['numero'], valor)  # Chamada positional only
                except ValueError:
                    print("Valor inválido!")
                    
            elif opcao == '2':
                try:
                    valor = float(input("Valor do saque: R$ "))
                    self.sacar(conta_num=conta['numero'], valor=valor)  # Chamada keyword only
                except ValueError:
                    print("Valor inválido!")
                    
            elif opcao == '3':
                self.visualizar_extrato(conta['numero'])  # Positional
                
            elif opcao == '4':
                self.visualizar_extrato(conta['numero'], detalhado=True)  # Positional + keyword
                
            elif opcao == '5':
                break
            else:
                print("\nOpção inválida!")

# Programa principal
if __name__ == "__main__":
    banco = Banco()
    
    while True:
        print("\n=== Sistema Bancário ===")
        print("1 - Login")
        print("2 - Criar novo usuário")
        print("3 - Sair")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            usuario = banco.login()
            if usuario:
                banco.menu_principal(usuario)
        elif opcao == '2':
            banco.criar_usuario()
        elif opcao == '3':
            print("\nObrigado por usar nosso sistema!")
            break
        else:
            print("\nOpção inválida!")