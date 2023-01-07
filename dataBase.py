import sqlite3


class DataBase:
    def __init__(self, file):
        self.connection = sqlite3.connect(file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.status = self.Status(file)
        self.balance = self.Balance(file)
        self.check = self.Check(file)

    def get_user(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
        if len(result) == 0:
            return False
        return result[0]


    def add_user(self, user_id):
        with self.connection:
            self.cursor.execute(f"INSERT INTO users (user_id) VALUES (?)", (user_id,))


    def list_users(self):
        with self.connection:
            result = self.cursor.execute(f"SELECT * FROM users").fetchall()
        answer = ""
        for user in result:
            if user[2] != "banned":
                answer += f"id: {user[0]}, статус: {user[2]}, баланс: {user[1]}руб.\n"
        return answer.strip("\n")


    class Status:
        """ Получить/ Изменить статус пользователя"""
        def __init__(self, file):
            self.connection = sqlite3.connect(file, check_same_thread=False)
            self.cursor = self.connection.cursor()

        def get(self, message=None, user_id=None):
            """ Получить статус пользователя """
            if message is not None:
                result = self.cursor.execute(f"SELECT status FROM users WHERE user_id = ?", (message.from_user.id,)).fetchall()
            elif user_id is not None:
                result = self.cursor.execute(f"SELECT status FROM users WHERE user_id = ?", (user_id,)).fetchall()
            else:
                exit("Как минимум одно значение должно быть указано")
                return False
            if len(result) > 0:
                return result[0][0]
            else:
                return None

        def banned(self, message=None, user_id=None):
            """ Забанить пользователя """
            if message is not None:
                if len(self.cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (message.text,)).fetchall()) == 0:
                    exit("Пользователь не найден")
                with self.connection:
                    self.cursor.execute(f"UPDATE users SET status = 'banned' WHERE user_id = ?", (message.text,))
            elif user_id is not None:
                if len(self.cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()) == 0:
                    exit("Пользователь не найден")
                with self.connection:
                    self.cursor.execute(f"UPDATE users SET status = 'banned' WHERE user_id = ?", (user_id,))
            else:
                exit("Как минимум одно значение должно быть указано")

        def admin(self, message=None, user_id=None):
            """ Повысить статус пользователя до admin """
            if message is not None:
                if len(self.cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (message.text,)).fetchall()) == 0:
                    exit("Пользователь не найден")
                with self.connection:
                    self.cursor.execute(f"UPDATE users SET status = 'admin' WHERE user_id = ?", (message.text,))
            elif user_id is not None:
                if len(self.cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()) == 0:
                    exit("Пользователь не найден")
                with self.connection:
                    self.cursor.execute(f"UPDATE users SET status = 'admin' WHERE user_id = ?", (user_id,))
            else:
                exit("Как минимум одно значение должно быть указано")

        def user(self, message=None, user_id=None):
            """ Разбанить / Понизить пользователя до статуса user"""
            if message is not None:
                if len(self.cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (message.text,)).fetchall()) == 0:
                    exit("Пользователь не найден")
                with self.connection:
                    self.cursor.execute(f"UPDATE users SET status = 'user' WHERE user_id = ?", (message.text,))
            elif user_id is not None:
                if len(self.cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()) == 0:
                    exit("Пользователь не найден")
                with self.connection:
                    self.cursor.execute(f"UPDATE users SET status = 'user' WHERE user_id = ?", (user_id,))
            else:
                exit("Как минимум одно значение должно быть указано")


    class Balance:
        """ Получить / Изменить баланс пользователя"""
        def __init__(self, file):
            self.connection = sqlite3.connect(file, check_same_thread=False)
            self.cursor = self.connection.cursor()

        def get(self, message=None, user_id=None):
            """ Получить баланс пользователя """
            if message is not None:
                result = self.cursor.execute(f"SELECT balance FROM users WHERE user_id = ?", (message.from_user.id,)).fetchall()
            elif user_id is not None:
                result = self.cursor.execute(f"SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchall()
            else:
                exit("Как минимум одно значение должно быть указано")
                return False
            if len(result) > 0:
                return result[0][0]
            else:
                return None


        def set(self, balance, user_id=None, message=None):
            """ Установить баланс для пользователя"""
            if message is not None:
                with self.connection:
                    self.cursor.execute(f"UPDATE users SET balance = ? WHERE user_id = ?",(balance, message.text,))
            elif user_id is not None:
                with self.connection:
                    self.cursor.execute(f"UPDATE users SET balance = ? WHERE user_id = ?",(balance, user_id,))
            else:
                exit("Как минимум одно значение из (user_id и message) должно быть указано")


    class Check:
        """ Создать / Удалить / Получить чек"""
        def __init__(self, file):
            self.connection = sqlite3.connect(file, check_same_thread=False)
            self.cursor = self.connection.cursor()

        def create(self, user_id, check_id, money, url):
            """ Создать чек """
            with self.connection:
                self.cursor.execute(f"INSERT INTO checks ('user_id', 'check_id', 'money', url) VALUES (?,?,?,?)", (user_id, check_id, money, url,))

        def delete(self, check_id):
            """ Удалить чек """
            with self.connection:
                self.cursor.execute(f"DELETE FROM checks WHERE check_id = ?", (check_id,))

        def get(self, check_id):
            """ Получить чек """
            with self.connection:
                result = self.cursor.execute(f"SELECT * FROM checks WHERE check_id = ?", (check_id,)).fetchall()
            if len(result) == 0:
                return False
            return result[0]

# db = DataBase("dataBase.db")
# print(db.get_user(user_id=5))