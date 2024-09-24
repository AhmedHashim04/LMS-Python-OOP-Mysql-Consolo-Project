from mysql.connector import connect

# Connect to the MySQL database
mydb = connect(host='localhost', user='root', password='', database='lms')
mycursor = mydb.cursor()

print(True)

# SQL statements to create tables
sql_statements = [
    '''
    CREATE TABLE IF NOT EXISTS students (
        id INT(255) NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        username VARCHAR(20) NOT NULL UNIQUE,
        password VARCHAR(20) NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    ''',
    '''
    CREATE TABLE IF NOT EXISTS lecturers (
        id INT(255) NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        username VARCHAR(20) NOT NULL UNIQUE,
        password VARCHAR(20) NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    ''',
    '''
    CREATE TABLE IF NOT EXISTS courses (
        id INT(11) NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        lecturer INT(11) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (lecturer) REFERENCES lecturers(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    ''',
    '''
    CREATE TABLE IF NOT EXISTS course_students (
        id INT(11) NOT NULL AUTO_INCREMENT,
        course_id INT(11) NOT NULL,
        student_id INT(11) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (course_id) REFERENCES courses(id),
        FOREIGN KEY (student_id) REFERENCES students(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    '''
]

# Execute SQL statements
for statement in sql_statements:
    mycursor.execute(statement)

mydb.commit()

class User:
    def __init__(self, **user_data):
        self.id = user_data['id']
        self.name = user_data['name']
        self.username = user_data['username']
        self.password = user_data['password']
        self.courses = user_data.get('courses', [])
    
    @classmethod
    def sign_up(cls):
        print("""
        Welcome to the LMS. Please choose your role:
        [1] Lecturer
        [2] Student
        [0] Close System
        """)
        
        choice = int(input("Choose from [0 - 2]: "))
        if choice == 1:
            role = "Lecturer"
        elif choice == 2:
            role = "Student"
        else:
            exit()

        new_username = input("Enter a username: ")
        new_password = input("Enter a password: ")
        new_name = input("Enter your full name: ")

        if role == "Lecturer":
            mycursor.execute("SELECT username FROM lecturers")
            usernames = [x[0] for x in mycursor.fetchall()]
            if new_username in usernames:
                print("Username already exists.")
                return
            
            sql = "INSERT INTO lecturers (name, username, password) VALUES (%s, %s, %s)"
            data = (new_name, new_username, new_password)
            mycursor.execute(sql, data)
            mydb.commit()
        else:
            mycursor.execute("SELECT username FROM students")
            usernames = [x[0] for x in mycursor.fetchall()]
            if new_username in usernames:
                print("Username already exists.")
                return

            sql = "INSERT INTO students (name, username, password) VALUES (%s, %s, %s)"
            data = (new_name, new_username, new_password)
            mycursor.execute(sql, data)
            mydb.commit()

        print("Account created successfully!")
        cls.login(new_username, new_password, role)
    
    @classmethod
    def login(cls, username, password, role):
        if role == "Lecturer":
            mycursor.execute("SELECT username, password FROM lecturers WHERE username = %s", (username,))
        else:
            mycursor.execute("SELECT username, password FROM students WHERE username = %s", (username,))

        result = mycursor.fetchone()

        if result and result[1] == password: #يعني لو طلع في يوزر نيم وباسورد بالاسم دا والباسورد = الباسورد خش
            print("Login successful!")
            if role == "Lecturer":
                mycursor.execute("SELECT id, name FROM lecturers WHERE username = %s", (username,))
                lecturer_data = mycursor.fetchone()
                cls.load_user_data(lecturer_data, "lecturers")
            else:
                mycursor.execute("SELECT id, name FROM students WHERE username = %s", (username,))
                student_data = mycursor.fetchone()
                cls.load_user_data(student_data, "students")
        else:
            print("Invalid username or password. Please try again.")
    
    @staticmethod
    def load_user_data(user_data, role):
        user_id, name = user_data
        mycursor.execute(f"SELECT name FROM courses WHERE {role[:-1]} = %s", (user_id,))
        courses = [x[0] for x in mycursor.fetchall()]
        user_info = {
            'id': user_id,
            'name': name,
            'username': user_data[0],
            'password': user_data[1],
            'courses': courses
        }
        if role == "lecturers":
            user = Lecturer(**user_info)
        else:
            user = Student(**user_info)

