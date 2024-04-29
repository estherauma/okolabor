# Jaguar


## How to set up
1. Clone the repository
1. Create a virtual environment and activate it
1. Install the dependencies by running `pip install -r requirements.txt`
1. Copy `.env.example` to `.env` and update the values. Make sure to fill all of them out.
    -  Database credentials are vital
    - If you need to send out emails, email credentials are also vital
1. Run `python manage.py migrate` to apply the migrations
1. Run `python manage.py runserver` to start the server
1. Visit `http://localhost:8000` to see the app running

## Testing
To execute tests, run
`python manage.py test` 

To execute tests with coverage, run 
`python manage.py test`  
This additionally generates results that are stored inside `./test-reports` directory.

## Linting
We've installed [flake8](https://flake8.pycqa.org/en/latest/) for linting.
To check the entire projeect, run  
`flake8 .`   

To lint a specific file, run   
`flake8 <path/to/file>`


## Credits
