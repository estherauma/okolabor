#!/bin/bash
shopt -s expand_aliases
source /root/.bash_aliases
branch="$1"
sudo su

start_ssh_agent() {
  echo 'Starting ssh-agent'
  eval "$(ssh-agent -s)"
  sudo ssh-add /root/.ssh/id_github_deploy
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
  sudo systemctl stop gunicorn.socket gunicorn.service
}

start_process() {
  echo 'Restarting the application'
  sudo systemctl start gunicorn.socket gunicorn.service
}

echo "Deploying branch $branch of the CMS"
start_ssh_agent && go_to_path_to_deploy && pull_latest_code && kill_process && start_process

exit 0
