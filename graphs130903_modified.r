#########################################################################
#
#	INPUT:	METRICS_xxxx.txt file produced by the HourlyMetrics program
#
#	OUTPUT:	Several standardized plots used by the National Park Service
#			
#			Hourplot:	Median hourly wideband dBA values
#
#			Freqplot	L10, L50, [Lnat], and L90 1/3 octave band plots 
#			Contour:	Plot with Hour on the X-axis, Frequency on the Y
#						axis.
#
#	USAGE:	Change any parameters down in the next section, run the
#			script in R. Plots will be produced in the directory chosen
#			by user in dialog box
#
#	ABOUT:	Written by Damon Joyce (damon_joyce@nps.gov)
#			2010.11.23
#
#########################################################################
#if(!exists(readMetrics, mode="function")) source("readMetrics.r")
#Begin User settings#####################################################

#Produce titles on plots? [T/F]
titlesOnPlots 	<-	F

#Which plots to produce? [T/F]
plotHRDBA 	<- 	T
plotTRUNCDBA 	<-	T
plotFREQDB 	<-	T
plotCONTOUR 	<-	T
plotPA 		<- 	T

#Plot the high and low frequencies? [T/F] (F when NVSPLs come from converted audio)
plotHLhz <- T

#How many days were analyzed for Lnat?
  # now passed in from Python!

#What's the upper limit for the hourly and frequency graphs? (must be a multiple of 3)
yMaxHr <- 50
yMaxHz <- 70

#What's the lower limit for the hourly and frequency graphs? (must be a multiple of 3)
yMinHr <- 5
yMinHz <- -12

#End User settings#######################################################

plotHRDBACOMB <- c(plotHRDBA, plotTRUNCDBA)

low20NF <- c(9.3,8.5,7.5,6.5,5.6,4.75,3.9,3.2,2.5,1.75,0.75,0.25,-0.25,-0.5,-0.75,-0.75,-0.75,-0.6,-0.2,0.2,0.75,1.5,2.2,2.75,3.25,3.75,4.25,4.5,4.3,3.7,3.2,2.2,1.2)

if(TRUE)
{
  pngWidth <- 1920 * 2
  pngHeight <-  1080 * 2
  fTitle <- 7
  fAxis <- 5
  fLab <- 7
  myLWD <- 6
}


fileData <- scan(filesToPlot, what="character", sep='\n', blank.lines.skip = F)
mVersion <- as.numeric(strsplit(fileData[grep("###",fileData)],"V")[[1]][2])
siteID <- sub(".txt","",sub("METRICS_","",basename(filesToPlot)))

hrdbaTitle <- NULL
hrdbaTruncTitle <- NULL
paTitle <- NULL
hzdbTitle <- NULL
hzhrTitle <- NULL

dayTime <- as.numeric(gsub(".*:\\s(\\d{2}).*","\\1",fileData[grep("Day:",fileData)]))
nightTime <- as.numeric(gsub(".*:\\s(\\d{2}).*","\\1",fileData[grep("Night:",fileData)]))
soiName <- gsub("Source of Interest: ","",fileData[grep("Source of Interest: ",fileData)])

if(titlesOnPlots)
{
  hrdbaTitle <- paste(siteID,": Hour v. Sound Pressure Level",sep='')
  hrdbaTruncTitle <- paste(siteID,": Hour v. Sound Pressure Level (20Hz - 1250Hz)",sep='')
  paTitle <- paste(siteID,": Hour v. Percent Time Audible",sep='')
  hzdbTitle <- paste(siteID,": Frequency v. Sound Pressure Level",sep='')
  hzhrTitle <- paste(siteID,": Contour Plot for ",sep='')
}

########################
# Percent Time Audible #
########################

