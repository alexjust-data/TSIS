# Links de Interés - TSIS.ai v2.0

## Fecha: 2026-01-15

Este documento recopila todas las fuentes consultadas para el desarrollo de la interfaz visual basada en nodos estilo Unreal Engine Blueprints.

---

## 1. Documentación Oficial Epic Games / Unreal Engine

### Slate UI Framework (Sistema de renderizado de UI)
| URL | Descripción |
|-----|-------------|
| https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-slate-ui-architecture-in-unreal-engine | Arquitectura de Slate UI |
| https://dev.epicgames.com/documentation/en-us/unreal-engine/slate-overview-for-unreal-engine | Overview de Slate |
| https://dev.epicgames.com/documentation/en-us/unreal-engine/slate-user-interface-programming-framework-for-unreal-engine | Framework Slate |
| https://docs.unrealengine.com/4.26/en-US/ProgrammingAndScripting/Slate | Slate UI Framework (UE4) |
| https://docs.unrealengine.com/4.27/en-US/ProgrammingAndScripting/Slate/Architecture | Arquitectura Slate (UE4) |
| https://docs.unrealengine.com/5.3/en-US/understanding-the-slate-ui-architecture-in-unreal-engine/ | Slate Architecture (UE5.3) |

### Blueprint Visual Scripting
| URL | Descripción |
|-----|-------------|
| https://dev.epicgames.com/documentation/es-es/unreal-engine/blueprints-visual-scripting-in-unreal-engine?application_version=5.6 | Documentación principal Blueprints (ES) |
| https://dev.epicgames.com/documentation/en-us/unreal-engine/nodes-in-unreal-engine | Nodos en Unreal Engine |
| https://docs.unrealengine.com/4.26/en-US/ProgrammingAndScripting/Blueprints/UserGuide/Nodes | User Guide - Nodes (UE4) |
| https://dev.epicgames.com/documentation/en-us/unreal-engine/connecting-nodes-in-unreal-engine | Conectando nodos |
| https://docs.unrealengine.com/4.27/en-US/ProgrammingAndScripting/Blueprints/BP_HowTo/ConnectingNodes | How To - Connecting Nodes |
| https://dev.epicgames.com/documentation/en-us/unreal-engine/converting-colors-in-unreal-engine-blueprints | Conversión de colores |
| https://docs.unrealengine.com/en-US/BlueprintAPI/Math/Color/index.html | Blueprint API - Color |

---

## 2. Tutoriales y Guías de la Comunidad

### Colores de Nodos y Pins
| URL | Descripción |
|-----|-------------|
| https://mchambers.gitbook.io/unreal-engine-5-notes/unreal-engine/programming/blueprints/learning-blueprints/blueprint-node-types-and-colors | **Tipos y colores de nodos** - Muy útil |
| https://michaeljcole.github.io/wiki.unrealengine.com/Blueprint_Fundamentals/ | **Fundamentos de Blueprint** - Wiki comunidad |
| http://www.tharlevfx.com/data-types | Data Types en Blueprints |
| https://forums.unrealengine.com/t/ue4-node-lines-colour-meanings/404255 | Significado de colores de líneas |

### Slate y Creación de Nodos Custom
| URL | Descripción |
|-----|-------------|
| https://unreal-garden.com/tutorials/ui-cpp-slate/ | Tutorial Slate con C++ |
| https://forums.unrealengine.com/t/blueprint-like-slate-nodes-creation/394280 | Creación de nodos estilo Blueprint |
| https://unrealist.org/custom-blueprint-nodes/ | Guía de nodos Blueprint custom |

### Recursos GitHub
| URL | Descripción |
|-----|-------------|
| https://github.com/YawLighthouse/UMG-Slate-Compendium | Compendio UMG y Slate |
| https://github.com/Allar/ue5-style-guide | Style Guide UE5 |

---

## 3. Artículos y Referencias Académicas

