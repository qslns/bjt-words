#!/bin/bash
# 11/15 한자 연결 고침(같은 한자 순서·짝 양쪽·읽기·읽기 중요도) 배포 전 전체 시험
cd /home/claude/work/app
D=${D:-/home/claude/work/build/data_app.json}
DATA=$D timeout 900 node test_app.mjs > t_lf_app.log 2>&1; echo EXIT $? >> t_lf_app.log
DATA=$D LV_BASE=http://127.0.0.1:8766/ LV_DATA=/tmp/data_lv.json timeout 900 node test_1114.mjs > t_lf_1114.log 2>&1; echo EXIT $? >> t_lf_1114.log
timeout 300 node fs_test.mjs > t_lf_fs.log 2>&1; echo EXIT $? >> t_lf_fs.log
timeout 300 node swupdate_test.mjs > t_lf_sw.log 2>&1; echo EXIT $? >> t_lf_sw.log
timeout 600 node kz_audio_test.mjs > t_lf_kz.log 2>&1; echo EXIT $? >> t_lf_kz.log
timeout 600 node furi_test.mjs > t_lf_furi.log 2>&1; echo EXIT $? >> t_lf_furi.log
OLD=/home/claude/bjt-words/index.html NEW=test/index.html EXPECT_GONE='' timeout 900 node progress_keep.mjs > t_lf_pk.log 2>&1; echo EXIT $? >> t_lf_pk.log
URL=http://127.0.0.1:8765/ VPS='820x1180,1180x820' PART=wk timeout 3000 node bug_all.mjs > t_lf_bug.log 2>&1; echo EXIT $? >> t_lf_bug.log
echo ALLDONE > t_lf_done.flag
