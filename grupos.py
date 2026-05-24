import mysql.connector
from datetime import datetime

def listar_grupos_por_livro(conexao, id_usuario_logado, id_livro):
    print("\n=================== GRUPOS DE LEITURA PARA ESTA OBRA ===================")
    
    cursor = conexao.cursor(dictionary=True)
    
    sql = """SELECT g.id_grupo, g.nome_grupo, g.link_externo_grupo,
               DATE_FORMAT(m.dt_meta, '%d/%m/%Y') data_meta, m.paginas_meta
        FROM tbl_grupos g
        INNER JOIN tbl_metas_leitura m ON g.id_grupo = m.id_grupo
        INNER JOIN meta_livro ml ON m.id_meta = ml.id_meta
        WHERE ml.id_livro = %s
        ORDER BY m.dt_meta DESC
    """
    cursor.execute(sql, (id_livro,))
    grupos_lendo = cursor.fetchall()
    
    if not grupos_lendo:
        print("Nenhum clube do livro está lendo esta obra no momento.")
        cursor.close()
        return

    for grupo in grupos_lendo:
        print(f"[{grupo['id_grupo']}]  {grupo['nome_grupo']}")
        print(f"      Meta Coletiva: Ler {grupo['paginas_meta']} páginas até {grupo['data_meta']}")
        print("-" * 60)
        
    escolha = input("\nDigite o ID do grupo para entrar/ver o link (ou 0 para voltar): ").strip()
    
    if escolha == "0" or not escolha.isdigit():
        cursor.close()
        return
        
    id_grupo_escolhido = int(escolha)
    grupo_selecionado = next((g for g in grupos_lendo if g['id_grupo'] == id_grupo_escolhido), None)
    
    if not grupo_selecionado:
        print("ID de grupo inválido para este livro.")
        cursor.close()
        return
        
    cursor.execute("SELECT status FROM participantes WHERE id_usuario = %s AND id_grupo = %s", (id_usuario_logado, id_grupo_escolhido))
    participante = cursor.fetchone()
    
    if participante:
        if participante['status'] == 'Aprovado':
            print(f"\nVocê já é membro do grupo '{grupo_selecionado['nome_grupo']}'!")
            print(f"Link de acesso exclusivo: {grupo_selecionado['link_externo_grupo']}")
        else:
            print(f"\nO seu pedido para '{grupo_selecionado['nome_grupo']}' está PENDENTE.")
            print("Aguarde a aprovação do fundador do grupo.")
    else:
        try:
            cursor.execute(
                "INSERT INTO participantes (id_usuario, id_grupo, admin, status) VALUES (%s, %s, FALSE, 'Pendente')",
                (id_usuario_logado, id_grupo_escolhido)
            )
            conexao.commit()
            print(f"\nPedido enviado! O fundador do grupo '{grupo_selecionado['nome_grupo']}' irá analisar sua solicitação em breve.")
        except mysql.connector.Error as e:
            conexao.rollback()
            print(f"Erro ao entrar no grupo: {e}")
            
    cursor.close()

def painel_comunidades(conexao, id_usuario_logado):
    while True:
        print("\n=================== MEUS GRUPOS E COMUNIDADES ===================")
        print("1. Ver Meus Grupos e Links de Acesso")
        print("2. Gerenciar Meus Grupos (Painel do Fundador)")
        print("3. Criar uma Nova Comunidade") 
        print("0. Voltar ao menu principal")
        
        escolha = input("\nEscolha uma opção: ").strip()
        
        if escolha == "0":
            break
        elif escolha == "1":
            ver_meus_grupos(conexao, id_usuario_logado)
        elif escolha == "2":
            painel_fundador(conexao, id_usuario_logado)
        elif escolha == "3":
            criar_grupo(conexao, id_usuario_logado)
        else:
            print("Opção inválida.")

