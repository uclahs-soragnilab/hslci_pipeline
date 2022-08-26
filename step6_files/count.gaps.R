### DESCRIPTION ###################################################################################
# Reads a vector of numbers and counts the number of discontinuities (connected regions of NAs)
### NOTES #########################################################################################
### PREAMBLE ######################################################################################

### ORGANOID TRACKING EDA #########################################################################
count.gaps <- function(vec) {
  NonNAindex <- which(!is.na(vec));
  # Iterate over each index
  num.gaps <- 0
  if (length(NonNAindex) <= 1) {
    num.gaps <- 0;
  } else {
    for (val in 1:(length(NonNAindex)-1)) {
      if (as.integer(NonNAindex[val]+1) != as.integer(NonNAindex[val+1])){ # The next index is not 1 more than the current
        num.gaps <- num.gaps+1;
      }
    }
  }
  return(num.gaps);
}