This is the webtree as you should find it on http://mdallsky.astro.umd.edu/

This is located on luna.astro.umd.edu:/n/www/mdallsky  so do not edit files
if you are not in a managed git tree. Or run the risk at an update they will
be overwritten.
We now maintain a script mdallsky_update which should maintain updates and
contains info on the current configuration if it would be updated in the future.

The http server uses /etc/httpd/conf/httpd.conf
In 2020 we are restucturing the OS and files, so this will likely wind up somewhere else
(indeed, this needs an update) 

The way this tree is structured, it assumes the docroot to be the root of this directory,
so it's currently not easy to get the full experience if you view it "locally".

