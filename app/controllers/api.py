from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

# Importaciones pesadas movidas a importación perezosa dentro de funciones
# para evitar que errores de dependencias bloqueen el arranque de la app.
from ..models import Student, Alert
from ..models import User, Course, Enrollment, ClassSession, AttendanceSummary, AdvisorCourseLink
import os
from werkzeug.utils import secure_filename
# Chatbot deshabilitado


api_bp = Blueprint("api", __name__)


# Endpoint de asistencia vía imagen removido: versión sin IA


@api_bp.post("/becarios/register")
def register_becario():
    """Registro de nuevo becario (Perfil Cliente) en MySQL.

    Espera JSON con: nombre_completo, email, password, codigo_becario.
    Valida datos, hashea contraseña y guarda en tabla `becarios`.
    """
    data = request.get_json(silent=True) or {}
    required = ["nombre_completo", "email", "password", "codigo_becario"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"error": "Datos incompletos", "missing": missing}), 400

    nombre = str(data["nombre_completo"]).strip()
    email = str(data["email"]).strip().lower()
    codigo = str(data["codigo_becario"]).strip()
    password_hash = generate_password_hash(str(data["password"]))

    # Verificación previa de unicidad (email / codigo), además capturamos IntegrityError por seguridad
    exists = db.session.execute(
        text("SELECT id FROM becarios WHERE email = :email OR codigo_becario = :codigo LIMIT 1"),
        {"email": email, "codigo": codigo},
    ).first()
    if exists:
        return jsonify({"error": "Email o código ya existen"}), 400

    try:
        db.session.execute(
            text(
                """
                INSERT INTO becarios (nombre_completo, email, password_hash, codigo_becario)
                VALUES (:nombre, :email, :password_hash, :codigo)
                """
            ),
            {
                "nombre": nombre,
                "email": email,
                "password_hash": password_hash,
                "codigo": codigo,
            },
        )
        db.session.commit()
        return jsonify({"mensaje": "Becario registrado exitosamente"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email o código ya existen"}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Error interno", "detalle": str(exc)}), 500


@api_bp.post("/becarios/login")
def becario_login():
    """Login de becario: valida credenciales y retorna JWT.

    Espera JSON con: email, password.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email y contraseña requeridos"}), 400

    row = db.session.execute(
        text("SELECT id, email, password_hash FROM becarios WHERE email = :email LIMIT 1"),
        {"email": email},
    ).mappings().first()

    if not row:
        return jsonify({"error": "No autorizado"}), 401

    if not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "No autorizado"}), 401

    token = create_access_token(
        identity=row["id"],
        additional_claims={"email": row["email"], "role": "client"},
    )

    return jsonify({"access_token": token}), 200


@api_bp.get("/becarios/asistencia")
@jwt_required()
def becario_asistencia():
    """Endpoint principal del dashboard del becario (protegido por JWT).

    Devuelve datos simulados de asistencia para el becario autenticado.
    """
    becario_id = get_jwt_identity()
    claims = get_jwt()  # contiene email y role si los agregamos en el login
    email = claims.get("email")

    # Simulación de datos
    nombre_becario = (email or f"Becario {becario_id}")
    asistencias = [
        {
            "fecha": "2024-10-28",
            "estado": "Asistió",
            "evidencia_hardware": "ESP32-CAM-Foto-001.jpg",
        },
        {
            "fecha": "2024-10-27",
            "estado": "Falta",
        },
    ]

    return jsonify({
        "nombre_becario": nombre_becario,
        "asistencias": asistencias,
    }), 200


# --- Asesores (perfil Cliente real) ---
@api_bp.post("/asesores/register")
def asesores_register():
    """Registro de Asesor (cliente) usando modelo User.

    Espera JSON: nombre_completo, email, password.
    Crea usuario con rol 'advisor' y contraseña hasheada.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    # Soporte de nombres: nombre_completo OR (nombres/apellidos) OR (first_name/last_name)
    nombre_completo = (data.get("nombre_completo") or "").strip()
    first_name = (data.get("first_name") or data.get("nombres") or "").strip()
    last_name = (data.get("last_name") or data.get("apellidos") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email y contraseña requeridos"}), 400

    # Si no vienen separados, intenta partir nombre completo
    if not first_name and nombre_completo:
        parts = nombre_completo.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    if not first_name:
        return jsonify({"error": "Nombres requeridos"}), 400

    from app.models.user import User

    # Verificar email único
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "El email ya está registrado"}), 409

    user = User(
        email=email,
        password_text=generate_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        role="advisor",
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"mensaje": "Asesor registrado exitosamente"}), 201


