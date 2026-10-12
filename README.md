![Microsoft Agent Framework](docs/assets/readme-banner.png)

# Welcome to Microsoft Agent Framework!

[![Microsoft Foundry Discord](https://dcbadge.limes.pink/api/server/b5zjErwbQM?style=flat)](https://discord.gg/b5zjErwbQM)
[![MS Learn Documentation](https://img.shields.io/badge/MS%20Learn-Documentation-blue)](https://learn.microsoft.com/en-us/agent-framework/)
[![PyPI](https://img.shields.io/pypi/v/agent-framework)](https://pypi.org/project/agent-framework/)
[![NuGet](https://img.shields.io/nuget/v/Microsoft.Agents.AI)](https://www.nuget.org/profiles/MicrosoftAgentFramework/)
[![GitHub stars](https://img.shields.io/github/stars/microsoft/agent-framework?style=social)](https://github.com/microsoft/agent-framework)


Microsoft Agent Framework (MAF) is an open, multi-language framework for building **production-grade AI agents and multi-agent workflows** in **.NET and Python**.

Microsoft Agent Framework is built for teams taking agents from prototype to production. It provides a consistent foundation for building, orchestrating, and operating agent systems across Python, .NET and Go, while keeping architecture choices open as requirements evolve, and supports a broad ecosystem including Microsoft Foundry, Azure OpenAI, OpenAI, and the GitHub Copilot SDK, with samples and hosting patterns for both local development and cloud deployment.

> [!NOTE]
> For the Go SDK, including its documentation, samples, contribution guidance, and issue tracker, visit [microsoft/agent-framework-go](https://github.com/microsoft/agent-framework-go/).

<p align="center">
  <a href="https://www.youtube.com/watch?v=AAgdMhftj8w" title="Watch the full Agent Framework introduction (30 min)">
    <img src="https://img.youtube.com/vi/AAgdMhftj8w/hqdefault.jpg"
         alt="Watch the full Agent Framework introduction (30 min)" width="480">
  </a>
</p>
<p align="center">
  <a href="https://www.youtube.com/watch?v=AAgdMhftj8w">
    Watch the full Agent Framework introduction (30 min)
  </a>
</p>

## Is this the right framework for you?

MAF is a strong fit if you:
- are building agents and workflows you expect to run in production,
- need orchestration beyond a single prompt or stateless chat loop,
- want graph-based patterns such as sequential, concurrent, handoff, and group collaboration,
- care about durability, restartability, observability, governance, or human-in-the-loop control,
- need provider flexibility so your architecture can evolve without major rewrites.

## Key Features
Explore new MAF capabilities and real implementation patterns on the [official blog](https://devblogs.microsoft.com/agent-framework/).

- **Python and C#/.NET Support**: Full framework support for both Python and C#/.NET implementations with consistent APIs
  - [Python packages](./python/packages/) | [.NET source](./dotnet/src/)
- **Go Support**: For the Go SDK, including its documentation, samples, contribution guidance, and issue tracker, visit [microsoft/agent-framework-go](https://github.com/microsoft/agent-framework-go/).
- **Multiple Agent Provider Support**: Support for various LLM providers with more being added continuously
  - [Python examples](./python/samples/02-agents/providers/) | [.NET examples](./dotnet/samples/02-agents/AgentProviders/)
- **Middleware**: Flexible middleware system for request/response processing, exception handling, and custom pipelines
  - [Python middleware](./python/samples/02-agents/middleware/) | [.NET middleware](./dotnet/samples/02-agents/Agents/Agent_Step11_Middleware/)
- **Orchestration Patterns & Workflows**: Build multi-agent systems with graph-based workflows supporting sequential, concurrent, handoff, and group collaboration patterns; includes checkpointing, streaming, human-in-the-loop, and time-travel
  - [Python workflows](./python/samples/03-workflows/) | [.NET workflows](./dotnet/samples/03-workflows/)
- **Foundry Hosted Agents (new)**: Deploy and host your agents to Foundry-hosted infrastructure with just 2 additional lines of code
  - [Python samples](./python/samples/04-hosting/foundry-hosted-agents/) | [.NET samples](./dotnet/samples/04-hosting/FoundryHostedAgents/)
- **Observability**: Built-in OpenTelemetry integration for distributed tracing, monitoring, and debugging
  - [Python observability](./python/samples/02-agents/observability/) | [.NET telemetry](./dotnet/samples/02-agents/AgentOpenTelemetry/)
- **Declarative Agents**: Define agents using YAML for faster setup and versioning
  - [Declarative agent samples](./declarative-agents/)
- **Agent Skills**: Build domain-specific knowledge bases from multiple sources—files, inline code, class libraries—for agents to discover and use
  - [Skills design](./docs/decisions/0037-agent-skills-design.md)
- **AF Labs**: Experimental packages for cutting-edge features including benchmarking, reinforcement learning, and research initiatives
  - [Labs directory](./python/packages/lab/)
- **DevUI**: Interactive developer UI for agent development, testing, and debugging workflows
  - [See the DevUI in action](https://www.youtube.com/watch?v=mOAaGY4WPvc)

## Table of Contents

- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Learning Resources](#learning-resources)
  - [Quickstart](#quickstart)
    - [Basic Agent - Python](#basic-agent---python)
    - [Basic Agent - .NET](#basic-agent---net)
- [More Examples & Samples](#more-examples--samples)
- [Community & Feedback](#community--feedback)
- [Troubleshooting](#troubleshooting)
- [Contributor Resources](#contributor-resources)

## Getting Started
### Installation
Python

```bash
pip install agent-framework
# This installs the standard package set; install `agent-framework-lab` separately for experimental modules.
# It may take a minute on first install on Windows.
```

.NET

```bash
dotnet add package Microsoft.Agents.AI
# For Foundry integration (used in the .NET quickstart below):
dotnet add package Microsoft.Agents.AI.Foundry
dotnet add package Azure.AI.Projects
dotnet add package Azure.Identity
```

### Learning Resources

- **[Overview](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview)** - High level overview of the framework
- **[Quick Start](https://learn.microsoft.com/agent-framework/tutorials/quick-start)** - Get started with a simple agent
- **[Tutorials](https://learn.microsoft.com/agent-framework/tutorials/overview)** - Step by step tutorials
- **[User Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/overview)** - In-depth user guide for building agents and workflows
- **[Migration from Semantic Kernel](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel)** - Guide to migrate from Semantic Kernel
- **[Migration from AutoGen](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen)** - Guide to migrate from AutoGen

### Quickstart

#### Basic Agent - Python

Create a simple Azure Responses Agent that writes a haiku about the Microsoft Agent Framework

```python
# pip install agent-framework
# Use `az login` to authenticate with Azure CLI
import os
import asyncio
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


async def main():
    # Initialize a chat agent with Microsoft Foundry
    # the endpoint, deployment name, and api version can be set via environment variables
    # or they can be passed in directly to the FoundryChatClient constructor
    agent = Agent(
      client=FoundryChatClient(
          credential=AzureCliCredential(),
          # project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
          # model=os.environ["FOUNDRY_MODEL"],
      ),
      name="HaikuAgent",
      instructions="You are an upbeat assistant that writes beautifully.",
    )

    print(await agent.run("Write a haiku about Microsoft Agent Framework."))

if __name__ == "__main__":
    asyncio.run(main())
```

#### Basic Agent - .NET
Create a simple Agent, using Microsoft Foundry that writes a haiku about the Microsoft Agent Framework

```c#
// This sample shows how to create and run a basic agent with AIProjectClient.AsAIAgent(...).

using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Agents.AI;

string endpoint = Environment.GetEnvironmentVariable("AZURE_AI_PROJECT_ENDPOINT") ?? throw new InvalidOperationException("AZURE_AI_PROJECT_ENDPOINT is not set.");
string deploymentName = Environment.GetEnvironmentVariable("AZURE_AI_MODEL_DEPLOYMENT_NAME") ?? "gpt-5.4-mini";

AIAgent agent =
    new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential())
    .AsAIAgent(model: deploymentName, instructions: "You are an upbeat assistant that writes beautifully.", name: "HaikuAgent");

// Once you have the agent, you can invoke it like any other AIAgent.
Console.WriteLine(await agent.RunAsync("Write a haiku about Microsoft Agent Framework."));
```

## More Examples & Samples

### Python

- [Getting Started](./python/samples/01-get-started): progressive tutorial from hello-world to workflows
- [Agent Concepts](./python/samples/02-agents): deep-dive samples by topic (tools, middleware, providers, etc.)
- [Workflows](./python/samples/03-workflows): workflow creation and integration with agents
- [Hosting](./python/samples/04-hosting): A2A, self-hosted protocol helpers, and Foundry hosted agents. Durable Task and Azure Functions samples are in the [Durable Agent Framework extension](https://github.com/microsoft/agent-framework-durable-extension/tree/main/python/samples).
- [End-to-End](./python/samples/05-end-to-end): full applications, evaluation, and demos

### .NET

- [Getting Started](./dotnet/samples/01-get-started): progressive tutorial from hello agent to workflows
- [Agent Concepts](./dotnet/samples/02-agents/Agents): basic agent creation and tool usage
- [Agent Providers](./dotnet/samples/02-agents/AgentProviders): samples showing different agent providers
- [Workflows](./dotnet/samples/03-workflows): advanced multi-agent patterns and workflow orchestration
- [Hosting](./dotnet/samples/04-hosting): A2A and Foundry hosted agents. Durable agent and workflow samples are in the [Durable Agent Framework extension](https://github.com/microsoft/agent-framework-durable-extension/tree/main/dotnet/samples).
- [End-to-End](./dotnet/samples/05-end-to-end): full applications and demos

## Community & Feedback

- **Found a bug?** File a [GitHub issue](https://github.com/microsoft/agent-framework/issues) to help us improve.
- **Enjoying MAF?** [![GitHub stars](https://img.shields.io/badge/Star-us%20on%20GitHub-yellow)](https://github.com/microsoft/agent-framework) to show your support and help others discover the project.
- **Have questions?** Join our [Discord](https://discord.gg/b5zjErwbQM) or visit [weekly office hours](./COMMUNITY.md#public-community-office-hours).

## Troubleshooting

### Authentication

| Problem | Cause | Fix |
|---------|-------|-----|
| Authentication errors when using Azure credentials | Not signed in to Azure CLI | Run `az login` before starting your app |
| API key errors | Wrong or missing API key | Verify the key and ensure it's for the correct resource/provider |

> **Tip:** `DefaultAzureCredential` is convenient for development but in production, consider using a specific credential (e.g., `ManagedIdentityCredential`) to avoid latency issues, unintended credential probing, and potential security risks from fallback mechanisms.

### Environment Variables
For environment variable configuration specific to each sample, refer to the README in the sample directory ([Python samples](./python/samples/) | [.NET samples](./dotnet/samples/)).

## Contributor Resources

- [Contributing Guide](./CONTRIBUTING.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Python Development Guide](./python/DEV_SETUP.md)
- [Design Documents](./docs/design)
- [Architectural Decision Records](./docs/decisions)

## Important Notes

> [!IMPORTANT]
> If you use Microsoft Agent Framework to build applications that operate with any third-party servers, agents, code, or non-Azure Direct models (“Third-Party Systems”), you do so at your own risk. Third-Party Systems are Non-Microsoft Products under the Microsoft Product Terms and are governed by their own third-party license terms. You are responsible for any usage and associated costs.
>
>We recommend reviewing all data being shared with and received from Third-Party Systems and being cognizant of third-party practices for handling, sharing, retention and location of data. It is your responsibility to manage whether your data will flow outside of your organization’s Azure compliance and geographic boundaries and any related implications, and that appropriate permissions, boundaries and approvals are provisioned.
>

# RECOMENDACION DEL INGE LEGENDARIO

Cómo correr un agente localmente usando **Ollama nativo** (sin Docker) y el
sample en Python, en lugar de la ruta con Docker/.NET descrita más arriba.
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
