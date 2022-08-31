def graphsR(iyore_dataset_path, repo_dir, unit, site, year_sampled):
    
    """
    Saves standard NSNSD graphics a site's Computational Outputs folder.
    
    Parameters
    ----------
    iyore_dataset_path: str, containing path to structure file for dataset in the format r"C:\"
    unit: str, code for NPS unit site was deployed in.  w{4}.
    site: str, code for station deployment. Either w{4} or d{3} formats will be accepted.
    year_sampled: int, year the deployment was initated, in YYYY format.

    
    Returns
    -------
    graphs in site's Computational Outputs folder
    """

    import numpy as np
    import pandas as pd
    import pyper as pr   
    from pyper import R
    import scipy as sp
    from scipy import stats
    import os.path
    import datetime
    import fnmatch

    import sys
    sys.path.append(os.path.join(repo_dir, "iyore"))
    sys.path.append(os.path.join(repo_dir, "soundDB"))
    sys.path.append(os.path.join(repo_dir, "derivedDataFunctions"))
    from soundDB import srcid
    import iyore
    from derivedDataFunctions import number_of_days_splatted

    ds = iyore.Dataset(iyore_dataset_path) # create an iyore dataset
    basicFolder = [os.path.basename(e.path) for e in ds.dataDir(unit=unit, site=site, year=year_sampled)][0]

    computationalOutDirectory = iyore_dataset_path + os.sep + basicFolder + os.sep + "02 ANALYSIS\Computational Outputs"
    dataDirectory = iyore_dataset_path + os.sep + basicFolder + os.sep + "02 ANALYSIS\SPL Analysis"
    
    
    if not os.path.exists(computationalOutDirectory):
        print("i'm taking the liberty of making a new folder for graphs and other computational outputs...")
        os.makedirs(computationalOutDirectory)
    
    # The remainder of the task uses PypeR, which uses R as a subprocess...
    
    r = R(RCMD="C:\\Program Files\\R\\R-3.5.3\\bin\\R", use_pandas = True) # start an instance of R
    r.run("rm(list=ls())")

    #get the number of analyzed days:
    n = number_of_days_splatted(srcid(ds, site=site, year=year_sampled).combine())
    r.assign("n", n)
    r.run('"numAnalyzedDays" <- as.character(n)') # used as input in 'graphs.r'

    # print the paths where data are coming from / where graphs are going
    metricsPath = dataDirectory + os.sep + "METRICS_" + unit + site + ".txt"
    metricsPath = metricsPath.replace("\\", "\\\\")
    print("metrics file to use:", metricsPath)
    computationalOutDirectory = computationalOutDirectory.replace("\\", "\\\\")
    print("graph output:", computationalOutDirectory)

    # assign the remaining variables required by 'graphs.r'
    r.assign("outDir", computationalOutDirectory)
    r.assign("metrics_path", metricsPath)
    r.run('filesToPlot <- as.character(metrics_path)')
    
    # now, actually run the R script!
    r.run('setwd("T:\\ResMgmt\\WAGS\\Sound\\Applications\\R\\")') # here's where the R script lives
    r.run("source('graphs130903_modified.r', local = FALSE)") #run Damon's 'graphs.r' script