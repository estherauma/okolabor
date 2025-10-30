#!/bin/bash
branch="$1"

start_ssh_agent() {
  echo "Starting ssh-agent"
  eval "$(ssh-agent -s)"
  ssh-add /root/.ssh/id_github_deploy
}

go_to_path_to_deploy() {
  echo -e "\n************* Changing path *********************************\n"
  echo -e "Currrent branch variable is: $branch"
  if [ "$branch" = "main" ]; then
    echo "Going to path to deploy master branch"
    cd "/var/www/okolabor-prod/"
  elif [ "$branch" = "staging" ]; then
    echo "Going to path to deploy staging branch"
    cd "/var/www/staging/"
  elif [ "$branch" = "dev" ]; then
    echo "Going to path to deploy dev branch"
    cd "/var/www/jaguar-web-api/"
  else
    echo "We can only deploy master, staging or dev branches"
    exit 0
  fi
  pwd
}

pull_latest_code() {
  echo -e "\n ************* Fetching changes *************************************** \n"
  echo "Pulling latest code from $branch"
  git stash
  git pull origin "$branch"
}

kill_process() {
  echo -e "\n ******************** Stopping the application ******************************* \n"
  echo "Stopping the application"
  if [ "$branch" = "main" ]; then
    systemctl stop gunicorn.socket gunicorn-prod.service
  else
    systemctl stop gunicorn.socket gunicorn.service
  fi
}

install_depedencies_and_collect_static() {
  echo -e "\n************** Collecting static ****************************** \n"
  echo "Collecting static files"
  source venv/bin/activate
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py export_cms_labels
  python manage.py compilemessages
  python manage.py collectstatic --noinput
}

start_process() {
  echo -e "\n*********** Stating the process ******************\n"
  echo "Restarting the application"
  if [ "$branch" = "main" ]; then
    systemctl start gunicorn.socket gunicorn-prod.service
  else
    systemctl start gunicorn.socket gunicorn.service
  fi
}

echo "Deploying branch $branch of the web application"
echo -e "************  Starting deploy* ******************************* \n"
start_ssh_agent && go_to_path_to_deploy && pull_latest_code && kill_process && install_depedencies_and_collect_static && start_process

echo -e "************  Deployed successfully ********************************\n"
exit 0
