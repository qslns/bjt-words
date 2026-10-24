#!/bin/bash
cd /home/claude/work/app
DATA=/home/claude/work/build/data_app.json timeout 900 node test_app.mjs > t_revert_app.log 2>&1; echo EXIT $? >> t_revert_app.log
timeout 300 node fs_test.mjs > t_revert_fs.log 2>&1; echo EXIT $? >> t_revert_fs.log
timeout 300 node swupdate_test.mjs > t_revert_sw.log 2>&1; echo EXIT $? >> t_revert_sw.log
