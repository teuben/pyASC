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

set f=(`ls $dir/*.FIT`)
set nf=$#f
echo Found $nf

if ($nf == 0) then
   echo No files to process
   exit 0
endif


set tmp=/tmp/tmp$$

$asdir/SkyStats.py  $f  > $tmp.tab
$asdir/SkyPie.py $tmp.tab

