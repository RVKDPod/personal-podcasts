@echo off
call compress.bat
python generate_feed.py
git add .
git commit -m "Update feeds"
git push
pause
