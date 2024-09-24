# Learning Management System (LMS)

## Introduction

This Learning Management System (LMS) is a Python-based application that enables seamless interaction between students and lecturers. The system facilitates the management of courses, student enrollments, assignments, and user authentication.

## Features

- **User Roles**: Supports two user roles: Lecturers and Students.
- **Account Management**: Users can create accounts, log in, and manage their profiles.
- **Course Management**: Lecturers can create new courses, view their courses, and manage student enrollments.
- **Assignment Management**: Lecturers can add, view, mark, and delete assignments for their courses.
- **Database Integration**: Utilizes MySQL for data storage and management.

## Requirements

- Python 3.12
- MySQL Server
- `mysql-connector-python` library

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AhmedHashim04/LMS-Python-OOP-Mysql-Consolo-Project.git
## Install the required library:
  pip install mysql-connector-python

## Set up your MySQL database:

Create a database named lms.
Run the SQL script provided in the project to create the necessary tables:

CREATE TABLE IF NOT EXISTS students (
    id INT(255) NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(20) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS lecturers (
    id INT(255) NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(20) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS courses (
    id INT(11) NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    lecturer INT(11) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (lecturer) REFERENCES lecturers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS course_students (
    id INT(11) NOT NULL AUTO_INCREMENT,
    course_id INT(11) NOT NULL,
    student_id INT(11) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

