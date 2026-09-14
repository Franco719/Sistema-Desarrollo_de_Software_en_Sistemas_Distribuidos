# Sistema de Gestión de Proyectos para ONG

Sistema distribuido desarrollado para la gestión y coordinación de proyectos de organizaciones no gubernamentales (ONG).

El sistema permite que las organizaciones se registren, gestionen sus proyectos y participen en iniciativas de otras organizaciones, facilitando la colaboración y el seguimiento de los recursos y etapas involucrados en cada proyecto.

El proyecto fue desarrollado en el marco de la asignatura **Desarrollo de Software en Sistemas Distribuidos**.

---

## Descripción

La aplicación busca centralizar la gestión de proyectos colaborativos entre ONG.

Una organización puede crear un proyecto, definir sus diferentes etapas y establecer los aportes necesarios para llevarlo adelante. A su vez, otras organizaciones pueden consultar los proyectos disponibles y colaborar con ellos mediante los aportes requeridos.

La coordinación del ciclo de vida de los proyectos se encuentra modelada mediante un proceso **BPMN**, implementado utilizando **Bonita Studio**.

De esta manera, la aplicación combina una arquitectura web con un motor de gestión de procesos de negocio (BPM), permitiendo separar la lógica de gestión de los proyectos de la ejecución y coordinación de sus procesos.

---

## Funcionalidades principales

### Gestión de organizaciones

- Registro y autenticación de organizaciones.
- Identificación de la ONG responsable de cada proyecto.
- Gestión de la información asociada a las organizaciones.

### Gestión de proyectos

Las organizaciones pueden crear y administrar proyectos indicando, entre otros datos:

- Nombre del proyecto.
- Organización responsable.
- Fecha de inicio.
- Fecha de finalización.
- Plan económico.
- Etapas que componen el proyecto.

### Gestión de etapas

Cada proyecto puede estar compuesto por múltiples etapas.

Las etapas permiten definir:

- Nombre de la etapa.
- Aporte requerido.
- Cantidad de aportes necesarios.
- Cantidad de aportes recibidos.
- Si la etapa requiere colaboración externa.

El sistema permite realizar un seguimiento de la cobertura de los aportes necesarios para cada etapa.

### Colaboración entre ONG

Las organizaciones pueden inspeccionar proyectos disponibles y colaborar con aquellos que requieren ayuda.

Esto permite modelar un escenario donde distintas ONG participan de proyectos que no necesariamente son propios, aportando los recursos necesarios para completar sus etapas.

---

## Arquitectura

El sistema está compuesto principalmente por dos partes:

```text
┌───────────────────────────┐
│       Aplicación Web      │
│          Django           │
└─────────────┬─────────────┘
              │
              │ API / integración
              ▼
┌───────────────────────────┐
│       Bonita BPM          │
│     Motor de procesos     │
└─────────────┬─────────────┘
              │
              │ Proceso BPMN
              ▼
┌───────────────────────────┐
│ Gestión del ciclo de vida │
│       del proyecto        │
└───────────────────────────┘

              │
              ▼
┌───────────────────────────┐
│       PostgreSQL          │
│      Persistencia         │
└───────────────────────────┘
```

La aplicación web se encarga de la interacción con los usuarios y de la gestión de los datos propios del sistema.

**Bonita** se utiliza para modelar y ejecutar el proceso de negocio encargado de coordinar el flujo de los proyectos.

**PostgreSQL** se utiliza como sistema de gestión de base de datos para la persistencia de la información de la aplicación.

---

## Gestión de procesos con BPMN

Una de las características principales del sistema es la incorporación de un proceso de negocio modelado mediante **BPMN (Business Process Model and Notation)**.

El proceso permite coordinar el ciclo de vida de un proyecto y las diferentes etapas que lo componen.

El modelo BPMN se encuentra dentro del directorio:

```text
01-modelo-de-proceso/
```

El proceso fue desarrollado utilizando **Bonita Studio** y posteriormente integrado con la aplicación Django.

La utilización de BPMN permite representar explícitamente el flujo de trabajo y separar la coordinación del proceso de negocio de la implementación tradicional de la aplicación.

---

## Tecnologías utilizadas

### Backend

- Python
- Django
- Django REST Framework
- PostgreSQL

### Gestión de procesos

- Bonita
- Bonita Studio
- BPMN

### Comunicación

- API REST
- JSON
- Autenticación mediante tokens

### Herramientas

- Git
- GitHub
- Poetry
- DBeaver

---

## Integración Django - Bonita

La aplicación Django se comunica con Bonita para iniciar y consultar procesos asociados a los proyectos.

El flujo general puede representarse de la siguiente manera:

```text
Usuario
   │
   ▼
Django
   │
   │ Crear / gestionar proyecto
   ▼
Bonita
   │
   │ Ejecutar proceso BPMN
   ▼
Gestión del proyecto
   │
   ▼
Django / PostgreSQL
```

Esta integración permite utilizar Django como aplicación de gestión y Bonita como motor encargado de la ejecución del proceso de negocio.

---

## Objetivo académico

El proyecto tuvo como objetivo aplicar conceptos relacionados con el desarrollo de **sistemas distribuidos**, integrando diferentes tecnologías y componentes para construir una aplicación de gestión de proyectos.

Entre los conceptos trabajados se encuentran:

- Arquitectura distribuida.
- Comunicación entre servicios.
- APIs REST.
- Persistencia de datos.
- Gestión de procesos de negocio.
- Modelado BPMN.
- Integración entre aplicaciones.
- Autenticación y autorización.
- Separación de responsabilidades entre componentes.

---

## Bonita

El modelo de proceso utilizado por el sistema se encuentra en:

```text
01-modelo-de-proceso/
```

El proceso debe ser importado/ejecutado mediante **Bonita Studio** y configurado para que la aplicación Django pueda comunicarse con el servidor Bonita.

---

## Estado del proyecto

Proyecto académico desarrollado como trabajo práctico para la asignatura:

**Desarrollo de Software en Sistemas Distribuidos**

El sistema se encuentra implementado como una aplicación funcional que integra una aplicación web, persistencia de datos y un motor BPM para la coordinación de procesos de negocio.