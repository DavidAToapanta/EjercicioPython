# Login sencillo con Flask

Proyecto educativo que implementa un inicio de sesión con Python y Flask.
Permite validar credenciales, confirmar la contraseña, mantener una sesión,
acceder a una página protegida y cerrar sesión.

No utiliza base de datos: trabaja con un usuario de demostración definido
en el código.

## Funcionalidades

- Inicio de sesión con usuario y contraseña.
- Confirmación de contraseña.
- Validación de contraseñas mediante hash.
- Protección de formularios contra ataques CSRF.
- Acceso a la página de inicio únicamente con una sesión activa.
- Bloqueo de 30 segundos después de tres intentos fallidos.
- Cierre de sesión.

## Tecnologías utilizadas

- Python.
- Flask: rutas, solicitudes, plantillas y sesiones.
- Flask-WTF: protección CSRF.
- Werkzeug: generación y comprobación del hash de contraseña.
- HTML y CSS: estructura y presentación de las páginas.

## Ejecutar en Windows con PowerShell

Crear el entorno virtual:

```powershell
python -m venv .venv
```

Instalar las dependencias:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

El archivo `requirements.txt` debe incluir las dependencias utilizadas,
entre ellas Flask y Flask-WTF.

Ejecutar la aplicación:

```powershell
.\.venv\Scripts\python.exe app.py
```

Abrir en el navegador:

http://127.0.0.1:5000

Credenciales de demostración:

- Usuario: `admin`
- Contraseña: `123456`
- Confirmación de contraseña: `123456`

Para detener el servidor, presionar `Ctrl+C`.

## Estructura del proyecto

| Archivo o carpeta | Descripción |
|---|---|
| `app.py` | Configuración, rutas, validaciones y control de intentos. |
| `requirements.txt` | Dependencias necesarias para ejecutar el proyecto. |
| `templates/base.html` | Plantilla base compartida por las páginas. |
| `templates/login.html` | Formulario de acceso y mensajes de error. |
| `templates/inicio.html` | Página protegida y formulario de cierre de sesión. |
| `static/style.css` | Estilos visuales de la aplicación. |

## Rutas de la aplicación

| Ruta | Método | Función | Comportamiento |
|---|---|---|---|
| `/` | GET | `inicio()` | Muestra la página de inicio si existe una sesión; de lo contrario, redirige al login. |
| `/login` | GET | `login()` | Muestra el formulario. Si ya hay sesión, redirige al inicio. |
| `/login` | POST | `login()` | Comprueba el bloqueo, la confirmación y las credenciales. |
| `/logout` | POST | `logout()` | Borra la sesión y redirige al login. |

## Variables principales

### Configuración y constantes

| Variable | Descripción |
|---|---|
| `app` | Instancia principal de Flask. |
| `SECRET_KEY` | Clave usada para firmar la sesión y los tokens CSRF. Se obtiene del entorno o se genera al iniciar. |
| `SESSION_COOKIE_HTTPONLY` | Impide que JavaScript acceda directamente a la cookie de sesión. |
| `SESSION_COOKIE_SAMESITE` | Con el valor `"Lax"`, limita el envío de la cookie en solicitudes entre sitios. |
| `csrf` | Activa la protección CSRF mediante `CSRFProtect`. |
| `USUARIO` | Nombre del usuario de demostración: `admin`. |
| `PASSWORD_HASH` | Hash generado a partir de la contraseña de demostración. |
| `MAX_INTENTOS` | Máximo de intentos fallidos antes del bloqueo: `3`. |
| `SEGUNDOS_BLOQUEO` | Duración del bloqueo: `30` segundos. |
| `intentos_login` | Diccionario en memoria que guarda los fallos y bloqueos por dirección IP. |
| `lock_login` | Evita que varios hilos modifiquen simultáneamente el control de intentos. |

### Variables del inicio de sesión

| Variable | Descripción |
|---|---|
| `error` | Mensaje que se envía a la plantilla cuando una validación falla. |
| `ip` | Dirección IP obtenida de `request.remote_addr`. Identifica el contador de intentos. |
| `usuario` | Nombre de usuario recibido del formulario, sin espacios al inicio ni al final. |
| `password` | Contraseña recibida del formulario. |
| `confirmar_password` | Segundo campo utilizado para comprobar que las contraseñas coincidan. |
| `ahora` | Valor de `monotonic()` utilizado para comprobar si terminó el bloqueo. |
| `estado` | Diccionario con los datos de intentos de una IP. |
| `password_valido` | Resultado de comparar la contraseña ingresada con `PASSWORD_HASH`. |
| `segundos` | Tiempo restante de bloqueo, redondeado hacia arriba. |
| `restantes` | Cantidad de intentos disponibles antes del bloqueo. |

Cada registro de `intentos_login` contiene:

| Campo | Descripción |
|---|---|
| `fallos` | Número de intentos con credenciales incorrectas. |
| `bloqueado_hasta` | Momento, medido con `monotonic()`, hasta el cual se mantiene el bloqueo. El valor `0` indica que no hay bloqueo programado. |

`monotonic()` mide tiempo transcurrido; su valor no representa una fecha
ni una hora del calendario.

## Funcionamiento del inicio de sesión

