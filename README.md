Name: Azkal Azkiya Arifi Putra

NPM: 2506636991

Class: PBP KEIKEIAI (KKI)

# Project Description - Azkal Azkiya Arifi Putra's Portfolio

A personal portfolio website for(and by :D) Azkal Azkiya Arifi Putra, a Computer Science student in the International Class (KKI) at Universitas Indonesia.


## Technology

- Django
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

4. Run the Django system check:

	```powershell
	python manage.py check
	```

5. Start the development server:

	```powershell
	python manage.py runserver
	```

6. Open `http://127.0.0.1:8000/` in a browser.

## Project Structure

```text
manage.py                 Django command-line utility
portofolio/               Django project configuration
templates/index.html      Portfolio page markup
static/css/style.css      Portfolio styles
static/img/               Profile and project images
requirements.txt          Python dependencies
```

## Weekly Progress
### Week 1
- added Hero section
- added Experience section
- added Finished Project section
- added Ongoing Project section
### Week 2

### Assignment 1
1. So why I used `<section>`, `<header>`, `<main>` and many others so that we can differentiate each components according to its semantic meaning, making it more readable for me. Also, in modern website we need to think about accessibility and semantic tags allow screen readers to read each components' meaning. 
2. The main challenge was keeping the grid layout from looking too cramped on a phone screen. I used a CSS media query for screens under 600px to force the grid into a single column. I chose to prioritize my name and photo to show up at the very top by reordering the grid areas, ensuring visitors see my main identity first without needing to scroll.
3. The biggest limitation is that updating the site is pretty annoying since I have to manually edit the HTML file every time I finish a new project. For the next iteration, I really want to add a database using Django's MVT architecture. That way, I can just upload new projects easily without having to mess with the code again.  

## AI Disclosure

So I used GitHub Copilot as a development assistant for this project. The assistance included planning the feature work, suggesting HTML structure, drafting initial project descriptions, and proposing responsive CSS patternss.

I carefully reviewed and understood every changes the AI proposed. I also made changes if I think the AI is wrong and implemented my own features :D 