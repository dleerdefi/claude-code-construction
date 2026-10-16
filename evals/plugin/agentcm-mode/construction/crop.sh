#!/bin/sh
# AgentCM: a box of a sheet as a PNG, to look at what the text files point to (roadmap 2.14e).
# Written with the agent files, which rewrite it: do not edit it.
#
#   sh .construction/crop.sh <sheet> <x> <y> <w> <h>
#
# <sheet> is the sheet's file name in .construction/sheets/ (its number, as INDEX.md gives it).
# x, y, w and h are the box as the sheet files give positions: 0 to 1 from the top left of the
# sheet. The PNG goes to .construction/crops/ (the newest 20 are kept) and its path is printed.
set -eu
if [ "$#" -ne 5 ]; then
  echo "usage: sh .construction/crop.sh <sheet> <x> <y> <w> <h> (0 to 1 from the top left of the sheet)" >&2
  exit 1
fi
sheet=$1 x=$2 y=$3 w=$4 h=$5
here=$(cd "$(dirname "$0")" && { pwd -W 2>/dev/null || pwd; })
root=$(dirname "$here")
case "$sheet" in
  'A-101') pdf='drawings/A-101.pdf'; page=1 ;;
  'A-102') pdf='drawings/A-102.pdf'; page=1 ;;
  'A-103') pdf='drawings/A-103.pdf'; page=1 ;;
  'A-601') pdf='drawings/A-601.pdf'; page=1 ;;
  'A-602') pdf='drawings/A-602.pdf'; page=1 ;;
  *) echo "crop: no sheet named $sheet; the sheets are listed in .construction/INDEX.md" >&2; exit 1 ;;
esac
default_bin=''
bin=${AGENTCM_POPPLER_BIN:-$default_bin}
if [ -n "$bin" ]; then pdfinfo="$bin/pdfinfo"; pdftoppm="$bin/pdftoppm"; else pdfinfo=pdfinfo; pdftoppm=pdftoppm; fi
if ! info=$("$pdfinfo" -box -f "$page" -l "$page" "$root/$pdf" 2>/dev/null); then
  echo "crop: Poppler's pdfinfo could not read $pdf: install Poppler, or set AGENTCM_POPPLER_BIN to its folder" >&2
  exit 1
fi
size=$(printf '%s\n' "$info" | sed -n 's/^Page *[0-9]* MediaBox: *\([-0-9.]*\) *\([-0-9.]*\) *\([-0-9.]*\) *\([-0-9.]*\).*/\1 \2 \3 \4/p' | head -n 1)
rot=$(printf '%s\n' "$info" | sed -n 's/^Page *[0-9]* rot: *\([0-9]*\).*/\1/p' | head -n 1)
plan=$(awk -v s="$size" -v rot="${rot:-0}" -v x="$x" -v y="$y" -v w="$w" -v h="$h" -v edge=2576 -v pixels=3750000 'BEGIN {
  num = "^[0-9]*[.]?[0-9]+$"
  if (x !~ num || y !~ num || w !~ num || h !~ num) { print "bad"; exit }
  if (split(s, a, " ") < 4) { print "nosize"; exit }
  pw = a[3] - a[1]; ph = a[4] - a[2]
  if (rot % 180 == 90) { t = pw; pw = ph; ph = t }
  if (w <= 0 || h <= 0 || x + w > 1.0001 || y + h > 1.0001) { print "bad"; exit }
  bw = w * pw / 72; bh = h * ph / 72
  dpi = 200
  long = bw > bh ? bw : bh
  if (long * dpi > edge) dpi = edge / long
  if (bw * bh * dpi * dpi > pixels) dpi = sqrt(pixels / (bw * bh))
  dpi = int(dpi)
  if (dpi < 150) { print "small " dpi; exit }
  printf "%d %d %d %d %d\n", dpi, int(x * pw * dpi / 72 + 0.5), int(y * ph * dpi / 72 + 0.5), int(w * pw * dpi / 72 + 0.5), int(h * ph * dpi / 72 + 0.5)
}')
case "$plan" in
  bad) echo "crop: x, y, w and h are fractions of the sheet, 0 to 1 from the top left, and the box must lie on it" >&2; exit 1 ;;
  nosize) echo "crop: pdfinfo gave no MediaBox for page $page of $pdf" >&2; exit 1 ;;
  small*) echo "crop: this box is too large to read: within 2576 px it would be ${plan#small } dpi, under 150; crop a smaller box" >&2; exit 2 ;;
esac
set -- $plan
mkdir -p "$here/crops"
name="${sheet}_${x}_${y}_${w}_${h}"
if ! "$pdftoppm" -f "$page" -l "$page" -r "$1" -x "$2" -y "$3" -W "$4" -H "$5" -png -singlefile "$root/$pdf" "$here/crops/$name"; then
  echo "crop: Poppler's pdftoppm could not render page $page of $pdf" >&2
  exit 1
fi
ls -t "$here/crops"/*.png 2>/dev/null | tail -n +21 | while IFS= read -r old; do rm -f "$old"; done
echo "$here/crops/$name.png"
