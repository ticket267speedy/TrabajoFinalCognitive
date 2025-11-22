import os
import cv2
import numpy as np
from datetime import datetime
import face_recognition

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOTOS_DIR = os.path.join(PROJECT_ROOT, "fotos_conocidas")
MODELO_PATH = os.path.join(PROJECT_ROOT, "modelo_caras.pkl")

def generar_modelo():
    import pickle
    if not os.path.isdir(FOTOS_DIR):
        return False
    nombres = []
    encodings = []
    extensiones = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    for item in os.listdir(FOTOS_DIR):
        ruta_item = os.path.join(FOTOS_DIR, item)
        if os.path.isdir(ruta_item):
            persona = item
            for archivo in os.listdir(ruta_item):
                ruta = os.path.join(ruta_item, archivo)
                _, ext = os.path.splitext(archivo)
                if not os.path.isfile(ruta) or ext.lower() not in extensiones:
                    continue
                try:
                    imagen = face_recognition.load_image_file(ruta)
                    ubicaciones = face_recognition.face_locations(imagen, model="hog")
                    if not ubicaciones:
                        continue
                    encoding = face_recognition.face_encodings(imagen, known_face_locations=ubicaciones)[0]
                    encodings.append(encoding)
                    nombres.append(persona)
                except Exception:
                    continue
        else:
            nombre, ext = os.path.splitext(item)
            if ext.lower() not in extensiones:
                continue
            ruta = ruta_item
            try:
                imagen = face_recognition.load_image_file(ruta)
                ubicaciones = face_recognition.face_locations(imagen, model="hog")
                if not ubicaciones:
                    continue
                encoding = face_recognition.face_encodings(imagen, known_face_locations=ubicaciones)[0]
                encodings.append(encoding)
                nombres.append(nombre)
            except Exception:
                continue
    if not encodings:
        return False
    modelo_data = {
        'encodings': encodings,
        'nombres': nombres,
        'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_encodings': len(encodings),
        'personas_unicas': len(set(nombres))
    }
    try:
        with open(MODELO_PATH, 'wb') as f:
            pickle.dump(modelo_data, f)
        return True
    except Exception:
        return False

def cargar_modelo():
    import pickle
    if not os.path.exists(MODELO_PATH):
        return None, None
    try:
        with open(MODELO_PATH, 'rb') as f:
            modelo_data = pickle.load(f)
        return modelo_data['encodings'], modelo_data['nombres']
    except Exception:
        return None, None

def verificar_modelo_actualizado():
    if not os.path.exists(MODELO_PATH):
        return False
    modelo_time = os.path.getmtime(MODELO_PATH)
    if os.path.isdir(FOTOS_DIR):
        for root, dirs, files in os.walk(FOTOS_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) > modelo_time:
                    return False
    return True

def detectar_rostros_directo(frame_bgr):
    if not hasattr(detectar_rostros_directo, 'detector'):
        detectar_rostros_directo.detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    faces = detectar_rostros_directo.detector.detectMultiScale(
        gray,
        scaleFactor=1.15,
        minNeighbors=7,
        minSize=(80, 80),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    face_locations = []
    for (x, y, w, h) in faces:
        aspect_ratio = w / float(h)
        if aspect_ratio < 0.7 or aspect_ratio > 1.4:
            continue
        if w < 80 or h < 80:
            continue
        margen = int(w * 0.1)
        top = max(0, y - margen)
        right = min(frame_bgr.shape[1], x + w + margen)
        bottom = min(frame_bgr.shape[0], y + h + margen)
        left = max(0, x - margen)
        face_locations.append((top, right, bottom, left))
    return face_locations

def reconocer_en_frame(frame_bgr, known_encodings, known_names, tolerance=0.55):
    face_locations = detectar_rostros_directo(frame_bgr)
    if not face_locations:
        return [], []
    small_frame = cv2.resize(frame_bgr, (0, 0), fx=0.5, fy=0.5)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    nombres_detectados = []
    face_locations_final = []
    for (top, right, bottom, left) in face_locations:
        top_s = top // 2
        right_s = right // 2
        bottom_s = bottom // 2
        left_s = left // 2
        if top_s >= bottom_s or left_s >= right_s:
            continue
        if top_s < 0 or left_s < 0 or bottom_s > rgb_small.shape[0] or right_s > rgb_small.shape[1]:
            continue
        ancho_region = right_s - left_s
        alto_region = bottom_s - top_s
        if ancho_region < 30 or alto_region < 30:
            continue
        rostro_region = rgb_small[top_s:bottom_s, left_s:right_s]
        std_dev = np.std(rostro_region)
        if std_dev < 15:
            continue
        face_location_small = [(top_s, right_s, bottom_s, left_s)]
        encs = face_recognition.face_encodings(
            rgb_small,
            face_location_small,
            num_jitters=1,
            model="small"
        )
        if not encs:
            continue
        face_encoding = encs[0]
        nombre = "Desconocido"
        if known_encodings:
            dists = face_recognition.face_distance(known_encodings, face_encoding)
            if len(dists) > 0:
                best_idx = int(np.argmin(dists))
                best_dist = dists[best_idx]
                if best_dist <= tolerance:
                    nombre = known_names[best_idx]
        nombres_detectados.append(nombre)
        face_locations_final.append((top, right, bottom, left))
    return face_locations_final, nombres_detectados

def dibujar_resultados(frame_bgr, face_locations, face_names):
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        color = (0, 255, 0) if name != "Desconocido" else (0, 0, 255)
        cv2.rectangle(frame_bgr, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame_bgr, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame_bgr, name, (left + 6, bottom - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    return frame_bgr

pass