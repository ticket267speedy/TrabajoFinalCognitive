from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context
import time
import subprocess
import threading
import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

# Importaciones de modelos desde la nueva estructura organizada por capas
from ..models import Student, User, Course, Enrollment, Alert, Attendance
import os
from werkzeug.utils import secure_filename
import base64

# Intento de importar excepciones de openai para usarlas en bloques except.
# Si openai no está instalado en el entorno de ejecución, definimos estas
# referencias como Exception para evitar UnboundLocalError cuando fallen
# imports posteriores (p. ej. si el módulo del chatbot no se puede importar).
try:
    from openai import AuthenticationError, RateLimitError, APIError  # type: ignore
except Exception:
    AuthenticationError = Exception
    RateLimitError = Exception
    APIError = Exception


api_bp = Blueprint("api", __name__)


# Endpoint de asistencia vía imagen (IA)
@api_bp.post("/admin/attendance/face")
@jwt_required()
def admin_attendance_face():
    """Recibe una imagen, detecta rostros y marca asistencia si hay coincidencia."""
    import numpy as np
    import cv2
    from app.services.face_recognition_service import reconocer_en_frame, cargar_modelo
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    
    if "image" not in request.files:
        return jsonify({"error": "No se envió imagen"}), 400
        
    file = request.files["image"]
    course_id = request.form.get("course_id")
    
    if not course_id:
        return jsonify({"error": "course_id requerido"}), 400
        
    # Validar que el curso existe
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Curso no encontrado"}), 404
        
    # Cargar modelo
    known_encodings, known_names = cargar_modelo()
    if not known_encodings:
        return jsonify({"error": "Modelo de IA no cargado o vacío"}), 500
        
    # Leer imagen
    npimg = np.fromfile(file, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    if frame is None:
        return jsonify({"error": "Imagen inválida"}), 400
        
    # Reconocer
    locs, names = reconocer_en_frame(frame, known_encodings, known_names, tolerance=0.5)
    
    results = []
    from ..services.attendance_service import mark_attendance
    
    for name in names:
        if name == "Desconocido":
            continue
            
        # Buscar estudiante por nombre (asumiendo formato "Nombre Apellido" o similar en carpetas)
        # Esto es una simplificación. Idealmente el nombre de carpeta debería ser el ID o mapeable.
        # Intentaremos buscar por concatenación de nombres
        
        # Estrategia: Buscar estudiante que coincida con el nombre detectado
        # Asumimos que 'name' viene de la carpeta, ej: "Juan Perez"
        
        # Opción A: Buscar exacto en base de datos (concatenando first_name + last_name)
        # Opción B: El nombre de la carpeta ES el ID del estudiante (más robusto)
        # Vamos a intentar buscar por ID si el nombre es un número, sino por texto
        
        student = None
        if name.isdigit():
             student = Student.query.get(int(name))
        else:
            # Búsqueda aproximada o exacta
            parts = name.split()
            if len(parts) >= 1:
                fname = parts[0]
                lname = " ".join(parts[1:]) if len(parts) > 1 else ""
                student = Student.query.filter(Student.first_name.ilike(f"%{fname}%")).first() # Simplificado
        
        if student:
            res = mark_attendance(session_id=active_session.id, student_id=str(student.id), course_id=int(course_id))
            results.append({"name": name, "student_id": student.id, "status": res})
        else:
            results.append({"name": name, "error": "Estudiante no encontrado en BD"})
            
    return jsonify({"results": results}), 200



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
        identity=str(row["id"]),
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
        identity=str(user.id),
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
        identity=str(user.id),
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


# --- Chatbot ---
@api_bp.post("/chatbot")
def chatbot_endpoint():
    """Endpoint para el chatbot GPT."""
    try:
        from ..ai.chatbot.gpt_service import GPTChatbotService

        data = request.get_json(silent=True) or {}
        message = data.get("message", "")
        # Intentar obtener rol del remitente (el widget puede enviar 'role' o 'user_role')
        user_role = data.get("role") or data.get("user_role") or None
        # Si no viene desde el widget, intentar leer rol desde JWT si el usuario está autenticado
        if not user_role:
            try:
                from flask_jwt_extended import verify_jwt_in_request, get_jwt
                # intenta verificar token de forma opcional
                verify_jwt_in_request(optional=True)
                claims = get_jwt()
                if claims:
                    user_role = claims.get('role')
            except Exception:
                # Si falla, seguimos sin rol
                user_role = user_role
        if not message:
            return jsonify({"response": "Hola! Soy el asistente virtual de CogniPass. En que puedo ayudarte?"}), 200

        # Usar el servicio GPT
        chatbot = GPTChatbotService()
        # Logear la entrada para depuración
        current_app.logger.info(f"/api/chatbot request json: {data}")
        response_text = chatbot.get_response(message, user_role=user_role)
        # Intentar exponer provider/model para diagnóstico
        provider = getattr(chatbot, 'provider', None)
        model_used = getattr(chatbot, 'model_name', None) or getattr(chatbot, 'GEMINI_MODEL', None) or getattr(chatbot, 'OPENAI_MODEL', None)
        return jsonify({"response": response_text, "provider": provider, "model_used": model_used}), 200

    except ValueError as e:
        # Si no hay API key configurada
        return jsonify({"error": str(e), "response": "Chatbot no disponible - API key no configurada"}), 500
    except AuthenticationError as e:
        return jsonify({"error": "Autenticación con OpenAI falló", "detail": str(e), "response": "Chatbot no disponible - problema de autenticación"}), 401
    except RateLimitError as e:
        return jsonify({"error": "Rate limit", "detail": str(e), "response": "Se alcanzó el límite de solicitudes. Intenta nuevamente más tarde."}), 429
    except APIError as e:
        return jsonify({"error": "Error en servicio externo", "detail": str(e), "response": "Servicio de IA temporalmente no disponible"}), 503
    except Exception as e:
        import logging
        logging.exception("Error en chatbot")
        return jsonify({"error": "Error al procesar la solicitud", "response": "Intenta nuevamente mas tarde"}), 500




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
    """Marca asistencia manualmente para un alumno en una sesión activa.

    También devuelve si la marca fue en tardanza (>=1 minuto luego del inicio de sesión).
    """
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    # Importación perezosa para evitar errores de arranque si cambian dependencias
    from ..services.attendance_service import mark_attendance
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    student_id = data.get("student_id")
    course_id = data.get("course_id")
    if not session_id or not student_id:
        return jsonify({"error": "session_id y student_id son requeridos"}), 400
    result = mark_attendance(session_id=int(session_id), student_id=str(student_id), course_id=int(course_id) if course_id else None)
    if not result or not result.get("ok"):
        return jsonify({"error": result.get("error") or "No se pudo registrar asistencia"}), 500
    return jsonify({"status": "ok", "student_id": str(student_id), "tardy": bool(result.get("tardy"))}), 200


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


# --- Admin: Assign courses to a student (Enrollments) ---

@api_bp.get("/admin/students/<int:student_id>/enrollments")
@jwt_required()
def admin_student_enrollments_get(student_id: int):
    """Lista los cursos (id y nombre) del alumno dentro de los cursos del profesor actual.

    Útil para precargar selección en UI de edición.
    """
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    student = Student.query.get_or_404(student_id)
    # Sólo considerar cursos que pertenecen al admin actual
    courses = (
        Course.query.join(Enrollment, Enrollment.course_id == Course.id)
        .filter(Enrollment.student_id == student.id, Course.admin_id == admin_id)
        .all()
    )
    items = [{"id": c.id, "name": c.name} for c in courses]
    return jsonify({"items": items}), 200


@api_bp.post("/admin/students/<int:student_id>/enrollments")
@jwt_required()
def admin_student_enrollments_set(student_id: int):
    """Asigna cursos al alumno dentro del ámbito del profesor actual.

    Body JSON: { "course_ids": [1,2,3] }
    - Sólo se permiten IDs de cursos cuyo admin_id coincide con el admin autenticado
    - Se eliminan matrículas existentes del alumno en cursos del admin que no estén en la nueva lista
    - Se crean matrículas faltantes para los IDs proporcionados
    """
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    Student.query.get_or_404(student_id)  # Validar existencia
    data = request.get_json(silent=True) or {}
    incoming_ids = data.get("course_ids") or []
    try:
        target_ids = {int(cid) for cid in incoming_ids}
    except Exception:
        return jsonify({"error": "course_ids debe ser una lista de enteros"}), 400

    # Limitar a cursos del admin actual
    allowed_courses = Course.query.filter(Course.admin_id == admin_id).all()
    allowed_ids = {c.id for c in allowed_courses}
    target_ids = target_ids & allowed_ids  # intersección con permitidos

    # Matrículas existentes del alumno en cursos del admin
    existing = (
        Enrollment.query.join(Course, Enrollment.course_id == Course.id)
        .filter(Enrollment.student_id == student_id, Course.admin_id == admin_id)
        .all()
    )
    existing_ids = {e.course_id for e in existing}

    # Eliminar las que ya no están en target
    to_delete_ids = existing_ids - target_ids
    if to_delete_ids:
        Enrollment.query.filter(Enrollment.student_id == student_id, Enrollment.course_id.in_(list(to_delete_ids))).delete(synchronize_session=False)

    # Agregar nuevas (evitar duplicados)
    to_add_ids = target_ids - existing_ids
    for cid in to_add_ids:
        db.session.add(Enrollment(student_id=student_id, course_id=cid))

    db.session.commit()
    # Responder con cursos finales
    final_courses = (
        Course.query.join(Enrollment, Enrollment.course_id == Course.id)
        .filter(Enrollment.student_id == student_id, Course.admin_id == admin_id)
        .all()
    )
    return jsonify({
        "status": "updated",
        "items": [{"id": c.id, "name": c.name} for c in final_courses]
    }), 200


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


# --- Admin: Estudiantes por Curso (Enrollments) ---

@api_bp.get("/admin/courses/<int:course_id>/students")
@jwt_required()
def admin_course_students_list(course_id: int):
    """Obtener lista de estudiantes en un curso"""
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    
    # Verificar que el admin sea propietario del curso
    course = Course.query.get_or_404(course_id)
    if course.admin_id != admin_id:
        return jsonify({"error": "No autorizado"}), 403
    
    # Obtener estudiantes inscritos en el curso
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    students = []
    
    for enrollment in enrollments:
        student = Student.query.get(enrollment.student_id)
        if student:
            students.append({
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "is_scholarship_student": student.is_scholarship_student
            })
    
    return jsonify(students), 200


@api_bp.post("/admin/courses/<int:course_id>/enroll")
@jwt_required()
def admin_course_enroll_student(course_id: int):
    """Agregar estudiante a un curso"""
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    
    # Verificar que el admin sea propietario del curso
    course = Course.query.get_or_404(course_id)
    if course.admin_id != admin_id:
        return jsonify({"error": "No autorizado"}), 403
    
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    
    if not student_id:
        return jsonify({"error": "ID del estudiante requerido"}), 400
    
    # Verificar que el estudiante exista
    student = Student.query.get_or_404(student_id)
    
    # Verificar si ya está inscrito
    existing = Enrollment.query.filter_by(course_id=course_id, student_id=student_id).first()
    if existing:
        return jsonify({"error": "Estudiante ya inscrito en este curso"}), 400
    
    # Crear enrollment
    enrollment = Enrollment(course_id=course_id, student_id=student_id)
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify({
        "id": enrollment.id,
        "course_id": course_id,
        "student_id": student_id
    }), 201


@api_bp.delete("/admin/courses/<int:course_id>/unenroll/<int:student_id>")
@jwt_required()
def admin_course_unenroll_student(course_id: int, student_id: int):
    """Eliminar estudiante de un curso"""
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    
    # Verificar que el admin sea propietario del curso
    course = Course.query.get_or_404(course_id)
    if course.admin_id != admin_id:
        return jsonify({"error": "No autorizado"}), 403
    
    # Obtener el enrollment
    enrollment = Enrollment.query.filter_by(course_id=course_id, student_id=student_id).first_or_404()
    
    db.session.delete(enrollment)
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
    # La sesión se inicia implícitamente cuando se registra la asistencia
    return jsonify({"course_id": course_id, "status": "session_started"}), 201


@api_bp.post("/admin/courses/<int:course_id>/session/end")
@jwt_required()
def admin_session_end(course_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    admin_id = _normalize_identity(get_jwt_identity())
    course = Course.query.get_or_404(course_id)
    if course.admin_id != admin_id:
        return jsonify({"error": "No autorizado"}), 403
    # La sesión se cierra implícitamente en el sistema
    return jsonify({"course_id": course_id, "status": "session_ended"}), 200


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
    course_id = request.args.get("course_id", type=int)
    from datetime import date
    q = Attendance.query
    if course_id:
        q = q.filter_by(course_id=course_id)
    # Obtener solo registros de hoy
    today = date.today()
    q = q.filter(db.func.date(Attendance.created_at) == today)
    records = q.all()
    items = [
        {
            "id": a.id,
            "course_id": a.course_id,
            "student_id": a.student_id,
            "date": a.date.isoformat(),
            "status": a.status,
            "entry_time": str(a.entry_time) if a.entry_time else None,
            "exit_time": str(a.exit_time) if a.exit_time else None,
        }
        for a in records
    ]
    return jsonify({"items": items}), 200


@api_bp.patch("/admin/summaries/<int:attendance_id>")
@jwt_required()
def admin_summary_update(attendance_id: int):
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    a = Attendance.query.get_or_404(attendance_id)
    data = request.get_json(silent=True) or {}
    if "status" in data:
        valid_statuses = ['presente', 'tardanza', 'falta', 'salida_repentina']
        if data.get("status") not in valid_statuses:
            return jsonify({"error": f"Status debe ser uno de: {','.join(valid_statuses)}"}), 400
        a.status = data.get("status")
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
        token = create_access_token(identity=str(user.id), additional_claims={"email": user.email, "role": "admin"})
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
            token = create_access_token(identity=str(user.id), additional_claims={"email": user.email, "role": role_value})
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
@api_bp.get("/video_stream")
@api_bp.get("/admin/video_stream")
def video_stream():
    camera_url = (request.args.get("url") or os.getenv("CAMERA_URL") or "http://192.168.18.122:81/stream").strip()
    if request.method == "HEAD":
        resp = Response(status=200)
        resp.headers["Content-Type"] = "multipart/x-mixed-replace; boundary=frame"
        return resp
    def gen():
        cap = cv2.VideoCapture(camera_url)
        try:
            while True:
                if not cap.isOpened():
                    cap.release()
                    cap = cv2.VideoCapture(camera_url)
                    time.sleep(0.5)
                    continue
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.05)
                    continue
                ok2, buf = cv2.imencode('.jpg', frame)
                if not ok2:
                    continue
                data = buf.tobytes()
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + data + b"\r\n"
        finally:
            try:
                cap.release()
            except Exception:
                pass
    return Response(stream_with_context(gen()), content_type="multipart/x-mixed-replace; boundary=frame")

FACE_PROC = None
KNOWN_ENCODINGS, KNOWN_NAMES = None, None  # Cargar perezosamente en la función que lo usa

def _load_face_model():
    global KNOWN_ENCODINGS, KNOWN_NAMES
    if KNOWN_ENCODINGS is None:
        from app.services.face_recognition_service import cargar_modelo
        KNOWN_ENCODINGS, KNOWN_NAMES = cargar_modelo()
    return KNOWN_ENCODINGS, KNOWN_NAMES

@api_bp.post("/admin/face/run")
def face_run():
    global FACE_PROC
    data = request.get_json(silent=True) or {}
    action = (data.get("action") or "").strip()
    name = (data.get("name") or "").strip()
    source = (data.get("source") or "").strip()
    ia_path = r"c:\\Cloud Computing\\PRUEBA IA\\IA_cortas_distancias.py"
    if not os.path.isfile(ia_path):
        return jsonify({"error": "IA no disponible"}), 404
    if FACE_PROC and FACE_PROC.poll() is None:
        return jsonify({"error": "Proceso en ejecución"}), 409
    def run_capture():
        p = subprocess.Popen(
            [sys.executable, ia_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(ia_path)
        )
        p.stdin.write("1\n")
        p.stdin.write(f"{source}\n")
        p.stdin.write(f"{name}\n")
        p.stdin.flush()
        return p
    def run_model():
        p = subprocess.Popen(
            [sys.executable, ia_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(ia_path)
        )
        p.stdin.write("2\n")
        p.stdin.flush()
        return p
    def run_recognize():
        p = subprocess.Popen(
            [sys.executable, ia_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(ia_path)
        )
        p.stdin.write("3\n")
        p.stdin.write(f"{source}\n")
        p.stdin.flush()
        return p
    try:
        if action == "capture":
            FACE_PROC = run_capture()
        elif action == "model":
            FACE_PROC = run_model()
        elif action == "recognize":
            FACE_PROC = run_recognize()
        else:
            return jsonify({"error": "Acción inválida"}), 400
    except Exception:
        FACE_PROC = None
        return jsonify({"error": "Fallo al iniciar IA"}), 500
    def drain(proc):
        try:
            proc.communicate()
        except Exception:
            pass
    threading.Thread(target=drain, args=(FACE_PROC,), daemon=True).start()
    return jsonify({"ok": True}), 202

@api_bp.post("/admin/model/build")
@jwt_required()
def admin_model_build():
    if not _require_role("admin"):
        return jsonify({"error": "No autorizado"}), 401
    ok = generar_modelo()
    if ok:
        return jsonify({"ok": True}), 200
    return jsonify({"error": "No se pudo generar modelo"}), 500

@api_bp.get("/admin/recognize_stream")
def recognize_stream():
    camera_url = request.args.get('url', '').strip()
    if not camera_url:
        return jsonify({"error": "url requerida"}), 400
    def gen():
        cap = cv2.VideoCapture(camera_url)
        process_every = 3
        i = 0
        last_locs, last_names = [], []
        try:
            while True:
                if not cap.isOpened():
                    cap.release()
                    cap = cv2.VideoCapture(camera_url)
                    time.sleep(0.5)
                    continue
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.05)
                    continue
                i += 1
                if i % process_every == 0:
                    enc, nms = _load_face_model()
                    locs, names = reconocer_en_frame(frame, enc or [], nms or [], tolerance=0.5)
                    last_locs, last_names = locs, names
                frame2 = dibujar_resultados(frame, last_locs, last_names)
                ok2, buf = cv2.imencode('.jpg', frame2)
                if not ok2:
                    continue
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
        finally:
            try:
                cap.release()
            except Exception:
                pass
    resp = Response(stream_with_context(gen()), content_type="multipart/x-mixed-replace; boundary=frame")
    resp.headers["Cache-Control"] = "no-cache"
    return resp

@api_bp.post("/admin/face/stop")
def face_stop():
    global FACE_PROC
    if FACE_PROC and FACE_PROC.poll() is None:
        try:
            FACE_PROC.terminate()
        except Exception:
            pass
    FACE_PROC = None
    return jsonify({"ok": True}), 200

@api_bp.post("/admin/face/capture")
def face_capture():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    source = (data.get("source") or "").strip()
    duration = int(data.get("duration") or 12)
    max_count = int(data.get("max_count") or 50)
    if not name or not source:
        return jsonify({"error": "name y source requeridos"}), 400
    dest_root = r"c:\\Cloud Computing\\PROYECTO_FINAL\\TrabajoFinalCognitive\\fotos_conocidas"
    try:
        safe = secure_filename(name)
    except Exception:
        safe = name.replace(" ", "_")
    dest_dir = os.path.join(dest_root, safe)
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except Exception:
        return jsonify({"error": "No se pudo crear carpeta"}), 500
    def run():
        def abrir_fuente(src):
            s = str(src).strip()
            if s.isdigit():
                try:
                    return cv2.VideoCapture(int(s), cv2.CAP_DSHOW)
                except Exception:
                    return cv2.VideoCapture(int(s))
            if s.startswith("rtsp://") or s.startswith("http://") or s.startswith("https://"):
                cap0 = cv2.VideoCapture(s)
                if not cap0.isOpened():
                    try:
                        cap0.release()
                    except Exception:
                        pass
                    cap0 = cv2.VideoCapture(s, cv2.CAP_FFMPEG)
                return cap0
            try:
                return cv2.VideoCapture(int(s), cv2.CAP_DSHOW)
            except Exception:
                return cv2.VideoCapture(s)

        cap = abrir_fuente(source)
        try:
            cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml'))
        except Exception:
            cascade = None
        end_t = time.time() + duration
        saved = 0
        while time.time() < end_t and saved < max_count:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.05)
                continue
            faces = []
            if cascade is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
            if not faces:
                h, w = frame.shape[:2]
                cx, cy = w//2, h//2
                size = min(w, h)//3
                x = max(cx - size//2, 0)
                y = max(cy - size//2, 0)
                faces = [(x, y, size, size)]
            for (x, y, w, h) in faces:
                roi = frame[y:y+h, x:x+w]
                try:
                    roi = cv2.resize(roi, (150, 150), interpolation=cv2.INTER_CUBIC)
                except Exception:
                    pass
                fn = datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.jpg'
                p = os.path.join(dest_dir, fn)
                try:
                    cv2.imwrite(p, roi)
                    saved += 1
                except Exception:
                    pass
                if saved >= max_count:
                    break
        try:
            cap.release()
        except Exception:
            pass
    threading.Thread(target=run, daemon=True).start()
    return jsonify({"ok": True, "dir": dest_dir}), 202
@api_bp.post("/admin/save_frame")
@jwt_required()
def handle_save_frame():
    if not _require_role("admin"):
        return jsonify({"msg": "Acceso denegado"}), 403
    data = request.get_json(silent=True) or {}
    person_name = (data.get('name') or '').strip()
    image_b64 = data.get('image_base64') or ''
    if not person_name or not image_b64:
        return jsonify({"msg": "Faltan 'name' o 'image_base64'"}), 400
    try:
        payload = image_b64.split(',', 1)[-1]
        raw = base64.b64decode(payload)
    except Exception:
        return jsonify({"msg": "Base64 inválido"}), 400
    try:
        dest_root = r"c:\\Cloud Computing\\PROYECTO_FINAL\\TrabajoFinalCognitive\\fotos_conocidas"
        try:
            safe = secure_filename(person_name)
        except Exception:
            safe = person_name.replace(" ", "_")
        dest_dir = os.path.join(dest_root, safe)
        os.makedirs(dest_dir, exist_ok=True)
        existing = [f for f in os.listdir(dest_dir) if f.lower().endswith('.jpg')]
        idx = len(existing)
        fname = f"rostro_{idx}.jpg"
        path = os.path.join(dest_dir, fname)
        with open(path, 'wb') as f:
            f.write(raw)
        return jsonify({"msg": "Imagen guardada", "path": path}), 200
    except Exception as e:
        return jsonify({"msg": f"Error al guardar: {str(e)}"}), 500


@api_bp.get("/admin/users")
@jwt_required()
def admin_users_list():
    """List users by role (admin, advisor, student)"""
    if not _require_role("admin"):
        return jsonify({"msg": "Acceso denegado"}), 403
    
    role = request.args.get('role', 'advisor')  # Default to advisor
    
    try:
        query = User.query
        
        if role == 'advisor':
            query = query.filter_by(role='advisor')
        elif role == 'student':
            query = query.filter_by(role='student')
        elif role == 'admin':
            query = query.filter_by(role='admin')
        
        users = query.all()
        
        return jsonify({
            'data': [{
                'id': u.id,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'email': u.email,
                'role': u.role,
                'created_at': u.created_at.isoformat() if hasattr(u, 'created_at') else None
            } for u in users]
        }), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500