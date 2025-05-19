# Miran Search API

> **Note**: The commands in this guide are tailored for **PowerShell** on Windows with WSL2 (Ubuntu-22.04).  
> If you are using **Linux** or **macOS**, run the same commands in **Terminal**, ensuring compatibility with your system.

## Project Overview

This project is a Django-based REST API developed for **Miran**, an AI-powered fitness app offering smart meal tracking, real-time workout guidance, and engaging fitness challenges. The API provides an efficient product search functionality, enabling users to search a database of thousands of products (including names, brands, categories, and nutrition facts) using partial keywords, handling misspellings, and supporting mixed-language queries (English and Arabic). The project demonstrates my expertise in backend development with Django, PostgreSQL database management, Redis caching, containerization with Docker, and writing clean, testable code.

### Task Requirements
- Build a Django-based API using Django 4.x and Django REST Framework (DRF).
- Support product searches with:
  - Partial keywords (e.g., "App" for "Apple").
  - Misspellings (e.g., "Aple" for "Apple").
  - Mixed-language queries (English and Arabic, e.g., "تفاحة" or "Apple").
- Use PostgreSQL as the database, pre-populated with thousands of products.
- Optimize performance using Redis for caching.
- Ensure scalability and fast response times for large datasets.

### My Solution
I built a robust product search API that meets all requirements:
- **Search Functionality**: Supports intelligent searches using PostgreSQL's `pg_trgm` extension for fuzzy matching, delivering accurate results for partial keywords, misspellings, and bilingual queries (English/Arabic). For example, "Aple" or "تفاح" returns products like "Apple" or "تفاحة".
- **Database**: PostgreSQL database pre-populated with 5000 products (via `populate_products` command), including names, brands, categories, and nutrition facts.
- **Performance**: Redis caching stores paginated product lists, reducing database queries. Cache keys use `products:all:page:<number>` for efficiency.
- **Scalability**: Uses DRF's pagination (`StandardResultsSetPagination`, 30 products per page) to handle large datasets.
- **Testing**: Includes 27 passing unit tests with 96% code coverage, ensuring reliability.
- **Containerization**: Fully containerized with Docker and Docker Compose (Django, PostgreSQL, Redis).
- **Data Generation**: Custom `populate_products` command generates realistic product data in English and Arabic using `Faker`.

## How the Solution Meets Evaluation Criteria

The solution aligns with Miran’s evaluation criteria:

- **Search Accuracy and Relevance (35%)**:
  - Leverages PostgreSQL’s `pg_trgm` extension with `TrigramSimilarity` and `TrigramWordSimilarity` for fuzzy matching.
  - Handles partial keywords (e.g., "App" matches "Apple"), misspellings (e.g., "Aple" matches "Apple"), and mixed-language queries (e.g., "تفاح" matches "تفاحة").
  - Configured via migration (`0003_enable_pg_trgm.py`) for robust bilingual search.

- **Performance and Query Optimization (25%)**:
  - Uses Redis to cache paginated results, minimizing database queries.
  - Employs `select_related('category')` to reduce database joins.
  - Implements pagination to ensure fast responses with 5000+ products.
  - Achieves sub-second response times for list and search endpoints.

- **Code Quality and Structure (20%)**:
  - Follows Django best practices with modular code (separate models, serializers, views).
  - Uses clear naming conventions and docstrings.
  - Includes 27 unit tests covering authentication, models, serializers, and views.
  - Achieves 96% code coverage, ensuring maintainability.

- **Documentation and Usability (10%)**:
  - Provides clear setup instructions in this `README.md`.
  - Includes API documentation with example requests and responses.
  - Offers Swagger UI (`/swagger/`) for interactive API exploration.

- **Bonus (10%)**:
  - Implements Redis caching for performance.
  - Supports bilingual search, exceeding basic requirements.
  - Includes comprehensive unit tests for robustness.

