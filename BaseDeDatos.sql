-- BaseDeDatos.sql
-- Script de datos de ejemplo para el proyecto (SQLite)
-- Limpia datos y pobla con mock sin tocar el esquema creado por migraciones.

PRAGMA foreign_keys = OFF;

-- Limpieza de datos (hijos primero, luego padres)
DELETE FROM enrollments;
DELETE FROM alerts;
DELETE FROM courses;
DELETE FROM users;
DELETE FROM students;

PRAGMA foreign_keys = ON;

-- Datos de ejemplo
-- Usuarios (incluye asesor para el curso y login de asesor)
INSERT INTO users (id, email, password_text, first_name, last_name, role, description) VALUES
  (1, 'asesor@demo.com', 'Password123', 'Ana', 'Asesora', 'advisor', 'Asesora de becas con experiencia en seguimiento académico'),
  (2, 'cliente@demo.com', 'Password123', 'Carlos', 'Cliente', 'client', NULL),
  (3, 'admin@demo.com', 'Password123', 'Elmer', 'Arellanos', 'admin', 'Profesor de Ingeniería Eléctrica con más de 15 años de experiencia en circuitos y sistemas digitales');

-- Estudiantes (becarios y no becarios)
INSERT INTO students (id, first_name, last_name, email, is_scholarship_student) VALUES
  (1, 'Felipe', 'García', 'felipe@example.com', 1),
  (2, 'Franco', 'Pérez', 'franco@example.com', 1),
  (3, 'Israel', 'López', 'israel@example.com', 0);

-- Cursos (administrados por el profesor Elmer Arellanos - admin con id=3)
INSERT INTO courses (id, name, admin_id) VALUES
  (1, 'Circuitos Eléctricos', 3),
  (2, 'Circuitos Eléctricos y Electrónicos I', 3),
  (3, 'Circuitos Digitales', 3);

-- Matrículas (becarios en los cursos del profesor Elmer)
INSERT INTO enrollments (id, student_id, course_id) VALUES
  (1, 1, 1), -- Felipe en Circuitos Eléctricos
  (2, 2, 1), -- Franco en Circuitos Eléctricos
  (3, 1, 2), -- Felipe en Circuitos Eléctricos y Electrónicos I
  (4, 2, 3), -- Franco en Circuitos Digitales
  (5, 1, 3); -- Felipe en Circuitos Digitales

-- Alertas para el asesor
INSERT INTO alerts (id, course_id, student_id, message, is_read, created_at) VALUES
  (1, 1, 1, 'Felipe García ha faltado 3 veces consecutivas', 0, datetime('now', '-2 days')),
  (2, 2, 1, 'Felipe García tiene bajo rendimiento en evaluaciones', 0, datetime('now', '-1 day')),
  (3, 3, 2, 'Franco Pérez necesita apoyo adicional en laboratorio', 1, datetime('now', '-3 days'));