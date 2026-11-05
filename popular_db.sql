-- Script para popular o banco de dados com dados fictícios
USE saep_db;

-- Tabela de Usuários (senhas: password_123, password_456, password_789)
INSERT IGNORE INTO usuarios (nome, email, senha_hash) VALUES
('Administrador', 'admin@gmail.com', 'scrypt:32768:8:1$YDFnR2OUs7ZhHXSB$316b138ef69e49a8317c07164b01c8a7c12742b1fe2afcfdf092d204589f165242b79f91db504a3dbfd49dd7162f4cccaac31480274203f48bdd151d150ef9f4'),
('Augusto Fernando', 'augusto.fernando@gmail.com', 'scrypt:32768:8:1$zEHWPyKUEy7IA5HH$f1d9f93da1ab837b647c50cba418aa2a7ac00c02a62ac0878237806b1a7f7005ee561b6c75ab769e349040efa5163c630a141e7c0e5dfde918f1b203341dfa58'),
('Maria Oliveira', 'maria.oliveira@gmail.com', 'scrypt:32768:8:1$CbFMLEvhz7jTymqa$4ed1e36726348296ecafadc2e4f9aabb0b650672bc950cc0aae0c57612f3869ee8f1be9266fa7eb1090e8ba71fd9932c4ea45ccba51d7243a8c4992eae14d27b');

-- Tabela de Tutores (CPFs criptografados com Fernet: 11122233344, 22233344455, 33344455566)
INSERT IGNORE INTO tutores (id, nome, cpf_criptografado, email, telefone) VALUES
(1, 'João Silva', 'gAAAAABqGKUA69yjCFtndJBRLgB4o1uMk0uvIrZNJ7LB-DpUCkJf_6Gqbfo6qup5oAOC-9xo14-0zrpkQ7lc7BnRiuHmZ_7BEA==', 'joao.silva@gmail.com', '11999999999'),
(2, 'Maria Oliveira', 'gAAAAABqGKUAuvV99SdWSkLrux09uQCe73q0yAftXdVIu2a87idkumlm217AhFoVgjrgjSrfSXx4tF_Iv1ZNrQupFIhU4yaQjw==', 'maria.oliveira@gmail.com', '11888888888'),
(3, 'Carlos Souza', 'gAAAAABqGKUARm8izy4jUgVr56h7y5PpHzWtYOex_ThT9r6B0VJyYyAPnnqxWuIEyQSfra-U3iM7KwzHDl3irfwRJxLBDVOM6A==', 'carlos.souza@gmail.com', '11777777777');

-- Tabela de Pets
INSERT IGNORE INTO pets (id, id_tutor, nome, especie, raca, peso) VALUES
(1, 1, 'Thor', 'Cachorro', 'Labrador', '30kg'),
(2, 1, 'Mia', 'Gato', 'Siamês', '4kg'),
(3, 2, 'Trovão', 'Cachorro', 'Golden Retriever', '28kg'),
(4, 3, 'Luna', 'Gato', 'Rajada', '5kg');

-- Tabela de Agendamentos
INSERT IGNORE INTO agendamentos (id, tutor_id, pet_id, objetivo, data, horario, observacao) VALUES
(1, 1, 1, 'Banho', '2026-06-15', '10:15:00', ''),
(2, 1, 2, 'Vacinação', '2026-06-16', '14:30:00', ''),
(3, 2, 3, 'Exame Geral', '2026-06-17', '09:00:00', 'Jejum de 12 horas'),
(4, 3, 4, 'Banho e Tosa', '2026-06-18', '11:15:00', '');