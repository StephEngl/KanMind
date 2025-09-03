# KanMind Django Project

KanMind is a backend project built with Django REST Framework.  
It provides a RESTful API for managing boards, tasks, users, and comments — ideal for Kanban-style productivity applications and team collaboration tools.

**This project is licensed under the [MIT License](LICENSE).**

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### ⚙️ Prerequisites

- Python 3.10+
- pip (Python package manager)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/) (recommended)

### 📦 Installation

1. **Clone the repository**
    ```sh
    git clone https://github.com/StephEngl/KanMind.git
    cd KanMind
    ```

2. **Create and activate a virtual environment**
    ```sh
    python -m venv env
    source env/Scripts/activate  # On Mac: env\bin\activate
    ```

3. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```

4. **Apply migrations**
    ```sh
    python manage.py migrate
    ```

5. **Create a superuser (optional, for admin access)**
    ```sh
    python manage.py createsuperuser
    ```

6. **Run the development server**
    ```sh
    python manage.py runserver
    ```

7. **If your frontend uses a guest user, create one in the admin panel:**
    - Go to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
    - Create a user with:
        - Username: `Guest`
        - First name: `Guest`
        - Last name: `Guest`
        - Email: `guest@kanmind.de`
        - Password: `321kanMind987+`
    > **Note:** Don't forget to add the Guest user information to your frontend configuration so it can authenticate as the guest user.

## 🔒 Security Information

- **Secret Key:** Never share your Django `SECRET_KEY`. Use environment variables for production.
- **Debug Mode:** Set `DEBUG = False` in production.
- **Allowed Hosts:** Update `ALLOWED_HOSTS` in `settings.py` for your deployment.
- **Passwords:** Change default passwords (like the Guest user) in production.
- **Database:** Use strong credentials and restrict access.
- **HTTPS:** Always use HTTPS in production.
- **Admin Panel:** Restrict admin access and use strong passwords.
- **.env Files:** Make sure `.env` files are not pushed to the repo (see `.gitignore`).
- **Database Files:** Do not commit database files (`*.sqlite3`).

### 🔗 API Endpoints

#### 🛡️ Authentication
- `POST /api/login/` – Login
- `POST /api/registration/` – Register
- `POST /api/email-check/` – Check if email exists

#### 🗂️ Boards (`app_board`)
- `GET /api/boards/` – List all boards
- `POST /api/boards/` – Create a new board
- `GET /api/boards/<id>/` – Get board details
- `PATCH /api/boards/<id>/` – Update board
- `DELETE /api/boards/<id>/` – Delete board

#### 📋 Tasks (`app_task`)
- `GET /api/tasks/assigned-to-me/` – List all tasks, where user is assignee
- `GET /api/tasks/reviewing/` – List all tasks, where user is reviewer
- `POST /api/tasks/` – Create a new task
- `PATch /api/tasks/<id>/` – Update task
- `DELETE /api/tasks/<id>/` – Delete task
- `GET /api/tasks/<id>/comments/` – List comments for a task
- `POST /api/tasks/<id>/comments/` – Add comment to a task
- `DELETE /api/tasks/<id>/comments/<id>` – Delete comment from a task

### 📁 Project Structure

- [`core`](core ) – Django project settings and root URLs
- [`app_auth`](app_auth ) – User authentication and registration
- [`app_board`](app_board ) – Board management
- [`app_task`](app_task ) – Task and comment management

---

For more details, see the [`core/settings.py`](core/settings.py ) and [`core/urls.py`](core/urls.py ) files.
