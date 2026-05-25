-- INSERT COMPLETO PARA TESTES (VERSÃO V4) - ORBITLIT

USE orbitlit_db;

-- 1. Inserindo Usuários
INSERT INTO tbl_usuario (id_usuario, nome_usuario, email_usuario, dt_nascimento_usuario, senha_usuario, bio_usuario, admin_usuario) VALUES 
(1, 'João Silva', 'joao@orbitlit.com', '1995-04-12', 'senha123', 'Leitor assíduo de ficção científica. Adoro debater sobre distopias.', TRUE),
(2, 'Maria Souza', 'maria@email.com', '1998-10-25', 'senha123', 'Fundadora do Canto da Fantasia. Viajando por mundos mágicos desde 2010.', FALSE),
(3, 'Carlos Andrade', 'carlos@email.com', '2001-02-05', 'senha123', 'Explorando novos universos literários. Fã incondicional de Frank Herbert.', FALSE);

-- 2. Inserindo Livros
INSERT INTO tbl_livros (id_livro, titulo_livro, sinopse_livro, total_paginas, dt_de_publicacao) VALUES 
(1, 'O Senhor dos Anéis: A Sociedade do Anel', 'Um hobbit recebe a tarefa de destruir um anel mágico.', 576, '1954-07-29'),
(2, '1984', 'Um homem tenta sobreviver sob a vigilância do Grande Irmão.', 328, '1949-06-08'),
(3, 'Duna', 'Intrigas políticas e religião em um planeta deserto chamado Arrakis.', 680, '1965-08-01'),
(4, 'Deuses Americanos', 'Os deuses antigos andam pela América se preparando para a guerra.', 464, '2001-06-19');

-- 3. Inserindo Autores
INSERT INTO tbl_autor (id_autor, nome_autor) VALUES 
(1, 'J.R.R. Tolkien'),
(2, 'George Orwell'),
(3, 'Frank Herbert'),
(4, 'Neil Gaiman');

-- 4. Inserindo Gêneros
INSERT INTO tbl_generos (id_genero, nome_genero) VALUES 
(1, 'Fantasia'),
(2, 'Ficção Científica'),
(3, 'Distopia'),
(4, 'Mistério');

-- 5. Relacionamento: Livros <-> Autores
INSERT INTO livro_autor (id_livro, id_autor) VALUES 
(1, 1), (2, 2), (3, 3), (4, 4);

-- 6. Relacionamento: Livros <-> Gêneros
INSERT INTO livro_genero (id_livro, id_genero) VALUES 
(1, 1), (2, 2), (2, 3), (3, 2), (4, 1), (4, 4);

-- 7. Inserindo Avaliações
INSERT INTO tbl_avaliacoes (nota_avaliacao, comentario_avaliacao, id_usuario, id_livro) VALUES 
(5.0, 'Uma obra prima absoluta! O universo que ele criou é incrível.', 2, 1),
(4.5, 'Livro assustadoramente atual. O final me deixou de queixo caído.', 3, 2),
(4.0, 'Muito bom, mas demorei para pegar o ritmo da leitura.', 2, 4);

-- 8. Inserindo Grupos de Leitura
INSERT INTO tbl_grupos (id_grupo, nome_grupo, descricao_grupo, link_externo_grupo) VALUES 
(1, 'Clube da Ficção Científica', 'Para amantes de viagens espaciais e mundos distópicos.', 'https://discord.gg/convite-fake-sf'),
(2, 'Canto da Fantasia', 'Leituras focadas em alta fantasia, magia e mundos medievais.', 'https://chat.whatsapp.com/convite-fake-fantasia');

-- 9. Vinculando Participantes aos Grupos (AGORA COM O STATUS DE APROVAÇÃO)
INSERT INTO participantes (id_usuario, id_grupo, admin, status) VALUES 
(1, 1, TRUE, 'Aprovado'), -- João administra o grupo 1
(2, 1, FALSE, 'Aprovado'), -- Maria é membro aprovada no grupo 1
(2, 2, TRUE, 'Aprovado'), -- Maria administra o grupo 2
(3, 2, FALSE, 'Aprovado'), -- Carlos é membro aprovado no grupo 2
(3, 1, FALSE, 'Pendente'); -- Carlos quer entrar no grupo 1 (Aparecerá na Sala de Espera do João)

-- 10. Inserindo Metas de Leitura
INSERT INTO tbl_metas_leitura (id_meta, paginas_meta, dt_meta, id_grupo) VALUES 
(1, 328, '2026-06-30', 1), -- Meta do Grupo Sci-Fi
(2, 576, '2026-07-15', 2); -- Meta do Grupo Fantasia

-- 11. Vinculando Metas aos Livros
INSERT INTO meta_livro (id_meta, id_livro) VALUES 
(1, 2), -- Grupo de Sci-Fi está lendo 1984
(2, 1); -- Grupo de Fantasia está lendo Senhor dos Anéis

-- 12. Inserindo o Controle de Leituras (Estante Pessoal)
INSERT INTO tbl_leituras (concluido_leitura, pg_lidas_leitura, dt_inicio_leitura, dt_fim_leitura, id_usuario, id_livro) VALUES 
(TRUE, 328, '2026-04-01', '2026-04-15', 2, 2),  -- Maria leu 1984
(FALSE, 150, '2026-05-01', NULL, 2, 1), -- Maria está lendo Senhor dos Anéis
(FALSE, 25, '2026-05-10', NULL, 3, 3), -- Carlos está lendo Duna
(FALSE, 0, '2026-05-20', NULL, 1, 4); -- João quer ler Deuses Americanos