### DESCRIPTION ###################################################################################
# Reads a vector of numbers returns the nth highest change between adjacent points
### NOTES #########################################################################################
### PREAMBLE ######################################################################################

### ORGANOID TRACKING EDA #########################################################################
n.lgst.dm.dt <- function(vec,n) {
  # Get all dm/dt
  dm.dt <- diff(vec);
  # Sort
  sorted.dm.dt <- sort(dm.dt, decreasing = TRUE);
  dm.dt.n <- sorted.dm.dt[n]
  
  return(dm.dt.n);
}