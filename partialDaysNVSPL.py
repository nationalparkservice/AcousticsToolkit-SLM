def partial_days_NVSPL(iyore_dataset_path):
	'''
	Combs through an entire `iyore` dataset and moves incomplete days of NVSPL 
	to a new folder, "PartialDays_NVSPL".
	Assumes:
		- an AKR data structure with NVSPL in directories named \\01 DATA\\NVSPL'
	
	Parameters
    ----------
    iyore_dataset_path : str 
    	Absolute path to a folder containing an `iyore` .structure.txt file

	'''

	import numpy as np
	import os
	import pandas as pd
	import sys
	sys.path.append(r'C:\Users\DBetchkal\PythonScripts\3_GITHUB_REPOSITORIES\iyore')
	import iyore

	ds = iyore.Dataset(iyore_dataset_path)

	# determine which sites in the dataset have NVSPL files
	sitesWithNVSPL = set([entry.site for entry in ds.nvspl()])

	# then iterate through the sites with NVSPL...
	for site in sitesWithNVSPL:
	    
	    print("Currently processing", site)
	    
	    # find the unique days for which NVSPL exist
	    uniqueDays = [{'day':int(c[2:4]), 'month':int(c[0:2])} for 
	                  c in set([entry.month + entry.day for entry in ds.nvspl(site=site)])]
	    
	    
	    # iterate through those days
	    for day in uniqueDays:
	        
	        # finding the number of files that exist for each day
	        NVSPL_originalNames = [entry.path for entry in ds.nvspl(site=site, items=[day])]
	        length = len(NVSPL_originalNames)
	        

	        # if there isn't a full day of data...
	        if(length < 24):
	            
	            # first check to see if there is a 'PartialDays_NVSPL' folder
	            outPath = [entry.path for entry in ds.nvspl(site=site)][0].split("NVSPL")[0] + "PartialDays_NVSPL"
	            
	            if not os.path.exists(outPath):
	                
	                # if not, make the directory!
	                os.makedirs(outPath)
	                
	            # now process the output filenames for moving with os.rename
	            # first cut the filenames into pieces
	            splitPaths = [n.split("\\") for n in NVSPL_originalNames]

	            # replace 'NVSPL' with 'PartialDays_NVSPL'
	            for split in splitPaths:
	                split[4] = "PartialDays_NVSPL"  
	    
	            # and rejoin the split filenames again
	            NVSPL_renamed = ["\\".join(splits) for splits in splitPaths]
	        
	            # finally, move them.
	            for original, new in zip(NVSPL_originalNames, NVSPL_renamed):
	                
	                try:
	                    os.rename(original, new)
	                
	                except FileExistsError:
	                    print("PartialDays_NVSPL already exists for " + site + ".  Please address!!")
	                    
	            
	            # give an indicator of what happened
	            print("Moved", length, "files on", day)
	            
	    print("\n")
	    
	print("Finished!")