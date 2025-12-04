"""__init__ de Modelos - Importa todos los modelos para la inicialización"""
from .users.user import User
from .students.student import Student
from .courses.course import Course, Enrollment
from .attendance.attendance import Attendance, Alert

__all__ = ['User', 'Student', 'Course', 'Enrollment', 'Attendance', 'Alert']