#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)
pid = args[1]
bid_arr = args[-(0:1)]

library(RMySQL)
library(e1071)

# Connect to database
db = dbConnect(MySQL(), user='whaze', password='', dbname='mlb_stats', host='127.0.0.1')
query = "select balls,strikes,outs,start_speed,end_speed,px,pz,pfx_x,pfx_z,break_y,break_angle,break_length,spin_dir,spin_rate"


# Get pitcher data (Training Data)
pitcher_query = paste(query, ",pitcher_success from pitches where pitcher_id=", pid, sep=" ")
print (pitcher_query)
p  = dbSendQuery(db, pitcher_query)
p_data = fetch(p, n=-1)



#	Remove the responsive variables from the data set 
p_y = subset(p_data, select = pitcher_success)
p_x = subset(p_data, select = -pitcher_success)
print(nrow(p_x))
print(nrow(p_y))

cat("Starting classification of pitcher data\n")
svm_p <- svm(x=p_x, y=p_y, gamma = 0.1, probability=TRUE)

for (i in bid_arr) {

	cat("Starting prediction: ")
	print(i)

	# Get batter data
	batter_query = paste(query, "from pitches where batter_id=",i, "and pitcher_success<0", sep=" ")
	b  = dbSendQuery(db, batter_query)
	b_data = fetch(b, n=-1)

	res  <- predict(svm_p, b_data, probability=TRUE)
	print(summary(res))
	cat("\n\n")
}

#cat("Writing to file")
#fh <-file("Results.txt")
#write(res, file=fh, sep="\n")

