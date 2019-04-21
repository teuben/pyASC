#! /usr/bin/env python
import argparse as ap
import glob
import datetime



if __name__ == "__main__":
    path = '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] to [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    parser = ap.ArgumentParser()
    parser.add_argument('-i','--filein', nargs=1, help = 'Directory of outputs of try_astride.py')

    args = vars(parser.parse_args())
    
    if args['filein'] != None: 
        file_path = (args['filein'][0])
    else:
        # example directory match "2019-12-02 to 2019-12-03"
        list_dir = glob.glob(path)
        #module called filepath that can use instead of glob.glob
        file_path = max(list_dir, key = lambda f:datetime.date(int(f[0:4]),int(f[5:7]),int(f[8:10]))) 
        
    summary = open(file_path+"/summary.txt", 'r')

    for line in summary:
        if line.startswith("Streaks detected:"):
            print(line[18:])

