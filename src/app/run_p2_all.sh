#!/bin/bash
# P2 배포 전 전체 시험 (11/13 페이지)
cd /home/claude/work/app
bash run_revert_tests.sh
timeout 600 node kz_audio_test.mjs > t_kz.log 2>&1; echo EXIT $? >> t_kz.log
timeout 600 node furi_test.mjs > t_furi.log 2>&1; echo EXIT $? >> t_furi.log
OLD=/home/claude/bjt-words/index.html NEW=test/index.html EXPECT_GONE='B:751-885:step,B:501-885:review,B:1-885:all' timeout 900 node progress_keep.mjs > t_pk.log 2>&1; echo EXIT $? >> t_pk.log
URL=http://127.0.0.1:8765/ VPS='820x1180,1180x820' PART=w timeout 1800 node bug_all.mjs > t_bug.log 2>&1; echo EXIT $? >> t_bug.log
echo ALLDONE > t_p2_done.flag
