from __init__ import CURSOR, CONN

class Department:
    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name   # uses property
        self.location = location   # uses property

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string.")
        if len(value) < 1:
            raise ValueError("Name must be at least 1 character.")
        self._name = value

    @property
    def location(self):
        return self._location
    
    @location.setter
    def location(self, value):
        if not isinstance(value, str):
            raise ValueError("Location must be a string.")
        if len(value) < 1:
            raise ValueError("Location must be at least 1 character.")
        self._location = value

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT
            );
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS departments;")
        CONN.commit()

    def save(self):
        sql = "INSERT INTO departments (name, location) VALUES (?, ?)"
        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()
        self.id = CURSOR.lastrowid

    @classmethod
    def create(cls, name, location):
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        CURSOR.execute(
            "UPDATE departments SET name = ?, location = ? WHERE id = ?",
            (self.name, self.location, self.id)
        )
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM departments WHERE id = ?", (self.id,))
        CONN.commit()
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        return cls(row[1], row[2], row[0])

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM departments").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute("SELECT * FROM departments WHERE id = ?", (id,)).fetchone()
        if row:
            return cls.instance_from_db(row)

    @classmethod
    def find_by_name(cls, name):
        row = CURSOR.execute("SELECT * FROM departments WHERE name = ?", (name,)).fetchone()
        if row:
            return cls.instance_from_db(row)

    def employees(self):
        from employee import Employee
        return [emp for emp in Employee.get_all() if emp.department_id == self.id]
