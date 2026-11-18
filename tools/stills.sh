#!/usr/bin/env bash
# usage: stills.sh <entry-id> <video-url> <out-dir> <tmp-dir>
set -u
id="$1"; url="$2"; out="$3"; tmp="$4"
mkdir -p "$out" "$tmp/sheets"
v="$tmp/$id.mp4"
curl -sL --max-time 300 -o "$v" "$url" || { echo "$id download failed"; exit 1; }
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$v")
n=0
for f in 0.12 0.37 0.62 0.87; do
  n=$((n+1)); t=$(awk -v d="$dur" -v f="$f" 'BEGIN{printf "%.2f", d*f}')
  ffmpeg -v error -y -ss "$t" -i "$v" -frames:v 1 -vf "scale=960:-2" -q:v 4 "$out/$id-$n.jpg"
done
ffmpeg -v error -y -i "$out/$id-1.jpg" -i "$out/$id-2.jpg" -i "$out/$id-3.jpg" -i "$out/$id-4.jpg" \
  -filter_complex "[0][1][2][3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0,scale=1100:-2" -q:v 5 "$tmp/sheets/$id.jpg"
rm -f "$v"
echo "$id ok dur=${dur%.*}s"
