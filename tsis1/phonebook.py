# Основная логика работы с телефонной книгой
import psycopg2
from connect import get_connection

# Выполнение SQL-файла для создания структуры базы данных
def execute_sql_file(filename):
    with open(filename, 'r') as file:
        sql = file.read()  # Чтение SQL-скрипта из файла
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)  # Выполнение SQL-запроса
        conn.commit()  # Применение изменений

# Функция для получения или создания группы
def get_or_create_group(cur, group_name):
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    result = cur.fetchone()
    
    if result:
        return result[0]  # Егер топ бар болса, оның ID-ін қайтарамыз
    else:
        # Егер топ жоқ болса, оны құрып, RETURNING арқылы ID-ін аламыз
        cur.execute("INSERT INTO groups(name) VALUES (%s) RETURNING id", (group_name,))
        new_id = cur.fetchone()[0]
        return new_id

# Добавление нового контакта
def add_contact(username, email, birthday, group_name):
    with get_connection() as conn:
        with conn.cursor() as cur:
            group_id = get_or_create_group(cur, group_name)  # Получаем ID группы
            cur.execute("INSERT INTO contacts(username, email, birthday, group_id) VALUES (%s, %s, %s, %s)", 
                        (username, email, birthday, group_id))  # Добавление контакта
            conn.commit()

def add_phone_to_contact(username, phone, phone_type):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Пайдаланушының ID-ін алу
            cur.execute("SELECT id FROM contacts WHERE username = %s", (username,))
            result = cur.fetchone()
            
            if result:
                contact_id = result[0]
                # 2. Баған атын 'type' деп өзгертіп көрейік
                cur.execute("INSERT INTO phones(contact_id, phone, type) VALUES (%s, %s, %s)", 
                            (contact_id, phone, phone_type))
                conn.commit()
                print(f"Phone added for {username}")
            else:
                print(f"Contact {username} not found!")

# Поиск контактов по имени
def search_contacts_console():
    name = input("Enter contact name: ")  # Ввод имени для поиска
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM contacts WHERE username LIKE %s", (f'%{name}%',))  # Поиск в БД
            rows = cur.fetchall()  # Получаем все результаты
            for row in rows:
                print(row)  # Выводим результаты

# Главное меню
def menu():
    while True:
        print("1. Add contact")
        print("2. Add phone")
        print("3. Search contacts")
        print("0. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            username = input("Username: ")
            email = input("Email: ")
            birthday = input("Birthday (YYYY-MM-DD): ")
            group_name = input("Group: ")
            add_contact(username, email, birthday, group_name)  # Добавление контакта
        elif choice == '2':
            username = input("Username: ")
            phone = input("Phone: ")
            phone_type = input("Phone type (home/work/mobile): ")
            add_phone_to_contact(username, phone, phone_type)  # Добавление телефона
        elif choice == '3':
            search_contacts_console()  # Поиск контактов
        elif choice == '0':
            break  # Выход из программы
        else:
            print("Invalid option.")

if __name__ == "__main__":
    try:
        execute_sql_file('schema.sql')

    except Exception as e:
        print(f"Database setup notice: {e}")
        
    menu()