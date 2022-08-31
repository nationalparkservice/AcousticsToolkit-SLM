def create_LOUDEVENTS_AKR(iyore_dataset_path, site, year_sampled, source = "air"):
    
    """
    Calculates and saves an NSNSD LOUDEVENTS file to a site's Computational Outputs folder.
    
    Parameters
    ----------
    iyore_dataset_path: str, containing path to structure file for dataset in the format r"C:\"
    site: str, code for station deployment. Either w{4} or d{3} formats will be accepted.
    year_sampled: int, year the deployment was initated, in YYYY format.
    source: str.  Which subset of srcid codes to summarize - choose either "all" or "air".  Defaults to "air" if unspecified.
    
    Returns
    -------
    txt file in site's SPL Analysis folder
    """

    import soundDB
    import iyore
    import pandas as pd
    import numpy as np
    import datetime
    import os

    ds = iyore.Dataset(iyore_dataset_path) 
    
    # load the files required to make the LOUDEVENTS file
    dailypa = soundDB.dailypa(ds, site=site, year=year_sampled).combine()
    n = soundDB.nvspl(ds, site=site, year=year_sampled, columns=["dbA"]).combine()
    srcid = soundDB.srcid(ds, site=site, year=year_sampled).combine()
            
    
    # this next section creates a DataFrame that contains the "natural ambient level" for each hour in the record
    # the columns are hour of the day, the indices are the date
    
    sourceDict = {"air":"Total_1", "all":"Total_All"}
    
    indexes = []
    NaturalAmbient = pd.DataFrame([]) # create an empty dataframe
    
    # loop through each hour in the day
    for hour in range(24):
        
        # dailypa has columns that have zero-padded hour numbers followed by an h, i.e., "03h"
        hourStr = str(hour).zfill(2)+"h"
        h = dailypa[hourStr]
        
        # there's a lot going on in these two lines
        # but in essence, retrieve the source information of interest from dailypa and convert back to a percentage
        hourlyPAvalues = h[h.index.get_level_values('srcid') == sourceDict[source]].reset_index(level=1, drop=True)*(1/100)
        # then convert this percentage to a quantile value
        Ph = ((1 - hourlyPAvalues)/2) + hourlyPAvalues
        
        # this loop will then go through and calculate Lnat values for each day/hour combination
        # it's pretty slow...
        Lnats = []
        for tupl in Ph.iteritems():
            date, x = tupl
            year = int(date[0:4])
            month = int(date[5:7])
            day = int(date[8:10])
            currentHour = datetime.datetime(year, month, day, hour)
            plusOneHour = currentHour + datetime.timedelta(hours=1)

            indexes.append(date[0:10])
            
            Lnat = n[(n.index.get_level_values(1) >= currentHour)&
          (n.index.get_level_values(1) < plusOneHour)].quantile(x).values[0]

            print(currentHour, Lnat)

            Lnats.append(Lnat)

        NaturalAmbient[hourStr] = Lnats

    NaturalAmbient.index = sorted(list(set(indexes)))
    
    
    # remove all the srcid codes that indicate days without events
    srcid = srcid[srcid.srcID != 0.0]
    
    # if the source is restricted to aircraft prune out the other codes
    if(source == "air"):
        srcid = srcid[(srcid.srcID >= 1.0)&(srcid.srcID < 2.0)]

    # this massive line creates a DataFrame containing two columns:
    #    (1) a timestamp for each event with the date and the hour the event occurs in, rounded down
    #    (2) a boolean value that describes whether the MaxSPL of the event is > Lnat for that hour
    lE = pd.DataFrame([[datetime.datetime.strptime(str(timestamp)[0:10] + " " + str(timestamp.hour).zfill(2), "%Y-%m-%d %H"),
                                MaxSPL > NaturalAmbient.loc[str(timestamp)[0:10], str(timestamp.hour).zfill(2) + "h"]] 
                               for timestamp, MaxSPL in srcid["MaxSPL"].iteritems()], columns = ["datetime", "loud"])

    # these next two lines tidy up the previous dataframe by setting the index as the datetime
    # and then dropping the datetime column
    loudEvents = lE.set_index(lE.datetime)
    loudEvents = loudEvents.drop('datetime', 1)
 
    # generate the column headers for the LOUDEVENTS file
    columnHeaders = ["Date"]

    for i in range(3):

        if(i == 0):
            suffix = "h_nAbove"
        elif(i == 1):
            suffix = "h_nAll"
        elif(i == 2):
            suffix = "h_nPercent"

        for j in range(24):
            columnHeaders.append(str(j).zfill(2) + suffix)
    
    # set up the format of the LOUDEVENTS file
    FINAL = pd.DataFrame(columns = columnHeaders, index = sorted(list(set(indexes))))

    # group the events in the table by which hour they occured in
    groupbyHour = loudEvents.groupby(loudEvents.index)

    # then iterate through each of these hour-grouped clusters of events
    # and fill in the LOUDEVENTS file with
    #   (1) the total number of events
    #   (2) the number of those that are above Lnat
    #   (3) the percentage above Lnat
    for d in groupbyHour:

        hr = str(d[0])[11:13]
        date = str(d[0])[0:10]

        # h_nAbove
        FINAL.set_value(date,hr + "h_nAbove", np.sum(d[1].loud))
        # h_nAll
        FINAL.set_value(date,hr + "h_nAll", len(d[1].loud))
        # h_nPercent
        FINAL.set_value(date,hr + "h_nPercent", 100*(np.sum(d[1].loud)/len(d[1].loud)))

    # assign the date column the values from the index (the index will not be in the output txt file)
    FINAL["Date"] = FINAL.index
    
    # fill in the NaN values with either 0 or 100 where appropriate
    for i, column in enumerate(FINAL):
        
        if((i >= 1)&(i < 25)):
            FINAL[column].fillna(value=0, inplace=True)
        elif((i >= 25)&(i < 49)):
            FINAL[column].fillna(value=0, inplace=True)
        elif((i >= 49)&(i < 73)):
            FINAL[column].fillna(value=100, inplace=True)
    
    # set up the output directory
    basicFolder = str(set([e.year + " " + e.unit + e.site + " " + e.name for e in ds.srcid(site=site, year=year_sampled)]))
    basicFolder = ''.join( c for c in basicFolder if  c not in "{''}" )
    suffix = str(set([e.unit + e.site for e in ds.srcid(site=site, year=year_sampled)]))
    suffix = ''.join( c for c in suffix if  c not in "{''}" )
    OutDirectory = iyore_dataset_path + os.sep + basicFolder + os.sep + "02 ANALYSIS" + os.sep + "SPL Analysis"

    # write it out 
    FINAL.to_csv(OutDirectory + os.sep + 'LOUDEVENTS_' + suffix + '.txt', header=True, index=False, sep='\t')