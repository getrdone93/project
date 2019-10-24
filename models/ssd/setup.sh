#!/bin/bash
PROJECT=ssd.pytorch

if [ ! -d $PROJECT ]; then
  echo "Pulling down $PROJECT project..."
  git clone https://github.com/amdegroot/$PROJECT  
else
  echo "$PROJECT exists, nothing to do, exiting"
fi

