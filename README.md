# Task API: Ruby on Rails vs. Python FastAPI

Proyecto educativo que implementa el mismo microservicio CRUD en dos stacks:

- Ruby 3.4 + Rails 8.1 en modo API.
- Python 3.14 + FastAPI 0.141 + SQLAlchemy 2.0.

Ambos guardan tareas en una base SQLite local, aceptan el mismo JSON y exponen
los mismos cuatro endpoints. El objetivo es comparar ideas equivalentes, no
proponer una arquitectura de producción.

Una tarea tiene esta forma:

```json
{
  "id": 1,
  "title": "Learn Ruby",
  "completed": false
}
```

## Endpoints

| Método y ruta | Acción | Respuesta correcta |
|---|---|---|
| `GET /tasks` | Listar las tareas, ordenadas por `id` | `200 OK` |
| `GET /tasks/:id` | Consultar una tarea | `200 OK` o `404 Not Found` |
| `POST /tasks` | Crear una tarea | `201 Created` o `422 Unprocessable Content` |
| `DELETE /tasks/:id` | Eliminar una tarea | `204 No Content` o `404 Not Found` |

El cuerpo de `POST /tasks` es plano e idéntico en los dos servicios:

```json
{
  "title": "Compare Rails and FastAPI",
  "completed": false
}
```

## Estructura

```text
microservices-demo/
├── ruby-service/
│   ├── app/
│   │   ├── controllers/tasks_controller.rb
│   │   └── models/task.rb
│   ├── config/routes.rb
│   ├── db/migrate/20260819000000_create_tasks.rb
│   ├── test/integration/tasks_test.rb
│   ├── Gemfile
│   └── Gemfile.lock
├── python-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── tests/test_api.py
│   ├── requirements.txt
│   └── requirements-dev.txt
├── .gitignore
└── README.md
```

Las bases `*.sqlite3`, el entorno virtual y los archivos temporales se generan
localmente y están ignorados por Git.

## Ejecutar el servicio Ruby/Rails

Se verificó con Ruby `3.4.10`, Rails `8.1.3.1`, SQLite `2.9.6` y Puma `8.0.2`.
Es necesario tener Ruby, SQLite y Bundler instalados.

```bash
cd microservices-demo/ruby-service
gem install bundler
bundle install
bin/rails db:migrate
bin/rails server -p 3000
```

La API queda en `http://localhost:3000`. `db:migrate` ejecuta las migraciones
pendientes y crea `storage/development.sqlite3`.

Para ejecutar las pruebas de integración:

```bash
bin/rails test
```

### Gems, Bundler y Gemfile

Una **gem** es un paquete de Ruby. `Gemfile` es comparable a
`requirements.txt`: declara Rails, el adaptador SQLite y Puma. **Bundler**
resuelve e instala esas gems con `bundle install`; `Gemfile.lock` registra las
versiones exactas resueltas para obtener instalaciones reproducibles.

`bin/rails` es el ejecutable propio del proyecto. Usarlo evita depender de otro
Rails instalado globalmente.

## Ejecutar el servicio Python/FastAPI

Se verificó con Python `3.14.7`, FastAPI `0.141.1`, Uvicorn `0.52.4` y
SQLAlchemy `2.0.52`.

```bash
cd microservices-demo/python-service
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

La API queda en `http://localhost:8000`. Al arrancar por primera vez,
SQLAlchemy crea `tasks.sqlite3`. FastAPI también genera documentación
interactiva en `http://localhost:8000/docs`.

Para instalar y ejecutar las pruebas:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Probar todos los endpoints con curl

Arranca uno de los servicios y elige su URL base:

```bash
# Rails
BASE_URL=http://localhost:3000

# O FastAPI
# BASE_URL=http://localhost:8000
```

Crear una tarea:

```bash
curl -i -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Ruby","completed":false}'
```

Listar tareas:

```bash
curl -i "$BASE_URL/tasks"
```

Consultar la tarea `1`:

```bash
curl -i "$BASE_URL/tasks/1"
```

Eliminar la tarea `1`:

```bash
curl -i -X DELETE "$BASE_URL/tasks/1"
```

