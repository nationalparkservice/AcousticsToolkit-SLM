def A_weight():

    '''
    A-weighting network: to adjust flat-weighted (Z-weighted) third-octave band measurements for human audibility.

    returns
    -------
    A_weighting_network (pd.DataFrame) a single-column DataFrame with linearly-additive adjustments in deciBels.
    '''

    A_weighting_network = pd.DataFrame([-63.6, -56.4, -50.4, -44.8, -39.5, -34.5, 
                                       -30.3, -26.2, -22.4, -19.1, -16.2, -13.2, 
                                        -10.8, -8.7, -6.6, -4.8, -3.2, -1.9, -0.8,
                                         0.0, 0.6, 1.0, 1.2, 1.3, 1.2, 1.0, 0.6,
                                         -0.1, -1.1, -2.5, -4.3, -6.7, -9.3],
                                         index=[12.5, 15.8, 20, 25, 31.5, 40,
                                                50, 63, 80, 100, 125, 160, 200, 
                                                250, 315, 400, 500, 630, 800, 
                                                1000, 1250, 1600, 2000, 2500,
                                                3150, 4000, 5000, 6300, 8000,
                                                10000, 12500, 16000, 20000],
                                         columns=["Adjustment (dB)"])

    return A_weighting_network


def units_with_NVSPL(Synology_path):
    
    '''
    Quickly search and compile a list of units with NVSPL data
    
    TODO: expand for better searches with `iyore`
    '''
    
    # strip out the units codes for which we have acoustic data
    unit_folders = [ f.path for f in os.scandir(Synology_path) if f.is_dir()]
    
    
    NVSPL_units = []
    
    # iterate through each unit
    for unit_path in unit_folders:
        
        try: 
            ds = iyore.Dataset(unit_path) # initialize the `iyore` dataset
            ds.nvspl.info() # test whether it has NVSPL files, if not we except the error
            NVSPL_units.append(unit_path)
        except:
            pass
        
    return NVSPL_units

def Type1_Sites():
    
    import pyodbc

    # set up a connection to the database
    cnxn = pyodbc.connect("Driver={SQL Server};"
                          "Server=inp2300sql01\\irma;"
                          "Trusted_Connection=Yes;"
                          "Database=NSNSD_Acoustic;")

    cursor = cnxn.cursor() # establish cursor

    # /////// load data into a dataframe ///////////   
    sql = "SELECT ID, UnitID, Code, Name, LAT, LON FROM Site"
    metadata = pd.read_sql(sql,cnxn)  # without parameters [non-prepared statement]

    # close both the cursor and connection    
    cursor.close()
    cnxn.close()

    return metadata


def get_third_octave_limits():
  
    '''
    Scrape limits of one-third octave bands from Engineering Toolbox HTML table.
    '''
    
    url = "https://www.engineeringtoolbox.com/octave-bands-frequency-limits-d_1602.html"
    dfs = pd.read_html(url)

    # drop the multi-index
    dfs[1].columns = dfs[1].columns.droplevel()
    third_octave_limits = dfs[1].copy()

    return third_octave_limits

def third_octave_sums(fs, recieved):
  
    '''
    Sum recieved energy within each third-octave band.
    '''

    lims = get_third_octave_limits()

    for ind, row in lims.iterrows():

        # find the indices that correspond to the current third-octave band
        in_band_indices = np.argwhere((fs >= row["Lower Band Limit(Hz)"])&(fs < row["Upper Band Limit(Hz)"]))

        # sum the energy in the band
        log_sum = np.sum(np.power(10, recieved[in_band_indices]/10))

        lims.loc[ind, "Level"] = np.real(10*np.log10(log_sum))


    return lims

def r_calc(mic_height, distance_from_stream, stream_width):
  
    '''
    A geometry helper-function for computing ground effect.
    '''
    
    # first get r1 from the Pythagorean theorem
    r1 = np.power(np.power(mic_height,2) + np.power(distance_from_stream,2), 1/2)
    
    # notice that r2 is easily calculated by adding the stream width
    r2 = np.power(np.power(mic_height,2) + np.power(distance_from_stream + (stream_width/2),2), 1/2)
    
    return r1, r2

def A_ground(k, d1, d2, h1, h2, w, Q=2):
    
    '''
    Compute impedance-based attenuation as per Attenborough 1988.
    
    Inputs
    ------
    k (float): wavenumber
    d1 (float): distance between observer and riverbank
    d2 (float): distance between riverbank and center of river
    h1 (float): height of observer
    h2 (float): height of riverbank
    w (float): width of river
    Q (float): directionality factor, defaults to hemispherical spreading (Q=2)
    
    Returns
    ------- 
    A_ground (float): acoustic attenuation due to impedance-based ground effects (dB)
    '''
    
    # geometric computation
    r1, r2 = r_calc(h1+h2, d1+d2, w)
    
    # compute ground attenuation
    ψ = np.exp(1j*k*r1)/(1j*k*r1) + Q*np.exp(1j*k*r2)/(1j*k*r2)
    
    A_ground = 20*np.log10(ψ/(np.exp(1j*k*r1)/r1))
    
    return A_ground

