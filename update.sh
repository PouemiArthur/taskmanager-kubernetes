#!/bin/bash
deploy="$1"
tag="$2"
if [ -z ./$deploy ]; then
   echo "$deploy doesn't match a corresponding directory in the root project directory "
   exit 1
fi
echo "building Docker image $deploy:$tag"
docker build -t $deploy:$tag ./$deploy
echo "succesfully built image $deploy:$tag ___________________________________"

kind load docker-image $deploy:$tag --name kind
echo "$deploy:$tag image has been loaded in the kubernetes cluster ____________"

if [ -z $deploy-deployment.yaml ]; then
   echo "did not find a manifest called $deploy-deployment.yaml in this directory "
   exit 1
fi
sed -i s/$deploy:[0-9]*\.[0-9]*\.[0-9]*/$deploy:$tag/g $deploy-deployment.yaml
echo "$deploy manfifest updated _______________________________________________"

kubectl set image deployment/$deploy $deploy=$deploy:$tag
echo "$deploy Deployment update complete! _____________________________________"
