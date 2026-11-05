DROP DATABASE IF EXISTS saep_db;
CREATE DATABASE IF NOT EXISTS saep_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE saep_db;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_usuarios_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tutores (
    id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    cpf_criptografado TEXT NOT NULL,
    email VARCHAR(120) NOT NULL,
    telefone VARCHAR(20),
    PRIMARY KEY (id),
    UNIQUE KEY uk_tutores_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pets (
    id INT NOT NULL AUTO_INCREMENT,
    id_tutor INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    especie VARCHAR(50) NOT NULL,
    raca VARCHAR(120) NOT NULL,
    peso VARCHAR(20),
    PRIMARY KEY (id),
    CONSTRAINT fk_pets_tutor FOREIGN KEY (id_tutor)
        REFERENCES tutores (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS agendamentos (
    id INT NOT NULL AUTO_INCREMENT,
    tutor_id INT NOT NULL,
    pet_id INT NOT NULL,
    objetivo VARCHAR(100) NOT NULL,
    data DATE NOT NULL,
    horario TIME NOT NULL,
    observacao TEXT,
    PRIMARY KEY (id),
    CONSTRAINT fk_agendamentos_tutor FOREIGN KEY (tutor_id)
        REFERENCES tutores (id) ON DELETE RESTRICT,
    CONSTRAINT fk_agendamentos_pet FOREIGN KEY (pet_id)
        REFERENCES pets (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- IMPORTANTE!
-- Acesso inicial:
-- admin@clinica.local / admin123
-- admin@gmail.com / password_123
-- augusto.fernando@gmail.com / password_456
-- maria.oliveira@gmail.com / password_789
-- As senhas abaixo estão em hash (scrypt) e os CPFs criptografados (Fernet), conforme exigido pela LGPD.

INSERT IGNORE INTO usuarios (id, nome, email, senha_hash) VALUES
(1, 'Administrador', 'admin@clinica.local', 'scrypt:32768:8:1$3zKrQJnj1qjDYx3B$858812ea8a4fc35d7b506e36dc62b61e4399d40d1a907f46d0572b3739547afea3d3702569b2cf2b9aad95d1ba7729a987536837456048cb25d1ba605bf6079d'),
(2, 'Augusto Fernando', 'augusto.fernando@gmail.com', 'scrypt:32768:8:1$zEHWPyKUEy7IA5HH$f1d9f93da1ab837b647c50cba418aa2a7ac00c02a62ac0878237806b1a7f7005ee561b6c75ab769e349040efa5163c630a141e7c0e5dfde918f1b203341dfa58'),
(3, 'Maria Oliveira', 'maria.oliveira@gmail.com', 'scrypt:32768:8:1$CbFMLEvhz7jTymqa$4ed1e36726348296ecafadc2e4f9aabb0b650672bc950cc0aae0c57612f3869ee8f1be9266fa7eb1090e8ba71fd9932c4ea45ccba51d7243a8c4992eae14d27b');

INSERT IGNORE INTO tutores (id, nome, cpf_criptografado, email, telefone) VALUES
(1, 'João Silva', 'gAAAAABqGKUA69yjCFtndJBRLgB4o1uMk0uvIrZNJ7LB-DpUCkJf_6Gqbfo6qup5oAOC-9xo14-0zrpkQ7lc7BnRiuHmZ_7BEA==', 'joao.silva@gmail.com', '11999999999'),
(2, 'Maria Oliveira', 'gAAAAABqGKUAuvV99SdWSkLrux09uQCe73q0yAftXdVIu2a87idkumlm217AhFoVgjrgjSrfSXx4tF_Iv1ZNrQupFIhU4yaQjw==', 'maria.oliveira@gmail.com', '11888888888'),
(3, 'Carlos Souza', 'gAAAAABqGKUARm8izy4jUgVr56h7y5PpHzWtYOex_ThT9r6B0VJyYyAPnnqxWuIEyQSfra-U3iM7KwzHDl3irfwRJxLBDVOM6A==', 'carlos.souza@gmail.com', '11777777777');

INSERT IGNORE INTO pets (id, id_tutor, nome, especie, raca, peso) VALUES
(1, 1, 'Thor', 'Cachorro', 'Labrador', '30kg'),
(2, 1, 'Mia', 'Gato', 'Siamês', '4kg'),
(3, 2, 'Trovão', 'Cachorro', 'Golden Retriever', '28kg'),
(4, 3, 'Luna', 'Gato', 'Rajada', '5kg');

INSERT IGNORE INTO agendamentos (id, tutor_id, pet_id, objetivo, data, horario, observacao) VALUES
(1, 1, 1, 'Banho', '2026-06-15', '10:15:00', ''),
(2, 1, 2, 'Vacinação', '2026-06-16', '14:30:00', ''),
(3, 2, 3, 'Exame Geral', '2026-06-17', '09:00:00', 'Jejum de 12 horas'),
(4, 3, 4, 'Banho e Tosa', '2026-06-18', '11:15:00', '');