@api_bp.post("/asesores/login")
def asesores_login():
    """Login de Asesor (cliente).

    Espera JSON: email, password.
    Devuelve JWT en campo access_token.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email y contraseña requeridos"}), 400

    from app.models.user import User
    # Busca por email sin filtrar rol; permite 'advisor' o 'client' (compatibilidad)
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No autorizado"}), 401

    if user.role not in ("advisor", "client"):
        return jsonify({"error": "Perfil no autorizado"}), 401

    # Soporta contraseñas antiguas en texto plano
    valid = False
    try:
        valid = check_password_hash(user.password_text, password)
    except Exception:
        valid = False

    if not valid and user.password_text == password:
        # Upgrade transparente a hash seguro
        user.password_text = generate_password_hash(password)
        db.session.commit()
        valid = True

    if not valid:
        return jsonify({"error": "No autorizado"}), 401

    token = create_access_token(
        identity=user.id,
        additional_claims={"email": user.email, "role": "advisor"},
    )
    return jsonify({"access_token": token}), 200


# --- Admin (Profesor) ---

@api_bp.post("/admin/login")
def admin_login():
    """Login de Administrador/Profesor.

    Espera JSON: email, password.
    Devuelve JWT con rol 'admin'.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email y contraseña requeridos"}), 400

    user = User.query.filter_by(email=email, role="admin").first()
    if not user:
        return jsonify({"error": "No autorizado"}), 401

    valid = False
    try:
        valid = check_password_hash(user.password_text, password)
    except Exception:
        valid = False
    if not valid and user.password_text == password:
        user.password_text = generate_password_hash(password)
        db.session.commit()
        valid = True
    if not valid:
        return jsonify({"error": "No autorizado"}), 401

    token = create_access_token(
        identity=user.id,
        additional_claims={"email": user.email, "role": "admin"},
    )
    return jsonify({"access_token": token}), 200


def _require_role(role: str):
    claims = get_jwt()
    if not claims or claims.get("role") != role:
        return False
    return True


def _normalize_identity(identity):
    """Devuelve el identity del JWT como entero si es posible, o tal cual si no."""
    try:
        return int(identity)
    except Exception:
        return identity


# --- Admin: Perfil ---

@api_bp.get("/admin/profile")
@jwt_required()
def admin_profile_get():
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    user = User.query.get_or_404(admin_id)
    courses = Course.query.filter_by(admin_id=admin_id).all()
    return jsonify({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "description": user.description,
        "profile_photo_url": user.profile_photo_url,
        "courses": [{"id": c.id, "name": c.name} for c in courses],
    }), 200


@api_bp.patch("/admin/profile")
@jwt_required()
def admin_profile_patch():
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = get_jwt_identity()
    user = User.query.get_or_404(admin_id)
    data = request.get_json(silent=True) or {}
    if "description" in data:
        user.description = data.get("description")
    db.session.commit()
    return jsonify({"status": "updated"}), 200


@api_bp.post("/admin/profile/photo")
@jwt_required()
def admin_profile_photo():
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = get_jwt_identity()
    user = User.query.get_or_404(admin_id)
    if "photo" not in request.files:
        return jsonify({"error": "Archivo 'photo' requerido"}), 400
    file = request.files["photo"]
    if not file.filename:
        return jsonify({"error": "Nombre de archivo inválido"}), 400
    filename = secure_filename(file.filename)
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    save_name = f"admin_{admin_id}_" + filename
    path = os.path.join(upload_dir, save_name)
    file.save(path)
    user.profile_photo_url = f"/static/uploads/{save_name}"
    db.session.commit()
    return jsonify({"profile_photo_url": user.profile_photo_url}), 200