def A_spreading(f, d1, d2, h1, h2, Q=2):
    
    '''
    Geometric spreading loss for rivers, assuming a hemispherical surface.
    
    Inputs
    ------
    f (float): frequency
    d1 (float): distance between observer and riverbank
    d2 (float): distance between riverbank and center of river
    h1 (float): height of observer
    h2 (float): height of riverbank
    Q (float): directionality factor, defaults to hemispherical spreading (Q=2)
    
    Returns
    ------- 
    A_spread (float): acoustic attenuation due to geometric spreading loss (dB)
    '''
    
    # compute the actual slant distance from observer to center
    d = np.sqrt(np.power(h1 + h2, 2) + np.power(d1 + d2, 2))
    
    A_spread = 10*np.log10(1/(Q*np.power(d, 2)))
    
    return A_spread

def A_diffraction(f, d1, d2, h1, h2, c_air=343):
    
    '''
    Kurze-Anderson diffraction-based attenuation for a riverbank.
    
    Inputs
    ------
    f (float): frequency
    d1 (float): distance between observer and riverbank
    d2 (float): distance between riverbank and center of river
    h1 (float): height of observer
    h2 (float): height of riverbank
    c_air (float): speed of sound in air, defaults to 343 m/s
    
    Returns
    ------- 
    A_diff (float): acoustic attenuation due to diffraction around riverbank barrier (dB)
    '''
    
    A = np.sqrt(np.power(h2, 2)+np.power(d2, 2))
    B = np.sqrt(np.power(h1, 2)+np.power(d1, 2))
    d = np.sqrt(np.power(h1 + h2, 2)+np.power(d1 + d2, 2))
    N = ((2*f)/c_air)*(A + B - d)
    
    # note original equation begins with "5 + ..."
    A_diff = 0 - 20*np.log(np.sqrt(2*np.pi*N)/np.tanh(np.sqrt(2*np.pi*N)))
    
    return A_diff

    
def A_atmosphere(f, d1, d2, h1, h2, elevation, air_temp_celcius=25., percent_relative_humidity=75.):
    
    '''
    Atmospheric attenuation due to absorption.
    
    Inputs
    ------
    f (float): frequency
    d1 (float): distance between observer and riverbank (m)
    d2 (float): distance between riverbank and center of river (m)
    h1 (float): height of observer (m)
    h2 (float): height of riverbank (m)
    elevation (float): mean elevation between source and observer (m)
    air_temp_celcius (float): air temperature, defaults to 25° C
    percent_relative_humidity (float): relative humidity, defaults to 75%
    
    Returns
    ------- 
    A_atm (float): acoustic attenuation due to atmospheric absorption (dB)
    '''
    
    # compute expected atmospheric pressure from elevation, kPa
    atm_pressure = 101.325*np.power(1 - 2.25577e-5*(elevation), 5.25588)

    T_K = air_temp_celcius + 273.15
    psat = 101.325*np.power(10, (-6.8346*np.power(273.16/T_K, 1.261))+4.6151) # atmospheric saturation pressure
    
    x = 1/(10*np.log10(np.power(np.exp(1),2)))  # 'equation shortener #1'
    h = percent_relative_humidity*(psat/atm_pressure)/100  # molar concentration of water vapor

    frO = (atm_pressure/101.325)*(24 + (4.04*np.power(10, 4)*h*((0.02 + h)/(0.391 + h)))) # oxygen relaxation frequency
    frN = (atm_pressure/101.325)*np.power(T_K/293.15, -0.5)*(9 + (280 *h*np.exp(-4.17*(-1*np.power(T_K/293.15, -1/3))))) # nitrogen relaxation frequency

    z = 0.1068*np.exp(-3352/T_K)*np.power((frN+np.power(f,2))/frN, -1) # 'equation shortener #2'
    y = np.power(T_K/293.15, -5/2)*((0.01275*np.exp(-2239.1/T_K)*np.power((frO+np.power(f,2))/frO, -1))+z) # 'equation shortener #3'


    # here's the atmospheric absorption coefficient, itself:
    a = 8.686*np.power(f,2)*(1.84*np.power(10., -11)*np.power(atm_pressure/101.325, -1)*np.power(T_K/293.15,0.5)+y)
    
    # compute the overall distance from the source
    d = np.sqrt(np.power(h1 + h2, 2)+np.power(d1 + d2, 2))
    
    # now compute the attenuation with distance...
    A_atm = a*d
    
    return A_atm

def interpolate_heading(start_heading, end_heading, num_points):
    
    """
    Because heading is periodic, in many cases we cannot use 
    simple linear interpolation to correctly space out values.
    
    Inputs
    ------
    start_headings (float): the heading of the first point
    end_heading (float): the heading of the last point
    num_points (int): the number of interpolated points desired between the first and last
    
    Returns
    -------
    headings (numpy array): an inclusive list of interpolated headings
    
    """

    # first we need to know if the shortest path is through zero
    passes_zero = np.abs(end_heading - start_heading) > 180

    if(passes_zero):

        # add 360 to the minimum value to ensure linearity
        # note: this can reorder the sequence
        headings = np.linspace(np.maximum(start_heading, end_heading), np.minimum(start_heading, end_heading) + 360, num_points)%360
        
        # correct for reordering if necessary
        if(headings[0] != start_heading):
            headings = headings[::-1]

        return headings
    
    else:
        
        # this is standard linear interpolation
        headings = np.linspace(start_heading, end_heading, num_points)
        
        return headings