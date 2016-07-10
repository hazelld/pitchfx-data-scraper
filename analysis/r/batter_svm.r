#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)
pid = args[1]
bid = args[2]

library(RMySQL)
library(e1071)

# Connect to database
db = dbConnect(MySQL(), user='whaze', password='', dbname='mlb_stats', host='127.0.0.1')
query = "select balls,strikes,outs,start_speed,end_speed,px,pz,pfx_x,pfx_z,break_y,break_angle,break_length,spin_dir,spin_rate"


# Get batter data
batter_query = paste(query, ",pitcher_succes from pitches where batter_id=",bid, sep=" ")
b  = dbSendQuery(db, batter_query)
b_data = fetch(b, n=-1)
b_y = subset(b_data, select=pitcher_success)
b_x = subset(b_data, select=-pitcher_success)
print(nrow(b_y))
print(nrow(b_x))

# Get pitcher data (Prediction Data)
pitcher_query = paste(query, "from pitches where pitcher_id=", pid, sep=" ")
print (pitcher_query)
p  = dbSendQuery(db, pitcher_query)
p_data = fetch(p, n=-1)



#	Remove the responsive variables from the data set 
cat("Starting classification of batter data\n")
svm_b <- svm(x=b_x, y=b_y, gamma = 0.1, probability=TRUE)

cat("Starting prediction: ")
print(i)


res  <- predict(svm_p, p_data, probability=TRUE)
print(summary(res))
cat("\n\n")


#cat("Writing to file")
#fh <-file("Results.txt")
#write(res, file=fh, sep="\n")