if(plotPA)
{
  if(mVersion > 1.2){
    dataPos <- grep("Time Audible \\(%\\)",fileData)
  }else dataPos <- grep("Percent Time Audible",fileData)
  
  if(length(dataPos) != 0)
  {
    for(sIdx in 1:length(dataPos))
    {
      nAD <- numAnalyzedDays
      
      gInfo <- scan(filesToPlot, skip = dataPos[sIdx] - 1, sep = "!", n = 1, what = "character")
      
      season <- gsub(".*,\\s([A-Za-z]+)\\s.+$","\\1",gInfo)
      pngFile <- paste(outDir,"\\",siteID,"_audibleplot.png",sep='')
      
      if(grepl("n = ", gInfo)) nAD <- gsub(".+\\s(\\d+)\\)","\\1",gInfo)
      
      paTitleP <- paTitle
      
      if(season != "All") pngFile <- paste(outDir,"\\",siteID,"_",season,"_audibleplot.png",sep='')
      if(season != "All" & titlesOnPlots) paTitleP <- paste(paTitle, " (", season, ")", sep="")
      
      if(mVersion > 1.2){
        data <- t(read.table(filesToPlot,skip = dataPos[sIdx], nrows = 2,header=T,row.names=1,sep='\t'))
      }else data <- read.table(filesToPlot,skip = dataPos[sIdx], nrows = 24,header=T,sep='\t')
      
      png(file=pngFile,
          bg="white",width=pngWidth,height=pngHeight)
      
      par(mar=c(fTitle * 2, fTitle * 2, fAxis * 2, fAxis) + 0.1, mgp=c(fTitle, 1, 0), ljoin = 1, lend=2)
      #par(mar=c(6, 7, 5, 2) + 0.1, mgp=c(4, 1, 0), family="serif")
      
      plot(1, 1, main=paTitleP, xlab="",
           ylab="" ,type="n", xlim=c(0,24), ylim=c(0,100), bty="l",
           xaxs="i", yaxs="i", xaxt="n", yaxt="n", cex.lab=fLab, cex.axis=fAxis, cex.main=fTitle)
      
      mtext("Hour", side=1, line=fTitle + 2, cex=fLab)
      mtext(paste("n = ",nAD,sep=""), side=1, line=fTitle * 2 - 1, cex=fAxis)
      mtext("Audibility (%)", side=2, line=fTitle + 2, cex=fLab)
      
      axis(2,at=seq(0,100,10),las=2,labels=F,fg="grey90",tck=1, lwd=myLWD)
      axis(2,at=seq(0,100,10),las=2,cex.axis=fAxis)
      
      axis(1,at=seq(0.5, 23.5, by=1),las=1,labels=c(0:23),fg="white",line=2, cex.axis=fAxis)
      
      barplot(data[,"Total"],xpd=F,names.arg=c(0:23),border="black",axes=F, axisnames=F,
              add=T,space=0,col="grey80",axis.lty=1,cex.names=fAxis,las=1, lwd=myLWD)
      
      barplot(data[,"SoI"],xpd=F,names.arg=c(0:23),border="black",axes=F, axisnames=F,
              add=T,space=0,col="grey50",axis.lty=1,cex.names=fAxis,las=1, lwd=myLWD)
      
      legend(1,80,legend=c(soiName, "Total"),pch=c(15,15),
             col=c("grey50","grey80"),bg="white",cex=fAxis, bty="n")
      
      graphics.off()
    }
  }
}

