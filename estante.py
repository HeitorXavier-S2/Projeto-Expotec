from datetime import date
import mysql.connector

def adicionar_a_estante(conexao, id_usuario_logado, id_livro):
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_leitura FROM tbl_leituras WHERE id_usuario = %s AND id_livro = %s", (id_usuario_logado, id_livro))
        existe = cursor.fetchone()

        if existe:
            print("\nEste livro já está na tua estante!")
            print("Para atualizar o teu progresso ou removê-lo, usa a opção 'Gerenciar Leituras' no Painel Principal.")
            return

        cursor.execute("SELECT titulo_livro, total_paginas FROM tbl_livros WHERE id_livro = %s", (id_livro,))
        livro = cursor.fetchone()
        
        print("\n=================== ADICIONAR À ESTANTE ===================")
        print(f"Livro: {livro['titulo_livro']}")
        print("1. Adicionar como 'Quero Ler'")
        print("2. Adicionar como 'Lendo' (Iniciar leitura hoje)")
        print("3. Adicionar como 'Lido' (Marcar como Concluído)")
        print("0. Cancelar")
        
        escolha = input("\nEscolha uma opção: ").strip()
        hoje = date.today().strftime('%Y-%m-%d')
        
        if escolha == "1":
            cursor.execute(
                "INSERT INTO tbl_leituras (concluido_leitura, pg_lidas_leitura, id_usuario, id_livro) VALUES (FALSE, 0, %s, %s)",
                (id_usuario_logado, id_livro)
            )
            print("\nAdicionado à tua lista de 'Quero Ler'!")
            
        elif escolha == "2":
            cursor.execute(
                "INSERT INTO tbl_leituras (concluido_leitura, pg_lidas_leitura, dt_inicio_leitura, id_usuario, id_livro) VALUES (FALSE, 0, %s, %s, %s)",
                (hoje, id_usuario_logado, id_livro)
            )
            print("\nAdicionado como 'Lendo'! Boa leitura!")
            
        elif escolha == "3":
            cursor.execute(
                "INSERT INTO tbl_leituras (concluido_leitura, pg_lidas_leitura, dt_inicio_leitura, dt_fim_leitura, id_usuario, id_livro) VALUES (TRUE, %s, %s, %s, %s, %s)",
                (livro['total_paginas'], hoje, hoje, id_usuario_logado, id_livro)
            )
            print("\nAdicionado como 'Lido'! Parabéns por mais uma obra concluída.")
            
        conexao.commit()
    except mysql.connector.Error as e:
        conexao.rollback()
        print(f"Erro ao adicionar à estante: {e}")
    finally:
        cursor.close()


def gerenciar_leituras(conexao, id_usuario_logado):
    while True:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT e.id_leitura, l.titulo_livro, l.total_paginas, e.concluido_leitura, e.pg_lidas_leitura
                FROM tbl_leituras e
                INNER JOIN tbl_livros l ON e.id_livro = l.id_livro
                WHERE e.id_usuario = %s
            """, (id_usuario_logado,))
            leituras = cursor.fetchall()
            
            print("\n=================== GERENCIAR MINHAS LEITURAS ===================")
            if not leituras:
                print("A tua estante está vazia. Explora o acervo para adicionar livros!")
                cursor.close()
                break
                
            for idx, lt in enumerate(leituras, start=1):
                status = "Lido" if lt['concluido_leitura'] else "Lendo/Quero Ler"
                print(f"[{idx}] {lt['titulo_livro']} | Status: {status} ({lt['pg_lidas_leitura']}/{lt['total_paginas']} pgs)")
            print("0. Voltar")
            
            opcao = input("\nEscolha o número do livro para gerenciar (ou 0 para voltar): ").strip()
            if opcao == "0" or not opcao.isdigit():
                cursor.close()
                break
                
            idx_escolhido = int(opcao) - 1
            if idx_escolhido < 0 or idx_escolhido >= len(leituras):
                print("Opção inválida.")
                cursor.close()
                continue
                
            leitura_sel = leituras[idx_escolhido]
            
            while True:
                print(f"\n|=---- GERENCIANDO: {leitura_sel['titulo_livro'].upper()} ----=|")
                print("1. Atualizar páginas lidas")
                print("2. Marcar como Concluído (Lido)")
                print("3. Remover da estante")
                print("0. Voltar")
                
                sub_opcao = input("\nEscolha uma opção: ").strip()
                if sub_opcao == "0":
                    break
                    
                elif sub_opcao == "1":
                    if leitura_sel['concluido_leitura']:
                        print("\nEste livro já está concluído!")
                    else:
                        try:
                            novas_pg = int(input(f"\nQuantas páginas leu até agora? (Máx: {leitura_sel['total_paginas']}): "))
                            if 0 <= novas_pg <= leitura_sel['total_paginas']:
                                cursor.execute("UPDATE tbl_leituras SET pg_lidas_leitura = %s WHERE id_leitura = %s", (novas_pg, leitura_sel['id_leitura']))
                                conexao.commit()
                                print("\nProgresso atualizado!")
                                leitura_sel['pg_lidas_leitura'] = novas_pg
                            else:
                                print(f"\nErro: O número deve ser entre 0 e {leitura_sel['total_paginas']}.")
                        except ValueError:
                            print("\nDigite apenas números inteiros.")
                            
                elif sub_opcao == "2":
                    if leitura_sel['concluido_leitura']:
                        print("\nEste livro já está concluído!")
                    else:
                        hoje = date.today().strftime('%Y-%m-%d')
                        cursor.execute(
                            "UPDATE tbl_leituras SET concluido_leitura = TRUE, pg_lidas_leitura = %s, dt_fim_leitura = %s WHERE id_leitura = %s",
                            (leitura_sel['total_paginas'], hoje, leitura_sel['id_leitura'])
                        )
                        conexao.commit()
                        print("\nParabéns! Livro marcado como concluído!")
                        leitura_sel['concluido_leitura'] = True
                        leitura_sel['pg_lidas_leitura'] = leitura_sel['total_paginas']
                        
                elif sub_opcao == "3":
                    certeza = input("\nTens a certeza que desejas remover este livro da estante? (S/N): ").strip().upper()
                    if certeza == "S":
                        cursor.execute("DELETE FROM tbl_leituras WHERE id_leitura = %s", (leitura_sel['id_leitura'],))
                        conexao.commit()
                        print("\nLivro removido com sucesso!")
                        break
            
        except mysql.connector.Error as e:
            print(f"Erro na base de dados: {e}")
        finally:
            cursor.close()