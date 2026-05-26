
-- CRIAÇÃO DO BANCO DE DADOS - ORBITLIT (VERSÃO FINAL)

DROP DATABASE IF EXISTS orbitlit_db;
CREATE DATABASE orbitlit_db;
USE orbitlit_db;

-- 1. TABELAS PRINCIPAIS

CREATE TABLE IF NOT EXISTS tbl_usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome_usuario VARCHAR(200) NOT NULL,
    email_usuario VARCHAR(200) UNIQUE NOT NULL,
    dt_nascimento_usuario DATE,
    senha_usuario VARCHAR(260) NOT NULL,
    bio_usuario VARCHAR(500) DEFAULT 'Olá! Sou um novo leitor no OrbitLit.', -- NOVA COLUNA ADICIONADA
    admin_usuario BOOLEAN DEFAULT FALSE 
);

CREATE TABLE IF NOT EXISTS tbl_grupos (
    id_grupo INT AUTO_INCREMENT PRIMARY KEY,
    nome_grupo VARCHAR(200) NOT NULL,
    descricao_grupo VARCHAR (3000),
    link_externo_grupo VARCHAR(260),
    dt_criacao_grupo DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tbl_livros (
    id_livro INT AUTO_INCREMENT PRIMARY KEY,
    titulo_livro VARCHAR(200) NOT NULL,
    sinopse_livro VARCHAR(2000) NOT NULL,
    total_paginas INT NOT NULL DEFAULT 0, 
    dt_de_publicacao DATE
);

CREATE TABLE IF NOT EXISTS tbl_autor (
    id_autor INT AUTO_INCREMENT PRIMARY KEY,
    nome_autor VARCHAR(200) UNIQUE NOT NULL 
);

CREATE TABLE IF NOT EXISTS tbl_generos (
    id_genero INT AUTO_INCREMENT PRIMARY KEY,
    nome_genero VARCHAR(100) UNIQUE NOT NULL 
);


-- 2. TABELAS DEPENDENTES (Com 1 ou 2 Chaves Estrangeiras)

-- Metas do Grupo
CREATE TABLE IF NOT EXISTS tbl_metas_leitura (
    id_meta INT AUTO_INCREMENT PRIMARY KEY,
    paginas_meta INT NOT NULL,
    dt_meta DATE NOT NULL,
    id_grupo INT NOT NULL,
    FOREIGN KEY (id_grupo) REFERENCES tbl_grupos(id_grupo) ON DELETE CASCADE
);

-- Avaliações (Usuário avalia Livro)
CREATE TABLE IF NOT EXISTS tbl_avaliacoes (
    id_avaliacao INT AUTO_INCREMENT PRIMARY KEY,
    nota_avaliacao DECIMAL(3,1) NOT NULL,
    dt_avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    comentario_avaliacao VARCHAR(3000),
    id_usuario INT NOT NULL,
    id_livro INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES tbl_usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_livro) REFERENCES tbl_livros(id_livro) ON DELETE CASCADE
);

-- Leituras (Controle de páginas lidas pelo Usuário)
CREATE TABLE IF NOT EXISTS tbl_leituras (
    id_leitura INT AUTO_INCREMENT PRIMARY KEY,
    concluido_leitura BOOLEAN DEFAULT FALSE,
    pg_lidas_leitura INT DEFAULT 0,
    dt_inicio_leitura DATE,
    dt_fim_leitura DATE,
    id_usuario INT NOT NULL,
    id_livro INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES tbl_usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_livro) REFERENCES tbl_livros(id_livro) ON DELETE CASCADE
);


-- 3. TABELAS ASSOCIATIVAS (Relacionamentos N:M)

-- Usuários <-> Grupos
CREATE TABLE IF NOT EXISTS participantes (
    id_usuario INT NOT NULL,
    id_grupo INT NOT NULL,
    admin BOOLEAN DEFAULT FALSE,
    dt_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pendente', 'Aprovado') DEFAULT 'Pendente',
    PRIMARY KEY (id_usuario, id_grupo),
    FOREIGN KEY (id_usuario) REFERENCES tbl_usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_grupo) REFERENCES tbl_grupos(id_grupo) ON DELETE CASCADE
);

-- Metas <-> Livros
CREATE TABLE IF NOT EXISTS meta_livro (
    id_meta INT NOT NULL,
    id_livro INT NOT NULL,
    PRIMARY KEY (id_meta, id_livro),
    FOREIGN KEY (id_meta) REFERENCES tbl_metas_leitura(id_meta) ON DELETE CASCADE,
    FOREIGN KEY (id_livro) REFERENCES tbl_livros(id_livro) ON DELETE CASCADE
);

-- Livros <-> Autores
CREATE TABLE IF NOT EXISTS livro_autor (
    id_livro INT NOT NULL,
    id_autor INT NOT NULL,
    PRIMARY KEY (id_livro, id_autor),
    
    -- Se apagar o livro, a ponte some (CASCADE)
    FOREIGN KEY (id_livro) REFERENCES tbl_livros(id_livro) ON DELETE CASCADE,
    
    -- Se apagar o autor, o banco BLOQUEIA a operação (RESTRICT)
    FOREIGN KEY (id_autor) REFERENCES tbl_autor(id_autor) ON DELETE RESTRICT
);

-- Livros <-> Gêneros
CREATE TABLE IF NOT EXISTS livro_genero (
    id_livro INT NOT NULL,
    id_genero INT NOT NULL,
    PRIMARY KEY (id_livro, id_genero),
    
    -- Se apagar o livro, a ponte some (CASCADE)
    FOREIGN KEY (id_livro) REFERENCES tbl_livros(id_livro) ON DELETE CASCADE,
    
    -- Se apagar o gênero, o banco BLOQUEIA a operação (RESTRICT)
    FOREIGN KEY (id_genero) REFERENCES tbl_generos(id_genero) ON DELETE RESTRICT
);