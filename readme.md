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

## Test credentails
1. Set up `TEST_ACCOUNT_PASSWORD` inside `.env` file
1. Run `python manage.py create_test_credentials` to create groups and roles for you
1. The groups are `worker`, `recruiter`, `employer`, `admin`
1. The usernames will be `testworker@okolabor.com`, `testrecruiter@okolabor.com`, `testemployer@okolabor.com`, and `testadmin@okolabor.com`
1. The password will be, e.g for the worker `testworker_TEST_ACCOUNT_PASSWORD`. Remember to replace `TEST_ACCOUNT_PASSWORD` with the value you set in the `.env` file
