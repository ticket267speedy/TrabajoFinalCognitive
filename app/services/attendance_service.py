from typing import Optional

from ..repositories.attendance_repository import mark_attendance as repo_mark_attendance


def mark_attendance(session_id: Optional[str], student_id: str, course_id: Optional[str] = None) -> bool:
    """Marca asistencia del alumno en la sesión indicada.

    Por ahora delega a repositorio (stub). Posteriormente validará sesión activa,
    evitar duplicados, y reglas de negocio.
    """
    return repo_mark_attendance(session_id=session_id, student_id=student_id, course_id=course_id)