import parcels as pc
import xarray as xr
import functions as mf
# import datetime as dati


# Specify file names
sparse_file = "C:/Users/treimer/Documents/R-temp-files/oceanparcels-playground/SHOC_flowfield_files/in_trans_2024-05.nc"
expanded_file = "C:/Users/treimer/Documents/R-temp-files/oceanparcels-playground/SHOC_flowfield_files/in_trans_2024-05_expanded.nc"

# Convert the file
mf.convert_sparse_to_full_grid(sparse_file, expanded_file)

# Load and inspect the result
ds_result = xr.open_dataset(expanded_file)
print(ds_result)

fset = pc.FieldSet.from_mitgcm(
    filenames=expanded_file,
    variables={'U': 'u1mean', 'V': 'u2mean', 'W': 'wmean'},
    dimensions={'time': 'time_days', 'depth': 'depth_grid', 'lat': 'latitude_grid', 'lon': 'longitude_grid'},
    # time_periodic=False,
    chunksize='auto',
    allow_time_extrapolation=True
)

print("Fieldset created successfully!")
print("You have created a fieldset with grid type: %s" %fset.U.grid.gtype)
print(f"Available fields: {fset.get_fields()}")
print(f"Time range: {fset.U.grid.time_full[0]} to {fset.U.grid.time_full[-1]}")

# fset.U.show(show_time = dati.timedelta(days = 5).total_seconds(), depth_level = 8)
# fset.U.show(show_time = dati.timedelta(days = 30).total_seconds(), depth_level = 8)
