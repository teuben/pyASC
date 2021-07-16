#! /usr/bin/csh -f
#
#    create the table and pictures/thumbnails

source /n/astromake/astromake_start.csh
astroload python
set asdir=/n/astromake/opt/allsky/pyASC/ASC/


if ($#argv == 0) then
  set dirs=(.)
else
  set dirs=($*)
endif

# make sure group can write too
umask 2

foreach dir ($dirs)

  echo " ==================================== working on $dir "

  if ( ! -d $dir ) then
    echo $dir is not a directory
    continue
  endif

  set f=(`ls $dir/*.FIT $dir/*.fits`)
  set nf=$#f
  echo Found $nf

  if ($nf == 0) then
     echo No files to process in $dir
     continue
  endif


  set tmp=$dir/sky

  $asdir/SkyStats.py  $f  > $tmp.tab
  $asdir/SkyPie.py $tmp.tab
  convert $tmp.tab.png -transparent white -crop 400x400+128+64 -resize 40x40^   $tmp.tab.thumb.png
  echo Created $tmp.tab $tmp.tab.png $tmp.tab.thumb.png 

end  


# chgrp midas $tmp.*
#
# chmod g+s ASC -R 