class Lecturer(User):
    def __init__(self, **user_data):
        super().__init__(**user_data)
        self.show_menu()
    
    def show_menu(self):
        print(f"Welcome, Dr. {self.name}")
        while True:
            print("""
            [1] Teach a new course
            [2] View my courses
            [0] Logout
            """)
            choice = int(input("Choose an option: "))
            if choice == 1:
                self.teach_new_course()
            elif choice == 2:
                self.view_my_courses()
            else:
                break
    
    def teach_new_course(self):
        new_course_name = input("Enter the course name: ")
        sql = "INSERT INTO courses (name, lecturer) VALUES (%s, %s)"
        data = (new_course_name, self.id)
        mycursor.execute(sql, data)
        mydb.commit()
        print(f"Course '{new_course_name}' has been created.")
    
    def view_my_courses(self):
        for idx, course in enumerate(self.courses, 1):
            print(f"{idx}. {course}")
            
        choise = int(input("Go To Course number : "))
        
        if choise in range(1, len(self.courses)):
            self.enter_course_list(course=choise-1)
        else:
            exit()
    
    def enter_course_list(self, course):
        print(f"You are in {self.courses[course]}")
        enterd_course = self.courses[course]
        
        print("""
            [1] - Course Join-Requests
            [2] - Course Quit-Requests
            [3] - Show Assignments
            [4] - Add Assignment
            [5] - Delete Assignment
            [6] - Block Student From Course 
                ---------------
            [0] - Close System
        """)
        
        choise = int(input("Do Operation number: "))
        
        if choise == 1:
            self.Accept_request_join(enterd_course)
        elif choise == 2:
            self.Accept_request_quit(enterd_course)
        elif choise == 3:
            self.show_Assignments(enterd_course)
        elif choise == 4:
            self.add_Assignment(enterd_course)
        elif choise == 5:
            self.delete_Assignment(enterd_course)
        elif choise == 6:
            self.block_student_from_course(enterd_course)
        else:
            exit()

    def Accept_request_join(self, enterd_course):
        mycursor.execute(f'SELECT * FROM requests WHERE lecturer={self.id} AND course="{enterd_course}" AND type="join"')
        students = [x for x in mycursor.fetchall()]
        
        for n, student in enumerate(students, 1):
            print(f'{n} - {student}')
        
        choice = int(input("Student number: "))
        while choice not in range(1, len(students)+1):
            choice = int(input(f"Student number from 1 to {len(students)}: "))
        
        mycursor.execute(f'SELECT id FROM courses WHERE name="{enterd_course}"')
        course_id = mycursor.fetchone()[0]
        student_id = students[choice-1][0]
        
        sql = "INSERT INTO course_students (course_id, student_id) VALUES (%s, %s)"
        data = (course_id, student_id)
        mycursor.execute(sql, data)
        mydb.commit()
        print(f"Student {student_id} added to course {course_id}")

    def Accept_request_quit(self, enterd_course):
        mycursor.execute(f'SELECT * FROM requests WHERE lecturer={self.id} AND course="{enterd_course}" AND type="quit"')
        students = [x for x in mycursor.fetchall()]
        
        for n, student in enumerate(students, 1):
            print(f'{n} - {student}')
        
        choice = int(input("Student number: "))
        while choice not in range(1, len(students)+1):
            choice = int(input(f"Student number from 1 to {len(students)}: "))
        
        mycursor.execute(f'SELECT id FROM courses WHERE name="{enterd_course}"')
        course_id = mycursor.fetchone()[0]
        student_id = students[choice-1][0]
        
        sql = "DELETE FROM course_students WHERE course_id=%s AND student_id=%s"
        data = (course_id, student_id)
        mycursor.execute(sql, data)
        mydb.commit()
        print(f"Student {student_id} removed from course {course_id}")

    def show_Assignments(self, enterd_course):
        mycursor.execute(f"SELECT question FROM assignments WHERE course='{enterd_course}'")
        assignments = mycursor.fetchall()
        
        if not assignments:
            print("No assignments found.")
            return
        
        for n, assignment in enumerate(assignments, 1):
            print(f"{n} - {assignment[0]}")

        assignment_num = int(input("Enter assignment number: "))
        if assignment_num in range(1, len(assignments)+1):
            self.enter_Assignments(assignment_num)
        else:
            print("Invalid assignment number.")
    
    def enter_Assignments(self, assignments_number):
        join_assignment = int(input("Enter assignment number: "))
        if join_assignment == 0:
            quit()
    
    def mark_Assignment(self, enterd_course):
        mycursor.execute(f"SELECT * FROM assignments WHERE course='{enterd_course}'")
        assignments = mycursor.fetchall()
        
        if not assignments:
            print("No assignments found for this course.")
            return
        
        for n, assignment in enumerate(assignments, 1):
            print(f"{n} - {assignment[1]}")
        
        choice = int(input("Enter the assignment number to mark: "))
        if choice < 1 or choice > len(assignments):
            print("Invalid choice.")
            return
        
        assignment_id = assignments[choice - 1][0]
        mycursor.execute(f"SELECT student_id FROM course_students WHERE course_id='{enterd_course}'")
        students = mycursor.fetchall()
        
        for n, student in enumerate(students, 1):
            print(f"{n} - Student ID: {student[0]}")
        
        student_choice = int(input("Enter the student number to mark: "))
        if student_choice < 1 or student_choice > len(students):
            print("Invalid choice.")
            return
        
        student_id = students[student_choice - 1][0]
        mark = int(input("Enter the mark for the student: "))
        
        sql = "INSERT INTO assignment_marks (assignment_id, student_id, mark) VALUES (%s, %s, %s)"
        data = (assignment_id, student_id, mark)
        mycursor.execute(sql, data)
        mydb.commit()
        print(f"Mark {mark} assigned to student {student_id} for assignment {assignment_id}.")
    
    def delete_Assignment(self, enterd_course):
        mycursor.execute(f"SELECT * FROM assignments WHERE course='{enterd_course}'")
        assignments = mycursor.fetchall()
        
        if not assignments:
            print("No assignments to delete.")
            return
        
        for n, assignment in enumerate(assignments, 1):
            print(f"{n} - {assignment[1]}")
        
        choice = int(input("Enter the assignment number to delete: "))
        if choice < 1 or choice > len(assignments):
            print("Invalid choice.")
            return
        
        assignment_id = assignments[choice - 1][0]
        mycursor.execute(f"DELETE FROM assignments WHERE id={assignment_id}")
        mydb.commit()
        print(f"Assignment {assignment_id} deleted.")
    
    def add_Assignment(self, enterd_course):
        assignment_name = input("Enter the assignment name: ")
        assignment_desc = input("Enter the assignment description: ")
        
        sql = "INSERT INTO assignments (course, name, description) VALUES (%s, %s, %s)"
        data = (enterd_course, assignment_name, assignment_desc)
        mycursor.execute(sql, data)
        mydb.commit()
        print(f"Assignment '{assignment_name}' added to course {enterd_course}.")
    
    def show_students_in_course(self, enterd_course):
        mycursor.execute(f"SELECT student_id FROM course_students WHERE course_id='{enterd_course}'")
        students = mycursor.fetchall()
        
        if not students:
            print("No students are enrolled in this course.")
            return
        
        for n, student in enumerate(students, 1):
            print(f"{n} - Student ID: {student[0]}")
    
    def block_student_from_course(self, enterd_course):
        self.show_students_in_course(enterd_course)
        student_id = int(input("Enter the student ID to block: "))
        
        sql = "UPDATE course_students SET blocked=1 WHERE course_id=%s AND student_id=%s"
        data = (enterd_course, student_id)
        mycursor.execute(sql, data)
        mydb.commit()
        print(f"Student {student_id} has been blocked from course {enterd_course}.")
        
        
