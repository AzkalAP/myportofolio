Name: Azkal Azkiya Arifi Putra

NPM: 2506636991

Class: PBP KEIKEIAI (KKI)

# Project Description - Azkal Azkiya Arifi Putra's Portfolio

A personal portfolio website for(and by :D) Azkal Azkiya Arifi Putra, a Computer Science student in the International Class (KKI) at Universitas Indonesia.


## Technology

- Django
- Django MVT architecture
- Django ORM
- Django built-in authentication, sessions, and groups
- Django CSRF protection
- Semantic HTML5
- CSS3
- SQLite for local development
- WhiteNoise for static file serving

## Local Setup

1. Clone the repository and open the project directory.

2. Create and activate a virtual environment:

	```powershell
	python -m venv env
	.\env\Scripts\Activate.ps1
	```

3. Install the project dependencies:

	```powershell
	pip install -r requirements.txt
	```

4. Apply the database migrations:

	```powershell
	python manage.py migrate
	```

5. Create the portfolio-owner account:

	```powershell
	python manage.py createsuperuser
	```

	The owner account can create, update, and delete Experience and Project records.
	To grant update-only access, sign in to `/admin/`, create a group named `Editor`
	under **Groups**, and add the intended users to it. Assign Editor membership only
	through Django Admin. Editors can update records but cannot create or delete them.

	The role permissions are:

	| Role | Read | Star projects | Create/delete | Update |
	| --- | --- | --- | --- | --- |
	| Visitor | Yes | No | No | No |
	| Regular user | Yes | Yes | No | No |
	| Editor | Yes | Yes | No | Yes |
	| Portfolio owner (superuser) | Yes | Yes | Yes | Yes |

6. Run the Django system check:

	```powershell
	python manage.py check
	```

7. Run the tests:

	```powershell
	python manage.py test main
	```

8. Start the development server:

	```powershell
	python manage.py runserver
	```

9. Open `http://127.0.0.1:8000/` in a browser.

## Project Structure

```text
manage.py                  Django command-line utility
portofolio/                Django project configuration
templates/index.html       Portfolio page markup
templates/base.html        Shared HTML layout and navigation
templates/experience.html  Experience listing and management controls
templates/experience_form.html  Experience add/edit form
templates/projects.html    Project listing and management controls
templates/projects_form.html  Project add/edit form
templates/register.html    Account registration form
templates/login.html       Account login form
templates/components/      Star and delete confirmation components
static/css/style.css       Portfolio styles
static/img/                Profile and project images
requirements.txt           Python dependencies
main/models.py             Experience and Project database models
main/forms.py              Experience and Project forms
main/views.py              View logic and JSON endpoints
main/urls.py               Application URL routes
main/migrations/           Database migration files
main/tests.py              Experience and Project tests
```

## Pages

- `/` - Main portfolio page
- `/experience/` - Database-backed experience page
- `/experience/add/` - Add an experience record
- `/experience/<uuid>/edit/` - Edit an experience record
- `/experience/<uuid>/delete/` - Delete an experience record (owner only, POST)
- `/projects/` - Database-backed projects page
- `/projects/add/` - Add a project record (owner only)
- `/projects/<id>/edit/` - Edit a project record (Editor or owner)
- `/projects/<id>/delete/` - Delete a project record (owner only, POST)
- `/projects/<id>/star/` - Toggle the current user's project star (login required, POST)
- `/register/`, `/login/`, `/logout/` - Account registration, login, and logout
- `/admin/` - Django Admin for users and Editor group membership

## JSON Endpoints

- `/api/experience/` - Public serialized Experience records
- `/api/projects/` - Public Project records, with optional `?title=` filtering. The
	response includes project fields but omits `starred_by` and user identities.

## Testing

Run the test suite with:

```powershell
python manage.py test main
```

The tests cover:

- Experience and Project models.
- Page accessibility and template rendering.
- Experience and Project form validation.
- Creating, editing, and deleting Experience records.
- Creating and editing Project records.
- Registration, login/logout, and last-login cookie lifecycle.
- Visitor, regular-user, Editor, and owner access rules for Experience and Project mutations.
- Role-based visibility of create, update, and delete controls.
- Project star toggling, star counts, and per-user star state.
- Public project JSON field privacy.
- Experience and Project JSON endpoints.
- Project search and filtering.
- Status display, images, external links, and empty states.

## Weekly Progress
### Week 1
- added Hero section
- added Experience section
- added Finished Project section
- added Ongoing Project section

