# R_organism_DESeq_stats.R
# Created 3/08/2017, by Sam Westreich
# Last updated 3/28/2017

library("DESeq2")
library(data.table)

setwd("~/R_testing/")

control_files <- list.files(
  pattern = "control_org*", full.names = T, recursive = FALSE)
control_names = ""
for (name in control_files) {
  control_names <- c(control_names, unlist(strsplit(name, split='_', fixed=TRUE))[1])} 
control_names <- control_names[-1]
control_names_trimmed = ""
for (name in control_names) {
  control_names_trimmed <- c(control_names_trimmed, unlist(strsplit(name, split='.', fixed=TRUE))[2])}
control_names_trimmed <- control_names_trimmed[-1]

exp_files <- list.files(
  pattern = "experiment_org*", full.names = T, recursive = FALSE)
exp_names = ""
for (name in exp_files) {
  exp_names <- c(exp_names, unlist(strsplit(name, split='_', fixed=TRUE))[1])}
exp_names <- exp_names[-1]
exp_names_trimmed = ""
for (name in exp_names) {
  exp_names_trimmed <- c(exp_names_trimmed, unlist(strsplit(name, split='.', fixed=TRUE))[2])}
exp_names_trimmed <- exp_names_trimmed[-1]
rm (exp_names, control_names, name)

# loading the control table
y <- 0
for (x in control_files) {
  y <- y + 1
  if (y == 1) {
    control_table <- read.table(file = x, header=F, quote = "", sep = "\t", fill = TRUE)
    if (ncol(control_table) == 4) {
      colnames(control_table) = c("DELETE", x, "V3", "md5")
      control_table <- control_table[,c(4,2,3)] 
    } else {
      colnames(control_table) = c("DELETE", x, "V3")
      control_table <- control_table[,c(3,2)] }
    if (nrow(control_table) > 1000) {
       control_table <- control_table[c(1:1000),] }}     # can be deleted, restricts to top 1k hits
  if (y > 1) {
    temp_table <- read.table(file = x, header = F, quote = "", sep = "\t", fill = TRUE)
    if (nrow(temp_table) > 1000) {
      temp_table <- temp_table[c(1:1000),] }      # can be deleted, restricts to top 1k hits
    print (x)
    if (ncol(temp_table) == 4) {
      colnames(temp_table) = c("DELETE", x, "V3", "md5") 
    } else {
      colnames(temp_table) = c("DELETE", x, "V3") }
    control_table <- merge(control_table, temp_table[,c(2,3)], by = "V3", all.x = T)  }
}
control_table[is.na(control_table)] <- 0
rownames(control_table) = control_table$V3
control_table_trimmed <- control_table[,-1, drop = FALSE]

# loading the exp table
y <- 0
for (x in exp_files) {
  y <- y + 1
  if (y == 1) {
    exp_table <- read.table(file = x, header=F, quote = "", sep = "\t", fill = TRUE)
    if (ncol(exp_table) == 4) {
      colnames(exp_table) = c("DELETE", x, "V3", "md5")
      exp_table <- exp_table[,c(4,2,3)] 
    } else {
      colnames(exp_table) = c("DELETE", x, "V3")
      exp_table <- exp_table[,c(3,2)] }
    if (nrow(exp_table) > 1000) { exp_table <- exp_table[c(1:1000),] }} # can be deleted, restricts to top 1k hits
  if (y > 1) {
    temp_table <- read.table(file = x, header = F, quote = "", sep = "\t", fill = TRUE)
    if (nrow(temp_table) > 1000) { temp_table <- temp_table[c(1:1000),] }    # can be deleted, restricts to top 1k hits
    print (x)
    if (ncol(temp_table) == 4) {
      colnames(temp_table) = c("DELETE", x, "V3", "md5") 
    } else {
      colnames(temp_table) = c("DELETE", x, "V3") }
    exp_table <- merge(exp_table, temp_table[,c(2,3)], by = "V3", all.x = T)  }
}
exp_table[is.na(exp_table)] <- 0
rownames(exp_table) = exp_table$V3
exp_table_trimmed <- exp_table[,-1, drop = FALSE]
rm(control_table, exp_table, x, y)

if (colnames(control_table_trimmed[1]) == "md5") {
  colnames(control_table_trimmed) = c("md5", control_names_trimmed)
  colnames(exp_table_trimmed) = c("md5", exp_names_trimmed) 
} else {
  colnames(control_table_trimmed) = c(control_names_trimmed)
  colnames(exp_table_trimmed) = c(exp_names_trimmed) } 

complete_table <- merge(control_table_trimmed, exp_table_trimmed, by=0, all = TRUE)
complete_table[is.na(complete_table)] <- 1

# this next step compresses out duplicates
complete_table2 <- complete_table
complete_table2 <- data.table(complete_table2)
complete_table2 <- complete_table2[, lapply(.SD, sum), by=Row.names]
complete_table2 <- as.data.frame(complete_table2)
complete_table2 <- complete_table2[!is.na(complete_table2$Row.names), ]
rownames(complete_table2) = complete_table2$Row.names
complete_table2 <- complete_table2[, -1]

# DESeq time
completeCondition <- data.frame(condition=factor(c(rep("control", length(control_files)), 
                               rep("experimental", length(exp_files)))))
dds <- DESeqDataSetFromMatrix(complete_table2, completeCondition, ~ condition)
dds <- DESeq(dds)

baseMeanPerLvl <- sapply( levels(dds$condition), function(lvl) rowMeans( 
  counts(dds,normalized=TRUE)[,dds$condition == lvl] ) )

res <- results(dds, contrast = c("condition", "experimental", "control"))
org_results <- data.frame(res)
org_results <- merge(org_results, baseMeanPerLvl, by="row.names")
org_results <- org_results[,c(1,8,2,9,10,3,4,5,6,7)]
colnames(org_results)[c(4,5)] <- c("controlMean", "experimentalMean")
sorted_org_results <- org_results[order(-org_results$baseMean),]
colnames(sorted_org_results)[1] <- "Organism Name"

# optional - write out the results as a table
write.table(org_results, file = "DESeq_org_output.tab", append = FALSE, 
            quote = FALSE, sep = "\t", row.names = FALSE, col.names = TRUE)