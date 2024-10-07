import sqlite3
from datetime import datetime

db = sqlite3.connect('people.db')
cursor = db.cursor()

# Создаем таблицу пользователей с полем для последней даты получения бонуса
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        inviter INTEGER, 
        user_id INTEGER, 
        referals INTEGER, 
        balance INTEGER,
        last_bonus_date TEXT
    )
""")


def new_user(ref_id, id):
    with sqlite3.connect('people.db') as db:
        cursor = db.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (inviter, user_id, referals, balance, last_bonus_date)
            VALUES (?, ?, ?, ?, ?)
        """, (ref_id, id, 0, 0, None))
        db.commit()


def add_bonus(bonus, user_id):
    with sqlite3.connect('people.db') as db:
        cursor = db.cursor()
        add_bonus = cursor.execute(f'UPDATE users SET balance = balance + ? WHERE user_id = ?',
                                   (bonus, user_id))
        db.commit()
        if add_bonus:
            return True
        else:
            return False


def add_ref_balance(ref_id):
    with sqlite3.connect('people.db') as db:
        cursor = db.cursor()
        balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (ref_id,)).fetchone()[0]
        referals = cursor.execute('SELECT referals FROM users WHERE user_id = ?', (ref_id,)).fetchone()[0]

        cursor.execute(f'UPDATE users SET referals = {referals + 1} WHERE user_id = ?', (ref_id,))
        cursor.execute(f'UPDATE users SET balance = {balance + 10} WHERE user_id = ?', (ref_id,))
        db.commit()


def check_user(user_id):
    with sqlite3.connect('people.db') as db:
        cursor = db.cursor()
        result = cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)).fetchall()
        if result:
            return result
        else:
            return None


def get_info(user_id):
    with sqlite3.connect('people.db') as db:
        cursor = db.cursor()
        result = cursor.execute("SELECT balance, referals FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if result:
            return result
        else:
            return None, None


def bonusAccess(user_id):
    with sqlite3.connect('people.db') as db:
        cursor = db.cursor()

        # Получаем последнюю дату получения бонуса
        result = cursor.execute('SELECT last_bonus_date FROM users WHERE user_id = ?', (user_id,)).fetchone()
        if result and result[0]:
            last_bonus_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        else:
            last_bonus_date = None

        # Проверяем, прошло ли 3 дня -> 259200 секунд или 1 день -> 86400 секунд
        if last_bonus_date is None or (datetime.now() - last_bonus_date).total_seconds() > 259200:
            # Обновляем дату последнего бонуса
            cursor.execute('UPDATE users SET last_bonus_date = ? WHERE user_id = ?',
                           (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
            db.commit()
            return True
        else:
            return False
