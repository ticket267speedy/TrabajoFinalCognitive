"""
Servicio de Asistencia

Orquesta la lógica de negocio para operaciones con asistencia.
Utiliza el repositorio para acceder a datos.
Implementa alertas automáticas por inasistencia.
"""
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from ..repositories.attendance.attendance_repository import (
    mark_attendance as repo_mark_attendance,
    get_attendance_by_student as repo_get_attendance_by_student,
    get_absence_count
)
from ..models import Attendance, Alert, Student, Course


class AttendanceService:
    """Servicio para gestionar asistencia"""
    
    # Umbral de faltas para generar alerta
    ABSENCE_THRESHOLD = 3
    
    def mark_attendance(self, student_id: int, course_id: int, status: str = 'presente',
                       entry_time: Optional[str] = None, exit_time: Optional[str] = None,
                       attendance_date: Optional[str] = None) -> Dict[str, Any]:
        """Marca la asistencia de un estudiante y genera alertas si es necesario"""
        try:
            result = repo_mark_attendance(
                student_id=student_id,
                course_id=course_id,
                status=status,
                entry_time=entry_time,
                exit_time=exit_time,
                attendance_date=attendance_date
            )
            
            if result.get('ok') and status == 'falta':
                # Verificar si debe generarse alerta
                self._check_and_create_alert(student_id, course_id)
            
            return result
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al marcar asistencia: {str(e)}"
            }
    
    def get_student_attendance(self, student_id: int, course_id: Optional[int] = None,
                              start_date: Optional[str] = None, end_date: Optional[str] = None,
                              limit: int = 50) -> Dict[str, Any]:
        """Obtiene el registro de asistencia de un estudiante"""
        try:
            # Verificar que el estudiante existe
            student = Student.query.get(student_id)
            if not student:
                return {
                    "ok": False,
                    "message": f"Estudiante {student_id} no encontrado"
                }
            
            # Usar el repositorio para obtener datos
            query = Attendance.query.filter_by(student_id=student_id)
            
            if course_id:
                query = query.filter_by(course_id=course_id)
            
            if start_date:
                query = query.filter(Attendance.date >= start_date)
            
            if end_date:
                query = query.filter(Attendance.date <= end_date)
            
            total = query.count()
            attendance_records = query.order_by(Attendance.date.desc()).limit(limit).all()
            
            return {
                "ok": True,
                "data": [self._attendance_to_dict(a) for a in attendance_records],
                "total": total,
                "limit": limit
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener asistencia: {str(e)}"
            }
    
    def get_course_attendance(self, course_id: int, attendance_date: Optional[str] = None,
                             status: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Obtiene la asistencia de todos los estudiantes en un curso"""
        try:
            course = Course.query.get(course_id)
            if not course:
                return {
                    "ok": False,
                    "message": f"Curso {course_id} no encontrado"
                }
            
            query = Attendance.query.filter_by(course_id=course_id)
            
            if attendance_date:
                query = query.filter_by(date=attendance_date)
            
            if status:
                query = query.filter_by(status=status)
            
            total = query.count()
            records = query.order_by(Attendance.date.desc()).limit(limit).all()
            
            return {
                "ok": True,
                "data": [self._attendance_to_dict(a) for a in records],
                "total": total,
                "limit": limit
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener asistencia del curso: {str(e)}"
            }
    
    def get_attendance_stats(self, student_id: int, course_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene estadísticas de asistencia de un estudiante"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {
                    "ok": False,
                    "message": f"Estudiante {student_id} no encontrado"
                }
            
            query = Attendance.query.filter_by(student_id=student_id)
            
            if course_id:
                query = query.filter_by(course_id=course_id)
            
            records = query.all()
            
            if not records:
                return {
                    "ok": True,
                    "data": {
                        "total_sessions": 0,
                        "present": 0,
                        "late": 0,
                        "absent": 0,
                        "early_exit": 0,
                        "attendance_rate": 0.0
                    }
                }
            
            total = len(records)
            present = len([r for r in records if r.status == 'presente'])
            late = len([r for r in records if r.status == 'tardanza'])
            absent = len([r for r in records if r.status == 'falta'])
            early_exit = len([r for r in records if r.status == 'salida_repentina'])
            
            attendance_rate = (present / total * 100) if total > 0 else 0
            
            return {
                "ok": True,
                "data": {
                    "total_sessions": total,
                    "present": present,
                    "late": late,
                    "absent": absent,
                    "early_exit": early_exit,
                    "attendance_rate": round(attendance_rate, 2)
                }
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener estadísticas: {str(e)}"
            }
    
    def get_absence_alerts(self, student_id: int) -> Dict[str, Any]:
        """Obtiene alertas de inasistencia de un estudiante"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {
                    "ok": False,
                    "message": f"Estudiante {student_id} no encontrado"
                }
            
            alerts = Alert.query.filter_by(student_id=student_id).all()
            
            return {
                "ok": True,
                "data": [self._alert_to_dict(a) for a in alerts],
                "total": len(alerts)
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Error al obtener alertas: {str(e)}"
            }
    
    def update_attendance(self, attendance_id: int, status: Optional[str] = None,
                         entry_time: Optional[str] = None, exit_time: Optional[str] = None) -> Dict[str, Any]:
        """Actualiza un registro de asistencia"""
        try:
            attendance = Attendance.query.get(attendance_id)
            
            if not attendance:
                return {
                    "ok": False,
                    "message": f"Registro de asistencia {attendance_id} no encontrado"
                }
            
            if status:
                attendance.status = status
            if entry_time:
                attendance.entry_time = entry_time
            if exit_time:
                attendance.exit_time = exit_time
            
            from ..extensions import db
            db.session.commit()
            
            return {
                "ok": True,
                "message": "Asistencia actualizada exitosamente"
            }
        except Exception as e:
            from ..extensions import db
            db.session.rollback()
            return {
                "ok": False,
                "message": f"Error al actualizar asistencia: {str(e)}"
            }
    
    def delete_attendance(self, attendance_id: int) -> Dict[str, Any]:
        """Elimina un registro de asistencia"""
        try:
            attendance = Attendance.query.get(attendance_id)
            
            if not attendance:
                return {
                    "ok": False,
                    "message": f"Registro de asistencia {attendance_id} no encontrado"
                }
            
            from ..extensions import db
            db.session.delete(attendance)
            db.session.commit()
            
            return {
                "ok": True,
                "message": "Asistencia eliminada exitosamente"
            }
        except Exception as e:
            from ..extensions import db
            db.session.rollback()
            return {
                "ok": False,
                "message": f"Error al eliminar asistencia: {str(e)}"
            }
    
    def _check_and_create_alert(self, student_id: int, course_id: int) -> None:
        """Verifica si debe crearse una alerta por inasistencia"""
        try:
            from ..extensions import db
            
            # Contar faltas del estudiante en el curso
            absence_count = Attendance.query.filter(
                Attendance.student_id == student_id,
                Attendance.course_id == course_id,
                Attendance.status == 'falta'
            ).count()
            
            if absence_count >= self.ABSENCE_THRESHOLD:
                # Verificar si ya existe una alerta activa
                existing_alert = Alert.query.filter(
                    Alert.student_id == student_id,
                    Alert.course_id == course_id
                ).first()
                
                if not existing_alert:
                    alert = Alert(
                        student_id=student_id,
                        course_id=course_id,
                        message=f"El estudiante ha acumulado {absence_count} faltas en el curso"
                    )
                    db.session.add(alert)
                    db.session.commit()
        except Exception as e:
            print(f"Error al crear alerta de inasistencia: {str(e)}")
    
    @staticmethod
    def _attendance_to_dict(attendance: Attendance) -> Dict[str, Any]:
        """Convierte un objeto Attendance a diccionario"""
        return {
            "id": attendance.id,
            "student_id": attendance.student_id,
            "course_id": attendance.course_id,
            "date": attendance.date.isoformat() if attendance.date else None,
            "entry_time": str(attendance.entry_time) if attendance.entry_time else None,
            "exit_time": str(attendance.exit_time) if attendance.exit_time else None,
            "status": attendance.status,
            "created_at": attendance.created_at.isoformat() if attendance.created_at else None
        }
    
    @staticmethod
    def _alert_to_dict(alert: Alert) -> Dict[str, Any]:
        """Convierte un objeto Alert a diccionario"""
        return {
            "id": alert.id,
            "student_id": alert.student_id,
            "course_id": alert.course_id,
            "message": alert.message,
            "created_at": alert.created_at.isoformat() if alert.created_at else None
        }