#!/bin/bash
# 11/27 N2 3·4부(1,001~1,573) + 한자 그림 카드 46자 + 덱 음성 고침 4 배포 전 전체 시험
cd /home/claude/work/app
D=${D:-/home/claude/work/build/data_app.json}
DATA=$D timeout 900 node test_app.mjs > t_n2p3_app.log 2>&1; echo EXIT $? >> t_n2p3_app.log
DATA=$D LV_BASE=http://127.0.0.1:8766/ LV_DATA=/tmp/data_lv.json timeout 900 node test_1114.mjs > t_n2p3_1114.log 2>&1; echo EXIT $? >> t_n2p3_1114.log
timeout 300 node fs_test.mjs > t_n2p3_fs.log 2>&1; echo EXIT $? >> t_n2p3_fs.log
timeout 300 node swupdate_test.mjs > t_n2p3_sw.log 2>&1; echo EXIT $? >> t_n2p3_sw.log
timeout 600 node kz_audio_test.mjs > t_n2p3_kz.log 2>&1; echo EXIT $? >> t_n2p3_kz.log
timeout 600 node furi_test.mjs > t_n2p3_furi.log 2>&1; echo EXIT $? >> t_n2p3_furi.log
OLD=/home/claude/bjt-words/index.html NEW=test/index.html EXPECT_GONE='' EXPECT_KZ_NEW=1 timeout 900 node progress_keep.mjs > t_n2p3_pk.log 2>&1; echo EXIT $? >> t_n2p3_pk.log
URL=http://127.0.0.1:8765/ VPS='820x1180,1180x820' PART=wk timeout 3000 node bug_all.mjs > t_n2p3_bug.log 2>&1; echo EXIT $? >> t_n2p3_bug.log
echo ALLDONE > t_n2p3_done.flag
