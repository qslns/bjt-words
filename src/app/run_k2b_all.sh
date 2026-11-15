#!/bin/bash
# 11/15 K2 N3·N2 한자 그림 카드 326자 배포 전 전체 시험
cd /home/claude/work/app
D=${D:-/home/claude/work/build/data_app.json}
DATA=$D timeout 900 node test_app.mjs > t_k2b_app.log 2>&1; echo EXIT $? >> t_k2b_app.log
DATA=$D LV_BASE=http://127.0.0.1:8766/ LV_DATA=/tmp/data_lv.json timeout 900 node test_1114.mjs > t_k2b_1114.log 2>&1; echo EXIT $? >> t_k2b_1114.log
timeout 300 node fs_test.mjs > t_k2b_fs.log 2>&1; echo EXIT $? >> t_k2b_fs.log
timeout 300 node swupdate_test.mjs > t_k2b_sw.log 2>&1; echo EXIT $? >> t_k2b_sw.log
timeout 600 node kz_audio_test.mjs > t_k2b_kz.log 2>&1; echo EXIT $? >> t_k2b_kz.log
timeout 600 node furi_test.mjs > t_k2b_furi.log 2>&1; echo EXIT $? >> t_k2b_furi.log
OLD=/home/claude/bjt-words/index.html NEW=test/index.html EXPECT_GONE='' timeout 900 node progress_keep.mjs > t_k2b_pk.log 2>&1; echo EXIT $? >> t_k2b_pk.log
URL=http://127.0.0.1:8765/ VPS='820x1180,1180x820' PART=wk timeout 3000 node bug_all.mjs > t_k2b_bug.log 2>&1; echo EXIT $? >> t_k2b_bug.log
echo ALLDONE > t_k2b_done.flag
