from datetime import datetime
import mysql.connector

def verificar_data(data):
        try:
            datetime.strptime(data, "%Y-%m-%d")
            return True
        except ValueError:
            print("Data inválida. Use o formato YYYY-MM-DD (ex: 2026-05-17)")
            return False

def cadastrar_livro(conexao):
    listar_livros(conexao)

    titulo = input("\nTitulo: ").strip()
    if not titulo:
        print("Nome invalido.")
        return

    print("\nDica: Para mais de um autor, separe por vírgulas.")
    autores = input("Nome do(s) Autor(es): ").strip()
    if not autores: 
        print("Autor invalido.")
        return 

    lista_autores = list(set([a.strip() for a in autores.split(',') if a.strip()]))

    cursor = conexao.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT l.id_livro, GROUP_CONCAT(LOWER(a.nome_autor)) as autores_existentes
        FROM tbl_livros l
        INNER JOIN livro_autor la ON l.id_livro = la.id_livro
        INNER JOIN tbl_autor a ON la.id_autor = a.id_autor
        WHERE LOWER(l.titulo_livro) = LOWER(%s)
        GROUP BY l.id_livro
    """, (titulo,))
    
    livros_encontrados = cursor.fetchall()
    
    duplicado = False
    for livro in livros_encontrados:
        autores_banco = livro['autores_existentes'].split(',') if livro['autores_existentes'] else []
        
        for autor_novo in lista_autores:
            if autor_novo.lower() in autores_banco:
                duplicado = True
                break
        if duplicado:
            break
            
    if duplicado:
        print(f"\nErro: A obra '{titulo}' vinculada a este autor já existe no acervo!")
        cursor.close()
        return
        
    cursor.close()

    sinopse = input("Sinopse: ").strip()
    if not sinopse:
        print("Sinopse invalida.")
        return
    
    while True:
        try:
            paginas = int(input("Total de páginas: ").strip())
            if paginas > 0:
                break
            print("O número de páginas deve ser maior que zero.")
        except ValueError:
            print("Inválido. Digite apenas números inteiros.")
    
    while True:
        dt_publicacao = input("Data de lançamento (YYYY-MM-DD): ").strip()
        if verificar_data(dt_publicacao):
            break
        
    print("\nDica: Para mais de um gênero, separe por vírgulas.")
    generos = input("Gênero(s) Literário(s): ").strip()
    if not generos: 
        print("Gênero invalido.")
        return

    lista_generos = list(set([g.strip() for g in generos.split(',') if g.strip()]))

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            "INSERT INTO tbl_livros (titulo_livro, sinopse_livro, total_paginas, dt_de_publicacao) VALUES (%s, %s, %s, %s)",
            (titulo, sinopse, paginas, dt_publicacao)
        )
        id_livro = cursor.lastrowid
    
        for autor in lista_autores:
            cursor.execute("SELECT id_autor FROM tbl_autor WHERE nome_autor = %s", (autor,))
            resultado = cursor.fetchone()

            if resultado:
                id_autor = resultado['id_autor']
            else:
                cursor.execute("INSERT INTO tbl_autor (nome_autor) VALUES (%s)", (autor,))
                id_autor = cursor.lastrowid
            
            cursor.execute("INSERT INTO livro_autor (id_livro, id_autor) VALUES (%s, %s)", (id_livro, id_autor))

        for genero in lista_generos:
            cursor.execute("SELECT id_genero FROM tbl_generos WHERE nome_genero = %s", (genero,))
            resultado = cursor.fetchone()

            if resultado:
                id_genero = resultado['id_genero']
            else:
                cursor.execute("INSERT INTO tbl_generos (nome_genero) VALUES (%s)", (genero,))
                id_genero = cursor.lastrowid
            
            cursor.execute("INSERT INTO livro_genero (id_livro, id_genero) VALUES (%s, %s)", (id_livro, id_genero))

        conexao.commit()
        print(f"\nLivro '{titulo}' cadastrado com sucesso!")

    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Não foi possível cadastrar o livro. Erro no banco de dados: {e}")
    except Exception as e:
        conexao.rollback()
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        cursor.close()

def listar_livros(conexao):
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""SELECT 
            l.id_livro, 
            l.titulo_livro, 
            l.sinopse_livro,
            l.total_paginas,
            l.dt_de_publicacao,
            GROUP_CONCAT(DISTINCT a.nome_autor SEPARATOR ', ') autores,
            GROUP_CONCAT(DISTINCT g.nome_genero SEPARATOR ', ') generos,
            ROUND(AVG(av.nota_avaliacao), 1) as media_nota
            FROM tbl_livros l
            LEFT JOIN livro_autor la ON l.id_livro = la.id_livro
            LEFT JOIN tbl_autor a ON la.id_autor = a.id_autor
            LEFT JOIN livro_genero lg ON l.id_livro = lg.id_livro
            LEFT JOIN tbl_generos g ON lg.id_genero = g.id_genero
            LEFT JOIN tbl_avaliacoes av ON l.id_livro = av.id_livro
            GROUP BY l.id_livro
            ORDER BY l.id_livro
    """)

    livros = cursor.fetchall() 

    if not livros:
        print("Nenhum livro cadastrado.")
        cursor.close()
        return

    print("\n=================== ESTANTE DO ORBITLIT ====================")

    for livro in livros:
        autores = livro['autores'] if livro['autores'] else "Autor desconhecido"
        generos = livro['generos'] if livro['generos'] else "Gênero não classificado"
        data_pub = livro['dt_de_publicacao'] if livro['dt_de_publicacao'] else "Data não informada"
    
        nota_visual = f"⭐ {livro['media_nota']}/5.0" if livro['media_nota'] else "⭐ Sem avaliações"
        
        print(f"[{livro['id_livro']}] {livro['titulo_livro']} ({data_pub}) - {livro['total_paginas']} páginas | {nota_visual}")
        print(f"Autor(es): {autores}")
        print(f"Gênero(s): {generos}")
        print(f"Sinopse: {livro['sinopse_livro']}")
        print("-" * 60)
        
    cursor.close()

