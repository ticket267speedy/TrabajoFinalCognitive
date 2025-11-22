import os
import cv2
import face_recognition
import numpy as np
from ultralytics import YOLO
import torch
import pickle
from datetime import datetime

# ============= CONFIGURACIÓN GPU =============
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"[INFO] Usando dispositivo: {DEVICE}")

# ============= RUTAS DE ARCHIVOS =============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOTOS_DIR = os.path.join(BASE_DIR, "fotos_conocidas")
MODELO_PATH = os.path.join(BASE_DIR, "modelo_caras.pkl")

# ============= MODELO YOLO =============
YOLO_MODEL = None

def inicializar_yolo():
    global YOLO_MODEL
    try:
        YOLO_MODEL = YOLO('yolov8n.pt')
        YOLO_MODEL.to(DEVICE)
        print("[INFO] Modelo YOLO cargado exitosamente")
    except Exception as e:
        print(f"[ERROR] No se pudo cargar YOLO: {e}")
        return None
    return YOLO_MODEL


# ============= GESTIÓN DEL MODELO DE ENCODINGS =============
def generar_modelo():
    """
    Genera el modelo de encodings a partir de las fotos conocidas
    y lo guarda en un archivo pickle para carga rápida
    """
    print("\n" + "="*60)
    print("  GENERANDO MODELO DE RECONOCIMIENTO FACIAL")
    print("="*60 + "\n")
    
    if not os.path.isdir(FOTOS_DIR):
        print(f"[ERROR] No existe la carpeta '{FOTOS_DIR}'")
        print("Primero debes capturar rostros usando la opción 'capturar'")
        return False
    
    nombres = []
    encodings = []
    extensiones = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    total_procesadas = 0
    total_exitosas = 0
    
    print("[INFO] Procesando imágenes...\n")
    
    # Procesar carpetas de personas
    for item in os.listdir(FOTOS_DIR):
        ruta_item = os.path.join(FOTOS_DIR, item)
        
        if os.path.isdir(ruta_item):
            persona = item
            print(f"[PROCESANDO] Persona: {persona}")
            contador_persona = 0
            
            for archivo in os.listdir(ruta_item):
                ruta = os.path.join(ruta_item, archivo)
                _, ext = os.path.splitext(archivo)
                
                if not os.path.isfile(ruta) or ext.lower() not in extensiones:
                    continue
                
                total_procesadas += 1
                try:
                    imagen = face_recognition.load_image_file(ruta)
                    ubicaciones = face_recognition.face_locations(imagen, model="cnn")
                    
                    if not ubicaciones:
                        print(f"  ⚠ No se detectó rostro en: {archivo}")
                        continue
                    
                    encoding = face_recognition.face_encodings(imagen, known_face_locations=ubicaciones)[0]
                    encodings.append(encoding)
                    nombres.append(persona)
                    total_exitosas += 1
                    contador_persona += 1
                    
                except Exception as e:
                    print(f"  ✗ Error en {archivo}: {e}")
                    continue
            
            print(f"  ✓ {contador_persona} imágenes procesadas exitosamente\n")
        
        # Procesar archivos sueltos (sin carpeta de persona)
        else:
            nombre, ext = os.path.splitext(item)
            if ext.lower() not in extensiones:
                continue
            
            ruta = ruta_item
            total_procesadas += 1
            
            try:
                imagen = face_recognition.load_image_file(ruta)
                ubicaciones = face_recognition.face_locations(imagen, model="cnn")
                
                if not ubicaciones:
                    print(f"  ⚠ No se detectó rostro en: {item}")
                    continue
                
                encoding = face_recognition.face_encodings(imagen, known_face_locations=ubicaciones)[0]
                encodings.append(encoding)
                nombres.append(nombre)
                total_exitosas += 1
                print(f"[PROCESANDO] Imagen suelta: {nombre} ✓")
                
            except Exception as e:
                print(f"  ✗ Error en {item}: {e}")
                continue
    
    if not encodings:
        print("\n[ERROR] No se pudo generar ningún encoding.")
        print("Verifica que las imágenes contengan rostros visibles.")
        return False
    
    # Guardar modelo
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
        
        print("\n" + "="*60)
        print("  ✓ MODELO GENERADO EXITOSAMENTE")
        print("="*60)
        print(f"\n📊 Estadísticas:")
        print(f"  • Imágenes procesadas: {total_procesadas}")
        print(f"  • Encodings exitosos: {total_exitosas}")
        print(f"  • Personas únicas: {len(set(nombres))}")
        print(f"  • Archivo guardado: {MODELO_PATH}")
        print(f"  • Tamaño: {os.path.getsize(MODELO_PATH) / 1024:.2f} KB")
        print(f"  • Fecha: {modelo_data['fecha_creacion']}\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] No se pudo guardar el modelo: {e}")
        return False


