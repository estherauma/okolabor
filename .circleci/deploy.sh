#!/bin/bash
shopt -s expand_aliases
source /root/.bash_aliases
branch="$1"

start_ssh_agent() {
  echo 'Starting ssh-agent'
  eval "$(ssh-agent -s)"
  ssh-add /root/.ssh/id_ed25519_github_deploy
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
    cd "/var/www/dev/"
  else
    echo 'We can only deploy master, staging or dev branches'
  fi
  pwd
}

exit 0