1. Flask-WTF comprueba el token CSRF de la solicitud POST.
2. La aplicación recibe el usuario, la contraseña y su confirmación.
3. Obtiene el registro de intentos correspondiente a la IP.
4. Si existe un bloqueo activo, rechaza el acceso e informa el tiempo restante.
5. Si el bloqueo terminó, reinicia el contador de fallos.
6. Comprueba que la contraseña y su confirmación coincidan.
7. Compara el usuario y verifica la contraseña mediante su hash.
8. Si las credenciales son correctas:
   - Elimina el registro de intentos de esa IP.
   - Limpia la sesión anterior.
   - Guarda el usuario en `session["usuario"]`.
   - Redirige a la página de inicio.
9. Si las credenciales son incorrectas:
   - Incrementa el contador de fallos.
   - Muestra los intentos restantes.
   - Al tercer fallo, activa un bloqueo de 30 segundos.

La confirmación de contraseña se incluye como parte de la práctica.
En una aplicación habitual se utiliza al registrarse o cambiar la
contraseña, no al iniciar sesión.

## Qué ocurre cuando falla una validación

| Situación | Resultado |
|---|---|
| Falta un campo obligatorio en el navegador | El atributo HTML `required` impide el envío normal del formulario. No sustituye la validación del servidor. |
| Las contraseñas no coinciden | Muestra un error y devuelve HTTP 400. No incrementa el contador de credenciales incorrectas. |
| Usuario o contraseña incorrectos, antes del tercer fallo | Incrementa el contador y muestra los intentos restantes en el formulario. |
| Tercer intento fallido | Activa el bloqueo y devuelve HTTP 429. |
| Intento durante el bloqueo | Rechaza el acceso, incluso con credenciales correctas, y devuelve HTTP 429. |
| Token CSRF ausente, inválido o vencido | Flask-WTF rechaza la solicitud con HTTP 400 antes de ejecutar la validación del login. |
| Acceso a `/` sin sesión | Redirige al formulario de login. |

Las respuestas HTTP 429 incluyen la cabecera `Retry-After`, que indica
cuántos segundos debe esperar el cliente.

El tiempo restante se actualiza cuando se realiza otro intento.
La página no incluye un contador animado.

## Control de intentos

Los intentos se guardan en el servidor por dirección IP.

- Los fallos se acumulan hasta un acceso correcto o hasta que termine
  un bloqueo y se procese un nuevo intento.
- Los intentos realizados durante un bloqueo no prolongan su duración.
- Después de 30 segundos se permiten tres nuevos intentos.
- Recargar la página o borrar las cookies no elimina el contador del servidor.
- Reiniciar la aplicación elimina todos los registros de intentos.
- Las personas que compartan una IP también comparten el contador.

## Sesiones y contraseñas

Flask utiliza por defecto una cookie de sesión firmada. La firma permite
detectar modificaciones, pero no cifra el contenido: no deben guardarse
contraseñas ni otros secretos dentro de la sesión.

`session["usuario"]` indica que el usuario inició sesión correctamente.
`session.clear()` elimina los datos de la sesión al cerrar sesión o
antes de establecer un nuevo acceso.

La contraseña ingresada se comprueba con `check_password_hash()`.
No obstante, la contraseña de demostración `123456` aparece en el código
como entrada de `generate_password_hash()`: usar un hash no convierte
estas credenciales públicas en credenciales seguras para producción.

Si no se define `SECRET_KEY` en el entorno, se genera una clave nueva
al iniciar la aplicación. En ese caso, reiniciarla invalida las sesiones
anteriores.

## Protección CSRF

Los formularios POST incluyen este campo oculto:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

Flask-WTF genera y valida el token para ayudar a impedir que otro sitio
realice acciones utilizando la sesión del usuario.

La protección se aplica tanto al inicio como al cierre de sesión.

## Pruebas manuales

| Prueba | Resultado esperado |
|---|---|
| Entrar a `/` sin iniciar sesión | Redirección al login. |
| Ingresar las credenciales correctas y una confirmación igual | Acceso a la página de inicio. |
| Escribir una confirmación diferente | Mensaje de contraseñas distintas, sin sumar un fallo. |
| Fallar una vez | Quedan dos intentos. |
| Fallar una segunda vez | Queda un intento. |
| Fallar una tercera vez | Bloqueo de 30 segundos. |
| Ingresar credenciales correctas durante el bloqueo | Acceso rechazado. |
| Esperar 30 segundos e ingresar correctamente | Acceso permitido. |
| Cerrar sesión e intentar volver a `/` | Redirección al login. |
| Enviar un POST sin un token CSRF válido | Respuesta HTTP 400. |

## Limitaciones

Este proyecto está diseñado para una práctica local:

- Tiene un único usuario fijo.
- No permite registro ni recuperación de contraseña.
- No utiliza base de datos.
- Los intentos se guardan únicamente en la memoria de un proceso.
- El bloqueo por IP puede afectar a varias personas de una misma red.
- El bloqueo global de hilos simplifica el ejemplo, pero limita
  el procesamiento simultáneo de inicios de sesión.

Para desplegarlo con varios procesos, el control de intentos necesita
almacenamiento compartido, como Redis, y operaciones atómicas.
También se requieren usuarios persistentes, una clave de sesión estable,
HTTPS y un servidor adecuado para producción.

## Referencias

- [Documentación de Flask](https://flask.palletsprojects.com/en/stable/)
- [Protección CSRF con Flask-WTF](https://flask-wtf.readthedocs.io/en/1.2.x/csrf/)