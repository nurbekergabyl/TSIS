# Модуль для подключения к базе данных PostgreSQL
import psycopg2
from config import DB_CONFIG

# Функция для получения подключения к базе данных
def get_connection():
    return psycopg2.connect(**DB_CONFIG)  # Подключение через параметры из config.py