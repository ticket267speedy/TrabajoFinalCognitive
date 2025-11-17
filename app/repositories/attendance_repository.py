from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.extensions import db
from app.models import ClassSession, AttendanceLog, AttendanceSummary, Enrollment, Course, Student


def mark_attendance(session_id: Optional[int], student_id: str, course_id: Optional[int] = None) -> Dict[str, Any]:
    """Registra asistencia y retorna metadatos.

    - Crea un AttendanceLog con timestamp UTC actual
    - Actualiza/crea AttendanceSummary para la sesión/alumno
    - Determina tardanza si la marca ocurre >= 1 minuto después del inicio de la sesión

    Devuelve: { ok: bool, tardy: bool, error?: str }
    """
    try:
        if not session_id or not student_id:
            return {"ok": False, "tardy": False, "error": "session_id y student_id requeridos"}

        # Validar sesión y curso
        sess = ClassSession.query.get(int(session_id))
        if not sess:
            return {"ok": False, "tardy": False, "error": "Sesión no encontrada"}
        if course_id and int(course_id) != int(sess.course_id):
            return {"ok": False, "tardy": False, "error": "Curso no coincide con la sesión"}

        # Validar existencia de alumno y su matrícula (si hay course_id)
        stu = Student.query.get(int(student_id))
        if not stu:
            return {"ok": False, "tardy": False, "error": "Alumno no encontrado"}
        if course_id:
            enrolled = Enrollment.query.filter_by(course_id=int(course_id), student_id=int(student_id)).first()
            if not enrolled:
                return {"ok": False, "tardy": False, "error": "Alumno no está matriculado en el curso"}

        now = datetime.utcnow()
        tardy = False
        try:
            if sess.start_time:
                tardy = (now - sess.start_time) >= timedelta(minutes=1)
        except Exception:
            # Si el tipo de start_time no es comparable, asumimos no tardy
            tardy = False

        # Crear log de asistencia con timestamp explícito
        log = AttendanceLog(session_id=int(session_id), student_id=int(student_id))
        # Evitamos server_default incompatibles en SQLite asignando explícitamente
        log.timestamp = now
        db.session.add(log)

        # Upsert del resumen de asistencia
        summary = AttendanceSummary.query.filter_by(session_id=int(session_id), student_id=int(student_id)).first()
        if not summary:
            summary = AttendanceSummary(session_id=int(session_id), student_id=int(student_id))
            db.session.add(summary)

        # Para demo: 100% presente si a tiempo, 50% si tardanza
        summary.presence_percentage = 50.0 if tardy else 100.0
        summary.is_manual_override = True

        db.session.commit()
        return {"ok": True, "tardy": tardy}
    except Exception as e:
        db.session.rollback()
        return {"ok": False, "tardy": False, "error": str(e)}