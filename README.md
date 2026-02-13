[LINK AL FRONT END](https://github.com/UEM-Grupo-4/Hotel-California-FrontEnd)

# 📖 Backend – Setup desde cero (Django + Docker)

Este documento explica cómo levantar el proyecto desde cero luego de clonar el repositorio.  
Los pasos están pensados para un usuario externo que no conoce el entorno.

⚠️ **Importante:**  
La aplicación **NO funciona si no se crea el archivo `.env` antes de ejecutar Docker Compose**.

---

## 🚀 Levantar aplicación con Docker Compose

Este proyecto se puede levantar fácilmente usando Docker Compose, sin necesidad de instalar Python ni dependencias en tu máquina local.

---

## 📚 Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado en tu sistema  
  (incluye Docker Compose).

Verificar instalación:
```bash
docker compose version
```

## 🔧 Cómo crear tu archivo .env
Copiá el archivo de ejemplo:
```bash
cp .env.copy .env
```

Reemplaza los valores por los tuyos
```bash
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=california_db
DB_USER=california_user
DB_PASSWORD=password123
DB_HOST=db
DB_PORT=3306
```

## 🚀 Levantar la aplicación.

Desde la raíz del proyecto (donde está docker-compose.yml), ejecuta:
```bash
Por primera vez usar:
docker compose up --build

Después usar:
docker compose up
```

## ⚙️ Configura tu DBeaver

<img width="657" height="316" alt="image" src="https://github.com/user-attachments/assets/5f34ec65-4f2e-4d1d-84bf-b2b3479d4bad" />
