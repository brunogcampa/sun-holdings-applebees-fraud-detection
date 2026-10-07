# Sun Holdings × Databricks — Applebee's

Estructura inicial del proyecto para identificar patrones sospechosos de descuentos y propinas y priorizar su revisión. Una anomalía no constituye evidencia de fraude.

## Estado

Este repositorio contiene la organización y documentación inicial. El pipeline, los análisis, las pruebas y los dashboards están pendientes de implementación.

## Estructura

```text
sun-holdings-applebees-fraud-detection/
├── README.md
├── .gitignore
├── docs/
├── notebooks/
├── src/
├── sql/
├── tests/
├── dashboards/
└── config/
```

## Flujo previsto

Datos de origen → Bronze → Silver validada → Gold con métricas y señales → Dashboard y cola de revisión.

## Datos

Los JSON originales de `Applebees_Clean_Dataset/dimensions/` y `Applebees_Clean_Dataset/facts/` se mantienen fuera del repositorio. Configurar su ruta de acceso en el entorno de Databricks antes de implementar la ingestión.

No publicar datos transaccionales, información de empleados, credenciales ni exportaciones con información sensible. Los documentos originales del reto se conservan en `Additional_Information/`, fuera del repositorio.

## Reglas que deben preservarse

- Validar la clave candidata `BusinessDate + LocationId + Check.Id` antes de adoptarla.
- Un `Void` representa cancelación y no implica fraude por sí solo.
- Los valores negativos de `Payments.Gratuity` son normales en este dataset; no invertir el signo automáticamente.
- No inferir categorías internas de `DiscountId` a partir de promociones públicas.
- Distinguir hechos confirmados, observaciones, hipótesis, supuestos y recomendaciones.

## Próximos pasos

1. Definir configuración de acceso a datos y contratos de esquema.
2. Implementar ingestión Bronze, normalización Silver y controles de calidad.
3. Definir y validar métricas de descuentos y propinas.
4. Construir tablas Gold, señales explicables y una cola de revisión.
5. Crear dashboards y documentar resultados y recomendaciones.
