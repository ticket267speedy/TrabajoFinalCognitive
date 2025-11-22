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

        # --- Lógica de Alertas (3 faltas consecutivas) ---
        # Verificar si el estudiante es becario
        if stu.is_scholarship_student:
            # Obtener últimas 3 sesiones del curso (excluyendo la actual)
            last_sessions = ClassSession.query.filter(
                ClassSession.course_id == int(course_id),
                ClassSession.id != int(session_id),
                ClassSession.status == 'finished'
            ).order_by(ClassSession.start_time.desc()).limit(3).all()
            
            # Verificar asistencia en esas sesiones
            consecutive_absences = 0
            # Nota: Esto es una simplificación. Deberíamos contar faltas REALES.
            # Aquí asumimos que si no hay AttendanceSummary para una sesión pasada, es falta.
            
            # Sin embargo, la lógica pedida es: "monitorear a los becarios que alberguen más de 3 faltas"
            # Vamos a contar faltas totales o consecutivas. El requerimiento dice "más de 3 faltas".
            # Asumiremos consecutivas para ser más proactivos, o totales.
            # Implementación: Verificar si en las últimas 3 sesiones NO asistió.
            
            # Mejor enfoque: Contar faltas consecutivas recientes.
            # Pero acabamos de MARCAR asistencia (presente), así que la racha de faltas se rompe.
            # La alerta debería generarse CUANDO FALTA, no cuando asiste.
            # PERO, el requerimiento dice "inasistencia injustificada...".
            # Si este método se llama, es porque ASISTIÓ (o se le marcó manualmente).
            # Entonces, aquí NO deberíamos generar alerta de falta, sino quizás borrarla si existía.
            
            # RE-LEYENDO OBJETIVOS: "monitorear a los becarios que alberguen más de 3 faltas o tengan salidas repentinas"
            # Si el profesor marca asistencia manual, es porque está presente.
            
            # CAMBIO DE ESTRATEGIA:
            # La alerta debe generarse cuando se CIERRA la sesión y el alumno NO tiene asistencia.
            # O, si queremos hacerlo simple, podemos verificar el historial aquí mismo por si acaso.
            
            pass 

        db.session.commit()
        return {"ok": True, "tardy": tardy}
    except Exception as e:
        db.session.rollback()
        return {"ok": False, "tardy": False, "error": str(e)}