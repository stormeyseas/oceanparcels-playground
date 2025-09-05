import xarray as xr
import numpy as np

def convert_sparse_to_full_grid(input_file, output_file):
    """
    Convert sparse grid netCDF to full 3D grid format.

    Parameters:
    -----------
    input_file : str
        Path to input netCDF file with sparse grid format
    output_file : str
        Path to output netCDF file with full grid format
    """

    # Open the original file
    ds = xr.open_dataset(input_file)

    # Extract grid dimensions
    ni_grid = ds.sizes['i_grid']
    nj_grid = ds.sizes['j_grid']
    nk_grid = ds.sizes['k_grid']
    ni_centre = ds.sizes['i_centre']
    nj_centre = ds.sizes['j_centre']
    nk_centre = ds.sizes['k_centre']
    nrecord = ds.sizes['record']

    # Read coordinate grids and convert to coordinate variables
    x_grid = ds['x_grid']  # [j_grid, i_grid]
    y_grid = ds['y_grid']  # [j_grid, i_grid]
    z_grid = ds['z_grid']  # [k_grid]
    x_centre = ds['x_centre']  # [j_centre, i_centre]
    y_centre = ds['y_centre']  # [j_centre, i_centre]
    z_centre = ds['z_centre']  # [k_centre]

    # Get original time coordinate
    time_orig = ds['t']  # [record]
    time_datetime64 = time_orig.values.astype('datetime64')

    # Create new time coordinate with datetime64 values
    time = xr.DataArray(
        time_datetime64,
        dims=['record'],
        attrs={
            'long_name': 'Time',
            'standard_name': 'time'
        }
    )

    # Read sparse grid mapping indices (convert to 0-based if needed)
    s2i = ds['s2i'].values  # Assuming 0-based indexing in original
    s2j = ds['s2j'].values
    s2k = ds['s2k'].values

    # Read sparse grid data
    u1_sparse = ds['u1mean']  # [record, ns3]
    u2_sparse = ds['u2mean']  # [record, ns3]
    w_sparse = ds['wmean']    # [record, ns3]
    temp_sparse = ds['temp']  # [record, ns3]
    salt_sparse = ds['salt']  # [record, ns3]

    # Create full 3D arrays filled with NaN
    u1_full = np.full((nrecord, nk_grid, nj_grid, ni_grid), np.nan, dtype=np.float64)
    u2_full = np.full((nrecord, nk_grid, nj_grid, ni_grid), np.nan, dtype=np.float64)
    w_full = np.full((nrecord, nk_grid, nj_grid, ni_grid), np.nan, dtype=np.float64)
    temp_full = np.full((nrecord, nk_grid, nj_grid, ni_grid), np.nan, dtype=np.float64)
    salt_full = np.full((nrecord, nk_grid, nj_grid, ni_grid), np.nan, dtype=np.float64)

    # Map sparse data back to full grid
    for t_idx in range(nrecord):
        u1_full[t_idx, s2k, s2j, s2i] = u1_sparse[t_idx, :].values
        u2_full[t_idx, s2k, s2j, s2i] = u2_sparse[t_idx, :].values
        w_full[t_idx, s2k, s2j, s2i] = w_sparse[t_idx, :].values
        temp_full[t_idx, s2k, s2j, s2i] = temp_sparse[t_idx, :].values
        salt_full[t_idx, s2k, s2j, s2i] = salt_sparse[t_idx, :].values

    # Create coordinate arrays for grid points
    # For grid coordinates, we need 1D arrays
    lon_grid_1d = x_grid[0, :].values  # Extract longitude from first row
    lat_grid_1d = y_grid[:, 0].values  # Extract latitude from first column
    depth_grid_1d = z_grid.values

    # For centre coordinates
    lon_centre_1d = x_centre[0, :].values
    lat_centre_1d = y_centre[:, 0].values
    depth_centre_1d = z_centre.values

    # Create new dataset with proper coordinate structure
    ds_new = xr.Dataset(
        # Data variables
        data_vars={
            'u1mean': (['record', 'k_grid', 'j_grid', 'i_grid'], u1_full,
                        {'long_name': 'Mean u1 velocity component', 'units': 'ms-1'}),
            'u2mean': (['record', 'k_grid', 'j_grid', 'i_grid'], u2_full,
                        {'long_name': 'Mean u2 velocity component', 'units': 'ms-1'}),
            'wmean': (['record', 'k_grid', 'j_grid', 'i_grid'], w_full,
                        {'long_name': 'Mean vertical velocity', 'units': 'ms-1'}),
            'temp': (['record', 'k_grid', 'j_grid', 'i_grid'], temp_full,
                    {'long_name': 'Temperature', 'units': 'degrees_C'}),
            'salt': (['record', 'k_grid', 'j_grid', 'i_grid'], salt_full,
                    {'long_name': 'Salinity', 'units': 'psu'}),
            
            # Store time_days as datetime64 array preserving correct day values
            'time_days': (['record'], time_datetime64,
                            {'long_name': 'Time as datetime64',
                            'standard_name': 'time'}),
            
            # Keep original 2D coordinate grids as data variables if needed
            'x_grid': (['j_grid', 'i_grid'], x_grid.values,
                        {'long_name': 'Grid x-coordinates', 'units': 'm'}),
            'y_grid': (['j_grid', 'i_grid'], y_grid.values,
                        {'long_name': 'Grid y-coordinates', 'units': 'm'}),
            'x_centre': (['j_centre', 'i_centre'], x_centre.values,
                        {'long_name': 'Centre x-coordinates', 'units': 'm'}),
            'y_centre': (['j_centre', 'i_centre'], y_centre.values,
                        {'long_name': 'Centre y-coordinates', 'units': 'm'}),
        },
        
        # Coordinates
        coords={
            'record': ('record', range(nrecord), {'long_name': 'Record number'}),
            'time': time,
            'i_grid': ('i_grid', range(ni_grid), {'long_name': 'Grid i-index'}),
            'j_grid': ('j_grid', range(nj_grid), {'long_name': 'Grid j-index'}),
            'k_grid': ('k_grid', range(nk_grid), {'long_name': 'Grid k-index'}),
            'i_centre': ('i_centre', range(ni_centre), {'long_name': 'Centre i-index'}),
            'j_centre': ('j_centre', range(nj_centre), {'long_name': 'Centre j-index'}),
            'k_centre': ('k_centre', range(nk_centre), {'long_name': 'Centre k-index'}),
            
            # 1D coordinate arrays
            'longitude_grid': ('i_grid', lon_grid_1d, {'long_name': 'Longitude', 'units': 'degrees_east'}),
            'latitude_grid': ('j_grid', lat_grid_1d, {'long_name': 'Latitude', 'units': 'degrees_north'}),
            'depth_grid': ('k_grid', depth_grid_1d, {'long_name': 'Depth', 'units': 'm', 'positive': 'down'}),
            'longitude_centre': ('i_centre', lon_centre_1d, {'long_name': 'Centre longitude', 'units': 'degrees_east'}),
            'latitude_centre': ('j_centre', lat_centre_1d, {'long_name': 'Centre latitude', 'units': 'degrees_north'}),
            'depth_centre': ('k_centre', depth_centre_1d, {'long_name': 'Centre depth', 'units': 'm', 'positive': 'down'}),
        },
        
        # Global attributes
        attrs={
            'title': 'Expanded 3D grid from sparse format',
            'description': 'Converted from sparse ns3 format to full i,j,k grid',
            'missing_value': np.nan,
            'Conventions': 'CF-1.6'
        }
    )

    # Set encoding to handle NaN values properly and compress
    encoding = {}
    for var in ['u1mean', 'u2mean', 'wmean', 'temp', 'salt']:
        encoding[var] = {'zlib': True, 'complevel': 4, '_FillValue': np.nan}

    # Save to new netCDF file
    ds_new.to_netcdf(output_file, encoding=encoding)

    # Close datasets
    ds.close()
    ds_new.close()

    print(f"Successfully converted {input_file} to {output_file}")
    print(f"Original sparse format: ns3={len(s2i)} points")
    print(f"New full grid format: {ni_grid}×{nj_grid}×{nk_grid}×{nrecord} = {ni_grid*nj_grid*nk_grid*nrecord} points")
    print(f"Data coverage: {len(s2i)/(ni_grid*nj_grid*nk_grid)*100:.1f}% of grid points have data")
