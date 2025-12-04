"""
Repositorio de Asesor de Becas

Encapsula todas las queries a la base de datos relacionadas con el
perfil de asesor de becas (becarios, alertas, resumen).
"""
from typing import List, Tuple, Optional
from ...extensions import db
from ...models import Student, Alert, Course, Enrollment
from sqlalchemy import desc


def get_scholarship_students_repo(limit: int = 100, offset: int = 0) -> Tuple[List[Student], int]:
    """
    Obtiene todos los estudiantes becarios.
    
    Args:
        limit: Cantidad máxima de resultados
        offset: Desplazamiento para paginación
        
    Returns:
        Tupla (lista de estudiantes, total de becarios)
    """
    query = Student.query.filter_by(is_scholarship_student=True)
    total = query.count()
    students = query.limit(limit).offset(offset).all()
    return students, total


def get_alerts_repo(limit: int = 100, offset: int = 0) -> Tuple[List[Alert], int]:
    """
    Obtiene todas las alertas ordenadas por fecha (más recientes primero).
    
    Args:
        limit: Cantidad máxima de resultados
        offset: Desplazamiento para paginación
        
    Returns:
        Tupla (lista de alertas, total de alertas)
    """
    query = Alert.query.order_by(desc(Alert.created_at))
    total = query.count()
    alerts = query.limit(limit).offset(offset).all()
    return alerts, total


def mark_alert_read_repo(alert_id: int) -> bool:
    """
    Marca una alerta como leída.
    
    Args:
        alert_id: ID de la alerta
        
    Returns:
        True si se actualizó, False si no existe
    """
    alert = Alert.query.get(alert_id)
    if not alert:
        return False
    
    alert.is_read = True
    db.session.commit()
    return True


def get_advisor_summary_repo() -> dict:
    """
    Obtiene resumen de estadísticas para el asesor.
    
    Returns:
        Diccionario con conteos de becarios, alertas no leídas y cursos
    """
    total_scholarship_students = Student.query.filter_by(is_scholarship_student=True).count()
    unread_alerts = Alert.query.filter_by(is_read=False).count()
    
    # Contar cursos que tienen al menos un becario inscrito
    courses_with_scholars = db.session.query(Course.id).join(
        Enrollment
    ).join(
        Student
    ).filter(
        Student.is_scholarship_student == True
    ).distinct().count()
    
    return {
        "total_scholarship_students": total_scholarship_students,
        "unread_alerts": unread_alerts,
        "courses_with_scholars": courses_with_scholars
    }