def buscar_livro(conexao, admin, id_usuario_logado):
    while True:
        print("\n=================== TIPOS DE BUSCA ====================")
        print("1. Buscar por Título ou Sinopse")
        print("2. Buscar por Autor")
        print("3. Buscar por Gênero Literário")
        print("4. Buscar por Data")
        print("0. Voltar")

        tipo_busca = input("\nEscolha uma opção de busca: ").strip()

        if tipo_busca == "0":
            return
        
        if tipo_busca not in ["1", "2", "3", "4"]:
            print("Opção inválida.")
            continue

        cursor = conexao.cursor(dictionary=True)
        
        sql = """SELECT 
            l.id_livro, 
            l.titulo_livro,
            l.sinopse_livro,
            l.total_paginas,
            l.dt_de_publicacao,
            GROUP_CONCAT(DISTINCT a.nome_autor SEPARATOR ', ') autores,
            GROUP_CONCAT(DISTINCT g.nome_genero SEPARATOR ', ') generos,
            ROUND(AVG(av.nota_avaliacao), 1) as media_nota
            FROM tbl_livros l
            LEFT JOIN livro_autor la ON l.id_livro = la.id_livro
            LEFT JOIN tbl_autor a ON la.id_autor = a.id_autor
            LEFT JOIN livro_genero lg ON l.id_livro = lg.id_livro
            LEFT JOIN tbl_generos g ON lg.id_genero = g.id_genero
            LEFT JOIN tbl_avaliacoes av ON l.id_livro = av.id_livro
        """

        if tipo_busca in ["1", "2", "3"]:
            termo = input("Digite o termo que deseja procurar: ").strip()
            if not termo:
                print("Termo inválido.")
                continue

            termo_busca = "%" + termo + "%"
        
        if tipo_busca == "1":
            sql_final = sql + " WHERE l.titulo_livro LIKE %s OR l.sinopse_livro LIKE %s GROUP BY l.id_livro ORDER BY l.id_livro"
            parametros = (termo_busca, termo_busca)
        
        elif tipo_busca == "2":
            sql_final = sql + " WHERE a.nome_autor LIKE %s GROUP BY l.id_livro ORDER BY l.id_livro"
            parametros = (termo_busca,)
        
        elif tipo_busca == "3":
            sql_final = sql + " WHERE g.nome_genero LIKE %s GROUP BY l.id_livro ORDER BY l.id_livro"
            parametros = (termo_busca,)
        
        elif tipo_busca == "4":
            print("\nBUSCA POR DATA")

            while True:
                data_inicial = input("\nDigite a data INICIAL (YYYY-MM-DD): ").strip()
                if verificar_data(data_inicial):
                    break
            
            while True:
                data_final = input("Digite a data FINAL (YYYY-MM-DD): ").strip()
                if verificar_data(data_final):
                    break

            sql_final = sql + " WHERE l.dt_de_publicacao BETWEEN %s AND %s GROUP BY l.id_livro ORDER BY l.id_livro"
            parametros = (data_inicial, data_final)
        
        cursor.execute(sql_final, parametros)
        livros = cursor.fetchall()
        cursor.close()

        if not livros:
            print("Nenhum livro encontrado.")
            continue

        print("\nResultado da busca:")
        print("-" * 60)
        for livro in livros:
            autores = livro['autores'] if livro['autores'] else "Autor desconhecido"
            generos = livro['generos'] if livro['generos'] else "Gênero não classificado"
            data_pub = livro['dt_de_publicacao'] if livro['dt_de_publicacao'] else "Data não informada"
            nota_visual = f"⭐ {livro['media_nota']}/5.0" if livro['media_nota'] else "⭐ Sem avaliações"
            
            print(f"[{livro['id_livro']}] {livro['titulo_livro']} ({data_pub}) - {livro['total_paginas']} páginas | {nota_visual}")
            print(f"Autor(es): {autores}")
            print(f"Gênero(s): {generos}")
            print(f"Sinopse: {livro['sinopse_livro']}")
            print("-" * 60)

        print()
        id_livro = input("Digite o ID do livro para abrir a ficha ou aperte Enter para voltar: ").strip()

        if not id_livro.isdigit():
            continue

        cursor = conexao.cursor(dictionary=True)
        cursor.execute(sql + " WHERE l.id_livro = %s GROUP BY l.id_livro", (int(id_livro),))
        livro_selecionado = cursor.fetchone()
        cursor.close()

        if not livro_selecionado:
            print("Livro não encontrado")
            continue

        while True:
            nota_cabecalho = f"⭐ {livro_selecionado['media_nota']}/5.0" if livro_selecionado['media_nota'] else "⭐ Sem avaliações"
            
            print("\n" + "-"*60)
            print(f"{livro_selecionado['titulo_livro'].upper()} | {nota_cabecalho}")
            print("-"*60)
            
            print("1. Ler resenhas e avaliações")
            print("2. Escrever uma nova resenha")
            print("3. Grupos de leitura")
            print("4. Adicionar à minha Estante")
            
            if admin:
                print("5. Remover resenha")
                print("6. Censurar/Editar resenha")
                
            print("0. Voltar para a busca")

            opcao = input("\nEscolha uma opção: ").strip() 
            if opcao == "0":
                break

            elif opcao == "1":
                import avaliacoes
                avaliacoes.listar_avaliacoes_direto(conexao, livro_selecionado['id_livro']) 
                
            elif opcao == "2":
                import avaliacoes
                avaliacoes.avaliar_livro_direto(conexao, id_usuario_logado, livro_selecionado['id_livro'])
                
            elif opcao == "3":
                import grupos
                grupos.listar_grupos_por_livro(conexao, id_usuario_logado, livro_selecionado['id_livro'])

            elif opcao == "4":
                import estante
                estante.adicionar_a_estante(conexao, id_usuario_logado, livro_selecionado['id_livro'])
            
            elif opcao == "5" and admin:
                import avaliacoes
                avaliacoes.remover_avaliacao_direto(conexao, livro_selecionado['id_livro'])
                
            elif opcao == "6" and admin:
                import avaliacoes
                avaliacoes.censurar_avaliacao_direto(conexao, livro_selecionado['id_livro']) 
                
            else:
                print("Opção inválida.")
                
            input("\nPressione Enter para voltar aos detalhes do livro...")

