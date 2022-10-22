#!/bin/bash
for variable  in $(seq 1 300)
do
        # usleep : 默认以微秒   ms表示毫秒   us表示微秒 
        # sleep : 默认为秒
        
        python3 /home/vision/projects/huhao_reptile_DON_NOT_DELETE/huhao/vision_reptile/get_rank.py
        echo "每隔1天访问一次"
        sleep 86400
        
done