###############
# Hour v. dBA #
###############
for(pType in 1:2)
{
  if(plotHRDBACOMB[pType])
  {
    if(mVersion > 1.2){
      if(pType == 1) dataPos <- grep("Median Hourly Metrics \\(dBA\\)",fileData)
      if(pType == 2) dataPos <- grep("Median Hourly Metrics \\(dBT\\)",fileData)
    }else
    {
      if(pType == 1) dataPos <- grep("Median dBA values by Hour",fileData)
      if(pType == 2) dataPos <- grep("Median Truncated dBA values by Hour",fileData)
    }
    
    if(length(dataPos) != 0)
    {
      for(sIdx in 1:length(dataPos))
      {
        gInfo <- scan(filesToPlot, skip = dataPos[sIdx] - 1, sep = "!", n = 1, what = "character")
        season <- gsub(".*,\\s(\\w+)\\s.*","\\1",gInfo)
        nSamples <- gsub(".*=\\s(\\d+)hr.*","\\1",gInfo)
        
        pngFile <- paste(outDir,"\\",siteID,"_DBAvHR.png",sep='')
        if(pType == 2) pngFile <- paste(outDir,"\\",siteID,"_DBTvHR.png",sep='')
        
        thisTitle <- hrdbaTitle
        if(pType == 2) thisTitle <- hrdbaTruncTitle
        
        if(season != "All") 
        {
          pngFile <- paste(outDir,"\\",siteID,"_",season,"_DBAvHR.png",sep='')
          if(pType == 2) pngFile <- paste(outDir,"\\",siteID,"_",season,"_DBTvHR.png",sep='')
          if(titlesOnPlots)
          {
            thisTitle <- paste(hrdbaTitle, " (", season, ")", sep="")
            if(pType == 2) thisTitle <- paste(hrdbaTruncTitle, " (", season, ")", sep="")
          }
        }
        
        if(mVersion > 1.2){
          data <- t(read.table(filesToPlot, skip = dataPos[sIdx], nrows = 9, header=T,row.names=1,
                               sep='\t', na.strings=c("--.-","-888.0")))
        }else data <- read.table(filesToPlot, skip = dataPos[sIdx], nrows = 24, header=T,
                                 sep='\t', na.strings=c("--.-","-888.0"))
        
        hasLNAT <- sum(!is.na(data[,"Lnat"])) > 0
        
        dataYmin <- min(data[,"L090"], na.rm=T)
        if(hasLNAT) dataYmin <- min(dataYmin, min(data[,"Lnat"], na.rm=T))
        dataYmax <- max(data[,"L010"], na.rm=T)
        
        if(ceiling(dataYmin / 3) * 3 < floor(dataYmax / 3) * 3)
        {
          tempAxis <- seq(ceiling(dataYmin / 3) * 3, floor(dataYmax / 3) * 3, by = 3)
          if((tempAxis[1] - dataYmin) < 2) tempAxis <- tempAxis[-1]
          if(length(tempAxis) != 0) 
          {	
            if((dataYmax - tempAxis[length(tempAxis)]) < 2) tempAxis <- tempAxis[-(length(tempAxis))]
            tempAxis <- c(dataYmin, tempAxis, dataYmax)
          }else
          {
            tempAxis <- c(dataYmin, dataYmax)
          }
        }else
        {
          tempAxis <- c(dataYmin, dataYmax)
        }
        
        x <- c(0:23)
        
        png(filename = pngFile,width=pngWidth,height=pngHeight)
        
        par(mar=c(fTitle * 2, fTitle * 2 + 2, fAxis * 2, fAxis) + 0.1, mgp=c(fTitle, 1, 0), ljoin = 1, lend=2)
        
        plot(1,1,type="n",main=thisTitle,bty="l",xaxt="n",yaxt="n",xlab="", ylab="",
             yaxs="i", xlim=c(0,23),ylim=c(yMinHr,yMaxHr),cex.main=fTitle)
        
        axis(1,at=c(0:23),labels=x,cex.axis=fAxis, line=2, fg="white")
        
        axis(2,at=c(tempAxis[1], tempAxis[length(tempAxis)]),labels=T,las=2,tick=T,cex.axis=fAxis) 
        axis(2,at=tempAxis[c(-1, -1 * length(tempAxis))],labels=T,las=2,tick=T,cex.axis=fAxis * 0.75, col.axis="grey50") 
        axis(2,at=c(yMaxHr, yMinHr),labels=T,las=2,tick=T,cex.axis=fAxis * 0.75, col.axis="grey50") 
        
        mtext("Hour", side=1, line=fTitle + 1, cex=fLab)
        if(pType == 1) mtext("Sound Pressure Level (dBA)", side=2, line=fTitle + 4, cex=fLab)
        if(pType == 2) mtext("Sound Pressure Level (Truncated dBA)", side=2, line=fTitle + 4, cex=fLab)
        mtext(paste("n = ",nSamples,sep=""), side=1, line=fTitle * 2 - 1, cex=fAxis)
        
        segments(x,data[,"L010"],x,data[,"L090"], col="grey75", lwd=myLWD)	
        segments(x - 0.125, data[,"L090"], x + 0.125, data[,"L090"], col="grey75", lwd=myLWD)
        segments(x - 0.125, data[,"L010"], x + 0.125, data[,"L010"], col="grey75", lwd=myLWD)
        
        if(hasLNAT){
          rect(x - 0.25, data[,"L050"], x + 0.25, data[,"Lnat"], col="black", lwd=myLWD)
        }else{
          segments(x - 0.25, data[,"L050"], x + 0.25, data[,"L050"], lwd=myLWD)
        }
        
        ### Legend ####################################################
        
        xLegHr <- 0
        yLegHr <- yMaxHr
        
        if(all(data[1:4,"L010"] < yMaxHr - 10, na.rm=T))
        {
          xLegHr <- 0
          yLegHr <- yMaxHr
        }else if(all(data[1:4,"L090"] > yMinHr + 10, na.rm=T))
        {
          xLegHr <- 0
          yLegHr <- yMinHr + 10
        }
        
        segments(xLegHr + 0.625, yLegHr - 1, xLegHr + 0.625, yLegHr - 9, col="grey75", lwd=myLWD)
        
        segments(xLegHr + 0.5, yLegHr - 1, xLegHr + 0.75, yLegHr - 1, col="grey75", lwd=myLWD)
        segments(xLegHr + 0.5, yLegHr - 9, xLegHr + 0.75, yLegHr - 9, col="grey75", lwd=myLWD)
        
        if(hasLNAT){
          rect(xLegHr + 0.375, yLegHr - 6.5, xLegHr + 0.875, yLegHr - 3.5,col="black", border="black")
          text(xLegHr + 0.75, yLegHr - 3.5, expression(phantom(0)%<-%"L"[50]), adj = c(0,0.5), cex = fAxis)
          text(xLegHr + 0.75, yLegHr - 6.5, expression(phantom(0)%<-%"L"[NAT]), adj = c(0,0.5), cex = fAxis)
        }else{
          segments(xLegHr + 0.375, yLegHr - 5, xLegHr + 0.875, yLegHr - 5,col="black", lwd=myLWD)
          text(xLegHr + 0.75, yLegHr - 5, expression(phantom(0)%<-%"L"[50]), adj = c(0,0.5), cex = fAxis)
        }
        
        text(xLegHr + 0.75, yLegHr - 1, expression(phantom(0)%<-%"L"[10]), adj = c(0,0.5), cex = fAxis)
        text(xLegHr + 0.75, yLegHr - 8.9, expression(phantom(0)%<-%"L"[90]), adj = c(0,0.5), cex = fAxis)
        
        graphics.off()
      }
    }
  }
}

