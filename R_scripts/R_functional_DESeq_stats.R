# R_functional_DESeq_stats_simplified.R
# Created 3/08/2017, by Sam Westreich
# Last updated 3/16/2017

library("DESeq2")
library(data.table)

setwd("~/R_testing/")

control_files <- list.files(
  pattern = "control_function*", full.names = T, recursive = FALSE)
control_names = ""
for (name in control_files) {
  control_names <- c(control_names, unlist(strsplit(name, split='_', fixed=TRUE))[1])} 
control_names <- control_names[-1]
control_names_trimmed = ""
for (name in control_names) {
  control_names_trimmed <- c(control_names_trimmed, unlist(strsplit(name, split='.', fixed=TRUE))[2])}
control_names_trimmed <- control_names_trimmed[-1]

exp_files <- list.files(
  pattern = "experiment_function*", full.names = T, recursive = FALSE)
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
control_table_trimmed <- control_table[,-ncol(control_table), drop = FALSE]

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
exp_table_trimmed <- exp_table[,-ncol(exp_table), drop = FALSE]
rm(control_table, exp_table, x, y)

if (colnames(control_table_trimmed[1]) == "md5") {
  colnames(control_table_trimmed) = c("md5", control_names_trimmed)
  colnames(exp_table_trimmed) = c("md5", exp_names_trimmed) 
} else {
  colnames(control_table_trimmed) = c(control_names_trimmed)
  colnames(exp_table_trimmed) = c(exp_names_trimmed) } 

# filtering
control_to_be_removed <- control_table_trimmed[grep("hypothetical", rownames(control_table_trimmed)),]
control_table_filtered <- control_table_trimmed[ !(rownames(control_table_trimmed) %in% rownames(control_to_be_removed)),]
control_to_be_removed <- control_table_trimmed[grep("predicted", rownames(control_table_trimmed)),]
control_table_filtered <- control_table_filtered[ !(rownames(control_table_filtered) %in% rownames(control_to_be_removed)),]

exp_to_be_removed <- exp_table_trimmed[grep("hypothetical", rownames(exp_table_trimmed)),]
exp_table_filtered <- exp_table_trimmed[ !(rownames(exp_table_trimmed) %in% rownames(exp_to_be_removed)),]
exp_to_be_removed <- exp_table_trimmed[grep("predicted", rownames(exp_table_trimmed)),]
exp_table_filtered <- exp_table_filtered[ !(rownames(exp_table_filtered) %in% rownames(exp_to_be_removed)),]
rm(control_to_be_removed, exp_to_be_removed)

complete_table <- merge(control_table_filtered, exp_table_filtered, by=c(0,1), all = TRUE)
complete_table[is.na(complete_table)] <- 1
complete_table <- complete_table[,-2]

complete_table$Simplified_Function <- sapply(strsplit(as.character(complete_table$Row.names), ";"), "[", 1)
complete_table$Simplified_Function <- as.factor(complete_table$Simplified_Function)
complete_table <- complete_table[,c(ncol(complete_table), 1:ncol(complete_table))]
complete_table <- complete_table[,c(-2, -ncol(complete_table))]

# this next step compresses out duplicates
complete_table2 <- complete_table
complete_table2 <- data.table(complete_table2)
complete_table2 <- complete_table2[, lapply(.SD, sum), by=Simplified_Function]
complete_table2 <- as.data.frame(complete_table2)
complete_table2 <- complete_table2[!is.na(complete_table2$Simplified_Function), ]
rownames(complete_table2) = complete_table2$Simplified_Function
complete_table2 <- complete_table2[, -1]

# DESeq time
completeCondition <- data.frame(condition=factor(c(rep("control", length(control_files)), 
                               rep("experimental", length(exp_files)))))
dds <- DESeqDataSetFromMatrix(complete_table2, completeCondition, ~ condition)
dds <- DESeq(dds)

baseMeanPerLvl <- sapply( levels(dds$condition), function(lvl) rowMeans( 
  counts(dds,normalized=TRUE)[,dds$condition == lvl] ) )

res <- results(dds, contrast = c("condition", "experimental", "control"))
func_results <- data.frame(res)
func_results$Function <- complete_table2$Simplified_Function
func_results <- merge(func_results, baseMeanPerLvl, by="row.names")
func_results <- func_results[,c(1,8,2,9,10,3,4,5,6,7)]
colnames(func_results)[c(4,5)] <- c("controlMean", "experimentalMean")
sorted_func_results <- func_results[order(-func_results$baseMean),]
colnames(sorted_func_results)[1] <- "Function Name"

# optional - write out the results as a table
write.table(func_results, file = "DESeq_functional_output_with_md5s.tab", append = FALSE, 
            quote = FALSE, sep = "\t", row.names = FALSE, col.names = TRUE)