Comprobar que ya no existe; ambos servicios responden `404` y
`{"detail":"Task not found"}`:

```bash
curl -i "$BASE_URL/tasks/1"
```

Los identificadores aumentan, por lo que después de borrar datos el siguiente
`id` puede no ser `1`. Usa el `id` devuelto por el `POST`.

## Flujo de una petición en Rails

Para `GET /tasks/1`, el recorrido es:

```text
HTTP GET /tasks/1
  → Route: config/routes.rb reconoce el recurso y la acción show
  → Controller: TasksController#show ejecuta set_task
  → Model: Task.find(params[:id]) usa Active Record
  → Database: Active Record consulta SQLite
  → JSON: render json: @task devuelve id, title y completed
```

En forma corta: **HTTP → Route → Controller → Model → Database → JSON**.

Rails aplica «convención sobre configuración»: `Task` se relaciona por
convención con la tabla plural `tasks`, y `TasksController#show` con la ruta de
consulta de un recurso.

## Comparación directa

| Concepto | Ruby / Rails | Python / FastAPI |
|---|---|---|
| Declarar una ruta | `resources :tasks` en `config/routes.rb` | Decorador `@app.get("/tasks")` |
| Atender una petición | Método del `TasksController` | Función de endpoint en `main.py` |
| Modelo persistente | `Task < ApplicationRecord` | `Task(Base)` de SQLAlchemy |
| ORM | Active Record incluido con Rails | SQLAlchemy, dependencia separada |
| Validación de entrada | Active Record y strong parameters | Esquema Pydantic `TaskCreate` |
| Serialización de salida | `render json: task` | `response_model=TaskRead` y retorno Python |
| Acceso a la petición | `params[:id]` y `params.permit(...)` | Argumentos tipados `task_id` y `payload` |
| Sesión de base de datos | Active Record la gestiona detrás del modelo | `Session` se inyecta con `Depends` |
| Crear tablas | Migración versionada de Rails | `Base.metadata.create_all` al arrancar |
| Dependencias | Gems en `Gemfile`, instaladas por Bundler | Paquetes en `requirements.txt`, instalados por pip |
| Servidor local | Puma mediante `bin/rails server` | Uvicorn |

Rails agrupa más decisiones dentro del framework. FastAPI es más pequeño y
permite escoger piezas independientes; aquí se eligieron Pydantic y SQLAlchemy.

La diferencia deliberada más importante está en la creación de tablas. Rails
usa una migración porque es una parte central y pedagógica de Active Record.
Agregar Alembic a Python duplicaría archivos y ocultaría la comparación básica,
así que el ejemplo Python usa `create_all`. En un sistema real, ambos lados
deberían usar migraciones versionadas.

Las rutas Python son `async def` para funcionar con el runtime Python 3.14 de
este entorno. Las operaciones SQLite siguen siendo síncronas; es una decisión
aceptable para esta demostración pequeña, no un patrón para una API de alta
concurrencia.

## Ruby para un programador de Python

### Clases, herencia y métodos

Ruby delimita estructuras con `end`, no con la indentación:

```ruby
class Task < ApplicationRecord
  validates :title, presence: true
end

def show
  render json: @task, only: task_fields
end
```

`<` indica herencia. `def` crea un método y los paréntesis al invocarlo suelen
omitirse. Ruby devuelve implícitamente el valor de la última expresión; por
ejemplo, `task_fields` devuelve `%i[id title completed]` sin escribir `return`.

### Símbolos, hashes y arrays

Un símbolo como `:title` es un nombre inmutable usado frecuentemente como
identificador o clave. No es lo mismo que el String mutable `"title"`.

```ruby
params.require(:task).permit(:title, :completed)
render json: { detail: "Task not found" }, status: :not_found
```

`{ detail: "Task not found" }` es un **Hash**, equivalente a un `dict` de
Python. La sintaxis `detail:` crea la clave símbolo `:detail`. `%i[index show]`
es una forma breve de escribir `[:index, :show]`.

### Bloques y `do/end`

Un bloque es código que se pasa a un método, parecido a proporcionar un
callback en Python. La migración recibe un objeto `t`:

