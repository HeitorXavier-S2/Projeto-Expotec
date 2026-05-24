from banco_de_dados.conexao import conectar, fechar_conexao
import re
import mysql.connector

def cadastrar_usuario(conexao):
    print("\n=================== CADASTRO DE NOVO LEITOR ===================")
    
    nome = input("Nome completo: ").strip()

    while True:
        email = input("E-mail: ").strip()
        padrao_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(padrao_email, email):
            break
        print("Formato de e-mail inválido. Tente novamente (ex: nome@email.com).")
    
    while True:
        dt_nascimento = input("Data de nascimento (YYYY-MM-DD): ").strip()
        if len(dt_nascimento) == 10: 
            break
        print("Formato inválido. Use YYYY-MM-DD.")
        
    senha = input("Crie uma senha: ").strip()
    
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "INSERT INTO tbl_usuario (nome_usuario, email_usuario, dt_nascimento_usuario, senha_usuario) VALUES (%s, %s, %s, %s)",
            (nome, email, dt_nascimento, senha)
        )
        conexao.commit()
        print(f"\nBem-vindo(a) à comunidade OrbitLit, {nome}! Seu cadastro foi realizado.")
    except mysql.connector.IntegrityError:
        conexao.rollback()
        print("\nEste e-mail já está cadastrado no nosso sistema.")
    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"\nErro no banco de dados: {e}")
    finally:
        cursor.close()

def fazer_login(conexao):
    print("\n=================== LOGIN - ORBITLIT ===================")
    
    email = input("E-mail: ").strip()
    senha = input("Senha: ").strip()
    
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id_usuario, nome_usuario, admin_usuario FROM tbl_usuario WHERE email_usuario = %s AND senha_usuario = %s",
            (email, senha)
        )
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"\nLogin efetuado com sucesso! Olá, {usuario['nome_usuario']}.")
            return usuario
        else:
            print("\nE-mail ou senha incorretos.")
            return None
            
    except mysql.connector.Error as e:
        print(f"\nErro ao acessar o banco de dados: {e}")
        return None
    finally:
        cursor.close()

def painel_do_usuario(conexao, usuario):
    admin = bool(usuario['admin_usuario'])
    id_user = usuario['id_usuario']
    
    while True:
        print(f"\n=================== PAINEL PRINCIPAL - Olá, {usuario['nome_usuario']}! ===================")
        if admin:
            print("👑 [Status: Conta de Administrador]")
        print("1. Explorar Acervo de Livros")
        print("2. Meu Perfil e Estante")
        print("3. Gerenciar Leituras Ativas (Atualizar Páginas / Remover)")
        print("4. Editar Perfil")
        print("5. Meus Grupos e Comunidades")
        if admin:
            print("6. Gestão Geral da Plataforma (Moderação)")
        print("0. Fazer Logout")
        
        escolha = input("\nPara onde deseja ir? ").strip()
        
        if escolha == "0":
            print("\nFazendo logout... Até logo!")
            break
            
        elif escolha == "1":
            import livrosV2
            livrosV2.iniciar(conexao, admin, id_user)
            
        elif escolha == "2":
            import perfil
            perfil.exibir_perfil(conexao, id_user)

        elif escolha == "3":
            import estante
            estante.gerenciar_leituras(conexao, id_user)
            
        elif escolha == "4":
            import perfil
            perfil.editar_perfil(conexao, id_user)
            
        elif escolha == "5":
            import grupos
            grupos.painel_comunidades(conexao, id_user)

        elif escolha == "6" and admin:
            import admin as painel_admin
            painel_admin.painel_administrador(conexao, id_user)
            
        else:
            print("Opção inválida.")

def menu_principal():
    conexao = conectar()
    if not conexao:
        print("Falha fatal: Não foi possível conectar ao banco de dados.")
        return

    while True:
        print("\n=================== BEM-VINDO AO ORBITLIT ===================")
        print("1. Fazer Login")
        print("2. Criar uma Conta")
        print("0. Sair")
        print("[Conta ADMIN]: email - joao@orbitlit.com  |  senha - senha123")
        
        escolha = input("\nEscolha uma opção: ").strip()
        
        if escolha == "0":
            print("Saindo do OrbitLit... Até a próxima leitura!")
            break
            
        elif escolha == "1":
            usuario_logado = fazer_login(conexao)
            
            if usuario_logado:
                input("\nPressione Enter para entrar no OrbitLit...")
                
                painel_do_usuario(conexao, usuario_logado)
                
        elif escolha == "2":
            cadastrar_usuario(conexao)
            print()
            input("\nPressione Enter para continuar...")
            
        else:
            print("Opção inválida.")

    fechar_conexao(conexao)

if __name__ == "__main__":
    menu_principal()

#Lembre de alterar o arqivo livros pra exibir a nota do livro na hora de listar e buscar
#lembre de ver como vai ser pra adicionar livros a estante, atualizar e remover
#lembre de usar o regex no email
#criar menu pro adm gerenciar usuarios 
#lembre de criar a parte de gerenciar grupos
#analisar de novo comos os grupos devem se conectar aos livros pela meta de leitura. Eles podem ter mais de um livro?