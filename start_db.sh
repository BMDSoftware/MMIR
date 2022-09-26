#!/bin/bash


DB_PORT=3306

DIR=$PWD
MYSQL_ROOT_PASSWORD=mmir2022
MYSQL_USER=redg
MYSQL_PASSWORD=mmir2022
MYSQL_DATABASE=mmirdb

CONTAINER_NAME=mmirdb



echo ""
echo ""
echo ""
echo ">>>>>>>to stop this contaier type >> docker stop $CONTAINER_NAME<< in another console<<<<<<<<<<<<<"
echo ""
echo ""
echo ""

#USER=`whoami`
#mkdir -p $DIR/docker/db/data
#chown -R $USER:$USER $DIR/docker/db/data
#chmod -R 777 $DIR/docker/db/data


#PORTS="-P "
PORTS="-p $DB_PORT:3306 "

#RUNMODE="-ti --rm"
RUNMODE="-d --restart=unless-stopped "

if [[ "$#" -gt 0 ]] ; then
    if [ "$1" == "daemon" ] ; then
        RUNMODE="-d --restart=unless-stopped "
    fi
fi



docker run \
	$RUNMODE \
	--name $CONTAINER_NAME \
	$PORTS \
	-v volumendb:/var/lib/mysql \
	-e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -e "MYSQL_USER=$MYSQL_USER" -e "MYSQL_PASSWORD=$MYSQL_PASSWORD" -e "MYSQL_DATABASE=$MYSQL_DATABASE" \
	mysql

echo "done"


