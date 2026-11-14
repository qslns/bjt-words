#!/bin/bash
# K2 한자 그림 카드(기본 158자) 배포 전 전체 시험 (11/14 새벽 페이지)
cd /home/claude/work/app
D=${D:-/home/claude/work/build/data_app.json}
DATA=$D timeout 900 node test_app.mjs > t_k2_app.log 2>&1; echo EXIT $? >> t_k2_app.log
DATA=$D LV_BASE=http://127.0.0.1:8766/ LV_DATA=/tmp/data_lv.json timeout 900 node test_1114.mjs > t_k2_1114.log 2>&1; echo EXIT $? >> t_k2_1114.log
timeout 300 node fs_test.mjs > t_k2_fs.log 2>&1; echo EXIT $? >> t_k2_fs.log
timeout 300 node swupdate_test.mjs > t_k2_sw.log 2>&1; echo EXIT $? >> t_k2_sw.log
timeout 600 node kz_audio_test.mjs > t_k2_kz.log 2>&1; echo EXIT $? >> t_k2_kz.log
timeout 600 node furi_test.mjs > t_k2_furi.log 2>&1; echo EXIT $? >> t_k2_furi.log
OLD=/home/claude/bjt-words/index.html NEW=test/index.html EXPECT_GONE='' timeout 900 node progress_keep.mjs > t_k2_pk.log 2>&1; echo EXIT $? >> t_k2_pk.log
URL=http://127.0.0.1:8765/ VPS='820x1180,1180x820' PART=wk timeout 3000 node bug_all.mjs > t_k2_bug.log 2>&1; echo EXIT $? >> t_k2_bug.log
echo ALLDONE > t_k2_done.flag