### Week 2
- Implemented Tutorial 2
- Implemented Django's Model-View-Template (MVT) architecture for the Experience section.
- Added the `Experience` model and database migrations.
- Added a separate Experience page at `/experience/`.
- Added the `Project` model with fields for title, description, status, image path, and external URL.
- Added initial database records for four projects.
- Added a separate dynamic Projects page at `/projects/`.
- Added navigation links to the Projects page.
- Added tests for the Experience and Projects MVT flows.
- Verified the application with Django system checks and automated tests.

### Week 3
- Refactored full-page templates to extend the shared `base.html` layout.
- Added Experience create, edit, delete, and JSON endpoint functionality.
- Added Project editing with a shared add/edit form.
- Added reusable delete confirmation components for Experience and Project records.
- Added tests for forms, CRUD operations, JSON responses, routes, and template controls.
- Updated the README with the current project structure, routes, endpoints, and test coverage.

### Week 4
- Added account registration, login, and logout using Django's built-in authentication system.
- Displayed authentication status in the shared navigation and added a `last_login` cookie.
- Added owner-only create/delete and Editor-or-owner update permissions for Experience and Projects.
- Added project star/unstar controls for authenticated users.
- Kept portfolio JSON endpoints public while excluding project star-user identities from the Projects response.
- Added tests for authentication, role permissions, template controls, project stars, and JSON privacy.

### Assignment 1
1. So why I used `<section>`, `<header>`, `<main>` and many others so that we can differentiate each components according to its semantic meaning, making it more readable for me. Also, in modern website we need to think about accessibility and semantic tags allow screen readers to read each components' meaning. 
2. The main challenge was keeping the grid layout from looking too cramped on a phone screen. I used a CSS media query for screens under 600px to force the grid into a single column. I chose to prioritize my name and photo to show up at the very top by reordering the grid areas, ensuring visitors see my main identity first without needing to scroll.
3. The biggest limitation is that updating the site is pretty annoying since I have to manually edit the HTML file every time I finish a new project. For the next iteration, I really want to add a database using Django's MVT architecture. That way, I can just upload new projects easily without having to mess with the code again.  

### Assignment 2 
1. When a user opens the Projects page, the browser sends a request to `/projects/`. The project's `portofolio/urls.py` receives the request and forwards it to the application's URL configuration using `include("main.urls")`. The application's `main/urls.py` matches the `/projects/` path and sends the request to the `show_projects` view. The view uses the `Project` model and Django ORM to retrieve the project data from the database with `Project.objects.all()`. It then sends the data to `templates/projects.html` through the `project_list` context variable. Finally, the template loops through `project_list` and displays the project title, description, status, image, and external link in the browser.

2. The data should be stored in a model instead of being written directly in the template because project information can change while the page design stays the same. Using a model makes the application easier to maintain because projects can be added, edited, or removed in the database without rewriting the HTML template. It also supports future development such as Django Admin, searching, filtering by project status, project detail pages, and sorting. The model stores the data, the view retrieves it, and the template displays it.

3. `makemigrations` and `migrate` have different purposes. `makemigrations` detects changes in the Django models and creates migration files that describe the database changes. `migrate` applies those migration files to the actual database. For example, if I add a `featured = models.BooleanField(default=False)` field to the `Project` model, I need to run `python manage.py makemigrations` to create the migration file and then `python manage.py migrate` to apply the change to the database and add the new column.

### Assignment 3

1. Django's `ModelForm` connects an HTML form directly to a model. It automatically creates fields, validates submitted data, and saves valid data, so we do not need to manually define and validate every HTML field. The `{% csrf_token %}` tag protects POST forms from Cross-Site Request Forgery attacks. Django checks this token to confirm that the request came from the application itself.

2. JSON is preferred because it is lightweight, readable, and easy for JavaScript to process. Its structure matches JavaScript objects and arrays naturally. XML is usually more verbose because it requires opening and closing tags for its data.

3. The view first retrieves portfolio objects from the database. Django's serializer converts those model objects into JSON, and the view returns the result with the `application/json` content type. Serialization is necessary because Django model instances are Python objects, not JSON data. It converts their fields into a standard format that browsers and other applications can understand.

## AI Disclosure

So I used GitHub Copilot as a development assistant for this project. The assistance included planning the feature work, suggesting HTML structure, drafting initial project descriptions, and proposing responsive CSS patternss.

I carefully reviewed and understood every changes the AI proposed. I also made changes if I think the AI is wrong and implemented my own features :D 