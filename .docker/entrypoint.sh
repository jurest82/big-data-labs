#!/bin/bash

COLOR_RED=$(tput setaf 1)
COLOR_GREEN=$(tput setaf 2)
COLOR_YELLOW=$(tput setaf 3)
COLOR_BLUE=$(tput setaf 4)
COLOR_MAGENTA=$(tput setaf 5)
COLOR_DEFAULT=$(tput sgr0)

EXEC_PATH=$(dirname $(readlink -f "$0"))
HOME_PATH=$EXEC_PATH/..
STEP=1
STEP_COUNT=3

echo "${COLOR_MAGENTA}${STEP}/$STEP_COUNT:${COLOR_GREEN} Configuring Git.${COLOR_DEFAULT}"
GIT_SCRIPT_PATH=$EXEC_PATH/git.sh
chmod +x $GIT_SCRIPT_PATH
. $GIT_SCRIPT_PATH
let STEP++

echo "$COLOR_BLUE"

if [ ! -d "$HOME_PATH/node_modules" ]; then
    echo "${COLOR_MAGENTA}${STEP}/$STEP_COUNT:${COLOR_GREEN} Installing ${COLOR_BLUE}$HOME_PATH/package.json${COLOR_GREEN} dependencies.${COLOR_DEFAULT}"
    cd $HOME_PATH && npm install
else
    echo "${COLOR_MAGENTA}${STEP}/$STEP_COUNT:${COLOR_GREEN} Folder ${COLOR_BLUE}$HOME_PATH/node_modules${COLOR_GREEN} found! Skipping npm installation.${COLOR_DEFAULT}"
fi
let STEP++

echo "${COLOR_MAGENTA}${STEP}/$STEP_COUNT:${COLOR_GREEN} Configuring AWS credentials.${COLOR_DEFAULT}"
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    AWS_SCRIPT_PATH=$EXEC_PATH/aws.sh
    chmod +x $AWS_SCRIPT_PATH
    $AWS_SCRIPT_PATH
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
    if [ -n "$AWS_ACCOUNT_ID" ]; then
        echo -e "${COLOR_GREEN}INFO: AWS account: ${AWS_ACCOUNT_ID}${COLOR_DEFAULT}"
    else
        echo -e "${COLOR_YELLOW}WARN: The AWS credentials in .envs/aws.env could not be verified.${COLOR_DEFAULT}"
    fi
else
    echo -e "${COLOR_YELLOW}INFO: No AWS credentials found in .envs/aws.env. Fine for the local labs; the AWS labs need them.${COLOR_DEFAULT}"
fi

echo "$COLOR_DEFAULT"
