### 2.3.1 Requerimientos del producto

#### 2.3.1.1 Requerimientos Funcionales (Capacidades de la Herramienta)

Estos requerimientos definen qué debe ser capaz de hacer la aplicación para el usuario final.


| ID         | Requerimiento                                      | Descripción                                                                                                                                                                                                             | Prioridad | Usuarios Clave       |
| :----------- | :--------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------- | :--------------------- |
| **RF-001** | **Búsqueda y Filtrado de Partners**               | Permitir la búsqueda de partners por:**Nombre**, **Industria**, **Territorio/Geografía** (país, región), **Segmento de Cliente** (Enterprise, Mid Market, Territory).                                                | Alta      | Todos                |
| **RF-002** | **Generación de un Score Compuesto**              | La herramienta debe calcular y mostrar un**"Partner Score"** único que combine  las métricas (foco de industria, relacionamiento, etc.). El score debe ser configurable.                                               | Alta      | Todos                |
| **RF-003** | **Recomendación Contextual**                      | Permitir al usuario introducir un**contexto de búsqueda** (Ej: "Cliente X" o "Industria Telco en Colombia") y obtener una lista de los partners más adecuados ordenados por su *Partner Score* contextual.             | Alta      | Equipos de Ventas    |
| **RF-004** | **Visualización de Perfil Detallado**             | Al seleccionar un partner, mostrar un perfil completo con todas las métricas usadas en el*score*, incluyendo información demográfica, historial de ventas, certificaciones, y las nuevas variables de valor.          | Media     | Ventas, Partner Mgmt |
| **RF-005** | **Identificación de Potenciales Nuevos Partners** | La herramienta debe incluir y puntuar**canales no-partners actuales** de Red Hat, basándose en la información de la industria/mercado para expandir la red de aliados.                                                 | Media     | Ventas, Marketing    |
| **RF-006** | **Explicabilidad del Score**                       | El usuario debe poder ver un desglose simple que explique**por qué** un partner obtuvo un *score* alto o bajo (Ej: "Puntuación alta por Foco de Industria (8/10), Puntuación media por Histórico de Ventas (5/10)"). | Alta      | Todos                |

---

#### 2.3.1.2. Requerimientos No Funcionales (Calidad y Despliegue)


| ID          | Requerimiento               | Descripción                                                                                                                                                                  |
| :------------ | :---------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **RNF-001** | **Rendimiento**             | La herramienta debe generar el*Partner Score* y mostrar los resultados de la búsqueda en menos de 3 segundos.                                                                |
| **RNF-002** | **Actualización de Datos** | El modelo de datos subyacente y los scores deben estar en la capacidad de actualizarse una vez actualizadas las fuentes de datos para reflejar los cambios en el rendimiento. |
| **RNF-003** | **Seguridad y Acceso**      | El acceso debe estar restringido únicamente a los usuarios internos autorizados (Ventas, Partner Management, Marketing).                                                     |
| **RNF-004** | **Escalabilidad**           | La solución debe ser capaz de manejar un incremento del 50% en el volumen de partners y usuarios en los próximos 18 meses sin degradar el rendimiento.                      |

### 2.3.2 Diseño del producto

![Diseno preliminar del Partner Score](docs/diseno.png)
**Archivo editable:** [Abrir archivo .excalidraw para editar](docs/diseno.excalidraw)
