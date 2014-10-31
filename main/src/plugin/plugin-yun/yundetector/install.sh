#!/bin/sh
#####sh  .../.../install.sh#####
cd ${0%/*}

run-avrdude ./sketch_room_detector.hex  >install.log  2>&1
if [ $? -ne 0 ];then
	echo 'install err'
	exit
fi

tar -xzvf install.tar.gz  >> install.log  2>&1
if [ $? -ne 0 ];then
	echo 'install err'
	exit
fi

cd ./install
./install.sh  >> ../install.log  2>&1

if [ $? -eq 0 ];then
	echo 'install ok'
else
	echo 'install err'
fi
#reboot >>/dev/null
exit