def make_cardinal_composite(iyore_dataset_path, unit, site, year):

	import sys
	sys.path.append(r"C:\Users\DBetchkal\PythonScripts\3_GITHUB_REPOSITORIES\iyore")
	import iyore

	import glob
	import os.path
	import datetime
	from PIL import Image
	from PIL import ImageDraw
	from PIL import ImageFont

	'''
	Creates a composite image for each site visit with photos facing North, South, East, and West.
	Assumes:
		- an AKR data structure with photos in directories named r'\01 DATA\PHOTOS\MM DD YYYY' 
		- .JPG photos
		- a unique suffix on photos as "Filename East" or "Filename east"
	
	Parameters
    ----------
    iyore_dataset_path : str 
    	Absolute path to a folder containing an `iyore` .structure.txt file
    unit : str
        Four letter park service unit code E.g. 'KATM'
    site : str
        Deployment site character code. E.g. 'CROS'
    year : int
        Deployment year. YYYY

	'''

	ds = iyore.Dataset(iyore_dataset_path)

	# you can set this however you like...
	for e in ds.dataDir(unit=unit, site=site, year=str(year)):
	    
	    # get the path where photos are located
	    path = [e.path for e in ds.dataDir(unit=unit, site=site, year=year)][0] + os.sep + "01 DATA" + os.sep + "PHOTOS"

	    # -----------------------------------------------

	    north = sorted(list(set(glob.glob(path + "\*\* North.JPG")) - set(glob.glob(path + "\*\* reconyx North.JPG"))))
	    west = sorted(list(set(glob.glob(path + "\*\* West.JPG")) - set(glob.glob(path + "\*\* reconyx West.JPG"))))
	    south = sorted(list(set(glob.glob(path + "\*\* South.JPG")) - set(glob.glob(path + "\*\* reconyx South.JPG"))))
	    east = sorted(list(set(glob.glob(path + "\*\* East.JPG")) - set(glob.glob(path + "\*\* reconyx East.JPG"))))
	    
	    font = ImageFont.truetype("micross.ttf", 95)

	    for i, file in enumerate(north):

	        convert_time = datetime.datetime.strptime(os.path.basename(os.path.dirname(north[i])), "%m %d %Y")
	        timestamp = datetime.datetime.strftime(convert_time, "%Y%m%d")

	        # i = 1 # low-resolution image

	        N = Image.open(north[i])
	        W = Image.open(west[i])
	        S = Image.open(south[i])
	        E = Image.open(east[i])

	        card = {"N":N, "W":W, "S":S, "E":E}

	        pad_h = int(card["N"].size[0]/100)
	        pad_v = int(card["N"].size[1]/100)
	        frame = Image.new("RGB", (int(card["N"].size[0])+pad_h, int(card["N"].size[1])+pad_v))

	        for d in card:

	            img_resize = card[d].resize((int(card[d].size[0]/2), int(card[d].size[1]/2)), Image.ANTIALIAS)
	            img_width, img_height = img_resize.size

	            draw = ImageDraw.Draw(frame)
	            # pad = 10 # low-resolution
	            pad = 30

	            if(d == "N"):
	                frame.paste(img_resize, (0,0))
	                h_buff, v_buff = draw.textsize("North", font=font)
	                label = draw.text((img_width - h_buff - pad, img_height - v_buff - pad),"North",fill=(88,255,23,255),font=font)  

	            elif(d == "W"):
	                frame.paste(img_resize, (img_width+pad_h,img_height+pad_v))
	                h_buff, v_buff = draw.textsize("West", font=font)
	                label = draw.text((img_width + pad + pad_h, img_height + pad),"West",fill=(88,255,23,255),font=font)          

	            elif(d == "S"):
	                frame.paste(img_resize, (0,img_height+pad_v))
	                h_buff, v_buff = draw.textsize("South", font=font)
	                label = draw.text((img_width - h_buff - pad, img_height + pad),"South",fill=(88,255,23,255),font=font)  

	            elif(d == "E"):
	                frame.paste(img_resize, (img_width+pad_h,0))
	                h_buff, v_buff = draw.textsize("East", font=font)
	                label = draw.text((img_width + pad + pad_h, img_height - v_buff - pad),"East",fill=(88,255,23,255),font=font)  


	        print("saving", unit + site, timestamp)
	        frame.save(path + "\CardinalPhotoComposite_" + unit + site + "_" + timestamp + ".jpg", optimize=True, quality=50)