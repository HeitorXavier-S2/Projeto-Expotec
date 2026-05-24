import mysql.connector
from datetime import datetime

def painel_administrador(conexao, id_usuario_logado):
    while True:
        print("\n===================  PAINEL DE CONTROLE GERAL ===================")
        print("1. Listar todos os usuários da plataforma")
        print("2. Atualizar dados de um usuário")
        print("3. Promover usuário a Administrador")
        print("4. Banir (Excluir) usuário da plataforma")
        print("5. Gerenciar Grupos: Remover Grupo")
        print("0. Voltar ao menu principal")
        
        escolha = input("\nEscolha uma opção de segurança: ").strip()
        
        if escolha == "0":
            break
            
        elif escolha == "1":
            listar_usuarios(conexao)
            input("\nPressione Enter para voltar ao menu...")
            
        elif escolha == "2":
            atualizar_usuario(conexao)
            
        elif escolha == "3":
            promover_usuario(conexao, id_usuario_logado)
            
        elif escolha == "4":
            banir_usuario(conexao, id_usuario_logado)
            
        elif escolha == "5":
            remover_grupo(conexao)
            
        else:
            print("Opção inválida.")

def listar_usuarios(conexao):
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id_usuario, nome_usuario, email_usuario, admin_usuario,
                   DATE_FORMAT(dt_nascimento_usuario, '%d/%m/%Y') AS nascimento
            FROM tbl_usuario
            ORDER BY id_usuario
        """)
        usuarios = cursor.fetchall()
        
        print("\n|=---- BASE DE USUÁRIOS DO ORBITLIT ----=|")
        for u in usuarios:
            cargo = "👑 ADMIN" if u['admin_usuario'] else "Leitor"
            print(f"[{u['id_usuario']}] {u['nome_usuario']} ({u['email_usuario']}) | Nasc: {u['nascimento']} | Status: {cargo}")
        print("-" * 50)
        
    except mysql.connector.Error as e:
        print(f"Erro ao listar usuários: {e}")
    finally:
        cursor.close()

def atualizar_usuario(conexao):
    listar_usuarios(conexao)
    id_usuario = input("Digite o ID do usuário que deseja ATUALIZAR (ou 0 para cancelar): ").strip()
    
    if id_usuario == "0" or not id_usuario.isdigit():
        return
        
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT nome_usuario, email_usuario, bio_usuario, DATE_FORMAT(dt_nascimento_usuario, '%Y-%m-%d') as dt_nascimento FROM tbl_usuario WHERE id_usuario = %s", (int(id_usuario),))
        usuario = cursor.fetchone()
        
        if not usuario:
            print("\nUsuário não encontrado.")
            return
            
        print(f"\n|=---- ATUALIZANDO: {usuario['nome_usuario']} ----=|")
        print("Dica: Deixe em branco e aperte Enter para manter a informação atual.")
        
        novo_nome = input(f"Nome [{usuario['nome_usuario']}]: ").strip()
        novo_email = input(f"E-mail [{usuario['email_usuario']}]: ").strip()
        nova_bio = input(f"Bio [{usuario['bio_usuario']}]: ").strip()
        
        while True:
            nova_dt = input(f"Data de Nascimento [{usuario['dt_nascimento']}] (YYYY-MM-DD): ").strip()
            if not nova_dt: 
                break
            try:
                datetime.strptime(nova_dt, "%Y-%m-%d")
                break
            except ValueError:
                print("Formato de data inválido. Use YYYY-MM-DD (Ex: 1995-04-12).")
            
        nome_final = novo_nome if novo_nome else usuario['nome_usuario']
        email_final = novo_email if novo_email else usuario['email_usuario']
        bio_final = nova_bio if nova_bio else usuario['bio_usuario']
        dt_final = nova_dt if nova_dt else usuario['dt_nascimento']
        
        cursor.execute("""
            UPDATE tbl_usuario 
            SET nome_usuario = %s, email_usuario = %s, bio_usuario = %s, dt_nascimento_usuario = %s 
            WHERE id_usuario = %s
        """, (nome_final, email_final, bio_final, dt_final, int(id_usuario)))
        
        conexao.commit()
        print("\nDados do usuário atualizados com sucesso!")
        
    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao atualizar usuário: {e}")
    finally:
        cursor.close()
        input("\nPressione Enter para continuar...")

def promover_usuario(conexao, id_usuario_logado):
    listar_usuarios(conexao)
    id_usuario = input("Digite o ID do usuário que deseja PROMOVER a Admin (ou 0 para cancelar): ").strip()
    
    if id_usuario == "0" or not id_usuario.isdigit():
        return
        
    if int(id_usuario) == id_usuario_logado:
        print("\nVocê já é um administrador!")
        return

    cursor = conexao.cursor()
    try:
        cursor.execute("UPDATE tbl_usuario SET admin_usuario = TRUE WHERE id_usuario = %s", (int(id_usuario),))
        conexao.commit()
        
        if cursor.rowcount == 0:
            print("\nUsuário não encontrado.")
        else:
            print(f"\nSucesso! O usuário ID {id_usuario} agora tem privilégios de Administrador.")
            
    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao promover usuário: {e}")
    finally:
        cursor.close()
        input("\nPressione Enter para continuar...")

def banir_usuario(conexao, id_usuario_logado):
    print("\nAVISO: O banimento excluirá a conta, a estante e as resenhas do usuário.")
    listar_usuarios(conexao)
    
    id_usuario = input("Digite o ID do usuário que deseja BANIR (ou 0 para cancelar): ").strip()
    
    if id_usuario == "0" or not id_usuario.isdigit():
        return
        
    if int(id_usuario) == id_usuario_logado:
        print("\nErro de Segurança: Você não pode banir a si mesmo.")
        return

    certeza = input(f"Tem certeza absoluta que deseja excluir o usuário ID {id_usuario} permanentemente? (S/N): ").strip().upper()
    if certeza != "S":
        print("Operação de banimento cancelada.")
        return

    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM tbl_usuario WHERE id_usuario = %s AND admin_usuario = FALSE", (int(id_usuario),))
        
        if cursor.rowcount == 0:
            print("\nFalha: Usuário não encontrado ou é um Administrador protegido.")
        else:
            conexao.commit()
            print(f"\nUsuário ID {id_usuario} foi excluído da plataforma.")
            
    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao banir usuário: {e}")
    finally:
        cursor.close()
        input("\nPressione Enter para continuar...")

def remover_grupo(conexao):
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_grupo, nome_grupo FROM tbl_grupos ORDER BY id_grupo")
        grupos = cursor.fetchall()
        
        if not grupos:
            print("\nNão há grupos cadastrados na plataforma.")
            return
            
        print("\n|=---- GRUPOS DA PLATAFORMA ----=|")
        for g in grupos:
            print(f"[{g['id_grupo']}] {g['nome_grupo']}")
            
        id_grupo = input("\nDigite o ID do grupo que deseja REMOVER (ou 0 para cancelar): ").strip()
        
        if id_grupo == "0" or not id_grupo.isdigit():
            return
            
        certeza = input(f"Tem certeza que deseja apagar o grupo ID {id_grupo} e todas as suas metas e membros? (S/N): ").strip().upper()
        if certeza != "S":
            print("Operação cancelada.")
            return
            
        cursor.execute("DELETE FROM tbl_grupos WHERE id_grupo = %s", (int(id_grupo),))
        if cursor.rowcount == 0:
            print("\nGrupo não encontrado.")
        else:
            conexao.commit()
            print("\nGrupo removido com sucesso de todo o sistema!")
            
    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao remover grupo: {e}")
    finally:
        cursor.close()
        input("\nPressione Enter para continuar...")