##############
# Freq v. dB #
##############

if(plotFREQDB)
{
  dataDayPos <- c(0, 0, 0, 0)
  dataNightPos <- c(0, 0, 0, 0)
  
  if(mVersion > 1.2){
    tempDayPos <-  grep("Median Daytime Frequency Metrics \\(dB\\).*Sum",fileData)
    tempNightPos <- grep("Median Nighttime Frequency Metrics \\(dB\\).*Sum",fileData)
    
    if(length(tempDayPos) > 0) dataDayPos[1] <- tempDayPos
    if(length(tempNightPos) > 0) dataNightPos[1] <- tempNightPos
    
    tempDayPos <- grep("Median Daytime Frequency Metrics \\(dB\\).*Fal",fileData)
    tempNightPos <- grep("Median Nighttime Frequency Metrics \\(dB\\).*Fal",fileData)
    
    if(length(tempDayPos) > 0) dataDayPos[2] <- tempDayPos
    if(length(tempNightPos) > 0) dataNightPos[2] <- tempNightPos
    
    tempDayPos <- grep("Median Daytime Frequency Metrics \\(dB\\).*Win",fileData)
    tempNightPos <- grep("Median Nighttime Frequency Metrics \\(dB\\).*Win",fileData)
    
    if(length(tempDayPos) > 0) dataDayPos[3] <- tempDayPos
    if(length(tempNightPos) > 0) dataNightPos[3] <- tempNightPos
    
    tempDayPos <- grep("Median Daytime Frequency Metrics \\(dB\\).*Spr",fileData)
    tempNightPos <- grep("Median Nighttime Frequency Metrics \\(dB\\).*Spr",fileData)
    
    if(length(tempDayPos) > 0) dataDayPos[4] <- tempDayPos
    if(length(tempNightPos) > 0) dataNightPos[4] <- tempNightPos
  }else
  {
    tempDayPos <-  grep("SPL.*Day.*Sum",fileData)
    tempNightPos <- grep("SPL.*Night.*Sum",fileData)
    
    if(length(tempDayPos) > 0) dataDayPos[1] <- tempDayPos
    if(length(tempNightPos) > 0) dataNightPos[1] <- tempNightPos
    
    tempDayPos <- grep("SPL.*Day.*Fal",fileData)
    tempNightPos <- grep("SPL.*Night.*Fal",fileData)
    
    if(length(tempDayPos) > 0) dataDayPos[2] <- tempDayPos
    if(length(tempNightPos) > 0) dataNightPos[2] <- tempNightPos
    
    tempDayPos <- grep("SPL.*Day.*Win",fileData)
    tempNightPos <- grep("SPL.*Night.*Win",fileData)
    
    if(length(tempDayPos) > 0) dataDayPos[3] <- tempDayPos
    if(length(tempNightPos) > 0) dataNightPos[3] <- tempNightPos
    
    tempDayPos <- grep("SPL.*Day.*Spr",fileData)
    tempNightPos <- grep("SPL.*Night.*Spr",fileData)
    
    if(length(tempDayPos) > 0) dataDayPos[4] <- tempDayPos
    if(length(tempNightPos) > 0) dataNightPos[4] <- tempNightPos
  }
  
  tohVals <- c(93.2,86.3,78.5,68.7,59.5,51.1,44,37.5,31.5,26.5,22.1,17.9,14.4,
               11.4,8.4,5.8,3.8,2.1,1.0,0.8,1.9,0.5,-1.5,-3.1,-4,-3.8,-1.8,2.5,
               6.8,9.8,14.4,43.7,84.7)
  
  xc <- 1:33
  
  myXLabels <- c("12.5","25","50","100","200","400","800","1.6k","3.15k","6.3k","12.5k")
  myXLabelPos <- seq(from=1, to=33, by=3)
  
  for(sIdx in 1:4)
  {
    hasDay <- dataDayPos[sIdx] > 0
    hasNight <- dataNightPos[sIdx] > 0
    if(hasDay || hasNight)
    {
      nSamplesDay <- ""
      nSamplesNight <- ""
      
      if(hasDay) 
      {
        gInfo <- scan(filesToPlot, skip = dataDayPos[sIdx] - 1, sep = "\n", n = 1, what = "character")
        nSamplesDay <- paste(gsub(".*=\\s(\\d+)hr.*","\\1",gInfo), " daytime hours", sep="")
        dayString <- paste("Day (",dayTime,"am-",nightTime%%12,"pm)",sep="")
        
        if(mVersion > 1.2){
          dataDay <- t(read.table(filesToPlot, skip = dataDayPos[sIdx], nrows = 4, header=T, row.names=1,
                                  sep='\t', na.strings=c("--.-","-888.0")))
        }else dataDay <- read.table(filesToPlot, skip = dataDayPos[sIdx], nrows = 33,
                                    header=T, sep='\t', na.strings=c("--.-","-888.0"))
      }
      if(hasNight)
      {
        gInfo <- scan(filesToPlot, skip = dataNightPos[sIdx] - 1, sep = "\n", n = 1, what = "character")
        nSamplesNight <- paste(gsub(".*=\\s(\\d+)hr.*","\\1",gInfo), " nighttime hours", sep="")
        nightString <- paste("Night (",nightTime%%12,"pm-",dayTime,"am)",sep="")
        
        if(mVersion > 1.2){
          dataNight <- t(read.table(filesToPlot, skip = dataNightPos[sIdx], nrows = 4, header=T, row.names=1,
                                    sep='\t', na.strings=c("--.-","-888.0")))
        }else dataNight <- read.table(filesToPlot, skip = dataNightPos[sIdx], nrows = 33,
                                      header=T, sep='\t', na.strings=c("--.-","-888.0"))
      }
      
      if(!plotHLhz & hasNight) dataNight[c(1:3, 29:33),] <- NA	
      if(!plotHLhz & hasDay) dataDay[c(1:3, 29:33),] <- NA
      
      season <- gsub(".*,\\s(\\w+)\\s.*","\\1",gInfo)
      
      pngFile <- paste(outDir,"\\",siteID,"_SPLvFREQ.png",sep='')
      
      hzdbTitleP <- hzdbTitle
      
      if(season != "All") pngFile <- paste(outDir,"\\",siteID,"_",season,"_SPLvFREQ.png",sep='')
      if(season != "All" & titlesOnPlots) hzdbTitleP <- paste(hzdbTitle, " (", season, ")", sep="")
      
      xLabPos <- 1
      yLabPos <- yMinHz + 14
      
      if(hasDay)
      {
        if(hasNight)
        {
          if(all(dataDay[26:33,"L010"] < (yMaxHz - 15), na.rm=T) && all(dataNight[26:33,"L010"] < (yMaxHz - 15), na.rm=T))
          {
            xLabPos <- 26
            yLabPos <- (yMaxHz - 2)
          }
        }else{
          if(all(dataDay[26:33,"L010"] < (yMaxHz - 15), na.rm=T))
          {
            xLabPos <- 26
            yLabPos <- (yMaxHz - 2)
          }
        }
      }else
      {
        if(all(dataNight[26:33,"L010"] < (yMaxHz - 15), na.rm=T))
        {			
          xLabPos <- 26
          yLabPos <- (yMaxHz - 2)
        }
      }
      
      if(hasDay) 
      {
        hasLNAT <- !is.na(dataDay[10,"Lnat"])
      }else hasLNAT <- !is.na(dataNight[10,"Lnat"])
      
      #if(hasDay && is.na(dataDay[1,2]))
      #{
      #	xc <- xc[3:33]
      #}else if(hasNight && is.na(dataNight[1,2])) xc <- xc[3:33]
      
      if(hasDay)
      {
        if(hasNight)
        {
          dataYmin <- min(min(dataDay[,"L090"], na.rm=T),min(dataNight[,"L090"], na.rm=T))
          dataYmax <- max(max(dataDay[,"L010"], na.rm=T),max(dataNight[,"L010"], na.rm=T))
        }else{
          dataYmin <- min(dataDay[,"L090"], na.rm=T)
          dataYmax <- max(dataDay[,"L010"], na.rm=T)
        }
      }else{
        dataYmin <- min(dataNight[,"L090"], na.rm=T)
        dataYmax <- max(dataNight[,"L010"], na.rm=T)
      }
      
      if(ceiling(dataYmin / 3) * 3 < floor(dataYmax / 3) * 3)
      {
        tempAxis <- seq(ceiling(dataYmin / 3) * 3, floor(dataYmax / 3) * 3, by = 3)
        if((tempAxis[1] - dataYmin) < 2) tempAxis <- tempAxis[-1]
        if(length(tempAxis) != 0) 
        {	
          if((dataYmax - tempAxis[length(tempAxis)]) < 2) tempAxis <- tempAxis[-(length(tempAxis))]
          tempAxis <- c(dataYmin, tempAxis, dataYmax)
        }else
        {
          tempAxis <- c(dataYmin, dataYmax)
        }
      }else
      {
        tempAxis <- c(dataYmin, dataYmax)
      }
      
      png(pngFile,width=pngWidth, height=pngHeight)
      
      par(mar=c(fTitle * 2, fTitle * 2, fAxis * 2, fAxis) + 0.1, mgp=c(fTitle, 1, 0), ljoin = 1, lend=2)
      
      plot(1,1,type="n",main=hzdbTitleP,xlab="",ylab="",axes=T,lty=1,bty="l",xaxs="i",yaxs="i",
           xaxt="n",yaxt="n",xlim=c(0,34),ylim=c(yMinHz,yMaxHz), cex.main=fTitle, lwd=myLWD)
      
      mtext("Frequency (Hz)", side=1, line=fTitle + 1, cex=fLab)
      mtext("Sound Pressure Level (dB)", side=2, line=fTitle + 2, cex=fLab)
      
      if(hasDay && hasNight)
      {
        mtext(paste("n = ", nSamplesDay, ", ", nSamplesNight ,sep=""), side=1, line=fTitle * 2 - 1, cex=fAxis)
      }else mtext(paste("n =", nSamplesDay, nSamplesNight ,sep=""), side=1, line=fTitle * 2 - 1, cex=fAxis)
      
      polygon(c(0,0,xc[2:33],34,34),c(yMinHz,tohVals,100,yMinHz),col=rgb(0.95,0.95,0.95),border=NA)
      
      axis(1,at=myXLabelPos,labels=myXLabels,tck=-0.0125, las=1,tick=F,cex.axis=fAxis, line=2)
      axis(1,at=c(0.5,xc + 0.5),labels=F,tck=0.0125, col="grey50")
      axis(1,at=c(0.5,xc + 0.5),labels=F,tck=-0.0125)
      
      axis(2,at=c(tempAxis[1], tempAxis[length(tempAxis)]),labels=T,las=2,tick=T,cex.axis=fAxis) 
      axis(2,at=tempAxis[c(-1, -1 *length(tempAxis))],labels=T,las=2,tick=T,cex.axis=fAxis * 0.75, col.axis="grey50") 
      axis(2,at=c(yMaxHz, yMinHz),labels=T,las=2,tick=T,cex.axis=fAxis * 0.75, col.axis="grey50") 
      
      dayColor <- c("palegoldenrod", "lightgoldenrod","goldenrod")
      nightColor <- c("plum1", "plum3", "darkorchid")
      
      ###Day
      if(hasDay)
      {
        rect(xc, dataDay[,"L010"], xc - 0.25, dataDay[,"L090"], lwd=myLWD, border=dayColor[2], col=dayColor[1])
        if(hasLNAT){
          rect(xc, dataDay[,"Lnat"], xc - 0.25, dataDay[,"L050"], col=dayColor[3], border=dayColor[3], lwd=0.5)
        }else
        {	
          segments(xc, dataDay[,"L050"], xc - 0.25, dataDay[,"L050"], lwd = myLWD, col=dayColor[3])
        }	
      }			
      
      ###Night
      if(hasNight)
      {
        rect(xc, dataNight[,"L010"], xc + 0.25, dataNight[,"L090"], lwd=myLWD, border=nightColor[2], col=nightColor[1])
        if(hasLNAT){
          rect(xc, dataNight[,"Lnat"], xc + 0.25, dataNight[,"L050"], col=nightColor[3], border=nightColor[3], lwd=0.5)
        }else
        {	
          segments(xc, dataNight[,"L050"], xc + 0.25, dataNight[,"L050"], lwd = myLWD, col=nightColor[3])
        }
      }			
      
      ### Legend ###############################################################################
      if(hasLNAT){
        rect(xc[xLabPos], yLabPos - 1, xc[xLabPos] - 0.25, yLabPos - 11, col="white", border="grey50", lwd=myLWD)
        rect(xc[xLabPos], yLabPos - 4, xc[xLabPos] - 0.25, yLabPos - 8, col = "grey50", border="grey50", lwd=0.5)
        
        text(xc[xLabPos] - 0.25, yLabPos - 1, expression(phantom(0)*phantom(0)%<-%"L"[10]), adj = c(0,0.5), cex = fAxis)
        text(xc[xLabPos] - 0.25, yLabPos - 4, expression(phantom(0)*phantom(0)%<-%"L"[50]), adj = c(0,0.5), cex = fAxis)   
        text(xc[xLabPos] - 0.25, yLabPos - 8, expression(phantom(0)*phantom(0)%<-%"L"[NAT]), adj = c(0,0.5), cex = fAxis)
        text(xc[xLabPos] - 0.25, yLabPos - 10.9, expression(phantom(0)*phantom(0)%<-%"L"[90]), adj = c(0,0.5), cex = fAxis)
        
        if(hasDay) rect(xc[xLabPos + 3], yLabPos - 2, xc[xLabPos + 3] + 0.5, yLabPos - 4, col = dayColor[1], border = dayColor[2], lwd=myLWD)
        if(hasNight) rect(xc[xLabPos + 3], yLabPos - 8, xc[xLabPos + 3] + 0.5, yLabPos - 10, col = nightColor[1], border = nightColor[2], lwd=myLWD) 
        if(hasDay) text(xc[xLabPos + 3] + 0.75, yLabPos - 3, dayString, adj = c(0,0.5), cex = fAxis)
        if(hasNight) text(xc[xLabPos + 3] + 0.75, yLabPos - 9, nightString, adj = c(0,0.5), cex = fAxis)
      }else{			
        rect(xc[xLabPos], yLabPos - 1, xc[xLabPos] - 0.25, yLabPos - 11, border="grey50", lwd=myLWD)
        segments(xc[xLabPos], yLabPos - 6, xc[xLabPos] - 0.25, yLabPos - 6, lwd=myLWD) 
        
        text(xc[xLabPos] - 0.25, yLabPos - 1, expression(phantom(0)*phantom(0)%<-%"L"[10]), adj = c(0,0.5), cex = fAxis)
        text(xc[xLabPos] - 0.25, yLabPos - 6, expression(phantom(0)*phantom(0)%<-%"L"[50]), adj = c(0,0.5), cex = fAxis)
        text(xc[xLabPos] - 0.25, yLabPos - 10.9, expression(phantom(0)*phantom(0)%<-%"L"[90]), adj = c(0,0.5), cex = fAxis)
        
        if(hasDay) rect(xc[xLabPos + 3], yLabPos - 2, xc[xLabPos + 3] + 0.5, yLabPos - 4, col = dayColor[1], border = dayColor[2], lwd=myLWD)
        if(hasNight) rect(xc[xLabPos + 3], yLabPos - 8, xc[xLabPos + 3] + 0.5, yLabPos - 10, col = nightColor[1], border = nightColor[2], lwd=myLWD) 
        if(hasDay) text(xc[xLabPos + 3] + 0.75, yLabPos - 3, dayString, adj = c(0,0.5), cex = fAxis)
        if(hasNight) text(xc[xLabPos + 3] + 0.75, yLabPos - 9, nightString, adj = c(0,0.5), cex = fAxis)
      }
      
      segments(10, yMinHz + 5 + 0.5, 19, yMinHz + 5 + 0.5, lwd=myLWD, col="grey50")
      segments(10, yMinHz + 5 + 0.5, 10, yMinHz + 7 + 0.5, lwd=myLWD, col="grey50")
      segments(19, yMinHz + 5 + 0.5, 19, yMinHz + 7 + 0.5, lwd=myLWD, col="grey50")
      segments(14.5, yMinHz + 5 + 0.5, 14.5, yMinHz + 3 + 0.5, lwd=myLWD, col="grey50")
      text(14.5, yMinHz + 1.65 + 0.5, "Transportation", cex = fAxis, col="grey50")
      
      segments(15, yMaxHz - 5 - 0.5, 25, yMaxHz - 5 - 0.5, lwd=myLWD, col="grey50")
      segments(15, yMaxHz - 5 - 0.5, 15, yMaxHz - 7 - 0.5, lwd=myLWD, col="grey50")
      segments(25, yMaxHz - 5 - 0.5, 25, yMaxHz - 7 - 0.5, lwd=myLWD, col="grey50")
      segments(20, yMaxHz - 3 - 0.5, 20, yMaxHz - 5 - 0.5, lwd=myLWD, col="grey50")
      text(20, yMaxHz - 1.75 - 0.5, "Conversation", cex = fAxis, col="grey50")
      
      segments(20, yMinHz + 5 + 0.5, 29, yMinHz + 5 + 0.5, lwd=myLWD, col="grey50")
      segments(20, yMinHz + 5 + 0.5, 20, yMinHz + 7 + 0.5, lwd=myLWD, col="grey50")
      segments(29, yMinHz + 5 + 0.5, 29, yMinHz + 7 + 0.5, lwd=myLWD, col="grey50")
      segments(24.5, yMinHz + 5 + 0.5, 24.5, yMinHz + 3 + 0.5, lwd=myLWD, col="grey50")
      text(24.5, yMinHz + 1.65 + 0.5, "Song birds", cex = fAxis, col="grey50")
      
      text(4, yMinHz + 15, "Threshold of human hearing", cex = fAxis, col="grey50", srt=-45)
      
      graphics.off()
      
      #Hillenbrand J, Getty LA, Clark MJ, Wheeler K (1995) Acoustic characteristics of American English vowels. J Acoust Soc Am 97: 3099-3111.
    }
  }
  
}

