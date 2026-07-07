# Digital Library & E-Book Circulation Portal

A Django-based digital library and e-book circulation portal with user accounts, book management, authors, circulation tracking, and dashboard reporting.

## Features
- User authentication and profile management
- Author and book management
- Book issuance and return workflow
- Overdue loan tracking
- Admin and member dashboards
- Report generation support

## Local development
1. Create and activate a virtual environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Environment variables
Copy `.env.example` to `.env` and update values as needed.

## GitHub deployment
This project is already configured for deployment to Render using `render.yaml`.

### Push to GitHub
```bash
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### Deploy from GitHub
1. Create a repository on GitHub.
2. Push the code using the commands above.
3. Connect the repository to Render or another hosting provider.
4. Set environment variables if needed.

> Note: GitHub Pages is not suitable for this Django application. Use a platform such as Render, Railway, or Heroku for hosting.
