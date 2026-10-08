# Ejecutar en Databricks Free Edition

1. Crear en Workspace/Home `Applebees_Databricks_Challenge/notebooks` e importar individualmente los tres `.ipynb` de `notebooks/import/`. No importar el ZIP de datos ni un ZIP genérico del proyecto como notebook.
2. Ejecutar `00_setup_catalog`. El catálogo `workspace` fue verificado disponible junto con `samples` y `system`; revisar la lista en cada entorno.
3. Usar **Upload to this volume** en `workspace.applebees_raw.source` para cargar el ZIP privado de datos.
4. Ejecutar `00_extract_source_data` con `archive_path=/Volumes/workspace/applebees_raw/source/applebees_source_data.zip` y `data_root=/Volumes/workspace/applebees_raw/source/applebees_source`. Debe extraer 119 JSON (115 hechos + 4 dimensiones). Si el destino existe, no sobreescribir: conservarlo o usar otra carpeta nueva.
5. Ejecutar `01_eda_applebees` desde la primera celda con `data_root` igual al destino anterior y `output_schema=workspace.applebees_eda`. Mantener las fechas del período o cambiarlas explícitamente.
6. Crear visualizaciones desde los resultados. Para porcentajes ya agregados, una fila por fecha/sucursal/código: usar Average, no sumar porcentajes. Para cambiar de granularidad, recalcular con numerador y denominador correctos.
7. Conservar el notebook HTML con outputs en la entrega privada. Compartir código, documentación y agregados en GitHub.

## Errores vistos y solución

- `NameError: ROOT/checks/coverage is not defined`: faltan celdas anteriores en la sesión, el cómputo reinició o cambió el nombre de variable. Ejecutar en orden desde la configuración; no sustituir nombres sin revisar dependencias.
- `errorifexists is not supported`: esta versión comprueba que el nombre nuevo no exista y escribe con append. No volver a ejecutar una celda de guardado con el mismo RUN. Reiniciar desde configuración crea nombres nuevos y evita duplicados.
- Error importando `applebees_databricks_workspace.zip`: usar IPYNB individuales.

No se requieren Git local ni un administrador de bases de datos para ejecutar estos notebooks desde la plataforma web. El cómputo serverless está sujeto a la disponibilidad y cuota de la cuenta.
