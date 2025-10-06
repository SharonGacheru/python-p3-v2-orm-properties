from __init__ import CURSOR, CONN
from department import Department

class Employee:
    _instances = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name      # uses property
        self.job_title = job_title  # uses property
        self.department_id = department_id  # uses property

        if self.id is not None:
            if self.id not in Employee._instances:
                Employee._instances[self.id] = []
            Employee._instances[self.id].append(self)

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
    def job_title(self):
        return self._job_title
    
    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str):
            raise ValueError("Job Title must be a string.")
        if len(value) < 1:
            raise ValueError("Job Title must be at least 1 character.")
        self._job_title = value

    @property
    def department_id(self):
        return self._department_id
    
    @department_id.setter
    def department_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Department ID must be an integer.")
        # FK check -- make sure department exists
        row = CURSOR.execute("SELECT * FROM departments WHERE id = ?", (value,)).fetchone()
        if not row:
            raise ValueError("No such department id.")
        self._department_id = value

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER REFERENCES departments(id)
            );
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS employees;")
        CONN.commit()

    def save(self):
        sql = "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)"
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        if self.id not in Employee._instances:
            Employee._instances[self.id] = []
        Employee._instances[self.id].append(self)

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def update(self):
        sql = "UPDATE employees SET name = ?, job_title = ?, department_id = ? WHERE id = ?"
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM employees WHERE id = ?", (self.id,))
        CONN.commit()
        target_id = self.id
        for obj in list(Employee._instances.get(target_id, [])):
            obj.id = None
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        obj = cls(row[1], row[2], row[3], row[0])
        if obj.id is not None:
            if obj.id not in Employee._instances:
                Employee._instances[obj.id] = []
            Employee._instances[obj.id].append(obj)
        return obj

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM employees").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_name(cls, name):
        row = CURSOR.execute("SELECT * FROM employees WHERE name = ?", (name,)).fetchone()
        if row:
            return cls.instance_from_db(row)

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute("SELECT * FROM employees WHERE id = ?", (id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