def ver_meus_grupos(conexao, id_usuario_logado):
    cursor = conexao.cursor(dictionary=True)

    sql = """
        SELECT g.nome_grupo, g.link_externo_grupo, p.status,
               GROUP_CONCAT(CONCAT(l.titulo_livro, ' (Até ', DATE_FORMAT(m.dt_meta, '%d/%m/%Y'), ')') SEPARATOR '  |  ') AS leituras_ativas
        FROM participantes p
        INNER JOIN tbl_grupos g ON p.id_grupo = g.id_grupo
        LEFT JOIN tbl_metas_leitura m ON g.id_grupo = m.id_grupo
        LEFT JOIN meta_livro ml ON m.id_meta = ml.id_meta
        LEFT JOIN tbl_livros l ON ml.id_livro = l.id_livro
        WHERE p.id_usuario = %s
        GROUP BY g.id_grupo, g.nome_grupo, g.link_externo_grupo, p.status
    """
    cursor.execute(sql, (id_usuario_logado,))
    meus_grupos = cursor.fetchall()
    cursor.close()
    
    print("\n|=---- LISTA DE COMUNIDADES ----=|")
    if not meus_grupos:
        print("Você ainda não participa de nenhum grupo.")
    else:
        for g in meus_grupos:
            if g['status'] == 'Aprovado':
                print(f"  {g['nome_grupo']}")
                print(f"  Link de Acesso: {g['link_externo_grupo']}")
                if g['leituras_ativas']:
                    print(f"  Leituras Ativas: {g['leituras_ativas']}")
                else:
                    print("  Leituras Ativas: Nenhuma meta ativa definida pelo fundador.")
            else:
                print(f"  {g['nome_grupo']}")
                print("  [Status: Pendente de aprovação pelo fundador]")
            print("-" * 55)
            
    input("\nPressione Enter para voltar...")

def criar_grupo(conexao, id_usuario_logado):
    print("\n=================== FUNDAR NOVO GRUPO ===================")
    nome = input("Nome da comunidade: ").strip()
    
    if not nome:
        print("O nome não pode estar vazio. Operação cancelada.")
        return
        
    descricao = input("Breve descrição do grupo: ").strip()
    link = input("Link de convite (Discord, WhatsApp, etc.): ").strip()
    
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "INSERT INTO tbl_grupos (nome_grupo, descricao_grupo, link_externo_grupo) VALUES (%s, %s, %s)",
            (nome, descricao, link)
        )
        id_novo_grupo = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO participantes (id_usuario, id_grupo, admin, status) VALUES (%s, %s, TRUE, 'Aprovado')",
            (id_usuario_logado, id_novo_grupo)
        )
        
        conexao.commit()
        print(f"\nParabéns! O grupo '{nome}' foi criado com sucesso.")
        print("Dica: Vá no 'Painel do Fundador' para definir a primeira Leitura do Mês!")
    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao criar o grupo: {e}")
    finally:
        cursor.close()

