import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).with_name('.env'))


class Config:
    # Nome e conexão ficam aqui; os valores locais podem ser definidos no .env.
    NOME_SISTEMA = os.getenv('SAEP_NOME_SISTEMA', 'Clinica Pet')
    SUBTITULO_SISTEMA = os.getenv('SAEP_SUBTITULO_SISTEMA', 'Clinica Veterinária')
    SECRET_KEY = os.getenv('SAEP_SECRET_KEY', 'c0bd3652a849d23961870be955facc8be1e81629666c9e8ae8175f5a935e68e18')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    DB_HOST = os.getenv('SAEP_DB_HOST', 'localhost')
    DB_USER = os.getenv('SAEP_DB_USER', 'root')
    DB_PASSWORD = os.getenv('SAEP_DB_PASSWORD', '')
    DB_NAME = os.getenv('SAEP_DB_NAME', 'saep_db')

    # Esta chave mantém compatibilidade com os CPFs já cadastrados no projeto.
    CPF_KEY = os.getenv('SAEP_CPF_KEY', 'wxO_FPmABYEhJSxyaZiZTbR5FLAfJiBi4VYIxnEIjX4=')
    DEBUG = os.getenv('SAEP_DEBUG', 'false').lower() in ('1', 'true', 'yes')