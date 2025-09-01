<h1 align="center"><b>📊 AsistenciasREST API</b></h1>
<h3 align="center">API REST robusta para la gestión de actividades extraescolares en el ITESZ</h3>

---

## 🚀 Descripción

**AsistenciasREST** es una **API REST modular** desarrollada con **FastAPI + MongoDB Atlas**, diseñada para digitalizar y optimizar el proceso de acreditación de créditos académicos en el ITESZ.  
Resuelve la problemática de control de **asistencias y actividades extraescolares**, ofreciendo una solución **escalable, segura y documentada**.

---

## 🛠️ Badges del Proyecto

<div align="center">
  
![Python](https://img.shields.io/badge/python-3.11-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=for-the-badge&logo=mongodb)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Build](https://img.shields.io/github/actions/workflow/status/Manuelillo-dev/AsistenciasREST/ci.yml?branch=master&label=Build&logo=github&style=for-the-badge)
![Coverage](https://img.shields.io/codecov/c/github/tu_usuario/AsistenciasREST?logo=codecov&style=for-the-badge)

</div>

---

## ✨ Características

- 📌 Arquitectura **orientada a dominios** (microservicios).  
- 👤 Gestión de **usuarios y roles**.  
- 📅 Administración de **actividades extraescolares**.  
- ✅ Registro y consulta de **asistencias**.  
- 🏫 Catálogos dinámicos: **grupos, ubicaciones, carreras, ciclos**.  
- 📖 Documentación interactiva con **Swagger UI**.  

---

## 🏛️ Arquitectura

El sistema está organizado en **routers independientes por dominio**:  
- `Usuarios`  
- `Actividades`  
- `Ciclos`  
- `Carreras`  
- `Grupos`  
- `Ubicaciones`  
- `Asistencias`
  ```mermaid
flowchart TD
    subgraph API[AsistenciasREST API - FastAPI]
        USR[Usuarios Router]
        ACT[Actividades Router]
        CIC[Ciclos Router]
        CAR[Carreras Router]
        GRP[Grupos Router]
        UBI[Ubicaciones Router]
        AST[Asistencias Router]
    end
    ```

     API --> DB[(MongoDB Atlas)]

👉 Esto facilita **mantenimiento, escalabilidad y despliegues independientes**.  

---

## 🛠️ Stack Tecnológico
<div align="center">
  | Componente | Tecnología | Propósito |
  |------------|------------|-----------|
  | **Framework** | FastAPI | API REST de alto rendimiento |
  | **Servidor** | Uvicorn | Servidor ASGI para ejecución |
  | **Base de Datos** | MongoDB Atlas | NoSQL en la nube |
  | **Driver DB** | PyMongo | Conexión y consultas |
  | **Validación** | Pydantic | Validación y serialización |
  | **Seguridad** | bcrypt + jose | Hash de contraseñas y JWT |
  | **Docs** | Swagger UI / ReDoc | Documentación automática |
</div>
---

## 🚀 Cómo Empezar

### 📋 Prerrequisitos
- Python 3.10+
- Instancia de MongoDB (Atlas o local)
- VSCode / editor favorito

### ⚡ Instalación
```bash
git clone https://github.com/tu_usuario/AsistenciasREST.git
cd AsistenciasREST
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt
```
<br/>

### 🔑 Variables de Entorno

  ###👉 Sugerencia: agrega un archivo .env con tus credenciales (no lo subas al repo).

  Ejemplo .env.example:
  ```bash
  MONGO_URI="mongodb+srv://<usuario>:<password>@<cluster>/<db>?retryWrites=true&w=majority"
  SECRET_KEY="clave_super_secreta"
  ```

<br/>

### 🫰 Ejecución
```bash
uvicorn main:app --reload 
```
Swagger → (http://127.0.0.1:8000/docs)

<div align="center">
  | Nombre                       | Contacto                                                          | Rol                      |
  | ---------------------------- | ----------------------------------------------------------------- | ------------------------ |
  | **Carlos H. García Lira**    | [L21010280@zamora.tecnm.mx](mailto:L21010280@zamora.tecnm.mx)     | Backend / DB Admin       |
  | **Leonardo B. Garibay**      | [leobeedrok7@gmail.com](mailto:leobeedrok7@gmail.com)             | Backend / API Design     |
  | **Carlos E. López Quesada**  | [lopezmany111@gmail.com](mailto:lopezmany111@gmail.com)           | Backend / Auth Lead      |
  | **Manuel Ramírez Rodríguez** | [manuel.raamirez03@gmail.com](mailto:manuel.raamirez03@gmail.com) | Project Manager / DevOps |
</div>
---

<div align="center"> <img src="https://media.giphy.com/media/xTiN0CNHgoRf1Ha7CM/giphy.gif" width="80%" alt="Glitch Separator"/> <h3>_"Optimizando la acreditación estudiantil, un endpoint a la vez."_ 🚀</h3> </div> ```