# --- Perfil público de usuario (visible para admin y asesor) ---
@api_bp.get("/users/<int:user_id>/profile")
@jwt_required()
def user_public_profile(user_id: int):
    # Permite cualquier rol autenticado
    u = User.query.get_or_404(user_id)
    courses = Course.query.filter_by(admin_id=u.id).all()
    return jsonify({
        "id": u.id,
        "role": u.role.value if hasattr(u.role, 'value') else u.role,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "description": u.description,
        "profile_photo_url": u.profile_photo_url,
        "courses": [{"id": c.id, "name": c.name} for c in courses],
    }), 200


# --- Chatbot removido ---


# --- Personas por curso ---
@api_bp.get("/courses/<int:course_id>/people")
@jwt_required()
def course_people(course_id: int):
    course = Course.query.get_or_404(course_id)
    # Profesor
    professor = User.query.get(course.admin_id) if course.admin_id else None
    prof_json = None
    if professor:
        prof_json = {
            "id": professor.id,
            "first_name": professor.first_name,
            "last_name": professor.last_name,
            "description": professor.description,
            "profile_photo_url": professor.profile_photo_url,
        }
    # Becarios en el curso (por Enrollment + Student)
    from sqlalchemy.orm import joinedload
    enrolls = Enrollment.query.options(joinedload(Enrollment.student)).filter_by(course_id=course.id).all()
    students = []
    for e in enrolls:
        s = e.student
        if not s:
            continue
        if s.is_scholarship_student:
            students.append({
                "id": s.id,
                "first_name": s.first_name,
                "last_name": s.last_name,
                "email": s.email,
                "is_scholarship_student": s.is_scholarship_student,
            })
    return jsonify({
        "course": {"id": course.id, "name": getattr(course, "name", None)},
        "professor": prof_json,
        "students": students,
    }), 200


# --- Admin: estudiantes por curso (todos los inscritos) ---
@api_bp.get("/admin/courses/<int:course_id>/students")
@jwt_required()
def admin_course_students(course_id: int):
    """Lista todos los estudiantes inscritos en un curso (no solo becarios)."""
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    course = Course.query.get_or_404(course_id)
    # No dependemos de relaciones en Enrollment; hacemos join explícito
    students = db.session.query(Student).join(Enrollment, Enrollment.student_id == Student.id).filter(
        Enrollment.course_id == course.id
    ).all()
    items = [
        {
            "id": s.id,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "email": s.email,
            "is_scholarship_student": s.is_scholarship_student,
        }
        for s in students
    ]
    return jsonify({"course": {"id": course.id, "name": getattr(course, "name", None)}, "students": items}), 200


# --- Admin: marcar asistencia manual ---
@api_bp.post("/admin/attendance/manual")
@jwt_required()
def admin_manual_attendance():
    """Marca asistencia manualmente para un alumno en una sesión activa."""
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    student_id = data.get("student_id")
    course_id = data.get("course_id")
    if not session_id or not student_id:
        return jsonify({"error": "session_id y student_id son requeridos"}), 400
    ok = mark_attendance(session_id=session_id, student_id=str(student_id), course_id=str(course_id) if course_id else None)
    if not ok:
        return jsonify({"error": "No se pudo registrar asistencia"}), 500
    return jsonify({"status": "ok", "student_id": str(student_id)}), 200


# --- Admin: Students CRUD ---

@api_bp.get("/admin/students")
@jwt_required()
def admin_students_list():
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    scholarship = (request.args.get("scholarship") or "").strip().lower()
    q = Student.query
    if scholarship in ("true", "false", "1", "0", "yes", "no"):
        want = scholarship in ("true", "1", "yes")
        q = q.filter_by(is_scholarship_student=want)
    students = q.all()
    items = []
    for s in students:
        # Cursos del profesor (admin) a los que pertenece el estudiante
        course_names = [
            c.name
            for c in Course.query.join(Enrollment, Enrollment.course_id == Course.id)
            .filter(Enrollment.student_id == s.id, Course.admin_id == admin_id)
            .all()
        ]
        items.append({
            "id": s.id,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "email": s.email,
            "is_scholarship_student": s.is_scholarship_student,
            "courses": course_names,
        })
    return jsonify({"items": items}), 200