```ruby
create_table :tasks do |t|
  t.string :title, null: false
  t.boolean :completed, null: false, default: false
end
```

`do ... end` delimita el bloque y `|t|` declara su parámetro. También se puede
usar `{ ... }` para bloques cortos; esas llaves no deben confundirse con las de
un Hash, cuyo contexto es diferente.

### Variables de instancia

`@task` es una variable de instancia del controlador. Se parece conceptualmente
a `self.task` en Python, aunque Ruby permite leerla y escribirla directamente.
El `before_action` la asigna antes de `show` y `destroy`.

Una variable sin `@`, como `task` en `create`, es local al método.

### Métodos que terminan en `?` o `!`

Son convenciones legibles, no operadores especiales:

- `completed?` pregunta por un booleano. Active Record lo genera para el campo
  `completed`, aunque en JSON el nombre siga siendo `completed`.
- `destroy!` intenta borrar y lanza una excepción si falla. Una versión sin
  `!` suele comunicar el fallo mediante su valor de retorno.

El signo no garantiza por sí solo ese comportamiento: el autor del método lo
implementa siguiendo la convención.

### `nil`, booleanos y condiciones

Ruby usa `nil`, `true` y `false`, equivalentes a `None`, `True` y `False`. Solo
`nil` y `false` son falsos en una condición; `0`, `""` y `[]` son verdaderos.

```ruby
if task.save
  render json: task, status: :created
else
  render json: { detail: task.errors.full_messages }, status: :unprocessable_content
end
```

### Routing, controllers y `render json:`

`resources :tasks, only: %i[index show create destroy]` genera cuatro rutas
REST y las conecta con métodos del controlador. En FastAPI esa relación está
junto a cada función mediante decoradores.

Un controller de Rails recibe la petición, coordina el modelo y termina con
`render json:` o `head :no_content`. `render json:` serializa objetos Ruby o
registros de Active Record y configura una respuesta HTTP JSON.

### Models, Active Record y migraciones

`Task < ApplicationRecord` es un modelo Active Record. Sus métodos de clase
operan sobre la tabla (`Task.order`, `Task.find`) y una instancia representa una
fila (`task.save`, `task.destroy!`). Esto combina el objeto y el acceso a datos.

La migración describe un cambio versionado del esquema. `bin/rails db:migrate`
la ejecuta y actualiza `db/schema.rb`. SQLAlchemy separa más explícitamente el
modelo, el `Session` y las consultas.

## Guion sugerido para una demostración corta

1. **`README.md`**: presentar el JSON, los cuatro endpoints y la tabla de
   equivalencias.
2. **`ruby-service/config/routes.rb`**: explicar el DSL, los símbolos y las
   rutas generadas; ejecutar `bin/rails routes` si hay tiempo.
3. **`ruby-service/app/controllers/tasks_controller.rb`**: mostrar `def/end`,
   `@task`, strong parameters, Hashes y `render json:`.
4. **`ruby-service/app/models/task.rb`** y la migración: explicar Active Record,
   convenciones de nombres, bloques y esquema.
5. **`ruby-service/Gemfile`**: distinguir Ruby, Rails, gems y Bundler.
6. **`python-service/app/main.py`**: recorrer las mismas cuatro rutas y comparar
   decoradores con `resources` y funciones con acciones del controller.
7. **`python-service/app/schemas.py`**, **`models.py`** y **`database.py`**:
   separar validación JSON, modelo ORM y sesión.
8. Crear, listar, consultar y borrar una tarea con los comandos `curl` de este
   documento, cambiando únicamente `BASE_URL` para repetirlos en el otro stack.

Para una exposición de 10–15 minutos no hace falta mostrar los archivos de
configuración generados por Rails: ayudan al framework a arrancar, pero no son
parte esencial del recorrido de la petición.

## Decisiones de alcance

- SQLite permite enseñar persistencia sin levantar servicios externos.
- No hay autenticación, frontend, Docker, Redis ni colas.
- Los dos servicios devuelven solo `id`, `title` y `completed`; Rails guarda
  además sus timestamps convencionales, pero no los expone.
- Rails conserva su migración estándar; Python crea la tabla al iniciar para no
  introducir Alembic en una demostración tan pequeña.