def remover_livro(conexao, admin):
    if not admin:
        print("\nAcesso negado. Apenas administradores podem remover livros do acervo.")
        return
    
    listar_livros(conexao)

    id_livro = input("ID do livro para remover: ").strip()
    if not id_livro.isdigit():
        print("ID invalido.")
        return

    cursor = conexao.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM tbl_livros WHERE id_livro = %s",
            (int(id_livro),),
        )
        conexao.commit()

        if cursor.rowcount == 0:
            print("Livro nao encontrado.")
        else:
            print("Livro removido com sucesso.")

    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao remover o livro: {e}")
    finally:
        cursor.close()

def atualizar_livro(conexao, admin):
    if not admin:
        print("\nAcesso negado. Apenas administradores podem alterar os dados de um livro.")
        return
    
    listar_livros(conexao)

    id_livro = input("\nID do livro que deseja atualizar: ").strip()
    if not id_livro.isdigit():
        print("ID invalido.")
        return

    novo_titulo = input("Novo titulo: ").strip()
    if not novo_titulo:
        print("Titulo invalido.")
        return

    nova_sinopse = input("Nova sinopse: ").strip()
    if not nova_sinopse:
        print("Sinopse invalida.")
        return
    
    while True:
        try:
            novas_paginas = int(input('Total de páginas: ').strip())
            if novas_paginas > 0:
                break
            print("O número de páginas deve ser maior que zero.")
        except ValueError:
            print("Inválido. Digite apenas números inteiros.")
    
    while True:
        nova_data = input("Nova data (YYYY-MM-DD): ").strip()
        if verificar_data(nova_data):
            break

    print("\nDica: Para manter os mesmos autores/gêneros, digite-os novamente. Separe por vírgulas.")
    novos_autores = input("Novo(s) Autor(es): ").strip()
    if not novos_autores:
        print("Autor invalido.")
        return
        
    novos_generos = input("Novo(s) Gênero(s): ").strip()
    if not novos_generos:
        print("Gênero invalido.")
        return

    lista_autores = [a.strip() for a in novos_autores.split(',') if a.strip()]
    lista_generos = [g.strip() for g in novos_generos.split(',') if g.strip()]

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            "UPDATE tbl_livros SET titulo_livro = %s, sinopse_livro = %s, total_paginas = %s, dt_de_publicacao = %s WHERE id_livro = %s",
            (novo_titulo, nova_sinopse, novas_paginas, nova_data, int(id_livro))
        )

        if cursor.rowcount == 0:
            print("Livro não encontrado.")
            return

        cursor.execute("DELETE FROM livro_autor WHERE id_livro = %s", (int(id_livro),))
        cursor.execute("DELETE FROM livro_genero WHERE id_livro = %s", (int(id_livro),))

        for autor in lista_autores:
            cursor.execute("SELECT id_autor FROM tbl_autor WHERE nome_autor = %s", (autor,))
            resultado = cursor.fetchone()

            if resultado:
                id_autor = resultado['id_autor']
            else:
                cursor.execute("INSERT INTO tbl_autor (nome_autor) VALUES (%s)", (autor,))
                id_autor = cursor.lastrowid
            
            cursor.execute("INSERT INTO livro_autor (id_livro, id_autor) VALUES (%s, %s)", (int(id_livro), id_autor))

        for genero in lista_generos:
            cursor.execute("SELECT id_genero FROM tbl_generos WHERE nome_genero = %s", (genero,))
            resultado = cursor.fetchone()

            if resultado:
                id_genero = resultado['id_genero']
            else:
                cursor.execute("INSERT INTO tbl_generos (nome_genero) VALUES (%s)", (genero,))
                id_genero = cursor.lastrowid
            
            cursor.execute("INSERT INTO livro_genero (id_livro, id_genero) VALUES (%s, %s)", (int(id_livro), id_genero))

        conexao.commit()
        print("\nDados do livro, autores e gêneros atualizados com sucesso!")

    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao atualizar o livro no banco de dados: {e}")
    finally:
        cursor.close()

