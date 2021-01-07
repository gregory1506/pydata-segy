# pydata-segy

Using tools in the pydata stack for reading segyfiles and converting them to useable formats for processing and visualization.

Seisimic data comes in many forms, but is predominantly shared in the form of SEGY for various proprietary reasons. Can the viewing of SEGY data be made cloud native without the loss of speed, generality or function?

Some formats lend themselves towards cloud architectures like NetCDF4, HDF5, Zarr and openVDS. The goal is to be able to choose interchangeably between these formats from SEGY and perform meaninful Business Intelligence and Visualizations.