## Prerequisites
- **Docker** and **Docker Compose** (`docker --version`, `docker-compose --version`).
- **Git** (`git --version`).
- **WSL2** on Windows (Ubuntu-22.04, `wsl --version`) or Linux/macOS.
- A text editor (e.g., VS Code, nano).

## Setup Instructions

### Step 1: Clone the Repository
Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/MrMohammed1/Miran_search.git
```
```bash
cd Miran_search
```

### Step 2: Configure Environment Variables
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in a text editor (e.g., `nano .env`) and update:
   - `DJANGO_SECRET_KEY`: Set a secure, unique key (e.g., generate via Python: `python -c "import secrets; print(secrets.token_urlsafe(50))"`).
   - `POSTGRES_PASSWORD`: Set a secure password.
   - Ensure `DATABASE_URL` reflects the password (e.g., `postgresql://postgres:your-password@db:5432/miran_search`).
   - Save the file (Ctrl+O, Enter, Ctrl+X in nano).

### Step 3: Start Docker and Build Containers
1. Ensure Docker is running:
   - **Windows/macOS**: Launch **Docker Desktop**, verify:
     ```bash
     docker ps
     ```
   - **Linux/WSL2**:
     - Enter WSL2:
       ```bash
       wsl
       ```
     - Start Docker:
       ```bash
       sudo service docker start
       ```
     - Verify Docker is running:
       ```bash
       docker ps
       ```
2. Check ports 8000 (Django), 5432 (PostgreSQL), 6379 (Redis) are free:
   ```bash
   ss -tuln | grep -E '8000|5432|6379'
   ```
   - If in use:
     - Identify the process using port 6379 (Redis):
       ```bash
       sudo lsof -i :6379
       ```
     - Stop the process using the listed PID:
       ```bash
       sudo kill -9 <PID>
       ```
     - Stop local Redis:
       ```bash
       sudo service redis-server stop
       ```
3. Build and start containers:
   ```bash
   docker-compose up --build -d
   ```

### Step 4: Verify Running Containers
Verify containers are running:
```bash
docker ps
```
- Expected (3 containers):
  ```
  CONTAINER ID   IMAGE                  COMMAND                  STATUS         PORTS
  <id>           miran_search-web       "sh -c 'sleep 20 && …'"  Up             0.0.0.0:8000->8000/tcp
  <id>           postgres:15            "docker-entrypoint.s…"   Up             0.0.0.0:5432->5432/tcp
  <id>           redis:7                "docker-entrypoint.s…"   Up             0.0.0.0:6379->6379/tcp
  ```

### Step 5: Populate the Database
> **Note**: If the database is empty (e.g., after running `docker-compose down -v` or on a fresh setup), apply migrations manually to create the necessary tables:
> ```bash
> docker-compose exec web python manage.py migrate
> ```

Populate with 5000 products:
```bash
docker-compose exec web python manage.py populate_products
```
- Expected:
  ```
  Starting to create 5000 products...
  Generating products: 100%|██████████████████████████| 5000/5000 [00:03<00:00, 1290.58it/s]
  Successfully created 5000 products!
  ```

### Step 6: Clear the Cache
Clear Redis cache:
```bash
docker-compose exec redis redis-cli flushall
```
- Verify empty cache:
  ```bash
  docker-compose exec redis redis-cli keys "*"
  ```
  (Returns `(empty array)`).

### Step 7: Run Tests
Run unit tests:
```bash
docker-compose exec web pytest -v
```
- Expected:
  ```
  ============================== test session starts ==============================
  collected 27 items
  products/tests/test_auth.py::AuthTests::test_obtain_token PASSED           [  3%]
  ...
  ============================ 27 passed in 42.67s ============================
  ```

### Step 8: Access the Application
Access the API at:
- **Product List**: `http://localhost:8000/api/products/`
  - Paginated (30 per page).
  - Example: `http://localhost:8000/api/products/?page=2`
