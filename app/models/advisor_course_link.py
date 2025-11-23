from app.extensions import db
from sqlalchemy.sql import func


class AdvisorCourseLink(db.Model):
    __tablename__ = 'advisor_course_links'

    id = db.Column(db.Integer, primary_key=True)

    # Curso (el profesor/admin del aula está definido en Course.admin_id)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    # Asesor (usuario con rol 'advisor')
    advisor_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Estado del vínculo según los flujos A/B/C
    status = db.Column(
        db.Enum('invited', 'requested', 'accepted', 'rejected', name='advisor_link_status_enum'),
        nullable=False,
        default='invited'
    )

    # Quién inició el vínculo (Profesor/Asesor/Sistema)
    initiated_by = db.Column(
        db.Enum('professor', 'advisor', 'system', name='advisor_link_initiator_enum'),
        nullable=False,
        default='professor'
    )

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    accepted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    rejected_reason = db.Column(db.String(255), nullable=True)

    # Relaciones bidireccionales
    # Ya se definen en Course.advisor_links y User.advisor_links con backrefs

    # Evita duplicados del mismo asesor en el mismo curso
    __table_args__ = (
        db.UniqueConstraint('course_id', 'advisor_user_id', name='uq_course_advisor'),
    )

    def __repr__(self):
        return f'<AdvisorCourseLink advisor={self.advisor_user_id} course={self.course_id} status={self.status}>'