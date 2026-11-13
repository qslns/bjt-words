#!/bin/bash
# K1(한자 칸 새 순서) 배포 전 전체 시험 (11/14 새벽 페이지) — DATA·EXPECT는 인자로
cd /home/claude/work/app
D=${D:-/tmp/k1/data_k1.json}
DATA=$D timeout 900 node test_app.mjs > t_k1_app.log 2>&1; echo EXIT $? >> t_k1_app.log
DATA=$D LV_BASE=http://127.0.0.1:8766/ LV_DATA=/tmp/data_lv.json timeout 900 node test_1114.mjs > t_k1_1114.log 2>&1; echo EXIT $? >> t_k1_1114.log
timeout 300 node fs_test.mjs > t_k1_fs.log 2>&1; echo EXIT $? >> t_k1_fs.log
timeout 300 node swupdate_test.mjs > t_k1_sw.log 2>&1; echo EXIT $? >> t_k1_sw.log
timeout 600 node kz_audio_test.mjs > t_k1_kz.log 2>&1; echo EXIT $? >> t_k1_kz.log
timeout 600 node furi_test.mjs > t_k1_furi.log 2>&1; echo EXIT $? >> t_k1_furi.log
OLD=/home/claude/bjt-words/index.html NEW=test/index.html EXPECT_GONE="${EXPECT_GONE:-}" EXPECT_KZ_NEW=1 timeout 900 node progress_keep.mjs > t_k1_pk.log 2>&1; echo EXIT $? >> t_k1_pk.log
URL=http://127.0.0.1:8765/ VPS='820x1180,1180x820' PART=wk timeout 3000 node bug_all.mjs > t_k1_bug.log 2>&1; echo EXIT $? >> t_k1_bug.log
echo ALLDONE > t_k1_done.flag