def gerenciar_categorias(conexao, admin):
    if not admin:
        print("\nAcesso negado. Apenas administradores podem gerenciar autores e gêneros.")
        return
    
    while True:
        print("=================== PAINEL ADMIN: AUTORES E GÊNEROS ===================")
        print("\n|=---- AUTORES ----=|")
        print("1. Listar Autores")
        print("2. Cadastrar novo Autor")
        print("3. Corrigir nome de Autor")
        print("4. Remover Autor")
        print("\n|=---- GÊNEROS ----=|")
        print("5. Listar Gêneros")
        print("6. Cadastrar novo Gênero")
        print("7. Corrigir nome de Gênero")
        print("8. Remover Gênero")
        print("0. Voltar")

        escolha = input("\nEscolha uma opção: ").strip()

        if escolha == "0":
            break
        
        if escolha not in [str(i) for i in range(1, 9)]:
            print("Opção inválida.")
            continue

        cursor = conexao.cursor(dictionary=True)

        try:
            if escolha == "1":
                cursor.execute("SELECT * FROM tbl_autor ORDER BY nome_autor")
                resultados = cursor.fetchall()
                print("\n|=---- AUTORES CADASTRADOS ----=|")
                for r in resultados:
                    print(f"[ID: {r['id_autor']}] {r['nome_autor']}")

            elif escolha == "2":
                nome = input("\nDigite o nome do novo Autor: ").strip()
                if nome:
                    cursor.execute("INSERT INTO tbl_autor (nome_autor) VALUES (%s)", (nome,))
                    conexao.commit()
                    print(f"Autor '{nome}' cadastrado com sucesso!")

            elif escolha == "3":
                id_autor = input("\nDigite o ID do Autor que deseja corrigir: ").strip()
                nome = input("Digite o nome correto: ").strip()
                
                cursor.execute("UPDATE tbl_autor SET nome_autor = %s WHERE id_autor = %s", (nome, int(id_autor)))
                conexao.commit()
                if cursor.rowcount == 0:
                    print("Autor não encontrado.")
                else:
                    print("Nome do autor atualizado!")

            elif escolha == "4":
                id_autor = input("\nDigite o ID do Autor para REMOVER: ").strip()

                sql_verificacao = """
                                SELECT l.titulo_livro 
                                FROM tbl_livros l
                                INNER JOIN livro_autor la ON l.id_livro = la.id_livro
                                WHERE la.id_autor = %s
                            """
                cursor.execute(sql_verificacao, (int(id_autor),))
                livros_vinculados = cursor.fetchall()
                
                if livros_vinculados:
                    print(f"\nOPERAÇÃO BLOQUEADA: Este autor possui {len(livros_vinculados)} obra(s) na estante:")
                    for livro in livros_vinculados:
                        print(f"   - {livro['titulo_livro']}")
                    print("\nPor favor, remova ou altere esses livros antes de apagar o autor.")
                else:
                    cursor.execute("DELETE FROM tbl_autor WHERE id_autor = %s", (int(id_autor),))
                    conexao.commit()
                    if cursor.rowcount == 0:
                        print("Autor não encontrado.")
                    else:
                        print("Autor removido com sucesso!")

            elif escolha == "5":
                cursor.execute("SELECT * FROM tbl_generos ORDER BY nome_genero")
                resultados = cursor.fetchall()
                print("\n|=---- GÊNEROS CADASTRADOS ----=|")
                for r in resultados:
                    print(f"[ID: {r['id_genero']}] {r['nome_genero']}")

            elif escolha == "6":
                nome = input("\nDigite o nome do novo Gênero: ").strip()
                if nome:
                    cursor.execute("INSERT INTO tbl_generos (nome_genero) VALUES (%s)", (nome,))
                    conexao.commit()
                    print(f"Gênero '{nome}' cadastrado com sucesso!")

            elif escolha == "7":
                id_genero = input("\nDigite o ID do Gênero que deseja corrigir: ").strip()
                nome = input("Digite o nome correto: ").strip()
                
                cursor.execute("UPDATE tbl_generos SET nome_genero = %s WHERE id_genero = %s", (nome, int(id_genero)))
                conexao.commit()
                if cursor.rowcount == 0:
                    print("Gênero não encontrado.")
                else:
                    print("Nome do gênero atualizado!")

            elif escolha == "8":
                id_genero = input("\nDigite o ID do Gênero para REMOVER: ").strip()
        
                sql_verificacao = """
                    SELECT l.titulo_livro 
                    FROM tbl_livros l
                    INNER JOIN livro_genero lg ON l.id_livro = lg.id_livro
                    WHERE lg.id_genero = %s
                """
                cursor.execute(sql_verificacao, (int(id_genero),))
                livros_vinculados = cursor.fetchall()
                
                if livros_vinculados:
                    print(f"\nOPERAÇÃO BLOQUEADA: Este gênero está classificado em {len(livros_vinculados)} obra(s):")
                    for livro in livros_vinculados:
                        print(f"   - {livro['titulo_livro']}")
                    print("\nPor favor, remova ou altere esses livros antes de apagar o gênero.")
                else:
                    cursor.execute("DELETE FROM tbl_generos WHERE id_genero = %s", (int(id_genero),))
                    conexao.commit()
                    if cursor.rowcount == 0:
                        print("Gênero não encontrado.")
                    else:
                        print("Gênero removido com sucesso!")

        except mysql.connector.IntegrityError:
            conexao.rollback()
            print("Erro: Este nome já está cadastrado no sistema (Restrição UNIQUE).")
        except mysql.connector.Error as e:
            conexao.rollback()
            print(f"Erro no banco de dados: {e}")
        except ValueError:
            print("ID inválido. Digite apenas números.")
        finally:
            cursor.close()
            
        input("\nPressione Enter para continuar...")

