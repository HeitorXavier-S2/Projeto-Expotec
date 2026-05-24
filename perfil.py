import mysql.connector

def exibir_perfil(conexao, id_usuario_logado):
    cursor = conexao.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT nome_usuario, DATE_FORMAT(dt_nascimento_usuario, '%d/%m/%Y') AS nascimento, bio_usuario 
            FROM tbl_usuario 
            WHERE id_usuario = %s
        """, (id_usuario_logado,))
        usuario = cursor.fetchone()

        if not usuario:
            print("Erro: Usuário não encontrado.")
            return

        print(f"\n=================== PERFIL DE {usuario['nome_usuario'].upper()} ===================")
        print(f"Nascimento: {usuario['nascimento']}")
        print(f"Bio: {usuario['bio_usuario']}")
        print("-" * 60)

        print("MINHA ESTANTE:")
        cursor.execute("""
            SELECT l.titulo_livro, l.total_paginas, e.concluido_leitura, e.pg_lidas_leitura
            FROM tbl_leituras e
            INNER JOIN tbl_livros l ON e.id_livro = l.id_livro
            WHERE e.id_usuario = %s
        """, (id_usuario_logado,))
        estante = cursor.fetchall()

        if not estante:
            print("Sua estante está vazia. Vá explorar o acervo!")
        else:
            for livro in estante:
                if livro['concluido_leitura']:
                    status = "Lido (100% concluído)"
                elif livro['pg_lidas_leitura'] > 0:
                    porcentagem = (livro['pg_lidas_leitura'] / livro['total_paginas']) * 100 if livro['total_paginas'] > 0 else 0
                    status = f"Lendo ({porcentagem:.1f}% concluído)"
                else:
                    status = "Quero Ler"
                    
                print(f"  {livro['titulo_livro']}")
                print(f"  Status: {status} | Páginas Lidas: {livro['pg_lidas_leitura']}/{livro['total_paginas']}")
        
        print("-" * 60)

        print("MEUS GRUPOS E COMUNIDADES:")
        cursor.execute("""
            SELECT g.nome_grupo, p.admin, 
                   GROUP_CONCAT(CONCAT(l.titulo_livro, ' (Até ', DATE_FORMAT(m.dt_meta, '%d/%m/%Y'), ')') SEPARATOR '  |  ') AS leituras_ativas
            FROM participantes p
            INNER JOIN tbl_grupos g ON p.id_grupo = g.id_grupo
            LEFT JOIN tbl_metas_leitura m ON g.id_grupo = m.id_grupo
            LEFT JOIN meta_livro ml ON m.id_meta = ml.id_meta
            LEFT JOIN tbl_livros l ON ml.id_livro = l.id_livro
            WHERE p.id_usuario = %s
            GROUP BY g.id_grupo, g.nome_grupo, p.admin
        """, (id_usuario_logado,))
        grupos = cursor.fetchall()

        if not grupos:
            print("  Você ainda não participa de nenhum grupo de leitura.")
        else:
            for grupo in grupos:
                cargo = "👑 Fundador" if grupo['admin'] else "Membro"
                print(f"   {grupo['nome_grupo']} [{cargo}]")
                if grupo['leituras_ativas']:
                    print(f"   Lendo agora: {grupo['leituras_ativas']}")
                else:
                    print("   Lendo agora: Sem leitura ativa no momento.")
                
        print("=" * 60)

    except mysql.connector.Error as e:
        print(f"Erro ao carregar perfil: {e}")
    finally:
        cursor.close()

    input("\nPressione Enter para voltar ao painel...")

def editar_perfil(conexao, id_usuario_logado):
        while True:
            print("\n=================== CONFIGURAÇÕES: EDITAR PERFIL ===================")
            print("1. Alterar Nome")
            print("2. Alterar Bio")
            print("3. Alterar Senha")
            print("4. Excluir Minha Conta")
            print("5. Alterar E-mail")
            print("0. Voltar")

            escolha = input("\nO que você deseja alterar? ").strip()

            if escolha == "0":
                break
                
            cursor = conexao.cursor()
            try:
                if escolha == "1":
                    novo_nome = input("Digite seu novo nome: ").strip()
                    if novo_nome:
                        cursor.execute("UPDATE tbl_usuario SET nome_usuario = %s WHERE id_usuario = %s", (novo_nome, id_usuario_logado))
                        print("\nNome atualizado com sucesso!")
                    else:
                        print("\nO nome não pode ficar em branco.")
                        
                elif escolha == "2":
                    print("\nDica: Fale um pouco sobre seus gêneros literários ou autores favoritos!")
                    nova_bio = input("Digite sua nova Bio: ").strip()
                    cursor.execute("UPDATE tbl_usuario SET bio_usuario = %s WHERE id_usuario = %s", (nova_bio[:500], id_usuario_logado))
                    print("\nBio atualizada com sucesso!")
                    
                elif escolha == "3":
                    nova_senha = input("Digite sua nova senha: ").strip()
                    if nova_senha:
                        cursor.execute("UPDATE tbl_usuario SET senha_usuario = %s WHERE id_usuario = %s", (nova_senha, id_usuario_logado))
                        print("\nSenha atualizada com sucesso!")
                    else:
                        print("\nA senha não pode ficar em branco.")

                elif escolha == "4":
                    certeza = input("\nTEM CERTEZA? Isso apagará seu perfil, resenhas e estante permanentemente. (S/N): ").strip().upper()
                    if certeza == "S":
                        cursor.execute("DELETE FROM tbl_usuario WHERE id_usuario = %s", (id_usuario_logado,))
                        conexao.commit()
                        print("\nSua conta foi excluída. Sentiremos sua falta!")
                        exit()
                    else:
                        print("\nOperação cancelada. Que bom que decidiu ficar!")
                        continue
                
                elif escolha == "5":
                    import re
                    novo_email = input("Digite o seu novo e-mail: ").strip()
                    padrao_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
                    
                    if not re.match(padrao_email, novo_email):
                        print("\nFormato de e-mail inválido.")
                        continue
        
                    try:
                        cursor.execute("UPDATE tbl_usuario SET email_usuario = %s WHERE id_usuario = %s", (novo_email, id_usuario_logado))
                        conexao.commit()
                        print("\nE-mail atualizado com sucesso!")
                        print("Lembre-se de usar este novo e-mail no seu próximo login!")
                    except mysql.connector.IntegrityError:
                        conexao.rollback()
                        print("\nErro: Este e-mail já está cadastrado em outra conta.")

                else:
                    print("\nOpção inválida.")
                    continue
                    
                conexao.commit()
                
            except mysql.connector.Error as e:
                conexao.rollback()
                print(f"\nErro ao atualizar o banco de dados: {e}")
            finally:
                cursor.close()
                
            if escolha in ["1", "2", "3"]:
                print()
                input("\nPressione Enter para continuar...")