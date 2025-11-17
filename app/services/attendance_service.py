from typing import Optional

from ..repositories.attendance_repository import mark_attendance as repo_mark_attendance


def mark_attendance(session_id: Optional[int], student_id: str, course_id: Optional[int] = None):
    """Marca asistencia del alumno en la sesión indicada.

    Devuelve dict con ok/tardy/error desde el repositorio.
    """
    return repo_mark_attendance(session_id=session_id, student_id=student_id, course_id=course_id)