#! /usr/bin/csh -f
#
#       Script to create the SkyPie table and graphics/thumbnails
#
# A typical month is about 50-100GB, and takes 20min to process
#
# Some useful shell commands to remember you might need as well.
#
# 
# umask 2
#
# chgrp -R allsky ASC
#
# chmod g+s ASC -R
#
# find . -type d -exec /n/astromake/opt/allsky/pyASC/ASC/SkyThumbs.csh '{}' \;


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

  echo " `date` ==================================== working on $dir "

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

  /usr/bin/time $asdir/SkyStats.py  $f  > $tmp.tab
  /usr/bin/time $asdir/SkyPie.py $tmp.tab
  convert $tmp.tab.png -transparent white -crop 400x400+128+64 -resize 40x40^   $tmp.tab.thumb.png
  echo Created $tmp.tab $tmp.tab.png $tmp.tab.thumb.png 

  chgrp allsky $tmp.*
end  


