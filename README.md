> **Nota:** Este README fue recortado para dejar solo lo que usamos en este
> proyecto (Ollama local). La documentación completa original de Microsoft
> Agent Framework (instalación, Foundry, .NET, Go, troubleshooting general,
> etc.) se movió a [`README.backup.md`](./README.backup.md).

# RECOMENDACION DEL INGE LEGENDARIO

Cómo correr un agente localmente usando **Ollama nativo** (sin Docker) y el
sample en Python, en lugar de la alternativa con Docker descrita más abajo.
Todo el modelo corre en tu propia máquina, sin depender de GPU ni de un
contenedor.

```sh
# 1. Instala Ollama de forma nativa en Windows (gestor de modelos local).
#    Esto instala el binario `ollama` y lo registra como servicio en el
#    puerto 11434 (http://localhost:11434).
winget install --exact --id Ollama.Ollama

# 2. Descarga el modelo llama3.2 (~2 GB) al disco local. Es necesario
#    para poder usarlo vía la API de Ollama (no hace falta `ollama run`,
#    eso solo serviría para chatear por CLI de forma interactiva).
ollama pull llama3.2

# 3. Instala el paquete de Python que conecta Agent Framework con Ollama
#    (expone la clase OllamaChatClient usada en el sample).
pip install agent-framework-ollama

# 4. Indica al sample qué modelo usar. OllamaChatClient lee esta variable
#    de entorno; si no se define, usa un modelo por defecto que puede no
#    estar descargado.
$env:OLLAMA_MODEL="llama3.2"

# 5. Entra a la carpeta del sample de Ollama en Python.
cd "C:\Users\User\OneDrive\Desktop\agent-framework\python\samples\02-agents\providers\ollama"

# 6. Ejecuta el sample: crea un agente con una herramienta (tool call)
#    que responde la hora de una ciudad, primero en modo "non-streaming"
#    (respuesta completa de una vez) y luego en modo "streaming"
#    (respuesta en pedazos conforme se genera).
python ollama_agent_basic.py
```

> **Nota:** si `ollama pull` falla o el modelo no se encuentra al correr el
> sample (`model 'llama3.2' not found`), corre `ollama list` para confirmar
> qué modelos están realmente descargados y repite el `ollama pull`.

## Alternativa: Ollama con Docker

Si prefieres no instalar Ollama directamente en Windows (por ejemplo, para
mantener tu máquina "limpia", aislar versiones, o correrlo igual en Linux/Mac
sin cambiar los comandos), puedes usar el contenedor oficial de Ollama en
lugar del binario nativo.

```sh
# 1. (Opcional) Elimina un contenedor previo con el mismo nombre si ya
#    existe, para evitar el error "container name already in use".
docker rm -f ollama

# 2. Levanta el contenedor de Ollama en modo CPU-only (sin --gpus=all).
#    -v monta un volumen local para persistir los modelos descargados
#    fuera del contenedor (si se borra el contenedor, no pierdes los
#    modelos). -p expone el puerto 11434 igual que la instalación nativa.
docker run -d -v "c:\temp\ollama:/root/.ollama" -p 11434:11434 --name ollama ollama/ollama

# 3. Descarga un modelo dentro del contenedor. Aquí con gpt-oss (~13 GB)
#    en vez de llama3.2, pero puede ser cualquier modelo soportado.
docker exec -it ollama ollama pull gpt-oss

# 4. El resto es igual que con la instalación nativa: configura la
#    variable de entorno con el nombre del modelo descargado y corre
#    el sample (Ollama sigue respondiendo en localhost:11434, el
#    sample no sabe ni le importa si es nativo o Docker).
$env:OLLAMA_MODEL="gpt-oss"
cd "C:\Users\User\OneDrive\Desktop\agent-framework\python\samples\02-agents\providers\ollama"
python ollama_agent_basic.py
```

### Nativo vs. Docker: ¿cuál conviene?

| | **Nativo (winget)** | **Docker** |
|---|---|---|
| **Rendimiento** | Más rápido: usa GPU/CPU directo, sin capa de virtualización extra | Más lento en Windows, sobre todo sin GPU (WSL2 agrega overhead); usar `--gpus=all` requiere drivers NVIDIA + WSL configurados correctamente |
| **Soporte GPU** | Directo si tienes drivers instalados | Requiere Docker Desktop + WSL2 + drivers NVIDIA para contenedores; propenso a errores como el que ya vimos (`WSL environment detected but no adapters were found`) |
| **Aislamiento** | Corre como servicio del sistema, comparte entorno con el resto de tu máquina | Aislado del sistema operativo; fácil de borrar/reinstalar sin dejar rastro (`docker rm -f ollama`) |
| **Portabilidad** | Instalación específica por SO (winget es solo Windows) | Mismos comandos en Windows/Linux/Mac, útil si el equipo tiene máquinas distintas |
| **Simplicidad** | Un solo paso de instalación, Ollama queda disponible globalmente en la terminal | Requiere Docker Desktop corriendo de fondo y gestionar el contenedor (start/stop/rm) |
| **Uso de disco** | Modelos en `~/.ollama` directo | Modelos en volumen montado (`c:\temp\ollama`), mismo tamaño pero depende de que el volumen no se borre |

**Recomendación:** para desarrollo local en Windows con buen hardware, usa la
instalación **nativa** (más simple y rápida). Usa **Docker** solo si necesitas
reproducibilidad entre distintos sistemas operativos/máquinas, o si por
política no puedes instalar software directo en el SO.