@api_bp.post("/admin/students")
@jwt_required()
def admin_students_create():
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json(silent=True) or {}
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    email = (data.get("email") or None)
    is_scholarship = bool(data.get("is_scholarship_student"))
    if not first_name or not last_name:
        return jsonify({"error": "Nombres y apellidos requeridos"}), 400
    s = Student(first_name=first_name, last_name=last_name, email=email, is_scholarship_student=is_scholarship)
    db.session.add(s)
    db.session.commit()
    return jsonify({"id": s.id}), 201


@api_bp.patch("/admin/students/<int:student_id>")
@jwt_required()
def admin_students_update(student_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    s = Student.query.get_or_404(student_id)
    data = request.get_json(silent=True) or {}
    for field in ("first_name", "last_name", "email"):
        if field in data:
            setattr(s, field, data.get(field))
    if "is_scholarship_student" in data:
        s.is_scholarship_student = bool(data.get("is_scholarship_student"))
    db.session.commit()
    return jsonify({"status": "updated"}), 200


@api_bp.delete("/admin/students/<int:student_id>")
@jwt_required()
def admin_students_delete(student_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    s = Student.query.get_or_404(student_id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({"status": "deleted"}), 200


# --- Admin: Courses CRUD ---

@api_bp.get("/admin/courses")
@jwt_required()
def admin_courses_list():
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    courses = Course.query.filter_by(admin_id=admin_id).all()
    items = [{"id": c.id, "name": c.name} for c in courses]
    return jsonify({"items": items}), 200


@api_bp.post("/admin/courses")
@jwt_required()
def admin_courses_create():
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Nombre requerido"}), 400
    c = Course(name=name, admin_id=admin_id)
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id}), 201


@api_bp.patch("/admin/courses/<int:course_id>")
@jwt_required()
def admin_courses_update(course_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    c = Course.query.get_or_404(course_id)
    admin_id = _normalize_identity(get_jwt_identity())
    if c.admin_id != admin_id:
        return jsonify({"error": "No autorizado"}), 403
    data = request.get_json(silent=True) or {}
    if "name" in data:
        c.name = (data.get("name") or c.name)
    db.session.commit()
    return jsonify({"status": "updated"}), 200


@api_bp.delete("/admin/courses/<int:course_id>")
@jwt_required()
def admin_courses_delete(course_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    c = Course.query.get_or_404(course_id)
    admin_id = _normalize_identity(get_jwt_identity())
    if c.admin_id != admin_id:
        return jsonify({"error": "No autorizado"}), 403
    db.session.delete(c)
    db.session.commit()
    return jsonify({"status": "deleted"}), 200


# --- Admin: Control de sesiones ---

@api_bp.post("/admin/courses/<int:course_id>/session/start")
@jwt_required()
def admin_session_start(course_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    course = Course.query.get_or_404(course_id)
    if course.admin_id != admin_id:
        return jsonify({"error": "No autorizado"}), 403
    active = ClassSession.query.filter_by(course_id=course_id, status="active").first()
    if active:
        return jsonify({"error": "Ya existe una sesión activa", "session_id": active.id}), 400
    sess = ClassSession(course_id=course_id, status="active")
    db.session.add(sess)
    db.session.commit()
    return jsonify({"session_id": sess.id, "status": "active"}), 201


@api_bp.post("/admin/courses/<int:course_id>/session/end")
@jwt_required()
def admin_session_end(course_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    course = Course.query.get_or_404(course_id)
    if course.admin_id != admin_id:
        return jsonify({"error": "No autorizado"}), 403
    active = ClassSession.query.filter_by(course_id=course_id, status="active").first()
    if not active:
        return jsonify({"error": "No hay sesión activa"}), 400
    from sqlalchemy.sql import func
    active.end_time = func.now()
    active.status = "finished"
    db.session.commit()
    return jsonify({"session_id": active.id, "status": "finished"}), 200


@api_bp.get("/admin/courses/<int:course_id>/session/active")
@jwt_required()
def admin_session_active(course_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    course = Course.query.get_or_404(course_id)
    if course.admin_id != admin_id:
        return jsonify({"error": "No autorizado"}), 403
    active = ClassSession.query.filter_by(course_id=course_id, status="active").first()
    if not active:
        return jsonify({"active": False}), 200
    return jsonify({"active": True, "session": {"id": active.id, "start_time": str(active.start_time)}}), 200


# --- Admin: AttendanceSummary edición ---

@api_bp.get("/admin/summaries")
@jwt_required()
def admin_summaries_list():
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    session_id = request.args.get("session_id", type=int)
    q = AttendanceSummary.query
    if session_id:
        q = q.filter_by(session_id=session_id)
    summaries = q.all()
    items = [
        {
            "id": a.id,
            "session_id": a.session_id,
            "student_id": a.student_id,
            "presence_percentage": a.presence_percentage,
            "is_manual_override": a.is_manual_override,
        }
        for a in summaries
    ]
    return jsonify({"items": items}), 200


@api_bp.patch("/admin/summaries/<int:summary_id>")
@jwt_required()
def admin_summary_update(summary_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    a = AttendanceSummary.query.get_or_404(summary_id)
    data = request.get_json(silent=True) or {}
    if "presence_percentage" in data:
        try:
            a.presence_percentage = float(data.get("presence_percentage"))
        except Exception:
            return jsonify({"error": "presence_percentage inválido"}), 400
    if "is_manual_override" in data:
        a.is_manual_override = bool(data.get("is_manual_override"))
    db.session.commit()
    return jsonify({"status": "updated"}), 200


# --- Admin: Invitaciones a asesores ---

@api_bp.post("/admin/courses/<int:course_id>/advisor-invitations")
@jwt_required()
def admin_invite_advisor(course_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = get_jwt_identity()
    course = Course.query.get_or_404(course_id)
    if course.admin_id != admin_id:
        return jsonify({"error": "No autorizado"}), 403
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "Email requerido"}), 400
    advisor = User.query.filter_by(email=email, role="advisor").first()
    if not advisor:
        return jsonify({"error": "Asesor no encontrado"}), 404
    # Crear vínculo si no existe
    existing = AdvisorCourseLink.query.filter_by(course_id=course.id, advisor_user_id=advisor.id).first()
    if existing:
        return jsonify({"status": "exists", "link_id": existing.id, "current_status": existing.status}), 200
    link = AdvisorCourseLink(course_id=course.id, advisor_user_id=advisor.id, status="invited", initiated_by="professor")
    db.session.add(link)
    db.session.commit()
    return jsonify({"link_id": link.id, "status": link.status}), 201


# --- Asesor: gestionar invitaciones ---

@api_bp.get("/asesores/invitations")
@jwt_required()
def advisor_invitations():
    if not _require_role("advisor"):
        return jsonify({"error": "No autorizado"}), 401
    advisor_id = get_jwt_identity()
    links = AdvisorCourseLink.query.filter_by(advisor_user_id=advisor_id).all()
    items = [
        {
            "id": l.id,
            "course_id": l.course_id,
            "status": l.status,
        }
        for l in links
    ]
    return jsonify({"items": items}), 200


@api_bp.post("/asesores/invitations/<int:link_id>/accept")
@jwt_required()
def advisor_invitation_accept(link_id: int):
    if not _require_role("advisor"):
        return jsonify({"error": "No autorizado"}), 401
    advisor_id = get_jwt_identity()
    link = AdvisorCourseLink.query.get_or_404(link_id)
    if link.advisor_user_id != advisor_id:
        return jsonify({"error": "No autorizado"}), 403
    from sqlalchemy.sql import func
    link.status = "accepted"
    link.accepted_at = func.now()
    db.session.commit()
    return jsonify({"status": "accepted"}), 200


@api_bp.post("/asesores/invitations/<int:link_id>/reject")
@jwt_required()
def advisor_invitation_reject(link_id: int):
    if not _require_role("advisor"):
        return jsonify({"error": "No autorizado"}), 401
    advisor_id = get_jwt_identity()
    link = AdvisorCourseLink.query.get_or_404(link_id)
    if link.advisor_user_id != advisor_id:
        return jsonify({"error": "No autorizado"}), 403
    link.status = "rejected"
    db.session.commit()
    return jsonify({"status": "rejected"}), 200


# --- Dashboard Asesor: Becarios y Alertas ---

@api_bp.get("/asesores/students")
def advisor_students():
    """Lista alumnos becarios.

    Query params:
      - scholarship=true (opcional): filtra por becarios; por ahora siempre filtra.
    """
    try:
      students = Student.query.filter_by(is_scholarship_student=True).all()
      items = [
          {
              "id": s.id,
              "first_name": s.first_name,
              "last_name": s.last_name,
              "email": s.email,
              "is_scholarship_student": s.is_scholarship_student,
          }
          for s in students
      ]
      return jsonify({"items": items}), 200
    except Exception as e:
      return jsonify({"error": "No se pudo listar becarios", "detail": str(e)}), 500


@api_bp.get("/alerts")
def list_alerts():
    """Lista alertas; si scholarship=true, solo de alumnos becarios.

    Devuelve campos del alumno para mostrar en el dashboard.
    """
    scholarship = (request.args.get("scholarship") or "").lower() in ("1", "true", "yes")
    try:
        query = Alert.query
        if scholarship:
            # Filtra por alumnos becarios
            query = query.join(Alert.student).filter(Student.is_scholarship_student == True)  # noqa: E712
        alerts = query.order_by(Alert.created_at.desc()).all()
        items = [
            {
                "id": a.id,
                "student_id": a.student_id,
                "student_first_name": getattr(a.student, "first_name", None),
                "student_last_name": getattr(a.student, "last_name", None),
                "course_id": a.course_id,
                "message": a.message,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "is_read": a.is_read,
            }
            for a in alerts
        ]
        return jsonify({"items": items}), 200
    except Exception as e:
        return jsonify({"error": "No se pudo listar alertas", "detail": str(e)}), 500


@api_bp.patch("/alerts/<int:alert_id>/read")
def mark_alert_read(alert_id: int):
    """Marca una alerta como leída."""
    try:
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({"error": "Alerta no encontrada"}), 404
        if not alert.is_read:
            alert.is_read = True
            db.session.commit()
        return jsonify({"status": "ok", "id": alert.id, "is_read": alert.is_read}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "No se pudo marcar como leída", "detail": str(e)}), 500


# Rutas de reconocimiento facial removidas para versión sin integración de IA.
# Login unificado para Admin y Asesor/Cliente
@api_bp.post("/login")
def universal_login():
    """Login unificado.

    - Intenta primero como admin; si falla, intenta asesor/cliente.
    - Devuelve `access_token` y `user` con rol para que el frontend redirija.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email y contraseña requeridos"}), 400

    # Helper para validar contraseña (soporta texto plano legado)
    def _validate_password(u, pw):
        valid = False
        try:
            valid = check_password_hash(u.password_text, pw)
        except Exception:
            valid = False
        if not valid and u.password_text == pw:
            # Upgrade transparente a hash seguro
            u.password_text = generate_password_hash(pw)
            db.session.commit()
            valid = True
        return valid

    # 1) Admin
    user = User.query.filter_by(email=email, role="admin").first()
    if user and _validate_password(user, password):
        token = create_access_token(identity=user.id, additional_claims={"email": user.email, "role": "admin"})
        role_value = user.role if not hasattr(user.role, 'value') else user.role.value
        return jsonify({
            "access_token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": role_value,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }), 200

    # 2) Asesor/Cliente
    user = User.query.filter_by(email=email).first()
    if user and (user.role in ("advisor", "client") or getattr(user.role, 'value', None) in ("advisor", "client")):
        if _validate_password(user, password):
            # Normalizar rol a string
            role_value = user.role if not hasattr(user.role, 'value') else user.role.value
            token = create_access_token(identity=user.id, additional_claims={"email": user.email, "role": role_value})
            return jsonify({
                "access_token": token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": role_value,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }), 200

    return jsonify({"error": "No autorizado"}), 401