| URL | Descripción |
|-----|-------------|
| https://www.researchgate.net/figure/Example-of-a-blueprint-in-UE4-Red-nodes-are-events-blue-nodes-are-functions-purple_fig2_330132411 | Paper con ejemplo de Blueprint |
| https://dannymcgee.dev/posts/unreal-engine-deserves-a-better-ui-story | Análisis crítico de UI en Unreal |
| https://techarthub.com/10-tips-for-blueprint-organization-in-unreal-engine/ | Tips organización Blueprints |

---

## 4. Información Extraída

### Colores de Headers de Nodos

| Tipo de Nodo | Color | Hex |
|--------------|-------|-----|
| Event | Rojo | `#8b0000` |
| Function (Impure) | Azul | `#0066cc` |
| Function (Pure) | Verde | `#228b22` |
| Flow Control | Gris | `#4a4a4a` |
| Macro | Gris oscuro | `#333333` |

### Colores de Pins/Cables por Tipo de Dato

| Tipo de Dato | Color | Hex |
|--------------|-------|-----|
| Exec (Ejecución) | Blanco | `#ffffff` |
| Boolean | Rojo oscuro | `#8b0000` |
| Integer | Cian | `#00ced1` |
| Float | Verde lima | `#32cd32` |
| String | Magenta | `#ff00ff` |
| Vector | Amarillo/Dorado | `#ffd700` |
| Rotator | Azul claro | `#87ceeb` |
| Transform | Naranja | `#ffa500` |
| Object | Azul | `#4169e1` |
| Name | Violeta | `#9370db` |

---

## 5. Tecnología de Renderizado

### ¿Cómo renderiza Unreal Engine los Blueprints?

**Slate** es el framework de UI propio de Unreal Engine:

- Escrito en **C++**
- Renderiza **directamente en la GPU** usando shaders
- Es **independiente de plataforma**
- Pre-data a UMG (Unreal Motion Graphics)
- Los nodos del Blueprint Editor son widgets `SGraphNode`
- Usa el **Slate Renderer** que se integra con el pipeline de renderizado 3D

### Equivalencias Web

| Unreal (Nativo) | Web Equivalent | Calidad |
|-----------------|----------------|---------|
| Slate + GPU | PixiJS / WebGL | ~80% |
| Slate + GPU | Three.js / WebGL | ~80% |
| Slate + GPU | WebGPU | ~90% |
| Slate + GPU | CSS/DOM | ~30% |

---

## 6. Imágenes de Referencia Locales

| Archivo | Descripción |
|---------|-------------|
| `C:\TSIS_Data\00_CTO\arquitectura\nodos\ungine\002.png` | Screenshot Unreal Blueprints |
| `C:\TSIS_Data\00_CTO\arquitectura\nodos\ungine\008.png` | Nodos con colores variados |
| `C:\TSIS_Data\999.png` | Nodos con cables magenta (strings) |

---

## 7. Documentos Internos del Proyecto

| Archivo | Contenido |
|---------|-----------|
| `C:\TSIS_Data\v1\SESSION_LOG.md` | Log de desarrollo v1 |
| `C:\TSIS_Data\00_CTO\TSIS_Node_Based_Architecture.md` | Arquitectura de nodos TSIS |
| `C:\TSIS_Data\00_CTO\arquitectura\nodos\oro.md` | Especificación "estándar de oro" |

---

## 8. Búsquedas Realizadas

```
1. "Unreal Engine Slate UI framework blueprint nodes rendering technology"
2. "Unreal Engine Blueprint node colors pin types visual reference"
3. "Unreal Engine Blueprint wire color boolean red integer cyan float green string magenta"
```

---

## Notas

- La documentación oficial de Epic Games tiene páginas muy extensas que dificultan el scraping automático
- Los colores exactos se obtuvieron principalmente de la wiki de la comunidad y las imágenes de referencia
- Slate no tiene equivalente directo en web; PixiJS con WebGL es la aproximación más cercana
