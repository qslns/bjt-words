#!/bin/bash
# 기본 전체 재배열 + 묶음별 약점 + 카드 표시 + N3·N2 칸 코드 — 배포 전 전체 시험 (11/13 밤 페이지)
cd /home/claude/work/app
timeout 300 node fs_test.mjs > t_revert_fs.log 2>&1; echo EXIT $? >> t_revert_fs.log
timeout 300 node swupdate_test.mjs > t_revert_sw.log 2>&1; echo EXIT $? >> t_revert_sw.log
timeout 600 node kz_audio_test.mjs > t_kz.log 2>&1; echo EXIT $? >> t_kz.log
timeout 600 node furi_test.mjs > t_furi.log 2>&1; echo EXIT $? >> t_furi.log
OLD=/home/claude/bjt-words/index.html NEW=test/index.html EXPECT_GONE='B:1-50:step,B:1-100:step,B:1-150:step,B:1-200:step,B:1-250:step,B:251-300:step,B:251-350:step,B:251-400:step,B:251-450:step,B:251-500:step,B:1-500:review,B:501-550:step,B:501-600:step,B:501-650:step,B:501-700:step,B:501-750:step,B:751-800:step,B:751-850:step,B:751-900:step,B:751-950:step,B:751-1000:step,B:501-1000:review,B:1001-1050:step,B:1001-1100:step,B:1001-1150:step,B:1001-1200:step,B:1001-1250:step,B:1251-1300:step,B:1251-1330:step,B:1001-1330:review,B:1-1330:all' timeout 900 node progress_keep.mjs > t_pk.log 2>&1; echo EXIT $? >> t_pk.log
URL=http://127.0.0.1:8765/ VPS='820x1180,1180x820' PART=w timeout 2400 node bug_all.mjs > t_bug.log 2>&1; echo EXIT $? >> t_bug.log
echo ALLDONE > t_j1_done.flag