def cargar_modelo():
    """
    Carga el modelo de encodings desde el archivo pickle
    Mucho más rápido que procesar todas las imágenes
    """
    if not os.path.exists(MODELO_PATH):
        print(f"\n[ERROR] No existe el modelo: {MODELO_PATH}")
        print("Primero debes generar el modelo usando la opción 'generar'")
        return None, None
    
    try:
        with open(MODELO_PATH, 'rb') as f:
            modelo_data = pickle.load(f)
        
        print("\n[INFO] Modelo cargado correctamente")
        print(f"  • Fecha de creación: {modelo_data.get('fecha_creacion', 'N/A')}")
        print(f"  • Total encodings: {modelo_data.get('total_encodings', len(modelo_data['encodings']))}")
        print(f"  • Personas únicas: {modelo_data.get('personas_unicas', len(set(modelo_data['nombres'])))}")
        
        return modelo_data['encodings'], modelo_data['nombres']
        
    except Exception as e:
        print(f"\n[ERROR] No se pudo cargar el modelo: {e}")
        print("Intenta generar un nuevo modelo con la opción 'generar'")
        return None, None


def verificar_modelo_actualizado():
    """
    Verifica si hay imágenes nuevas que requieran regenerar el modelo
    """
    if not os.path.exists(MODELO_PATH):
        return False
    
    modelo_time = os.path.getmtime(MODELO_PATH)
    
    # Verificar si hay archivos más recientes que el modelo
    if os.path.isdir(FOTOS_DIR):
        for root, dirs, files in os.walk(FOTOS_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) > modelo_time:
                    print("\n[ADVERTENCIA] Se detectaron imágenes nuevas")
                    print("Considera regenerar el modelo para incluirlas")
                    return False
    
    return True


# ============= CAPTURA DE ROSTROS =============
def abrir_fuente(source):
    if isinstance(source, int):
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        return cap
    return cv2.VideoCapture(source)


