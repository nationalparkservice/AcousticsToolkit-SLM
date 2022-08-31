def reportingGraphicsAKR(iyore_dataset_path, unit, site, year_sampled):

    import iyore
    import soundDB
    import pandas as pd 
    import pathlib
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as pe
    import matplotlib.lines as mlines
    import matplotlib
    import math
    import numpy as np
    import datetime
    import os.path
    import os
    import scipy as sp
    from scipy import stats
    import fnmatch
    import traceback
    
    #===================================================================================================================
    # Setup properties of the plots and file I/O
    #===================================================================================================================

    matplotlib.style.use('ggplot') #perhaps it'd be worthwhile to develop my own style:  http://matplotlib.org/users/style_sheets.html
    titles = False

    #initialize a lot of the generic qualities of plots:
    ax_width = 14.00
    ax_height = 8.00
    figsize = (ax_width, ax_height)
    
    
    ds = iyore.Dataset(iyore_dataset_path)
    sitename = site
    
    # check to see if you need to implement DENA Backcountry Management Plan indications on these plots
    if(unit == 'DENA'):

        DENA = True

        standardLookup = {
        'LOW':{
            'PA':5, 'EVENTS':1, 'SPL':40
        },
        'MEDIUM':{
            'PA':15, 'EVENTS':10, 'SPL':40
        },
        'HIGH':{
            'PA':25, 'EVENTS':25, 'SPL':60
        },
        'VERY HIGH':{
            'PA':50, 'EVENTS':50, 'SPL':60
        }
        }

        meta = pd.read_excel(r"V:\Complete_Metadata_AKR_2001-2017.xlsx")
        zone = meta[meta.code == sitename]["BCMP_zone"].values[0]

    else:
        DENA = False

    # set up the outupt directory folder

    folders = os.listdir(iyore_dataset_path)
    # print(folders)

    pattern = str(year_sampled) + ' ' + unit + site + ' *'
    basicFolder = fnmatch.filter(folders, pattern)[0]

    computationalOutDirectory = iyore_dataset_path + os.sep + basicFolder + os.sep + "02 ANALYSIS\Computational Outputs"

    print("Output Directory:", computationalOutDirectory)

    if not os.path.exists(computationalOutDirectory):
        print("i'm taking the liberty of making a new folder for graphs and other computational outputs...")
        os.makedirs(computationalOutDirectory)

    # calculate the hours for which data were successfully collected
    sampledhours = [datetime.datetime.strptime(e.year+e.month+e.day+e.hour, "%Y%m%d%H") for e in ds.nvspl(site=sitename)]
    dataRange = pd.Series([150 for i in range(len(sampledhours))])
    dataRange.index = sampledhours
    
    #===================================================================================================================
    # Plot 1: 'Aircraft Sound, Percentage of Time Audible'
    # From DailyPA, take all the Total_1 rows from 00h - 23h. 
    # Then, in chronological order by date, make a series out of all of these
    # Plot that series as a bar chart.
    #===================================================================================================================
    
    try:
        dailyPA = soundDB.dailypa(ds, site=sitename, year=year_sampled).combine()

        data = dailyPA.loc[(slice(None), "Total_1"), "00h":"23h"] # right now plots only AIRCRAFT

        # create a pandas series that contains hourly PA values and is indexed by datetime of each hour
        indexer = []
        hourlyPAs = []
        for index, day in data.iterrows():
            for i, hour in enumerate(day):
                indexer.append(pd.Timestamp(index[0]) + pd.to_timedelta(pd.to_numeric(day.index[i][:2]), unit='h'))
                hourlyPAs.append(hour)

        plotdata = pd.Series(hourlyPAs)
        plotdata.index = indexer


        fig1= plt.figure(figsize = figsize, dpi=600)
        ax = fig1.add_subplot(1,1,1, facecolor=(0.968627, 0.968627, 0.968627)) # gray background

        # plot the range over which where were valid data.  zorder parameter makes this the bottom layer in drawing order
        ax.bar(dataRange.index, dataRange, color='lightgray', edgecolor='None', fc=(1,  1,  1), zorder=-50)

        # against white data ranges grey grid lines look good
        ax.yaxis.grid(True, which="major", linestyle="-", color='#D6D6D6') 


        ax.bar(plotdata.index, plotdata,width=1/24, color="black", edgecolor='black')
        if(titles):  # if titles are turned on, the plot will have one.
            plt.title(sitename + ": Aircraft Sound, Percentage of Time Audible For Every Hour")

        plt.tick_params(top='off', left='off', right='off') # turn off all but bottom tick marks
        plt.ylabel("Percentage of Time Audible (%)")
        plt.xlabel("Date", labelpad=15)
        plt.xlim(plotdata.index[0], plotdata.index[-1])
        plt.ylim(0, 100)


        if(DENA): # for now, only Denali has standards

            #find the PA standard for this site.  it will be used to make a horizontal line across PA plots
            try:
                std = standardLookup[zone]['PA']
                ax.axhline(y=std, linestyle="-.", color="grey")
                plt.figtext(0.13, 0.0078*std+0.128, "BCMP Standard", size="small", color="black", path_effects=[pe.withStroke(linewidth=3, foreground="white")], alpha = 0.65)
            except KeyError:
                pass


        savePath = computationalOutDirectory + os.sep + unit + site + "_PA"   
        plt.savefig(str(savePath) +".png", bbox_inches='tight')
        plt.savefig(str(savePath) +".svg", bbox_inches='tight', dpi=600) # scalable vector graphics!  cool.
    
    except:
        print("There was an error with Plot 1!")
        traceback.print_exc()
    
    #===================================================================================================================
    # Plot 2: 'Aircraft Sound, Average Percentage of Time Audible'
    # take all the Total_1 rows from 00h - 23h,  plot as a box plot.
    #===================================================================================================================    

    try:
        dailyPA = soundDB.dailypa(ds, site=sitename, year=year_sampled).combine()

        data = dailyPA.loc[(slice(None), "Total_1"), "00h":"23h"]
        t =[hour for hour in data]

        fig = plt.figure(figsize = figsize, dpi=600) # intialize an instance of a figure
        ax2 = fig.add_subplot(1,1,1, facecolor="white") # initialize an instance of an axis, and make the background white
        ax2.yaxis.grid(True, which="major", linestyle="-", color='#D6D6D6') # but because the background is white, make the grid lines gray

        # set up the format of the box plots
        stroke = 'k'
        alpha_set = 0.3
        boxprops = dict(linestyle='-', linewidth=1, color=stroke, alpha = alpha_set)
        whiskerprops = dict(linestyle=':', linewidth=1, color=stroke, alpha = 0.4)
        capprops = dict(linestyle='-', linewidth=1, color=stroke, alpha = alpha_set)
        flierprops= dict(marker='x', markeredgewidth=1, color=stroke, alpha=0.15)
        medianprops = dict(linestyle='-', linewidth=2, color=stroke)

        plt.boxplot(data.values, notch=False, showfliers=True, showbox=True, 
                          meanline=True, showmeans=False, flierprops=flierprops,
                          capprops=capprops, boxprops=boxprops, whiskerprops=whiskerprops, medianprops=medianprops)

        if(titles):  # if titles are turned on, the plot will have one.
            plt.title(sitename + ": Hourly Percentage of Time Audible, Aircraft")

        plotO = str(data.index[0][0]).replace("-", "/")  # replace the dashes in the dates with backslashes
        plotF = str(data.index[-1][0]).replace("-", "/") 
        plt.xlabel(plotO[5:] + "  -  " + plotF[5:], labelpad=15) # and add just MM/DD to the plot

        labels = [datetime.datetime.strptime(str(tick), "%H").strftime('%H:%M') #this formats labels into times (0L:00)
         for tick,label in zip(range(24),ax2.get_xticklabels())]

        ax2.set_xticklabels(labels, size='small')  # and them actually change the labels for each boxplot
        plt.tick_params(top='off', bottom='off', left='off', right='off') # turn off all tick marks
        plt.ylabel("Percentage of Time Audible (%)", labelpad=10) 
        plt.ylim(-1, 100) # having the y-axis go slightly below 0 allows the median bars to be seen clearly

        savePath = computationalOutDirectory + os.sep + unit + site + "_HOURLYPA"  
        plt.savefig(str(savePath) +".png", bbox_inches='tight')
        plt.savefig(str(savePath) +".svg", bbox_inches='tight', dpi=600) # scalable vector graphics!  cool.

    except:
        print("There was an error with Plot 2!")
        traceback.print_exc()

        
    #===================================================================================================================
    # Plot 3: 'Number of Aicraft Events Per Day Over Natural Ambient Level'
    # from Loudevents, sum 00h_nAbove - 23h_nAbove for each row. plot as time series.
    #===================================================================================================================
    
    try:
        loudevents = soundDB.loudevents(ds, site=sitename, year=year_sampled).combine()

        loudevents["above"]
        dates = []
        eventsperday = []
        for index, values in loudevents["above"].iterrows():
            eventsperday.append(values.sum())
            dates.append(index)

        print(len(dates), " days")
        fig = plt.figure(figsize = figsize, dpi=200)
        # ax = fig.add_subplot(1,1,1, facecolor="white")
        ax = fig.add_subplot(1,1,1, facecolor=(0.968627, 0.968627, 0.968627)) # gray background
        ax.scatter(dates,eventsperday, color="black", zorder=100)

        def roundup(x):
            return int(math.ceil(x / 5.0)) * 5

        a, b = ax.get_ylim()
        if(max(eventsperday) < 20):
            plt.ylim(-1, 20)
        elif(max(eventsperday) >= 100):
            plt.ylim(-1, b)
        else:
            plt.ylim(-1, roundup(max(eventsperday)+1))


        # plot the range over which where were valid data.  zorder parameter makes this the bottom layer in drawing order
        ax.bar(dataRange.index, dataRange, color='lightgray', edgecolor='None', fc=(1,  1,  1), zorder=-50)


        ax.yaxis.grid(True, which="major", linestyle="-", color='#D6D6D6') # but because the background is white, make the grid lines gray


        # ax.plot(dates,eventsperday, linestyle=':', color="black", alpha=0.2)
        print("Median of", np.median(eventsperday), "events per day")
        print("Average of", "{:.1f}".format(np.mean(eventsperday)), "events per day")

        if(unit == 'DENA'):
            std = standardLookup[zone]['EVENTS']
            ax.axhline(y=std, linestyle="-.", color="grey")
            plt.figtext(0.13, 0.0078*std+0.129, "BCMP Standard", size="small", color="black", path_effects=[pe.withStroke(linewidth=3, foreground="white")], alpha = 0.65)


        plt.tick_params(top='off', left='off', right='off') # turn off all but bottom tick marks
        plt.xlim(dates[0]-pd.Timedelta('1 days'), dates[-1]+pd.Timedelta('1 days'))




        if(titles):  # if titles are turned on, the plot will have one.
            plt.title(sitename + ": Number of Aicraft Events Per Day Over Natural Ambient Level")

            plt.ylabel("Number of Events Per Day")
        plt.xlabel("Date", labelpad=15)


        savePath = computationalOutDirectory + os.sep + unit + site + "_EventsPerDay"
        plt.savefig(str(savePath) +".png", bbox_inches='tight')
        plt.savefig(str(savePath) +".svg", bbox_inches='tight', dpi=600) # scalable vector graphics!  cool.

        print()
        W, p = sp.stats.shapiro(eventsperday)
        print("Shapiro-Wilk test of normality")
        print("p =", "{:.7f}".format(p))

    except:
        print("There was an error with Plot 3!")  
        traceback.print_exc()
        
        
    #===================================================================================================================
    # Plot 4: 'Hourly Aircraft Event Distribution'
    # from Loudevents, plot the data in 00h_nAbove - 23h_nAbove as a box plot
    #===================================================================================================================
    try:
        loudevents = soundDB.loudevents(ds, site=sitename, year=year_sampled).combine()

        d = loudevents["above"]

        fig = plt.figure(figsize = figsize, dpi=600) # intialize an instance of a figure
        ax2 = fig.add_subplot(1,1,1, facecolor="white") # initialize an instance of an axis, and make the background white
        ax2.yaxis.grid(True, which="major", linestyle="-", color='#D6D6D6') # but because the background is white, make the grid lines gray

        # set up the format of the box plots
        stroke = 'k'
        alpha_set = 0.3
        boxprops = dict(linestyle='-', linewidth=1, color=stroke, alpha = alpha_set)
        whiskerprops = dict(linestyle=':', linewidth=1, color=stroke, alpha = 0.4)
        capprops = dict(linestyle='-', linewidth=1, color=stroke, alpha = alpha_set)
        flierprops= dict(marker='x', markeredgewidth=1, color=stroke, alpha=0.15)
        medianprops = dict(linestyle='-', linewidth=2, color=stroke)

        plt.boxplot(d.values, notch=False, showfliers=True, showbox=True, 
                          meanline=True, showmeans=False, flierprops=flierprops, 
                          capprops=capprops, boxprops=boxprops, whiskerprops=whiskerprops, medianprops=medianprops)

        if(titles):  # if titles are turned on, the plot will have one.
            plt.title(sitename + ": Hourly Aircraft Event Distribution")

        plotO = str(d.index[0]).replace("-", "/")  # replace the dashes in the dates with backslashes
        plotF = str(d.index[-1]).replace("-", "/") 
        plt.xlabel(plotO[5:10] + "  -  " + plotF[5:10]) # and add just MM/DD to the plot

        labels = [datetime.datetime.strptime(str(tick), "%H").strftime('%H:%M') #this formats labels into times (0L:00)
         for tick,label in zip(range(24),ax2.get_xticklabels())]

        ax2.set_xticklabels(labels, size='small')  # and them actually change the labels for each boxplot
        plt.tick_params(top='off', bottom='off', left='off', right='off') # turn off all tick marks
        plt.ylabel("Number of Events") 
        a, b = ax2.get_ylim()
        if(b > 15):
            plt.ylim(-1, b)
        elif(b <= 15):
            plt.ylim(-1, 15)


        savePath = computationalOutDirectory + os.sep + unit + site + "_HOURLYEVENTS"
        plt.savefig(str(savePath) +".png", bbox_inches='tight')
        plt.savefig(str(savePath) +".svg", bbox_inches='tight', dpi=600) # scalable vector graphics!  cool.

    except:
        print("There was an error with Plot 4!")  
        traceback.print_exc()
    
    #===================================================================================================================
    # Plot 5: 'Number of Aicraft Events Per Day Over Natural Ambient Level'
    # from Loudevents, sum 00h_nAbove - 23h_nAbove for each row. plot as time series.
    #===================================================================================================================
    try:
        loudevents = soundDB.loudevents(ds, site=sitename, year=year_sampled).combine()

        fig = plt.figure(figsize = figsize, dpi=200)
        ax = fig.add_subplot(1,1,1, facecolor="white")
        ax.yaxis.grid(True, which="major", linestyle="-", color='#D6D6D6') # but because the background is white, make the grid lines gray
        plt.tick_params(top='off', left='off', right='off') # turn off all but bottom tick marks
        plt.hist(eventsperday, bins=list(range(0,105,5)), color="k")
        if(titles):  # if titles are turned on, the plot will have one.
            plt.title(sitename + ": Number of Days on which the Event Frequency Was Observed")

        a, b = ax.get_ylim()
        if(b > 20):
            plt.ylim(0, b)
        elif(b <= 20):
            plt.ylim(0, 20)    

        plt.xlabel("Number of Overflight Events Per Day Over the Natural Ambient Level  (Bin Size = 5 events)")
        plt.ylabel("Number of Days Observed")


        savePath = computationalOutDirectory + os.sep + unit + site + "_EventsPerDayHistogram"
        plt.savefig(str(savePath) +".png", bbox_inches='tight')
        plt.savefig(str(savePath) +".svg", bbox_inches='tight', dpi=600) # scalable vector graphics!  cool

    except:
        print("There was an error with Plot 5!")  
        traceback.print_exc()
        
    #===================================================================================================================
    # Plot 6: 'Box Plot of Noise Free Intervals'
    #===================================================================================================================
    try:
        srcid = soundDB.srcid(ds, site=sitename, year=year_sampled).combine()

        #first let's get some noise free intervals
        dt = srcid.index.to_series()
        dt.sort()

        tds = []
        tds_hrs = []
        max_delta = 0
        min_delta = 1000000000
        for i in range(len(dt)+1):
            if(i < len(dt)-1):
                timedelta = dt[i+1] - dt[i]

                if(timedelta.total_seconds() > max_delta):
                    max_delta = timedelta.total_seconds()

                if(timedelta.total_seconds() < min_delta):
                    min_delta = timedelta.total_seconds()

                tds.append(timedelta)
                tds_hrs.append(timedelta.total_seconds()/3600)

        tds = pd.Series(tds)  
        tds_hrs = pd.Series(tds_hrs)

        # now, set up the plot
        fig = plt.figure(figsize = figsize, dpi=600) # intialize an instance of a figure
        ax2 = fig.add_subplot(111, facecolor="white") # initialize an instance of an axis, and make the background white
        ax2.yaxis.grid(True, which="major", linestyle="-", color='#D6D6D6') # but because the background is white, make the grid lines gray

        # set up the format of the box plots
        stroke = 'k'
        alpha_set = 0.3
        boxprops = dict(linestyle='-', linewidth=1, color=stroke, alpha = alpha_set)
        whiskerprops = dict(linestyle=':', linewidth=1, color=stroke, alpha = 0.4)
        capprops = dict(linestyle='-', linewidth=1, color=stroke, alpha = alpha_set)
        # flierprops= dict(marker='x', markeredgewidth=1, color=stroke, alpha=0.15)
        medianprops = dict(linestyle='-', linewidth=2.4, color=stroke)

        plt.boxplot(tds_hrs, notch=True, showfliers=False, showbox=True, 
                          meanline=True, showmeans=False, 
                          capprops=capprops, boxprops=boxprops, whiskerprops=whiskerprops, medianprops=medianprops)

        if(titles):  # if titles are turned on, the plot will have one.
            plt.title(sitename + ": Boxplot of Noise Free Intervals")

        ax2.get_yaxis().get_major_formatter().set_scientific(False)
        ax2.set_xticklabels("", size='medium')  
        ax2.tick_params(axis='y',which='major',right='off', left="off")
        ax2.tick_params(axis='x',which='major',top='off', bottom='off')

        plt.xlabel("Noise Free Intervals from  " + str(dt.irow([0]))[5:10].replace("-","/") + " to " \
                   + str(dt.irow([-1]))[5:10].replace("-","/"))
        plt.ylabel("Interval Length (hours)")
        plt.text(1.1, tds_hrs.median(), "Median of:  {:.2f}".format(tds_hrs.median()) \
                 + " hours  (about " + "{:.0f}".format(tds_hrs.median()*60) + " minutes)")

        a, b = ax2.get_ylim()
        if(b > 1):
            plt.ylim(0, b)
        elif(b <= 1):
            plt.ylim(0, 1)  


        savePath = computationalOutDirectory + os.sep + unit + site + "_NFIBoxplot"
        plt.savefig(str(savePath) +".png", bbox_inches='tight')
        plt.savefig(str(savePath) +".svg", bbox_inches='tight', dpi=600) # scalable vector graphics!  cool

    except:
        print("There was an error with Plot 6!")  
        traceback.print_exc() 
    
    #===================================================================================================================
    # Plot 7: 'Maximum One-Second SPL for Each Vehicle Event'
    #===================================================================================================================
    try:
        srcid = soundDB.srcid(ds, site=sitename, year=year_sampled).combine()
        maxSPL = srcid.loc[:,'MaxSPL'] 
        srcID = srcid.loc[:,'srcID'] 


        data = pd.DataFrame(maxSPL)
        data['srcID'] = srcID

        fig = plt.figure(figsize = figsize, dpi=200)
        # ax = fig.add_subplot(1,1,1, facecolor="white")
        ax = fig.add_subplot(1,1,1, facecolor=(0.968627, 0.968627, 0.968627)) # gray background

        # plot the range over which where were valid data.  zorder parameter makes this the bottom layer in drawing order
        ax.bar(dataRange.index, dataRange, color='lightgray', edgecolor='None', fc=(1,  1,  1), zorder=-50)

        ax.yaxis.grid(True, which="major", linestyle="-", color='#D6D6D6') # but because the background is white, make the grid lines gray

        # filled_markers = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd')
        # fillstyles = ('full', 'left', 'right', 'bottom', 'top', 'none')
        def choose_marker(ID):
            style_dict = {
                1.1: ["o", mlines.Line2D.fillStyles[5], "#c1a800", "Jet"],
                1.2: ["o", mlines.Line2D.fillStyles[0], "#1d309b", "Propeller"],
                1.3: ["o", mlines.Line2D.fillStyles[1], "#ec7500", "Helicopter"],
                2.0: ["s", mlines.Line2D.fillStyles[0], "#9d2a79", "Road Vehicle"],
                2.1: ["s", mlines.Line2D.fillStyles[0], "#9d2a79", "Road Vehicle"],
                2.2: ["s", mlines.Line2D.fillStyles[0], "#9d2a79", "Road Vehicle"],
                2.3: ["s", mlines.Line2D.fillStyles[0], "#9d2a79", "Road Vehicle"],
                3.0: ["*", mlines.Line2D.fillStyles[0], "#0f9ec1", "Watercraft"],
                4.1: ["x", mlines.Line2D.fillStyles[5], "#9d2a79", "Snowmachine"]
            }
            # Get the function from switcher dictionary
            func = style_dict.get(ID, ["", "none", "#fffff", ""])

            # Execute the function
            return func


        srcIDs_annotated = sorted(list(set([ float("{:.1f}".format(x)) if int(x) == 1 else float("{:.2f}".format(int(x))) for x in srcid["srcID"] ])))
        for ID in srcIDs_annotated:
            testData = data.loc[srcid.srcID.apply(lambda x: float("{:.1f}".format(x)) if int(x) == 1 else float("{:.2f}".format(int(x)))) == ID, :]
            styles = choose_marker(ID)
            ax.plot(testData.index,testData['MaxSPL'], markersize = 4, markerfacecolor=styles[2], markeredgecolor=styles[2], linestyle="", marker=styles[0], fillstyle=styles[1], label=styles[3])

        plt.axis((data.index[0]-datetime.timedelta(days=2),data.index[-1]+datetime.timedelta(days=4),0,100)) # set up the axes

        if(titles):  # if titles are turned on, the plot will have one.
            plt.title(sitename + ": Maximum One-Second SPL for Each Motorized Event")

        plt.tick_params(top='off', left='off', right='off') # turn off all but bottom tick marks
        plt.ylabel("Maximum Sound Pressure Level (dBA)")
        plt.xlabel("Date")

        if(DENA):
            try:
                std = standardLookup[zone]['SPL']
                ax.axhline(y=std, linestyle="-.", color="grey")
                plt.figtext(0.13, (0.0095*std), "BCMP Standard", size="small", color="black", path_effects=[pe.withStroke(linewidth=3, foreground="white")], alpha = 0.65)
            except KeyError:
                pass

        legend = plt.legend(frameon = 1, bbox_to_anchor=(1.2, 1))

        frame = legend.get_frame()
        frame.set_facecolor((1, 1, 1, 0.5))
        frame.set_edgecolor('#D6D6D6')


        savePath = computationalOutDirectory + os.sep + unit + site + "_MAXSPL"
        plt.savefig(str(savePath) +".png", bbox_inches='tight')
        plt.savefig(str(savePath) +".svg", bbox_inches='tight', dpi=600) # scalable vector graphics!  cool.
        plt.show()

    except:
        print("There was an error with Plot 7!")  
        traceback.print_exc()  
    
    #===================================================================================================================
    # Plot 8: 'Histogram of Maximum Sound Pressure Levels for All Aircraft'
    #===================================================================================================================
    try:
        srcid = soundDB.srcid(ds, site=sitename, year=year_sampled).combine()

        fig = plt.figure(figsize = figsize, dpi=200)
        ax = fig.add_subplot(1,1,1, facecolor="white")
        ax.yaxis.grid(True, which="major", linestyle="-", color='#D6D6D6') # but because the background is white, make the grid lines gray
        spls = [srcid.loc[(srcid.srcID >= 1.0) & (srcid.srcID < 2.0), 'MaxSPL']]
        plt.hist(spls, bins=list(range(0,102,2)),color= "black") #figsize= figsize)
        if(titles):
            plt.title(sitename + ": Histogram of Maximum Sound Pressure Levels for All Aircraft")

        med = np.median(spls)
        ax.axvline(x=med, linestyle="--", color="lightgrey")

        plt.tick_params(top='off', left='off', right='off') # turn off all but bottom tick marks
        plt.xlabel("Maximum A-Weighted Sound Pressure Level  (Bin Size = 2 dBA)")
        plt.ylabel("Number of Observations")
        top = 0
        a, b = ax.get_ylim()
        if(b > 30):
            plt.ylim(0, b)
            top = b
        elif(b <= 30):
            plt.ylim(0, 30)
            top = 30
        plt.text(med + 1, top - 2, "Median SPL: " + str(med) + " dBA", color="#b3b3b3")


        savePath = computationalOutDirectory + os.sep + unit + site + "_MaxSPLHistogram"
        plt.savefig(str(savePath) +".png", bbox_inches='tight')
        plt.savefig(str(savePath) +".svg", bbox_inches='tight', dpi=600) # scalable vector graphics

        W, p = sp.stats.shapiro(spls[0])
        print("Shapiro-Wilk test of normality")
        print("p =", "{:.7f}".format(p))

    except:
        print("There was an error with Plot 8!")  
        traceback.print_exc()  