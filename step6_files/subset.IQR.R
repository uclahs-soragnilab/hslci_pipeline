### DESCRIPTION ###################################################################################
# Reads a vector of numbers returns the IQR of the points at the specified start and stop locations of the na removed vector
### NOTES #########################################################################################
### PREAMBLE ######################################################################################

### ORGANOID TRACKING EDA #########################################################################
subset.IQR <- function(vec,start.ind,stop.ind) {
  # Get desired subset
  sub.vec <- na.omit(vec)[start.ind:stop.ind]
  sub.IQR <- IQR(sub.vec, na.rm = TRUE)
  return(sub.IQR);
}

