from typing import Optional


def mark_attendance(session_id: Optional[str], student_id: str, course_id: Optional[str] = None) -> bool:
    """Stub de persistencia de asistencia.

    Implementar con SQLAlchemy cuando los modelos estén listos.
    """
    # TODO: Persistir en BD usando modelos SQLAlchemy
    return True