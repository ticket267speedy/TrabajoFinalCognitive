"""
Servicio de Reconocimiento Facial

Este módulo encapsula toda la lógica de reconocimiento facial
usando la librería face_recognition basada en redes neuronales
profundas.

Flujo:
1. Capturar/Cargar imagen del estudiante
2. Detectar rostros en la imagen
3. Generar encoding (representación 128-dimensional del rostro)
4. Comparar con encodings guardados en BD
5. Si coincide, registrar asistencia automáticamente
"""

import face_recognition
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
import cv2


class FaceRecognitionService:
    """
    Servicio para reconocimiento facial de estudiantes.
    
    Métodos principales:
    - encode_face: Crea un encoding del rostro de una imagen
    - recognize_face: Compara un rostro contra una base de datos de encodings
    - train_model: Entrena el modelo con fotos de estudiantes conocidos
    """
    
    # Umbral de tolerancia para coincidencia (0-1, menor = más estricto)
    # 0.6 es el valor default, 0.5 es más estricto, 0.7 es más flexible
    TOLERANCE = 0.6
    
    def __init__(self):
        """Inicializa el servicio de reconocimiento facial."""
        self.known_face_encodings = []
        self.known_face_names = []
    
    @staticmethod
    def encode_face(image_path: str) -> Optional[np.ndarray]:
        """
        Crea un encoding (vector 128D) del rostro en una imagen.
        
        Args:
            image_path: Ruta a la imagen del estudiante
        
        Returns:
            Array numpy con el encoding si se encontró un rostro, None en caso contrario
        
        Ejemplo:
            >>> encoding = FaceRecognitionService.encode_face('fotos_conocidas/israel_3/face.jpg')
            >>> print(encoding.shape)  # (128,)
        """
        try:
            # Cargar imagen
            image = face_recognition.load_image_file(image_path)
            
            # Detectar rostros (devuelve lista de encodings)
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) == 0:
                return None
            
            # Retornar el primer rostro encontrado
            return face_encodings[0]
            
        except Exception as e:
            print(f"Error cargando imagen {image_path}: {str(e)}")
            return None
    
    @staticmethod
    def recognize_face(
        test_image_path: str,
        known_encodings: List[np.ndarray],
        known_names: List[str],
        tolerance: float = TOLERANCE
    ) -> Tuple[Optional[str], float]:
        """
        Reconoce un rostro comparándolo contra una base de datos de encodings.
        
        Pasos:
        1. Cargar la imagen a reconocer
        2. Extraer el encoding del rostro
        3. Comparar contra todos los encodings conocidos
        4. Encontrar la mejor coincidencia
        
        Args:
            test_image_path: Ruta a la imagen a reconocer
            known_encodings: Lista de encodings de rostros conocidos
            known_names: Lista de nombres/IDs correspondientes
            tolerance: Umbral de similitud (0-1, default 0.6)
        
        Returns:
            Tuple con (nombre_reconocido, confianza)
            - nombre_reconocido: Nombre del estudiante si coincide, "Unknown" si no
            - confianza: Valor de similitud (0-1, donde 1 es perfecta coincidencia)
        
        Ejemplo:
            >>> name, confidence = FaceRecognitionService.recognize_face(
            ...     'foto_entrada.jpg',
            ...     known_encodings,
            ...     ['Israel', 'Carlos', 'María']
            ... )
            >>> if name != "Unknown":
            ...     print(f"Reconocido: {name} (confianza: {confidence:.2f})")
        """
        try:
            # Cargar y procesar imagen de prueba
            test_image = face_recognition.load_image_file(test_image_path)
            test_encodings = face_recognition.face_encodings(test_image)
            
            if len(test_encodings) == 0:
                return "Unknown", 0.0
            
            test_encoding = test_encodings[0]
            
            # Comparar contra todos los encodings conocidos
            # Devuelve distancias euclidianas normalizadas (0-1)
            face_distances = face_recognition.face_distance(
                known_encodings,
                test_encoding
            )
            
            # Encontrar la mejor coincidencia
            best_match_index = np.argmin(face_distances)
            best_distance = face_distances[best_match_index]
            
            # Verificar si está dentro de la tolerancia
            if best_distance <= tolerance:
                name = known_names[best_match_index]
                # Convertir distancia a confianza (1 - distancia)
                confidence = 1 - best_distance
                return name, confidence
            else:
                return "Unknown", best_distance
                
        except Exception as e:
            print(f"Error reconociendo rostro en {test_image_path}: {str(e)}")
            return "Unknown", 0.0
    
    def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """
        Entrena el modelo cargando encodings de fotos conocidas.
        
        Estructura de training_data:
        [
            {'name': 'Israel', 'image_path': 'fotos_conocidas/israel_3/face.jpg'},
            {'name': 'Carlos', 'image_path': 'fotos_conocidas/carlos/face.jpg'},
            ...
        ]
        
        Args:
            training_data: Lista de dicts con name e image_path
        
        Returns:
            True si el entrenamiento fue exitoso
        
        Ejemplo:
            >>> service = FaceRecognitionService()
            >>> training_data = [
            ...     {'name': 'Israel', 'image_path': 'fotos_conocidas/israel_3/face.jpg'}
            ... ]
            >>> if service.train(training_data):
            ...     print("Modelo entrenado correctamente")
        """
        try:
            for entry in training_data:
                name = entry['name']
                image_path = entry['image_path']
                
                encoding = self.encode_face(image_path)
                if encoding is not None:
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(name)
            
            return len(self.known_face_encodings) > 0
            
        except Exception as e:
            print(f"Error entrenando modelo: {str(e)}")
            return False
    
    @staticmethod
    def process_video_frame(frame: np.ndarray) -> Tuple[List[np.ndarray], List[Tuple[int, int, int, int]]]:
        """
        Procesa un frame de video para detectar rostros.
        
        Nota: Esta función redimensiona la imagen por rendimiento.
        Los coordinados se deben escalar de vuelta al tamaño original.
        
        Args:
            frame: Array numpy con un frame de video (BGR)
        
        Returns:
            Tuple con:
            - face_encodings: Lista de encodings detectados
            - face_locations: Lista de tuplas (top, right, bottom, left) de cada rostro
        
        Ejemplo:
            >>> import cv2
            >>> cap = cv2.VideoCapture(0)
            >>> ret, frame = cap.read()
            >>> encodings, locations = FaceRecognitionService.process_video_frame(frame)
            >>> for (top, right, bottom, left), encoding in zip(locations, encodings):
            ...     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        """
        try:
            # Redimensionar para procesamiento más rápido (reduce por factor de 4)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convertir BGR (OpenCV) a RGB (face_recognition)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Detectar rostros y crear encodings
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            # Escalar coordinadas de vuelta al tamaño original
            face_locations = [
                (top*4, right*4, bottom*4, left*4)
                for (top, right, bottom, left) in face_locations
            ]
            
            return face_encodings, face_locations
            
        except Exception as e:
            print(f"Error procesando frame: {str(e)}")
            return [], []