# MENU PRINCIPAL

def iniciar(conexao, admin, id_usuario_logado):
    #conexao = conectar()

    if admin:
        opcoes = {
            "1": ("Adicionar novo livro à estante", cadastrar_livro),
            "2": ("Buscar livro", lambda c: buscar_livro(c, admin, id_usuario_logado)),
            "3": ("Atualizar livro", lambda c: atualizar_livro(c, admin)),
            "4": ("Remover livro", lambda c: remover_livro(c, admin)),
            "5": ("Explorar livros cadastrados", listar_livros),
            "6": ("Gerenciar Autores e Gêneros", lambda c: gerenciar_categorias(c, admin)),
        }

    else:
        opcoes = {
            "1": ("Adicionar novo livro à estante", cadastrar_livro),
            "2": ("Buscar livro", lambda c: buscar_livro(c, admin, id_usuario_logado)),
            "3": ("Explorar livros cadastrados", listar_livros),
        }

    while True:
        print("\n==== ACERVO DE LIVROS - ORBITLIT ====")
        for codigo, (descricao, _) in opcoes.items():
            print(f"{codigo}. {descricao}")
        print("0. Voltar / Sair")
        
        escolha = input("\nEscolha uma opcao: ").strip()
        
        if escolha == "0":
            print("Voltando ao menu principal...")
            break
            
        if escolha in opcoes:
            descricao, funcao_escolhida = opcoes[escolha]
            print(f"\n|=---- {descricao.upper()} ----=|")
            
            funcao_escolhida(conexao) 
            
            input("\nPressione Enter para continuar...")
        else:
            print("Opcao invalida. Tente novamente.")

    #fechar_conexao(conexao)