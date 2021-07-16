#! /usr/bin/csh -f
#
#    create the table and pictures/thumbnails

source /n/astromake/astromake_start.csh
astroload python
set asdir=/n/astromake/opt/allsky/pyASC/ASC/

if ($#argv == 1) then
   set dir=$1
else
   set dir=.
endif

if ( ! -d $dir ) then
  echo $dir is not a directory
  exit 0
endif

set f=(`ls $dir/*.FIT $dir/*.fits`)
set nf=$#f
echo Found $nf

if ($nf == 0) then
   echo No files to process
   exit 0
endif


set tmp=$dir/sky
set tmp=/tmp/sky

$asdir/SkyStats.py  $f  > $tmp.tab
$asdir/SkyPie.py $tmp.tab
convert $tmp.tab.png -transparent white -crop 400x400+128+64 -resize 40x40^   $tmp.tab.thumb.png

echo Created $tmp.tab $tmp.tab.png $tmp.tab.thumb.png 