class Student(User):
    def __init__(self, **user_data):
        super().__init__(**user_data)
        self.show_main_list()

    def show_main_list(self):
        while True:
            print(f"Welcome, {self.name}!")
            print("\nPlease choose an option:")
            print("""
                [1] - Send Request to join a Course
                [2] - View my Courses
                [0] - Close System
            """)
            choice = int(input("Enter your choice: "))
            if choice == 1:
                self.send_request_to_join_a_course()
            elif choice == 2:
                self.view_my_courses()
            else:
                break

    def send_request_to_join_a_course(self):
        course_name = input("Enter the course name you want to join: ")
        sql = "INSERT INTO requests (student, course, type) VALUES (%s, %s, 'join')"
        data = (self.id, course_name)
        mycursor.execute(sql, data)
        mydb.commit()
        print(f"Request to join '{course_name}' has been sent.")

    def view_my_courses(self):
        mycursor.execute(f"SELECT course_id FROM course_students WHERE student_id={self.id}")
        courses = [course[0] for course in mycursor.fetchall()]
        if courses:
            print("Your Courses:")
            for idx, course in enumerate(courses, 1):
                print(f"{idx}. {course}")
            course_choice = int(input("Enter the course number to view details: "))
            if course_choice in range(1, len(courses)+1):
                self.enter_course_list(courses[course_choice-1])
        else:
            print("You are not enrolled in any courses.")

    def enter_course_list(self, course):
        while True:
            print(f"Course: {course}")
            print("""
                [1] - Show Assignments
                [2] - Exit Course
                [0] - Go Back
            """)
            choice = int(input("Enter your choice: "))
            if choice == 1:
                self.show_course_assignments(course)
            elif choice == 2:
                self.send_request_to_exit_from_course(course)
                break
            else:
                break

    def show_course_assignments(self, course):
        mycursor.execute(f"SELECT id, question FROM assignments WHERE course='{course}'")
        assignments = mycursor.fetchall()
        if not assignments:
            print("No assignments available.")
            return
        for idx, (assignment_id, question) in enumerate(assignments, 1):
            print(f"{idx}. {question}")
        assignment_choice = int(input("Enter the assignment number to view details: "))
        if assignment_choice in range(1, len(assignments)+1):
            self.show_assignment(assignments[assignment_choice-1][0])

    def show_assignment(self, assignment_id):
        mycursor.execute(f"SELECT question, description FROM assignments WHERE id={assignment_id}")
        assignment = mycursor.fetchone()
        print(f"Assignment: {assignment[0]}\nDescription: {assignment[1]}")
        if input("Do you want to solve this assignment? (y/n): ").lower() == 'y':
            self.solve_assignment(assignment_id)

    def solve_assignment(self, assignment_id):
        solution = input("Enter your solution: ")
        sql = "INSERT INTO assignment_solutions (assignment_id, student_id, solution) VALUES (%s, %s, %s)"
        data = (assignment_id, self.id, solution)
        mycursor.execute(sql, data)
        mydb.commit()
        print("Your solution has been submitted.")

    def send_request_to_exit_from_course(self, course):
        sql = "INSERT INTO requests (student, course, type) VALUES (%s, %s, 'quit')"
        data = (self.id, course)
        mycursor.execute(sql, data)
        mydb.commit()
        print(f"Request to exit '{course}' has been sent.")
        
        
def main():
    while True:
        print("""
            [1] - Register
            [2] - Login
            [0] - Close System
        """)
        main_choice = int(input("Enter your choice: "))

        if main_choice == 1:
            User.sign_up()

        elif main_choice == 2:
            print("""
                - What is your rank?
                [1] - Lecturer
                [2] - Student
                [0] - Close System
            """)
            rank_choice = int(input("Enter your choice: "))
            if rank_choice == 1:
                rank = 'Lecturer'
            elif rank_choice == 2:
                rank = 'Student'
            else:
                break

            print('--- Login ---')
            username = input('Username: ')
            password = input('Password: ')
            if User.login(username, password, rank):
                if rank == 'Lecturer':
                    lecturer = Lecturer(name=username)
                elif rank == 'Student':
                    student = Student(name=username)
            else:
                print("Invalid login details.")
        else:
            break

if __name__ == "__main__":
    main()


