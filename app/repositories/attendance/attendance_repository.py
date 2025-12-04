"""
Repositorio de Asistencia

Este módulo contiene las funciones para acceder y modificar
los registros de asistencia en la base de datos.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, date

from app.extensions import db
from app.models import Attendance, Student, Course


def mark_attendance(
    student_id: int,
    course_id: int,
    status: str = 'presente',
    entry_time: Optional[datetime.time] = None,
    exit_time: Optional[datetime.time] = None,
    attendance_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Registra la asistencia de un estudiante en un curso.
    
    Args:
        student_id: ID del estudiante
        course_id: ID del curso
        status: Estado de la asistencia ('presente', 'tardanza', 'falta', 'salida_repentina')
        entry_time: Hora de entrada (opcional)
        exit_time: Hora de salida (opcional)
        attendance_date: Fecha de la asistencia (por defecto hoy)
    
    Returns:
        Dict con 'ok' (bool), 'message' (str), y 'id' si fue exitoso
    """
    try:
        if not student_id or not course_id:
            return {"ok": False, "message": "student_id y course_id requeridos"}

        # Validar que existan el estudiante y el curso
        student = Student.query.get(student_id)
        if not student:
            return {"ok": False, "message": f"Estudiante {student_id} no encontrado"}

        course = Course.query.get(course_id)
        if not course:
            return {"ok": False, "message": f"Curso {course_id} no encontrado"}

        # Usar la fecha proporcionada o la fecha actual
        if attendance_date is None:
            attendance_date = date.today()

        # Verificar si ya existe un registro para este estudiante y fecha
        existing = Attendance.query.filter_by(
            student_id=student_id,
            course_id=course_id,
            date=attendance_date
        ).first()

        if existing:
            # Actualizar el registro existente
            existing.status = status
            existing.entry_time = entry_time
            existing.exit_time = exit_time
            db.session.commit()
            return {
                "ok": True,
                "message": "Asistencia actualizada",
                "id": existing.id,
                "updated": True
            }
        else:
            # Crear nuevo registro
            attendance = Attendance(
                student_id=student_id,
                course_id=course_id,
                date=attendance_date,
                status=status,
                entry_time=entry_time,
                exit_time=exit_time
            )
            db.session.add(attendance)
            db.session.commit()
            return {
                "ok": True,
                "message": "Asistencia registrada",
                "id": attendance.id,
                "updated": False
            }

    except Exception as e:
        db.session.rollback()
        return {"ok": False, "message": f"Error al registrar asistencia: {str(e)}"}


def get_attendance_by_student(
    student_id: int,
    course_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene los registros de asistencia de un estudiante.
    
    Args:
        student_id: ID del estudiante
        course_id: ID del curso (opcional, para filtrar por curso)
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
    
    Returns:
        Lista de registros de asistencia
    """
    try:
        query = Attendance.query.filter_by(student_id=student_id)
        
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        attendances = query.order_by(Attendance.date.desc()).all()
        
        return [
            {
                "id": att.id,
                "student_id": att.student_id,
                "course_id": att.course_id,
                "date": att.date.isoformat(),
                "entry_time": att.entry_time.isoformat() if att.entry_time else None,
                "exit_time": att.exit_time.isoformat() if att.exit_time else None,
                "status": att.status,
                "created_at": att.created_at.isoformat()
            }
            for att in attendances
        ]
    except Exception as e:
        return []


def get_absence_count(
    student_id: int,
    course_id: int,
    days: int = 30
) -> int:
    """
    Cuenta las faltas de un estudiante en los últimos N días.
    
    Args:
        student_id: ID del estudiante
        course_id: ID del curso
        days: Número de días a considerar
    
    Returns:
        Cantidad de faltas
    """
    try:
        start_date = date.today() - timedelta(days=days)
        
        absences = Attendance.query.filter(
            Attendance.student_id == student_id,
            Attendance.course_id == course_id,
            Attendance.date >= start_date,
            Attendance.status.in_(['falta', 'salida_repentina'])
        ).count()
        
        return absences
    except Exception:
        return 0
