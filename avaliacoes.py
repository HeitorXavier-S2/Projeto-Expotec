import mysql.connector

def avaliar_livro_direto(conexao, id_usuario_logado, id_livro):
    print("\n=================== NOVA AVALIAÇÃO ===================")
    
    cursor = conexao.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id_avaliacao, nota_avaliacao FROM tbl_avaliacoes WHERE id_usuario = %s AND id_livro = %s", (id_usuario_logado, id_livro))
        avaliacao_existente = cursor.fetchone()
        
        if avaliacao_existente:
            print(f"\nVocê já avaliou este livro com a nota ⭐ {avaliacao_existente['nota_avaliacao']}.")
            escolha = input("Deseja ATUALIZAR sua avaliação antiga? (S/N): ").strip().upper()
            
            if escolha != 'S':
                print("\nOperação cancelada. Sua avaliação original foi mantida.")
                cursor.close()
                return
            print("\n|=---- ATUALIZANDO AVALIAÇÃO ----=|")
            
    except mysql.connector.Error as e:
        print(f"Erro ao verificar avaliações: {e}")
        cursor.close()
        return

    while True:
        try:
            nota = float(input("De 0.0 a 5.0, qual a sua nota? ").replace(',', '.'))
            if 0.0 <= nota <= 5.0:
                break
            else:
                print("A nota deve estar entre 0 e 5.")
        except ValueError:
            print("Formato inválido. Digite um número (ex: 4.5).")

    comentario = input("Escreva sua resenha (opcional): ").strip()

    try:
        if avaliacao_existente:
            cursor.execute(
                "UPDATE tbl_avaliacoes SET nota_avaliacao = %s, comentario_avaliacao = %s WHERE id_avaliacao = %s",
                (nota, comentario, avaliacao_existente['id_avaliacao'])
            )
            print("\nSua avaliação foi atualizada com sucesso!")
        else:
            cursor.execute(
                "INSERT INTO tbl_avaliacoes (nota_avaliacao, comentario_avaliacao, id_usuario, id_livro) VALUES (%s, %s, %s, %s)",
                (nota, comentario, id_usuario_logado, id_livro)
            )
            print("\nSua avaliação foi publicada com sucesso!")
            
        conexao.commit()
    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao salvar avaliação: {e}")
    finally:
        cursor.close()

def listar_avaliacoes_direto(conexao, id_livro):
    cursor = conexao.cursor(dictionary=True)

    sql = """
        SELECT 
        a.id_avaliacao, 
        u.nome_usuario,
        a.nota_avaliacao,
        a.comentario_avaliacao,
        DATE_FORMAT(a.dt_avaliacao, '%d/%m/%Y') data_formatada
        FROM tbl_avaliacoes a
        INNER JOIN tbl_usuario u ON a.id_usuario = u.id_usuario
        WHERE a.id_livro = %s
        ORDER BY a.dt_avaliacao DESC
    """

    cursor.execute(sql, (id_livro,))
    avaliacoes = cursor.fetchall()
    cursor.close()

    if not avaliacoes:
        print("\nEste livro ainda não possui nenhuma resenha.")
        return

    print("\n=================== RESENHAS DE LEITORES ===================")
    for avaliacao in avaliacoes:
        texto = avaliacao['comentario_avaliacao'] if avaliacao['comentario_avaliacao'] else "(Apenas deu nota)"
        print(f"[ID: {avaliacao['id_avaliacao']}]  {avaliacao['nome_usuario']}  |  ⭐ {avaliacao['nota_avaliacao']}  |  {avaliacao['data_formatada']}")
        print(f"{texto}")
        print("-" * 60)

def remover_avaliacao_direto(conexao, id_livro):
    print("\n=================== MODO MODERADOR: REMOVER AVALIAÇÃO ===================")
    
    listar_avaliacoes_direto(conexao, id_livro)
    
    id_avaliacao = input("\nDigite o [ID] da avaliação que deseja apagar (ou 0 para cancelar): ").strip()
    
    if id_avaliacao == "0" or not id_avaliacao.isdigit():
        print("Operação cancelada.")
        return
        
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "DELETE FROM tbl_avaliacoes WHERE id_avaliacao = %s AND id_livro = %s",
            (int(id_avaliacao), id_livro)
        )
        conexao.commit()
        
        if cursor.rowcount == 0:
            print("Avaliação não encontrada neste livro.")
        else:
            print("Avaliação removida com sucesso pelo Administrador!")
            
    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao remover avaliação: {e}")
    finally:
        cursor.close()

def censurar_avaliacao_direto(conexao, id_livro):
    print("\n=================== MODO MODERADOR: CENSURAR/EDITAR AVALIAÇÃO ===================")
    
    listar_avaliacoes_direto(conexao, id_livro)
    
    id_avaliacao = input("\nDigite o [ID] da avaliação que deseja censurar (ou 0 para cancelar): ").strip()
    
    if id_avaliacao == "0" or not id_avaliacao.isdigit():
        print("Operação cancelada.")
        return

    print("\nComo deseja censurar esta resenha?")
    print("1. Aplicar aviso padrão ('[Avaliação removida pela moderação]')")
    print("2. Escrever um aviso customizado")
    escolha = input("Escolha a opção: ").strip()

    if escolha == "1":
        novo_texto = "[Avaliação ocultada pela moderação por violação das diretrizes da comunidade.]"
    elif escolha == "2":
        novo_texto = input("Digite o aviso que substituirá a resenha original: ").strip()
    else:
        print("Opção inválida. Operação cancelada.")
        return
        
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "UPDATE tbl_avaliacoes SET comentario_avaliacao = %s WHERE id_avaliacao = %s AND id_livro = %s",
            (novo_texto, int(id_avaliacao), id_livro)
        )
        conexao.commit()
        
        if cursor.rowcount == 0:
            print("Avaliação não encontrada neste livro.")
        else:
            print("Avaliação censurada com sucesso pelo Administrador!")
            
    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao censurar avaliação: {e}")
    finally:
        cursor.close()