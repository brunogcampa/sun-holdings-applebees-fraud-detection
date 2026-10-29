# Databricks notebook source
# MAGIC %md
# MAGIC # Preparar datos originales de Applebee's
# MAGIC Subir `applebees_source_data.zip` a un volumen antes de ejecutar. Este notebook extrae exclusivamente dimensions/ y facts/, conservando fechas y nombres. No comparte los datos con GitHub.

# COMMAND ----------
import os
import zipfile
from pathlib import PurePosixPath
dbutils.widgets.text("archive_path", "", "Ruta /Volumes/.../applebees_source_data.zip")
dbutils.widgets.text("data_root", "", "Nueva carpeta /Volumes/.../applebees_source")
archive = dbutils.widgets.get("archive_path")
root = dbutils.widgets.get("data_root").rstrip("/")
assert archive.startswith("/Volumes/") and root.startswith("/Volumes/")
assert os.path.isfile(archive), "Primero subir el ZIP al volumen."
assert not os.path.exists(root), "Usar una carpeta nueva: no se sobrescriben fuentes existentes."

# COMMAND ----------
with zipfile.ZipFile(archive) as source:
    entries = source.infolist()
    names = [entry.filename for entry in entries]
    assert len(names) == len(set(names)), "El archivo contiene nombres repetidos."
    for entry in entries:
        path = PurePosixPath(entry.filename)
        assert not path.is_absolute() and ".." not in path.parts and "\\" not in entry.filename
        assert path.parts[0] in {"dimensions", "facts"} and path.suffix == ".json"
        assert not entry.is_dir()
    print("Archivos:", len(entries), "Bytes originales:", sum(entry.file_size for entry in entries))
    os.makedirs(root)
    # Extracción por archivo para mostrar progreso. zipfile valida CRC al leer.
    for index, entry in enumerate(entries, 1):
        source.extract(entry, root)
        if index % 10 == 0 or index == len(entries):
            print("Extraídos:", index, "de", len(entries))

# COMMAND ----------
actual = [(os.path.relpath(os.path.join(folder, name), root).replace(os.sep, "/"), os.path.getsize(os.path.join(folder, name)))
          for folder, _, files in os.walk(root) for name in files]
expected = {(entry.filename, entry.file_size) for entry in entries}
assert set(actual) == expected, "La extracción no coincide con el manifiesto del ZIP."
print("Extracción verificada:", len(actual), "archivos en", root)
print("Usar esta ruta en data_root del notebook 01_eda_applebees.")
