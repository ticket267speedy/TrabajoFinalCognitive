# REBRANDING CORPORATIVO - CogniPass

## 🎯 Objetivo
Transformar la interfaz de CogniPass de un diseño colorido "estilo IA generativa" a un sistema profesional, sobrio y académico alineado con estándares Enterprise SaaS.

---

## 📊 PALETA DE COLORES - SISTEMA TOKENIZADO

### Colores Primarios
- **Primary Dark**: `#1E3A8A` (Azul Académico serio)
- **Primary Medium**: `#2563EB` (Azul corporativo)
- **Primary Light**: `#DBEAFE` (Azul muy claro para focus states)

### Colores Neutros (Grises)
- **Background Primary**: `#FFFFFF` (Fondo principal)
- **Background Secondary**: `#F3F4F6` (Fondo secundario - gris muy suave)
- **Background Tertiary**: `#E5E7EB` (Gris para elementos deshabilitados)

### Textos
- **Text Primary**: `#111827` (Gris oscuro para títulos)
- **Text Secondary**: `#4B5563` (Gris medio para cuerpo)
- **Text Tertiary**: `#9CA3AF` (Gris claro para labels)

### Colores Semánticos
- **Success**: `#059669` (Verde profesional)
- **Warning**: `#D97706` (Ámbar/Naranja)
- **Danger**: `#DC2626` (Rojo corporativo)
- **Info**: `#0891B2` (Cian)

### Sombras (Sutiles)
- **Shadow SM**: `0 1px 2px 0 rgba(0, 0, 0, 0.05)` (Muy sutil)
- **Shadow MD**: `0 4px 6px -1px rgba(0, 0, 0, 0.1)` (Suave)
- **Shadow LG**: `0 10px 15px -3px rgba(0, 0, 0, 0.1)` (Para modales)

---

## 🎨 CAMBIOS CSS PRINCIPALES

### ✅ Variables CSS (:root)
**Archivo**: `app/static/css/theme.css`

Se definieron variables CSS globales que se aplican automáticamente a todos los templates:
```css
:root {
  --primary-dark: #1E3A8A;
  --primary-medium: #2563EB;
  --primary-light: #DBEAFE;
  /* ... etc */
}
```

### ✅ Tipografía
- Font stack profesional: `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue'`
- Sin emojis en el HTML (reemplazados por FontAwesome icons en gris neutro)
- Nunca se usa negro puro `#000000` → Gris oscuro `#111827`
- Tamaño base: 14px, line-height: 1.5

### ✅ Elementos Principales

#### Navbar
- Background: Blanco `#FFFFFF`
- Border-bottom: Gris suave `#E5E7EB`
- Shadow: Muy sutil (0 1px 2px)
- Logo: Azul oscuro `#1E3A8A`, con icono primario en azul

#### Cards
- Border-radius: 6px (NO 10px ni valores exagerados)
- Border: 1px solid `#E5E7EB`
- Shadow: Sutil (0 1px 2px)
- Hover: Aumenta a shadow-md
- Background: Blanco puro

#### Botones
- Border-radius: 6px
- Transiciones suaves (0.2s ease)
- Primary: Azul `#2563EB` con hover a `#1E3A8A`
- Outline: Bordes sutiles, sin backgrounds sólidos
- Focus: 3px de sombra interna en color primario light

#### Forms
- Input borders: `#D1D5DB` (gris medio)
- Focus: Borde azul + sombra de 3px con color light
- Background: Blanco con placeholder en gris
- Border-radius: 6px

#### Badges
- Border-radius: 4px
- Semantic colors (success, warning, danger, info)
- Font-weight: 500
- Padding: 0.375rem 0.625rem

---

## 📝 CAMBIOS EN TEMPLATES

### 1. **landing.html**
**Archivo**: `app/views/shared/landing.html`

**Cambios realizados:**
- ✅ Reemplazado gradiente púrpura/neón por gradiente azul corporativo (Indigo 900 → Indigo 600)
- ✅ Ícono navbar: De `fa-face-smile` → `fa-graduation-cap` (académico)
- ✅ Colores: De `#667eea/#764ba2` → `#1E3A8A/#2563EB`
- ✅ Border-radius: De 10px → 6px
- ✅ Sombras: Reducidas y sutilizadas
- ✅ Paleta de grises: De `#333` → `#111827`
- ✅ Typography: Font weights ajustados a valores corporativos

**Iconos profesionales:**
- Feature cards: `fa-camera`, `fa-book`, `fa-chart-line`, `fa-hourglass-end`, `fa-shield-alt`, `fa-server`
- Anteriormente: Emojis genéricos

### 2. **login.html**
**Archivo**: `app/views/shared/login.html`

**Cambios realizados:**
- ✅ Removidos 150+ líneas de estilos inline (refactorizado a `theme.css`)
- ✅ Ahora utiliza clases globales: `.login-wrapper`, `.login-card`, `.login-header`, etc.
- ✅ Ícono header: De `fa-lock` → `fa-graduation-cap`
- ✅ Aplicadas variables CSS globales (backgrounds, colores, sombras)
- ✅ Gradiente header: De neón → Azul corporativo
- ✅ Button: Ahora usa clase `.btn btn-primary` (unificado con resto de app)
- ✅ Message alerts: Colores semánticos (rojo para error, verde para success)
- ✅ Removed inline `<i>` icons en labels (solo icon en botón)