################
# Contour Plot #
################

if(plotCONTOUR)
{
  dataPos <- grep("L[0-9a-zA-Z]{2,3} Contour",fileData)
  if(length(dataPos) != 0)
  {
    for(sIdx in 1:length(dataPos))
    {
      gInfo <- scan(filesToPlot, skip = dataPos[sIdx] - 1, sep = "\n", nlines = 1, what = "character")
      season <- gsub(".*,\\s(\\w+)\\s.*","\\1",gInfo)
      nSamples <- gsub(".*=\\s(\\d+)hr.*","\\1",gInfo)
      lVal <- gsub("L([0-9a-zA-Z]{2,3}).*","\\1",gInfo)
      pngFile <- paste(outDir,"\\",siteID,"_L",lVal,"_CONTOUR.png",sep='')
      
      hzhrTitleA <- paste(hzhrTitle, "L", sep="")
      hzhrTitleB <- ""
      
      if(season != "All")
      {
        pngFile <- paste(outDir,"\\",siteID,"_",season,"_L",lVal,"_CONTOUR.png",sep='')
        hzhrTitleB <- paste(" (", season, ")", sep="")
      }
      
      data <- as.matrix(read.table(filesToPlot,skip = dataPos[sIdx],	nrows = 24, header=T,
                                   sep='\t'))[,2:34]
      
      freqs <- c("20","40","80","160","315","630","1.25k","2.5k","5k","10k","20k")
      
      png(filename = pngFile,width=pngWidth,height=pngHeight)
      
      #par(mar=c(5.1,4.1,4.1,5.1))		
      par(mar=c(fTitle * 2, fTitle * 2 + 2, fAxis * 2, fAxis) + 0.1, mgp=c(fTitle, 1, 0), ljoin = 1, lend=2)
      
      body(filled.contour)[[grep("rect",body(filled.contour))]] <- substitute(rect(0, levels[-length(levels)], 1, levels[-1L], col = col, border = col))
      
      filled.contour(x = 0:23, y = 1:33, data, zlim=c(-9,87),col=colorRampPalette(c("blue","orange","white"))(960),nlevels=960, 
                     key.axes = axis(4,at=seq(-9,87,6),las=2,cex.axis=fAxis), 
                     plot.axes = {	
                       axis(1,at=c(0:23),labels=T,cex.axis=fAxis, line=2, fg="white")
                       axis(2,at=seq(3,33,3),labels=freqs,las=2,cex.axis=fAxis)			
                     },
                     plot.title = title(main=substitute(titleA[x]*titleB,list(titleA=hzhrTitleA,x=lVal,titleB=hzhrTitleB)),
                                        xlab="", ylab="", cex.main=fTitle)
      )
      
      mtext("Hour", side=1, line=fTitle + 2, cex=fLab)
      mtext(paste("n = ",nSamples,sep=""), side=1, line=fTitle * 2 - 1, cex=fAxis)
      mtext("Frequency (Hz)", side=2, line=fTitle + 4, cex=fLab)
      mtext("Sound Pressure Level (dB)",side=4,line=3, cex=fAxis)
      
      graphics.off()
    }
  }
}


