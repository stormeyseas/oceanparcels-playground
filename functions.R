transform_time <- function(nc, start_time = NA) {
  # Get time data
  t <- ncvar_get(nc, "time")

  # If start time is not given, extract from data
  time_units <- nc$var$time$units
  if (is.null(time_units)) {
    time_units <- "1990-01-01 00:00:00"
  } else {
    time_units <- time_units %>% str_remove("days since ") %>% str_remove(" [+]10")
  }
  
  time_reference <- lubridate::parse_date_time2(time_units, orders = "%Y-%m-%d %H:%M:%S")
  t <- time_reference + lubridate::duration(t, "days")

  if (is.na(start_time)) {
    # If no start time is given, time starts at 0
    new_t <- t - t[1] # in seconds automatically
  } else {
    new_t <- t - start_time
  }
  
  return(as.numeric(new_t))
}

get_first_time <- function(nc) {
  t <- ncvar_get(nc, "time")[1]
  time_units <- nc$var$time$units
  if (is.null(time_units)) {
    time_units <- "1990-01-01 00:00:00"
  } else {
    time_units <- time_units %>% str_remove("days since ") %>% str_remove(" [+]10")
  }
  
  time_reference <- lubridate::parse_date_time2(time_units, orders = "%Y-%m-%d %H:%M:%S")
  t <- time_reference + lubridate::duration(t, "days")
  return(t)
}
