"""
Servicio de Asistencia

Este módulo contiene la lógica de negocio para gestionar la asistencia.
Utiliza los repositorios para acceder a los datos y encapsula la lógica
de validación, alertas y reportes.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta

from app.repositories.attendance.attendance_repository import (
    mark_attendance,
    get_attendance_by_student,
    get_absence_count
)
from app.models import Student, Alert, Attendance


class AttendanceService:
    """
    Servicio para gestionar la asistencia de estudiantes.
    
    Métodos:
    - register_attendance: Registra la asistencia de un estudiante
    - get_student_attendance: Obtiene el historial de asistencia
    - check_absence_alerts: Verifica si hay alertas por faltas
    - get_attendance_stats: Obtiene estadísticas de asistencia
    """
    
    @staticmethod
    def register_attendance(
        student_id: int,
        course_id: int,
        status: str = 'presente',
        entry_time: Optional[datetime.time] = None,
        exit_time: Optional[datetime.time] = None
    ) -> Dict[str, Any]:
        """
        Registra la asistencia de un estudiante.
        
        Si el estudiante es becario y tiene más de 3 faltas,
        se genera una alerta automáticamente.
        
        Args:
            student_id: ID del estudiante
            course_id: ID del curso
            status: Estado ('presente', 'tardanza', 'falta', 'salida_repentina')
            entry_time: Hora de entrada
            exit_time: Hora de salida
        
        Returns:
            Dict con resultado de la operación
        """
        # Registrar asistencia usando el repositorio
        result = mark_attendance(
            student_id=student_id,
            course_id=course_id,
            status=status,
            entry_time=entry_time,
            exit_time=exit_time
        )
        
        if not result['ok']:
            return result
        
        # Verificar si necesita alerta (solo si el estudiante es becario)
        student = Student.query.get(student_id)
        if student and student.is_scholarship_student:
            AttendanceService.check_absence_alerts(student_id, course_id)
        
        return result
    
    @staticmethod
    def get_student_attendance(
        student_id: int,
        course_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Obtiene el historial de asistencia de un estudiante.
        
        Args:
            student_id: ID del estudiante
            course_id: ID del curso (opcional)
            days: Número de días a considerar
        
        Returns:
            Dict con historial y estadísticas
        """
        start_date = date.today() - timedelta(days=days)
        end_date = date.today()
        
        attendances = get_attendance_by_student(
            student_id=student_id,
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Calcular estadísticas
        total = len(attendances)
        present = sum(1 for a in attendances if a['status'] == 'presente')
        tardy = sum(1 for a in attendances if a['status'] == 'tardanza')
        absent = sum(1 for a in attendances if a['status'] in ['falta', 'salida_repentina'])
        
        attendance_percentage = (present / total * 100) if total > 0 else 0
        
        return {
            "student_id": student_id,
            "course_id": course_id,
            "period_days": days,
            "statistics": {
                "total_sessions": total,
                "present": present,
                "tardy": tardy,
                "absent": absent,
                "attendance_percentage": round(attendance_percentage, 2)
            },
            "records": attendances
        }
    
    @staticmethod
    def check_absence_alerts(student_id: int, course_id: int) -> bool:
        """
        Verifica si el estudiante becario tiene más de 3 faltas
        y genera una alerta si es necesario.
        
        Args:
            student_id: ID del estudiante
            course_id: ID del curso
        
        Returns:
            True si se generó una alerta, False en caso contrario
        """
        from app.extensions import db
        
        absence_count = get_absence_count(student_id, course_id, days=30)
        
        if absence_count > 3:
            # Verificar si ya existe una alerta activa
            existing_alert = Alert.query.filter_by(
                student_id=student_id,
                course_id=course_id,
                is_read=False
            ).first()
            
            if not existing_alert:
                alert = Alert(
                    student_id=student_id,
                    course_id=course_id,
                    message=f"Alerta: El estudiante tiene {absence_count} faltas en los últimos 30 días"
                )
                db.session.add(alert)
                db.session.commit()
                return True
        
        return False
    
    @staticmethod
    def get_attendance_stats(course_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de asistencia para un curso.
        
        Args:
            course_id: ID del curso
        
        Returns:
            Dict con estadísticas agregadas del curso
        """
        try:
            attendances = Attendance.query.filter_by(course_id=course_id).all()
            
            if not attendances:
                return {"ok": False, "message": "No hay registros de asistencia"}
            
            total = len(attendances)
            present = sum(1 for a in attendances if a.status == 'presente')
            tardy = sum(1 for a in attendances if a.status == 'tardanza')
            absent = sum(1 for a in attendances if a.status in ['falta', 'salida_repentina'])
            
            return {
                "ok": True,
                "course_id": course_id,
                "total_registrations": total,
                "present": present,
                "tardy": tardy,
                "absent": absent,
                "average_attendance": round((present / total * 100), 2) if total > 0 else 0
            }
        except Exception as e:
            return {"ok": False, "message": str(e)}
