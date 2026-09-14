Name: Azkal Azkiya Arifi Putra

NPM: 2506636991

Class: PBP KEIKEIAI (KKI)

# Project Description - Azkal Azkiya Arifi Putra's Portfolio

A personal portfolio website for(and by :D) Azkal Azkiya Arifi Putra, a Computer Science student in the International Class (KKI) at Universitas Indonesia.


## Technology

- Django
- Django MVT architecture
- Django ORM
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

5. Run the Django system check:

	```powershell
	python manage.py check
	```

6. Run the tests:

	```powershell
	python manage.py test main
	```

7. Start the development server:

	```powershell
	python manage.py runserver
	```

8. Open `http://127.0.0.1:8000/` in a browser.

## Project Structure

```text
manage.py                  Django command-line utility
portofolio/                Django project configuration
templates/index.html       Portfolio page markup
static/css/style.css       Portfolio styles
static/img/                Profile and project images
requirements.txt           Python dependencies
main/models.py             Experience database model
main/views.py              View logic and template context
main/urls.py               Application URL routes
main/migrations/           Database migration files
main/tests.py              Experience and Project tests
templates/experience.html  Experience page template
templates/projects.html    Dynamic Projects page template
```

## Pages

- `/` - Main portfolio page
- `/experience/` - Database-backed experience page
- `/projects/` - Database-backed projects page

## Testing

Run the test suite with:

```powershell
python manage.py test main
```

The tests cover the Experience and Project models, page accessibility, database-backed rendering, project statuses, finished-project links and images, ongoing projects without images, and empty-state behavior.

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

### Assignment 1
1. So why I used `<section>`, `<header>`, `<main>` and many others so that we can differentiate each components according to its semantic meaning, making it more readable for me. Also, in modern website we need to think about accessibility and semantic tags allow screen readers to read each components' meaning. 
2. The main challenge was keeping the grid layout from looking too cramped on a phone screen. I used a CSS media query for screens under 600px to force the grid into a single column. I chose to prioritize my name and photo to show up at the very top by reordering the grid areas, ensuring visitors see my main identity first without needing to scroll.
3. The biggest limitation is that updating the site is pretty annoying since I have to manually edit the HTML file every time I finish a new project. For the next iteration, I really want to add a database using Django's MVT architecture. That way, I can just upload new projects easily without having to mess with the code again.  

### Assignment 2 
1. When a user opens the Projects page, the browser sends a request to `/projects/`. The project's `portofolio/urls.py` receives the request and forwards it to the application's URL configuration using `include("main.urls")`. The application's `main/urls.py` matches the `/projects/` path and sends the request to the `show_projects` view. The view uses the `Project` model and Django ORM to retrieve the project data from the database with `Project.objects.all()`. It then sends the data to `templates/projects.html` through the `project_list` context variable. Finally, the template loops through `project_list` and displays the project title, description, status, image, and external link in the browser.

2. The data should be stored in a model instead of being written directly in the template because project information can change while the page design stays the same. Using a model makes the application easier to maintain because projects can be added, edited, or removed in the database without rewriting the HTML template. It also supports future development such as Django Admin, searching, filtering by project status, project detail pages, and sorting. The model stores the data, the view retrieves it, and the template displays it.

3. `makemigrations` and `migrate` have different purposes. `makemigrations` detects changes in the Django models and creates migration files that describe the database changes. `migrate` applies those migration files to the actual database. For example, if I add a `featured = models.BooleanField(default=False)` field to the `Project` model, I need to run `python manage.py makemigrations` to create the migration file and then `python manage.py migrate` to apply the change to the database and add the new column.

## AI Disclosure

So I used GitHub Copilot as a development assistant for this project. The assistance included planning the feature work, suggesting HTML structure, drafting initial project descriptions, and proposing responsive CSS patternss.

I carefully reviewed and understood every changes the AI proposed. I also made changes if I think the AI is wrong and implemented my own features :D 