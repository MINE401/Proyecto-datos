# Frontend (Partner Finder)

Aplicación web para encontrar y evaluar partners basado en criterios de búsqueda y **Partner Score**.

## Características Implementadas

### ✅ Requerimientos Funcionales

- **RF-001: Búsqueda y Filtrado de Partners**
  - Búsqueda por Nombre/Cliente
  - Filtrado por País, Región, Ciudad (Territorio/Geografía)
  - Filtrado por Industria
  - Filtrado por Segmento (Enterprise, Mid Market, Territory)
  - Paginación configurable (límite de resultados)

- **RF-002 & RF-006: Partner Score y Explicabilidad**
  - Visualización del Partner Score compuesto (0-100)
  - Desglose visual de componentes del score (Foco de Industria, Relacionamiento, Histórico de Ventas, Certificaciones)
  - Barra de progreso visual con gradiente
  - Explicación clara de cada métrica individual

- **RF-004: Visualización de Perfil Detallado**
  - Vista detallada de cada partner
  - Información demográfica (país, región, ciudad, industria, segmento)
  - Histórico y métricas completas
  - JSON expandible con datos brutos

### ✅ Requerimientos No Funcionales

- **RNF-001: Rendimiento**
  - Búsquedas rápidas con proxy de desarrollo (Vite)
  - Interfaz responsiva y fluida

- **RNF-003: UI Profesional**
  - Diseño limpio y moderno
  - Accesibilidad básica
  - Compatibilidad con navegadores modernos

## Requisitos

- Node.js 18+
- npm o yarn

## Instalación

```bash
cd frontend
npm install
```

## Ejecución

### Desarrollo

```bash
# Desde la carpeta frontend
VITE_API_BASE="http://localhost:8000" npm run dev
```

Abre en el navegador: **http://localhost:3000**

### Build para producción

```bash
npm run build
```

Genera la carpeta `dist/` lista para desplegar.

### Preview de build

```bash
npm run preview
```

## Estructura del Proyecto

```
src/
├── main.jsx              # Entrypoint de la app
├── App.jsx               # Componente root
├── styles.css            # Estilos globales (responsive, cards, etc.)
├── api/
│   └── client.js         # Cliente HTTP para POST /query
├── components/
│   ├── SearchForm.jsx    # Filtros de búsqueda
│   └── CompanyList.jsx   # Grid de resultados con score visual
└── pages/
    ├── Home.jsx          # Página principal (coordinador)
    └── CompanyDetail.jsx # Vista detallada de partner
```

## Configuración de API

- **Desarrollo**: Vite proxy (automático) → `http://localhost:8000/query`
- **Producción**: Especifica `VITE_API_BASE` antes de build:
  ```bash
  VITE_API_BASE="https://api.ejemplo.com" npm run build
  ```

## Variables de Entorno

- `VITE_API_BASE`: URL base del API (default: `http://localhost:8000`)
- `VITE_SUPABASE_URL`: URL pública del proyecto Supabase (p.ej. `https://xyz.supabase.co`)
- `VITE_SUPABASE_ANON_KEY`: Clave anon/public del proyecto Supabase

Si configuras `VITE_SUPABASE_URL` y `VITE_SUPABASE_ANON_KEY`, la app intentará leer la tabla `companies` directamente desde Supabase para las acciones de `list_companies` y `search_company`. Si la consulta Supabase falla, la app volverá al endpoint `POST /query`.

## Uso de la Aplicación

1. **Búsqueda Básica**: Rellena al menos un filtro y haz clic en "🔍 Buscar"
2. **Ver Detalles**: Haz clic en cualquier card de partner
3. **Desglose del Score**: En la vista de detalle ves cada métrica individual
4. **Volver**: Botón "← Volver a resultados" para regresar a la lista

## Notas de Integración con Backend

- La app espera un endpoint `POST /query` que acepte payloads de búsqueda
- Formatos de respuesta soportados: `[...]`, `{results: [...]}`, `{items: [...]}`, `{data: [...]}`
- El score se busca en: `score`, `partner_score`, o se genera aleatorio (para testing)
- Si no hay datos de breakdown, se usan valores por defecto

## Vulnerabilidades y Auditoría

Se detectaron 2 vulnerabilidades moderadas en las dependencias. Para corregir:

```bash
npm audit fix --force
```

## Próximos Pasos (Opcional)

- Autenticación y autorización (RF-003 NRF-003)
- Integración real de score desde backend
- Recomendación contextual (RF-003)
- Identificación de nuevos partners (RF-005)
- Temas oscuros (Dark Mode)
- Internacionalización (i18n)
