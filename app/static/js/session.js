console.log("Session script loaded correctly");

// Obtener el ID del curso desde la URL (asumiendo /admin/course/X/session)
// O puedes ponerlo en un <input type="hidden" id="courseId" value="{{ course_id }}"> en el HTML
const pathSegments = window.location.pathname.split('/');
const courseId = pathSegments[pathSegments.indexOf('course') + 1];

// Referencias DOM
const video = document.getElementById("videoFeed");
const btnStart = document.getElementById("btnStart");
const btnStop = document.getElementById("btnStop");
const tableBody = document.querySelector("table tbody"); // Asegúrate de que tu tabla tenga un tbody

// --- 1. CARGA DE DATOS (Independiente de la cámara) ---
async function loadAttendanceList() {
    try {
        console.log("Cargando lista de asistencia...");
        // Usamos la API de asistencia que ya creaste en el backend
        const response = await fetch(`/api/admin/courses/${courseId}/attendance`);
        
        if (!response.ok) throw new Error("Error al cargar datos");
        
        const data = await response.json();
        renderTable(data.data);
    } catch (error) {
        console.error("Error:", error);
        // Si falla la API de asistencia (quizás es la primera vez), intentamos cargar solo estudiantes
        loadStudentsFallback(); 
    }
}

// Fallback: Si no hay registros de asistencia hoy, cargamos la lista de estudiantes base
async function loadStudentsFallback() {
    try {
        const response = await fetch(`/api/admin/courses/${courseId}/students`);
        const data = await response.json();
        // Transformamos formato estudiante a formato asistencia visual (status 'pendiente')
        const students = data.data.map(s => ({
            id: null, // No hay ID de asistencia aún
            student_id: s.id,
            student_name: `${s.first_name} ${s.last_name}`,
            status: 'ausente', // Por defecto
            profile_photo_url: s.profile_photo_url
        }));
        renderTable(students);
    } catch (err) {
        console.error("Error fatal cargando estudiantes:", err);
        if(tableBody) tableBody.innerHTML = `<tr><td colspan="4" class="text-center text-danger">Error cargando lista</td></tr>`;
    }
}

function renderTable(records) {
    if (!tableBody) return;
    tableBody.innerHTML = ""; // Limpiar tabla

    records.forEach(record => {
        // Definir colores según estado
        let badgeClass = "secondary";
        if (record.status === "presente") badgeClass = "success";
        else if (record.status === "tardanza") badgeClass = "warning";
        else if (record.status === "falta" || record.status === "ausente") badgeClass = "danger";
        else if (record.status === "salida_repentina") badgeClass = "dark";

        const row = `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar mr-2">
                             <img src="${record.profile_photo_url || 'https://ui-avatars.com/api/?name=' + record.student_name}" class="img-profile rounded-circle" style="width: 40px; height: 40px;">
                        </div>
                        <div>${record.student_name}</div>
                    </div>
                </td>
                <td>
                    <span class="badge badge-${badgeClass}">${record.status.toUpperCase()}</span>
                </td>
                <td>${record.entry_time || '--:--'}</td>
                <td>
                    <button class="btn btn-success btn-sm btn-action" data-student-id="${record.student_id}" data-status="presente" title="Presente"><i class="fas fa-check"></i></button>
                    <button class="btn btn-warning btn-sm btn-action" data-student-id="${record.student_id}" data-status="tardanza" title="Tardanza"><i class="fas fa-clock"></i></button>
                    <button class="btn btn-danger btn-sm btn-action" data-student-id="${record.student_id}" data-status="falta" title="Falta"><i class="fas fa-times"></i></button>
                </td>
            </tr>
        `;
        tableBody.insertAdjacentHTML('beforeend', row);
    });
}

// --- 2. CÁMARA (Lógica original) ---
if (btnStart) {
    btnStart.addEventListener("click", async function() {
        try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
                video.play();
                // Aquí podrías agregar un setInterval para enviar frames al backend
            } else {
                alert("No se puede acceder a la cámara.");
            }
        } catch (err) {
            alert("Error cámara: " + err.message);
        }
    });
}

if (btnStop) {
    btnStop.addEventListener("click", function() {
        if (video && video.srcObject) {
            video.pause();
            video.srcObject.getTracks().forEach(track => track.stop());
            video.srcObject = null;
        }
    });
}

// --- 3. ASISTENCIA MANUAL (Delegación de Eventos) ---
// Usamos esto porque los botones se crean DINÁMICAMENTE después de cargar la página
document.addEventListener('click', function(e) {
    // Buscamos si el click fue en un botón de acción o dentro de él (icono)
    const btn = e.target.closest('.btn-action');
    
    if (btn) {
        const studentId = btn.dataset.studentId;
        const status = btn.dataset.status;
        
        // Llamada a la API para actualizar/crear asistencia
        // Nota: Tu API actual es PATCH /attendance/{id}, pero aquí tenemos student_id.
        // Deberías tener un endpoint para "Registrar asistencia por Student ID" o buscar el ID de asistencia primero.
        // Por simplicidad, simularemos el éxito visualmente:
        
        alert(`Marcando ${status} para el estudiante ${studentId} (Lógica pendiente de backend)`);
        
        // Recargar tabla para ver cambios reales (cuando conectes el backend)
        // loadAttendanceList(); 
    }
});

// --- INICIALIZACIÓN ---
document.addEventListener("DOMContentLoaded", function() {
    loadAttendanceList(); // ¡Carga la lista INMEDIATAMENTE!
});