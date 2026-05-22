from banco_de_dados.conexao import conectar, fechar_conexao
from datetime import datetime

def verificar_data(data):
        try:
            datetime.strptime(data, "%Y-%m-%d")
            return True
        except ValueError:
            print("Data inválida. Use o formato YYYY-MM-DD (ex: 2026-05-17)")
            return False

def cadastrar_livro(conexao):
    print("\nLivros cadastrados atualmente:")
    listar_livros(conexao)

    titulo = input('Titulo:').strip()
    if not titulo:
        print("Nome invalido.")
        return

    sinopse = input('Sinopse:').strip()
    if not sinopse:
        print("Sinopse invalida.")
        return
    
    while True:
        dt_publicacao = input('Data de lançamento (YYYY-MM-DD):').strip()
        if verificar_data(dt_publicacao):
            break
        
    print("\nDica: Para mais de um autor/gênero, separe por vírgulas.")
    autores = input('Nome do(s) Autor(es): ').strip()
    if not autores: 
        print("Autor invalido.")
        return 

    generos = input('Gênero(s) Literário(s): ').strip()
    if not generos: 
        print("Gênero invalido.")
        return

    lista_autores = [a.strip() for a in autores.split(',')]
    lista_generos = [g.strip() for g in generos.split(',')]

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            "INSERT INTO tbl_livros (titulo_livro, sinopse_livro, dt_de_publicacao) VALUES (%s, %s, %s)",
            (titulo, sinopse, dt_publicacao)
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
    
    cursor.execute("""
        SELECT 
        l.id_livro, 
        l.titulo_livro, 
        l.sinopse_livro, 
        l.dt_de_publicacao,
        GROUP_CONCAT(DISTINCT a.nome_autor SEPARATOR ', ') autores,
        GROUP_CONCAT(DISTINCT g.nome_genero SEPARATOR ', ') generos
        FROM tbl_livros l
        LEFT JOIN livro_autor la ON l.id_livro = la.id_livro
        LEFT JOIN tbl_autor a ON la.id_autor = a.id_autor
        LEFT JOIN livro_genero lg ON l.id_livro = lg.id_livro
        LEFT JOIN tbl_generos g ON lg.id_genero = g.id_genero
        GROUP BY l.id_livro
        ORDER BY l.id_livro
    """)

    livros = cursor.fetchall() 

    if not livros:
        print("Nenhum livro cadastrado.")
        cursor.close()
        return

    print("\n" + "-"*60)
    print("=================== ESTANTE DO ORBITLIT ====================")
    print("-" * 60)

    for livro in livros:
        autores = livro['autores'] if livro['autores'] else "Autor desconhecido"
        generos = livro['generos'] if livro['generos'] else "Gênero não classificado"
        data_pub = livro['dt_de_publicacao'] if livro['dt_de_publicacao'] else "Data não informada"
        
        print(f"[{livro['id_livro']}] {livro['titulo_livro']} ({data_pub})")
        print(f"Autor(es): {autores}")
        print(f"Gênero(s): {generos}")
        print(f"Sinopse: {livro['sinopse_livro']}")
        print("-" * 60)
        
    cursor.close()

def buscar_livro(conexao):
    while True:
        print("\n" + "-"*60)
        print("=================== TIPOS DE BUSCA ====================")
        print("-" * 60)
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
            l.dt_de_publicacao,
            GROUP_CONCAT(DISTINCT a.nome_autor SEPARATOR ', ') autores,
            GROUP_CONCAT(DISTINCT g.nome_genero SEPARATOR ', ') generos
            FROM tbl_livros l
            LEFT JOIN livro_autor la ON l.id_livro = la.id_livro
            LEFT JOIN tbl_autor a ON la.id_autor = a.id_autor
            LEFT JOIN livro_genero lg ON l.id_livro = lg.id_livro
            LEFT JOIN tbl_generos g ON lg.id_genero = g.id_genero
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
            
            print(f"[{livro['id_livro']}] {livro['titulo_livro']} ({data_pub})")
            print(f"Autor(es): {autores}")
            print(f"Gênero(s): {generos}")
            print(f"Sinopse: {livro['sinopse_livro']}")
            print("-" * 60)

        print()
        id_livro = input("Digete o ID do livro para abrir a ficha ou aperte Enter para voltar: ").strip()

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
            print("\n" + "-"*60)
            print(f"{livro_selecionado['titulo_livro'].upper()}")
            print("-"*60)
            print("1. Ler resenhas e avaliações")
            print("2. Escrever uma nova resenha")
            print("3. Grupos de leitura")
            print("4. Remover resenha")
            print("5. Remover grupo")
            print("0. Voltar para a busca")

            opcao = input("\nEscolha uma opção: ").strip() 
            if opcao == "0":
                break
            print()
            input("Pressione Enter para voltar aos filtros de busca...")

def remover_livro(conexao):
    print("\nLivros cadastrados atualmente:")
    listar_livros(conexao)

    id_livro = input("ID do livro para remover: ").strip()
    if not id_livro.isdigit():
        print("ID invalido.")
        return

    cursor = conexao.cursor()
    cursor.execute(
        "DELETE FROM tbl_livros WHERE id_livro = %s",
        (int(id_livro),),
    )
    conexao.commit()

    if cursor.rowcount == 0:
        print("Livro nao encontrado.")
    else:
        print("Livro removido com sucesso.")
    cursor.close()

def atualizar_livro(conexao):
    print("\nLivros cadastrados atualmente:")
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

    lista_autores = [a.strip() for a in novos_autores.split(',')]
    lista_generos = [g.strip() for g in novos_generos.split(',')]

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            "UPDATE tbl_livros SET titulo_livro = %s, sinopse_livro = %s, dt_de_publicacao = %s WHERE id_livro = %s",
            (novo_titulo, nova_sinopse, nova_data, int(id_livro))
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

# MENU PRINCIPAL

def iniciar(admin):
    conexao = conectar()

    if admin:
        opcoes = {
            "1": ("Adicionar novo livro à estante", cadastrar_livro),
            "2": ("Buscar livro", buscar_livro), #usar o lambd aqui
            "3": ("Atualizar livro", atualizar_livro),
            "4": ("Remover livro", remover_livro),
            "5": ("Explorar livros cadastrados", listar_livros),
        }
    else:
        opcoes = {
            "1": ("Adicionar novo livro à estante", cadastrar_livro),
            "2": ("Buscar livro", buscar_livro),
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
            print(f"\n--- {descricao.upper()} ---")
            
            funcao_escolhida(conexao) 
            
            print()
            input('Pressione Enter para continuar...')
        else:
            print("Opcao invalida. Tente novamente.")

    fechar_conexao(conexao)