def painel_fundador(conexao, id_usuario_logado):
    cursor = conexao.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT g.id_grupo, g.nome_grupo 
        FROM participantes p
        INNER JOIN tbl_grupos g ON p.id_grupo = g.id_grupo
        WHERE p.id_usuario = %s AND p.admin = TRUE
    """, (id_usuario_logado,))
    grupos_admin = cursor.fetchall()
    
    if not grupos_admin:
        print("\nAcesso negado. Você não é fundador/administrador de nenhum grupo.")
        cursor.close()
        input("\nPressione Enter para voltar...")
        return
        
    print("\n|=---- PAINEL DO FUNDADOR ----=|")
    for g in grupos_admin:
        print(f"[{g['id_grupo']}] {g['nome_grupo']}")
        
    id_grp = input("\nDigite o ID do grupo para gerenciar (ou 0 para voltar): ").strip()
    if id_grp == "0" or not id_grp.isdigit():
        cursor.close()
        return
        
    id_grupo_escolhido = int(id_grp)
    
    if not any(g['id_grupo'] == id_grupo_escolhido for g in grupos_admin):
        print("Acesso negado. Você não gerencia este grupo.")
        cursor.close()
        return

    while True:
        print("\nGERENCIANDO O GRUPO")
        print("1. Analisar pedidos de entrada (Sala de Espera)")
        print("2. Atualizar link de acesso externo (Discord/WhatsApp)")
        print("3. Definir ou Atualizar a Leitura do Mês") 
        print("4. Remover Meta de Leitura")
        print("0. Voltar")
        
        opc = input("\nEscolha: ").strip()
        
        if opc == "0":
            break
            
        elif opc == "1":
            cursor.execute("""
                SELECT p.id_usuario, u.nome_usuario 
                FROM participantes p
                INNER JOIN tbl_usuario u ON p.id_usuario = u.id_usuario
                WHERE p.id_grupo = %s AND p.status = 'Pendente'
            """, (id_grupo_escolhido,))
            pendentes = cursor.fetchall()
            
            if not pendentes:
                print("\nA sala de espera está vazia no momento.")
            else:
                for p in pendentes:
                    print(f"\nSolicitação de: {p['nome_usuario']}")
                    acao = input("Deseja aprovar a entrada? (S/N): ").strip().upper()
                    
                    while True:
                        acao = input("Deseja aprovar a entrada? (S/N): ").strip().upper()
                        if acao in ['S', 'N']:
                            break
                        print("Digite apenas S para Sim ou N para Não.")
                        
                    if acao == 'S':
                        cursor.execute("UPDATE participantes SET status = 'Aprovado' WHERE id_usuario = %s AND id_grupo = %s", (p['id_usuario'], id_grupo_escolhido))
                        conexao.commit()
                        print("Membro aprovado!")

                    elif acao == 'N':
                        cursor.execute("DELETE FROM participantes WHERE id_usuario = %s AND id_grupo = %s", (p['id_usuario'], id_grupo_escolhido))
                        conexao.commit()
                        print("Solicitação rejeitada.")
        
        elif opc == "2":
            novo_link = input("\nCole o novo link de acesso: ").strip()
            if novo_link:
                cursor.execute("UPDATE tbl_grupos SET link_externo_grupo = %s WHERE id_grupo = %s", (novo_link, id_grupo_escolhido))
                conexao.commit()
                print("Link atualizado com sucesso para todos os membros!")
                
        elif opc == "3":
            id_livro = input("\nDigite o ID do Livro no acervo que o grupo vai ler: ").strip()
            if not id_livro.isdigit():
                print("ID inválido.")
                continue
                
            cursor.execute("SELECT titulo_livro, total_paginas FROM tbl_livros WHERE id_livro = %s", (int(id_livro),))
            livro = cursor.fetchone()
            
            if not livro:
                print("Livro não encontrado no acervo.")
                continue
                
            print(f"\nLivro selecionado: {livro['titulo_livro']} ({livro['total_paginas']} páginas)")
            
            cursor.execute("""
                SELECT m.id_meta 
                FROM tbl_metas_leitura m
                INNER JOIN meta_livro ml ON m.id_meta = ml.id_meta
                WHERE m.id_grupo = %s AND ml.id_livro = %s
            """, (id_grupo_escolhido, int(id_livro)))
            meta_existente = cursor.fetchone()
            
            while True:
                dt_meta_input = input("Qual a data limite para terminar essa leitura? (YYYY-MM-DD): ").strip()
                try:
                    datetime.strptime(dt_meta_input, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Formato de data inválido. Use YYYY-MM-DD (Ex: 2026-10-31)")

            try:
                if meta_existente:
                    cursor.execute(
                        "UPDATE tbl_metas_leitura SET dt_meta = %s WHERE id_meta = %s",
                        (dt_meta_input, meta_existente['id_meta'])
                    )
                    conexao.commit()
                    print(f"\nA data limite para a leitura de '{livro['titulo_livro']}' foi atualizada!")
                else:
                    cursor.execute(
                        "INSERT INTO tbl_metas_leitura (paginas_meta, dt_meta, id_grupo) VALUES (%s, %s, %s)",
                        (livro['total_paginas'], dt_meta_input, id_grupo_escolhido)
                    )
                    id_nova_meta = cursor.lastrowid
                    
                    cursor.execute(
                        "INSERT INTO meta_livro (id_meta, id_livro) VALUES (%s, %s)",
                        (id_nova_meta, int(id_livro))
                    )
                    conexao.commit()
                    print("\nMeta criada com sucesso! O grupo agora aparecerá na aba deste livro.")
                
            except mysql.connector.Error as e:
                conexao.rollback()
                print(f"Erro ao definir leitura: {e}")
                
        elif opc == "4":
            cursor.execute("""
                SELECT m.id_meta, l.titulo_livro, DATE_FORMAT(m.dt_meta, '%d/%m/%Y') AS data_meta
                FROM tbl_metas_leitura m
                INNER JOIN meta_livro ml ON m.id_meta = ml.id_meta
                INNER JOIN tbl_livros l ON ml.id_livro = l.id_livro
                WHERE m.id_grupo = %s
            """, (id_grupo_escolhido,))
            metas = cursor.fetchall()
            
            if not metas:
                print("\nEste grupo não possui nenhuma meta de leitura ativa no momento.")
                continue
                
            print("\n|=---- METAS DO GRUPO ----=|")
            for m in metas:
                print(f"[ID: {m['id_meta']}] {m['titulo_livro']} (Prazo: {m['data_meta']})")
                
            id_remover = input("\nDigite o ID da meta que deseja remover (ou 0 para cancelar): ").strip()
            
            if id_remover == "0" or not id_remover.isdigit():
                continue
                
            try:
                cursor.execute("DELETE FROM meta_livro WHERE id_meta = %s", (int(id_remover),))
                cursor.execute("DELETE FROM tbl_metas_leitura WHERE id_meta = %s AND id_grupo = %s", (int(id_remover), id_grupo_escolhido))
                
                if cursor.rowcount == 0:
                    print("\nMeta não encontrada neste grupo.")
                else:
                    conexao.commit()
                    print("\nMeta de leitura removida com sucesso!")
            except mysql.connector.Error as e:
                conexao.rollback()
                print(f"Erro ao remover meta: {e}")
                
    cursor.close()