- **Search**: `http://localhost:8000/api/products/search/?q=<query>`
  - Supports partial keywords, misspellings, mixed languages.
  - Examples:
    - `http://localhost:8000/api/products/search/?q=Aple`
    - `http://localhost:8000/api/products/search/?q=تفاح`
- **Swagger Documentation**: `http://localhost:8000/swagger/`
- **Admin Interface**: `http://localhost:8000/admin/` (login: `testuser`/`testpass`).

## Technical Details

### Architecture
- **Framework**: Django 4.2.9, Django REST Framework.
- **Database**: PostgreSQL with `pg_trgm` for fuzzy search.
- **Caching**: Redis for paginated product lists.
- **Containerization**: Docker, Docker Compose.
- **Testing**: Pytest, 27 tests, 96% coverage.
- **Data Generation**: `populate_products` command with `Faker`.

### Key Components
- **Models**:
  - `Category`: Unique names and slugs.
  - `Product`: Name, brand, description, nutrition facts, category (English/Arabic).
- **Serializers**:
  - `ProductSerializer`: Product data.
  - `ProductSearchSerializer`: Search results.
  - `CategorySerializer`: Category data.
- **Views**:
  - `ProductViewSet`: List, search, CRUD with caching.
  - `CategoryViewSet`: Category operations.
- **Search Logic**:
  - `pg_trgm` for trigram-based similarity.
  - Supports partial matches, misspellings, bilingual queries.
- **Pagination**:
  - `StandardResultsSetPagination`, `page_size=30`.
- **Authentication**:
  - JWT via `django-rest-framework-simplejwt`.
- **Management Commands**:
  - `populate_products`: Generates 5000 products.

### File Structure
- `docker-compose.yml`: Services (web, db, redis), volumes.
- `Dockerfile`: Django container build.
- `.env.example`: Environment variables template.
- `requirements.txt`: Dependencies (Django 4.2.9, psycopg2-binary, redis, pytest, Faker).
- `products/models.py`: `Category`, `Product` models.
- `products/views.py`: API endpoints, caching, search.
- `products/serializers.py`: Serialization logic.
- `products/tests/`: 27 unit tests.
- `products/management/commands/populate_products.py`: Data generation.

## API Usage

### Endpoints
- **GET** `/api/products/`
  - Lists paginated products (30 per page).
  - **Parameters**:
    - `page` (optional): Page number.
  - **Example**:
    ```
    GET http://localhost:8000/api/products/
    ```
    **Response**:
    ```json
    {
        "count": 5000,
        "next": "http://localhost:8000/api/products/?page=2",
        "previous": null,
        "results": [
            {
                "id": 1,
                "name": "Natural Apple Development",
                "brand": "Chavez, Brown and Collier",
                "description": "",
                "calories": 52,
                "protein": 0.0,
                "carbs": 0.0,
                "fats": 0.0,
                "created_at": "2025-05-19T06:11:20.419507Z",
                "updated_at": "2025-05-19T06:11:20.419597Z"
            },
            ...
        ]
    }
    ```

- **GET** `/api/products/search/?q=<query>`
  - Searches products by name.
  - **Parameters**:
    - `q`: Query (e.g., `Aple`, `تفاح`).
  - **Example**:
    ```
    GET http://localhost:8000/api/products/search/?q=Aple
    ```
    **Response**:
    ```json
    {
        "count": 10,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 1,
                "name": "Natural Apple Development",
                "brand": "Chavez, Brown and Collier",
                ...
            },
            ...
        ]
    }
    ```

- **GET** `/api/categories/`
  - Lists product categories.
  - **Example**:
    ```
    GET http://localhost:8000/api/categories/
    ```

### Testing with Postman
1. Open Postman, create a GET request.
2. Enter a URL (e.g., `http://localhost:8000/api/products/search/?q=تفاح`).
3. Send and verify the response contains relevant products.