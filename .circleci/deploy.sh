#!/bin/bash
branch="$1"


start_ssh_agent() {
  echo 'Starting ssh-agent'
  eval "$(ssh-agent -s)"
  ssh-add /root/.ssh/id_github_deploy
}

go_to_path_to_deploy() {
  echo "Currrent branch variable is: $branch"
  if [ "$branch" = "main" ]; then
    echo 'Going to path to deploy master branch'
    cd "/var/www/production/"
  elif [ "$branch" = "staging" ]; then
    echo 'Going to path to deploy staging branch'
    cd "/var/www/staging/"
  elif [ "$branch" = "skapeyi/58-2915-set-up-automatic-deployment-for-strapi" ]; then
    echo 'Going to path to deploy dev branch'
    cd "/var/www/jaguar-web-api/"
  else
    echo 'We can only deploy master, staging or dev branches'
  fi
  pwd
}

pull_latest_code() {
  echo "Pulling latest code from $branch"
  git stash
  git pull origin "$branch"
  yarn install
  yarn build
}

kill_process() {
  echo "Stopping the application"
  systemctl stop gunicorn.socket gunicorn.service
}

collect_static() {
  echo 'Collecting static files'
  source /var/www/jaguar-web-api/venv/bin/activate
  python manage.py collectstatic --noinput
}

start_process() {
  echo 'Restarting the application'
  systemctl start gunicorn.socket gunicorn.service
}

echo "Deploying branch $branch of the web application"
echo "*******************************************************\n"
start_ssh_agent && go_to_path_to_deploy && pull_latest_code && kill_process && collect_static && start_process

exit 0
