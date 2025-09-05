# oceanparcels-playground
This repo is just for me to play around with and explore OceanParcels.

## Files

**01_download-tasse-files.Rmd**: This script uses `curl` to download daily tasse SHOC files from the CSIRO thredds server. However, it turns out that these files don't include a w variable so can't actually be used. I'll leave the code here for now just in case.
**02_reindex-shoc-files.RMD**: I expended a lot of effort manually re-indexing the SHOC files so that they would be compatible with NEMO indexing. However, on further research, it turns out parcels can already handle the SHOC indexing with its [`from_mitgcm` method](https://docs.oceanparcels.org/en/latest/reference/fields.html#parcels.fieldset.FieldSet.from_mitgcm). So much for that.

**functions.py**: This handles all the conversion of SHOC sparse files to expanded SHOC files, making them easier to handle and extract data from.