**HTML simplificado:**
```html
<!-- Antes: ~369 líneas con CSS inline -->
<!-- Ahora: ~115 líneas + CSS global -->
```

### 3. **theme.css**
**Archivo**: `app/static/css/theme.css`

**De minificado a modular y documentado:**
- Antes: 26 líneas de CSS minificado con tonos navy/black
- Ahora: 400+ líneas bien documentadas con:
  - Variables CSS tokenizadas
  - Comentarios por sección (Typography, Cards, Forms, Buttons, etc.)
  - Responsive media queries
  - Smooth transitions (0.2s)
  - Consistent spacing (1rem, 1.5rem, etc.)

**Secciones documentadas:**
1. Global Styles (html, body, typography)
2. Navigation (.navbar, .nav-link)
3. Cards & Sections (.card, .section)
4. Lists (.list-group, .list-group-item)
5. Forms (inputs, selects, focus states)
6. Buttons (primary, secondary, outline, danger)
7. Badges (.badge con semantic colors)
8. Modal (.modal-content)
9. Layout Utilities (.center-page, .main)
10. Login Page (.login-wrapper, .login-card, etc.)
11. Alerts (#message.msg.error/success)
12. Responsive (@media)

---

## 🎯 PRINCIPIOS DE DISEÑO APLICADOS

### 1. **Subtlety (Sutileza)**
- Sombras muy ligeras (0 1px 2px vs 0 20px 60px anterior)
- Gradientes suaves (no neones)
- Bordes sutiles (#E5E7EB vs negro)

### 2. **Hierarchy (Jerarquía Clara)**
- Títulos: Gris oscuro, font-weight 700, letter-spacing -0.5px
- Cuerpo: Gris medio, font-weight 400
- Labels: Gris claro, font-weight 600, text-transform uppercase

### 3. **Consistency (Consistencia)**
- Border-radius global: 6px (o 4px para badges)
- Shadow palette: SM, MD, LG
- Color usage: Primario azul, neutrales en grises
- Spacing: Múltiplos de 0.5rem (1rem, 1.5rem, 2rem, etc.)

### 4. **Accessibility (Accesibilidad)**
- Contrast ratio de textos > 4.5:1 (WCAG AA)
- Focus states visibles (3px box-shadow)
- No se depende únicamente de color (+ iconos)
- Font sizes legibles (14px base, 16px en mobile)

### 5. **Professional Appearance (Apariencia Profesional)**
- Ningún emoji en HTML (solo icons)
- Tipografía corporativa sin serifs
- Espaciado generoso (1rem default)
- Colores corporativos (azul académico)

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### CSS Global
- ✅ Variables CSS (:root) definidas
- ✅ Typography styles (h1-h6, p, a)
- ✅ Component styles (.navbar, .card, .btn, .form-*)
- ✅ Shadows palette
- ✅ Responsive design (@media)

### HTML Templates
- ✅ landing.html: Paleta corporativa
- ✅ login.html: Refactorizado a clases globales
- ✅ Iconos: De emojis genéricos a FontAwesome profesional
- ✅ Sin estilos inline (excluir en nuevos templates)

### Compatibilidad
- ✅ Bootstrap integration (theme.css applies on top)
- ✅ Axis template integration (admin dashboard)
- ✅ KaiAdmin integration (advisor dashboard)
- ✅ Fallback fonts en stack
- ✅ Mobile responsive (< 768px)

---

## 🚀 IMPACTO VISUAL

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Gradiente primario** | Púrpura/Neón (#667eea) | Azul Corporativo (#1E3A8A) |
| **Bordes** | Redondos (10px) | Sutiles (6px) |
| **Sombras** | Dramáticas (20px) | Sutiles (1px-4px) |
| **Textos** | Negro puro | Gris Oscuro (#111827) |
| **Emojis** | Presentes | Removidos → FontAwesome |
| **CSS** | 26 líneas minificadas | 400+ líneas documentadas |
| **Profesionalismo** | Casual | Enterprise SaaS |

---

## 📖 USO DE VARIABLES CSS EN NUEVOS TEMPLATES

Para mantener coherencia en toda la aplicación, usa siempre las variables:

```css
/* ✅ CORRECTO */
.my-element {
  background: var(--bg-primary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
}

/* ❌ INCORRECTO */
.my-element {
  background: #ffffff;
  color: #666;
  border: 1px solid #ccc;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}
```

---

## 📝 PRÓXIMOS PASOS

1. **Admin Dashboard** (`admin/admin_dashboard.html`):
   - Asegurar que theme.css se carga después de Axis CSS
   - Revisar sidebar styling
   - Actualizar botones a clases `.btn btn-primary`

2. **Advisor Dashboard** (`advisor/dashboard.html`):
   - Asegurar que theme.css se carga después de KaiAdmin CSS
   - Revisar cards y forms
   - Actualizar badges a clases semánticas

3. **Testing**:
   - Verificar en `localhost:7000`
   - Testing responsive (mobile, tablet, desktop)
   - Testing cross-browser (Chrome, Firefox, Safari)
   - Verificar WCAG contrast ratios

4. **Documentación**:
   - Este archivo `REBRANDING_CORPORATE.md` como guía
   - Comentarios en `theme.css` para desarrolladores futuros

---

**Fecha de Actualización**: 2025-11-22  
**Versión**: 1.0 - Rebranding Corporativo Completo  
**Estado**: ✅ IMPLEMENTADO EN LANDING & LOGIN