def capturar_rostros(source, person_name, max_count=50):
    """
    Captura rostros de una persona para entrenar el modelo
    """
    if not os.path.isdir(FOTOS_DIR):
        os.makedirs(FOTOS_DIR)
    
    personalPath = os.path.join(FOTOS_DIR, person_name)
    if not os.path.isdir(personalPath):
        os.makedirs(personalPath)
    else:
        print(f"\n[INFO] La carpeta para '{person_name}' ya existe")
        print(f"[INFO] Las nuevas fotos se agregarán a: {personalPath}")

    cap = abrir_fuente(source)
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la fuente de video para captura.")
        return

    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    count = len([f for f in os.listdir(personalPath) if f.endswith('.jpg')])  # Continuar desde último número
    print(f"\n[INFO] Iniciando captura (ya hay {count} imágenes)")
    print("[INFO] Presiona ESC para salir antes de tiempo")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            auxFrame = frame.copy()

            faces = faceClassif.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                rostro = auxFrame[y:y + h, x:x + w]
                rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(os.path.join(personalPath, f"rostro_{count}.jpg"), rostro)
                count += 1
                if count >= max_count:
                    break
            
            # Mostrar progreso
            cv2.putText(frame, f"Capturadas: {count}/{max_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Captura de rostros', frame)
            
            k = cv2.waitKey(1)
            if k == 27 or count >= max_count:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\n[INFO] Captura finalizada: {count} imágenes guardadas")
        print("\n[IMPORTANTE] Recuerda ejecutar la opción 'generar' para actualizar el modelo")


# ============= DETECCIÓN LIGERA DE ROSTROS =============
def detectar_rostros_directo(frame_bgr):
    """
    Detecta rostros de forma LIGERA usando Haar Cascade (GPU acelerado)
    Con validaciones para reducir falsos positivos
    """
    # Crear detector Haar si no existe
    if not hasattr(detectar_rostros_directo, 'detector'):
        detectar_rostros_directo.detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    # Convertir a escala de grises (más rápido)
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    
    # Detectar rostros con parámetros MÁS ESTRICTOS para evitar falsos positivos
    faces = detectar_rostros_directo.detector.detectMultiScale(
        gray,
        scaleFactor=1.15,      # Más estricto (antes 1.1)
        minNeighbors=7,        # Más vecinos = menos falsos positivos (antes 5)
        minSize=(80, 80),      # Tamaño mínimo mayor (antes 60x60)
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Filtrar detecciones por relación de aspecto (rostros son ~cuadrados)
    face_locations = []
    for (x, y, w, h) in faces:
        # Verificar relación de aspecto (debe ser cercana a 1:1)
        aspect_ratio = w / float(h)
        if aspect_ratio < 0.7 or aspect_ratio > 1.4:
            continue  # Descartar si no parece un rostro
        
        # Verificar tamaño mínimo razonable
        if w < 80 or h < 80:
            continue
        
        # Agregar un poco de margen
        margen = int(w * 0.1)
        top = max(0, y - margen)
        right = min(frame_bgr.shape[1], x + w + margen)
        bottom = min(frame_bgr.shape[0], y + h + margen)
        left = max(0, x - margen)
        face_locations.append((top, right, bottom, left))
    
    return face_locations


def reconocer_en_frame_yolo(frame_bgr, known_encodings, known_names, tolerance=0.55):
    """Detecta y reconoce rostros de forma LIGERA y rápida con validaciones"""
    
    # 1. Detectar rostros con Haar Cascade (súper rápido)
    face_locations = detectar_rostros_directo(frame_bgr)
    
    if not face_locations:
        return [], []
    
    # 2. Procesar solo en frame reducido para VELOCIDAD
    small_frame = cv2.resize(frame_bgr, (0, 0), fx=0.5, fy=0.5)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    nombres_detectados = []
    face_locations_final = []
    
    # 3. Procesar cada rostro detectado
    for (top, right, bottom, left) in face_locations:
        # Escalar coordenadas al frame pequeño
        top_s = top // 2
        right_s = right // 2
        bottom_s = bottom // 2
        left_s = left // 2
        
        # Verificar que la región sea válida
        if top_s >= bottom_s or left_s >= right_s:
            continue
        if top_s < 0 or left_s < 0 or bottom_s > rgb_small.shape[0] or right_s > rgb_small.shape[1]:
            continue
        
        # Validar tamaño mínimo de la región
        ancho_region = right_s - left_s
        alto_region = bottom_s - top_s
        if ancho_region < 30 or alto_region < 30:
            continue
        
        try:
            # Extraer región del rostro
            rostro_region = rgb_small[top_s:bottom_s, left_s:right_s]
            
            # VALIDACIÓN ADICIONAL: Verificar que la región tenga suficiente variación
            # (los rostros reales tienen más variación que áreas planas)
            std_dev = np.std(rostro_region)
            if std_dev < 15:  # Muy poca variación = probablemente no es un rostro
                continue
            
            # Obtener encoding del rostro (en frame pequeño = más rápido)
            face_location_small = [(top_s, right_s, bottom_s, left_s)]
            face_encodings = face_recognition.face_encodings(
                rgb_small, 
                face_location_small, 
                num_jitters=1,
                model="small"  # Modelo pequeño para velocidad
            )
            
            if not face_encodings:
                continue
            
            face_encoding = face_encodings[0]
            nombre = "Desconocido"
            confianza = 1.0  # Distancia máxima por defecto
            
            if known_encodings:
                # Calcular distancias
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                
                if len(face_distances) > 0:
                    best_match_index = int(np.argmin(face_distances))
                    best_distance = face_distances[best_match_index]
                    confianza = best_distance
                    
                    if best_distance <= tolerance:
                        nombre = known_names[best_match_index]
                    else:
                        # Si la distancia es MUY alta (>0.8), probablemente no es un rostro
                        if best_distance > 0.8:
                            continue
            else:
                # Si no hay caras conocidas y llegó hasta aquí, probablemente es un rostro válido
                pass
            
            nombres_detectados.append(nombre)
            face_locations_final.append((top, right, bottom, left))
            
        except Exception as e:
            continue
    
    return face_locations_final, nombres_detectados


def dibujar_resultados(frame_bgr, face_locations, face_names):
    """Dibuja cajas y nombres en el frame"""
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        color = (0, 255, 0) if name != "Desconocido" else (0, 0, 255)
        cv2.rectangle(frame_bgr, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame_bgr, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame_bgr, name, (left + 6, bottom - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    return frame_bgr


# ============= RECONOCIMIENTO EN TIEMPO REAL =============
def iniciar_reconocimiento(source):
    """
    Inicia el reconocimiento facial en tiempo real
    usando el modelo pre-generado
    """
    # Ya no necesitamos YOLO, usamos face_recognition directo
    print("[INFO] Inicializando sistema de detección...")
    
    # Cargar modelo de caras (instantáneo!)
    known_encodings, known_names = cargar_modelo()
    if known_encodings is None:
        return
    
    # Verificar si el modelo está actualizado
    verificar_modelo_actualizado()
    
    cap = abrir_fuente(source)
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la fuente de video.")
        return

    # OPTIMIZACIÓN: procesar cada 3 frames para no laguear
    process_every = 3
    frame_index = 0
    last_face_locations = []
    last_face_names = []

    print("\n[INFO] Iniciando reconocimiento facial...")
    print("[INFO] Presiona 'q' para salir")
    print("[INFO] Presiona 's' para capturar screenshot\n")

    import time
    fps_counter = 0
    fps_start = time.time()
    fps_display = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] No se pudo leer frame.")
                break

            frame_index += 1
            fps_counter += 1

            if frame_index % process_every == 0:
                last_face_locations, last_face_names = reconocer_en_frame_yolo(
                    frame, known_encodings, known_names, tolerance=0.5
                )

            dibujar_resultados(frame, last_face_locations, last_face_names)

            if fps_counter >= 30:
                fps_end = time.time()
                fps_display = int(30 / (fps_end - fps_start))
                fps_counter = 0
                fps_start = time.time()

            # Mostrar información de debug
            rostros_texto = f"Rostros: {len(last_face_names)}"
            if last_face_names:
                rostros_texto += f" ({', '.join(last_face_names)})"
            
            cv2.putText(frame, f"FPS: {fps_display}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, rostros_texto, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            cv2.imshow("Reconocimiento Facial - YOLO + GPU", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                screenshot_name = f"screenshot_{int(time.time())}.jpg"
                cv2.imwrite(screenshot_name, frame)
                print(f"[INFO] Screenshot: {screenshot_name}")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n[INFO] Reconocimiento finalizado")


# ============= MENÚ PRINCIPAL =============
def main():
    print("\n" + "="*60)
    print("  SISTEMA DE RECONOCIMIENTO FACIAL CON IA")
    print("  Optimizado para GPU RTX 3050")
    print("="*60 + "\n")
    
    print("Selecciona una opción:\n")
    print("  1. Capturar rostros    - Tomar fotos de una persona")
    print("  2. Generar modelo      - Crear/actualizar modelo de IA")
    print("  3. Reconocer rostros   - Iniciar reconocimiento en vivo")
    print("  4. Salir\n")
    
    opcion = input("Opción [3]: ").strip() or "3"
    
    if opcion == "1":
        # CAPTURAR
        nombre = input("\nNombre de la persona: ").strip()
        if not nombre:
            print("[ERROR] Debes ingresar un nombre")
            return
        
        fuente_in = input("Fuente (índice de cámara o URL) [0]: ").strip()
        source = int(fuente_in) if fuente_in.isdigit() else (fuente_in if fuente_in else 0)
        
        capturar_rostros(source, nombre, max_count=50)
    
    elif opcion == "2":
        # GENERAR MODELO
        generar_modelo()
    
    elif opcion == "3":
        # RECONOCER
        fuente_in = input("\nFuente (índice de cámara o URL) [0]: ").strip()
        source = int(fuente_in) if fuente_in.isdigit() else (fuente_in if fuente_in else 0)
        
        iniciar_reconocimiento(source)
    
    elif opcion == "4":
        print("\n¡Hasta luego! 👋\n")
    
    else:
        print("\n[ERROR] Opción no válida")


if __name__ == "__main__":
    main()