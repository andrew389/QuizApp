# Quizz App
## Table of Contents
- [Installation](#installation)
- [Starting the Application](#starting-the-application)
- [Running Tests](#running-tests)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/andrew389/meduzzen_internship.git
    cd meduzzen_internship
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv/Scripts/activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Starting the Application

1. Make sure you are in the project directory and the virtual environment is activated.

2. Run the FastAPI application using Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

3. Open your browser and go to `http://127.0.0.1:8000` to see the application running.

## Running Tests

1. Ensure the virtual environment is activated.

2. Run the tests using `pytest`:

    ```bash
    pytest
    ```

3. You should see output indicating that the tests have passed.