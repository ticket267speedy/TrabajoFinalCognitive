from app import create_app
from app.extensions import db
from app.models import ClassSession, Course


def main():
    app = create_app()
    with app.app_context():
        all_sessions = ClassSession.query.order_by(ClassSession.id.desc()).all()
        active_sessions = ClassSession.query.filter_by(status='active').all()
        print("\n=== Todas las sesiones (últimas primero) ===")
        for s in all_sessions:
            print(f"id={s.id} course_id={s.course_id} status={s.status} start={s.start_time} end={s.end_time}")
        print("\n=== Sesiones activas ===")
        if not active_sessions:
            print("(ninguna)")
        for s in active_sessions:
            print(f"id={s.id} course_id={s.course_id} status={s.status} start={s.start_time} end={s.end_time}")


if __name__ == "__main__":
    main()