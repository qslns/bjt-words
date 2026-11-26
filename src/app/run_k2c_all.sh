#!/bin/bash
# 11/26 한자 그림 카드 N3·N2 1,001~ 131자 + 한자 읽기 고침(fix1126) 배포 전 전체 시험
cd /home/claude/work/app
D=${D:-/home/claude/work/build/data_app.json}
DATA=$D timeout 900 node test_app.mjs > t_k2c_app.log 2>&1; echo EXIT $? >> t_k2c_app.log
DATA=$D LV_BASE=http://127.0.0.1:8766/ LV_DATA=/tmp/data_lv.json timeout 900 node test_1114.mjs > t_k2c_1114.log 2>&1; echo EXIT $? >> t_k2c_1114.log
timeout 300 node fs_test.mjs > t_k2c_fs.log 2>&1; echo EXIT $? >> t_k2c_fs.log
timeout 300 node swupdate_test.mjs > t_k2c_sw.log 2>&1; echo EXIT $? >> t_k2c_sw.log
timeout 600 node kz_audio_test.mjs > t_k2c_kz.log 2>&1; echo EXIT $? >> t_k2c_kz.log
timeout 600 node furi_test.mjs > t_k2c_furi.log 2>&1; echo EXIT $? >> t_k2c_furi.log
OLD=/home/claude/bjt-words/index.html NEW=test/index.html EXPECT_GONE='' timeout 900 node progress_keep.mjs > t_k2c_pk.log 2>&1; echo EXIT $? >> t_k2c_pk.log
URL=http://127.0.0.1:8765/ VPS='820x1180,1180x820' PART=wk timeout 3000 node bug_all.mjs > t_k2c_bug.log 2>&1; echo EXIT $? >> t_k2c_bug.log
echo ALLDONE > t_k2c_done.flag
