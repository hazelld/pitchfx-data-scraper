
library(RMySQL)
library(e1071)

db <- dbConnect(MySQL(), user='whaze', password='', dbname='mlb_stats', host='127.0.0.1')
query <- "select batter_fp, ev from matchups"

b = dbSendQuery (db, query)
data = fetch(b, n=-1 )

ndata = cut (data$ev, breaks=quantile(data$ev, c(0, 0.25)), include.lowest=TRUE)
print(ndata)

pdf("result_q1.pdf")
plot(ndata, ylab="EV", xlab="Fantasy Points")
abline(lm(ndata["ev"]~ndata["batter_fp"]), col="red")

summary(data$ev)
garbage <- dev.off
