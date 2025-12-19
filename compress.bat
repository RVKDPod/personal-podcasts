@echo off
for %%f in (mp3\*.mp3) do (
  ffmpeg -y -i "%%f" -map_metadata 0 -vn -ac 1 -ab 96k "%%f.tmp"
  move /Y "%%f.tmp" "%%f"
)
pause
