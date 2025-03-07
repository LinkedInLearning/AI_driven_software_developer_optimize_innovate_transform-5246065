# Red30 Tech Landing Page

A Django web application featuring a landing page for Red30 Tech with a contact form.

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
- On macOS/Linux:
```bash
source venv/bin/activate
```
- On Windows:
```bash
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

## Running the Application

1. Start the development server:
```bash
python manage.py runserver
```

2. Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

## Features

- Modern, responsive landing page
- Contact form with name and email fields
- Form submission confirmation messages
- Bootstrap 5 styling 