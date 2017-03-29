# R_functional_graphs_simplified.R
# Created 3/08/2017, by Sam Westreich
# Last updated 3/08/2017

setwd("~/R_testing/")

control_files <- list.files(
  pattern = "con_*", full.names = T, recursive = FALSE)
control_names = ""
for (name in control_files) {
  control_names <- c(control_names, unlist(strsplit(name, split='_', fixed=TRUE))[2])} 
control_names <- control_names[-1]
control_names_trimmed = ""
for (name in control_names) {
  control_names_trimmed <- c(control_names_trimmed, unlist(strsplit(name, split='.', fixed=TRUE))[1])}
control_names_trimmed <- control_names_trimmed[-1]

exp_files <- list.files(
  pattern = "exp_*", full.names = T, recursive = FALSE)
exp_names = ""
for (name in exp_files) {
  exp_names <- c(exp_names, unlist(strsplit(name, split='_', fixed=TRUE))[2])}
exp_names <- exp_names[-1]
exp_names_trimmed = ""
for (name in exp_names) {
  exp_names_trimmed <- c(exp_names_trimmed, unlist(strsplit(name, split='.', fixed=TRUE))[1])}
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

# merging the two tables together for the graph
all_table <- control_table_filtered
all_table[, " "] <- 0
if (colnames(control_table_filtered[1]) == "md5") {
  all_table <- merge(all_table, exp_table_filtered, by = c(0,1), all = TRUE) # this step may take a while, depending on total number of annotations
} else {
  all_table <- merge(all_table, exp_table_filtered, by = 0, all = TRUE)
  rownames(all_table) <- all_table[,1]
}
all_table[is.na(all_table)] <- 0
all_table$md5 <- NULL
all_table[, "Total"] <- rowSums(all_table[,c(2:length(all_table))])
all_table <- all_table[ with(all_table, order(-Total)), ]
names(all_table)[names(all_table) == 'Row.names'] <- 'Function'
all_table$Function <- substring(all_table$Function, 2, nchar(all_table$Function)-1)

# let's save everything up to this point:
all_table_all <- all_table

# continue here to include only the top 30 most abundant functions.
all_table <- rbind(all_table[1:29,], all_table[nrow(all_table),])
all_table <- all_table[, -ncol(all_table)]

# melt here rearranges the shape for turning into a stacked bar graph
library(reshape2)
all_table_m <- melt(cbind(all_table, Function = rownames(all_table)), id.vars = c('Function'))

# combining similar functions
library(plyr)
all_table_m$Simplified_Function <- sapply(strsplit(as.character(all_table_m$Function), ";"), "[", 1)
all_table_m$Simplified_Function <- as.factor(all_table_m$Simplified_Function)

all_table_m2 <- all_table_m[c(4,2,3)]
all_table_m2 <- ddply(all_table_m2, c("Simplified_Function", "variable"), numcolwise(sum))
names(all_table_m2)[1] <- "Function"
all_table_m2$Function <- as.factor(all_table_m2$Function)
all_table_m3 <- all_table_m2[order(all_table_m2$variable, all_table_m2$Function),]
rm(all_table_m2, all_table_m)

CbPalette <- c("#a6cee3", "#1f78b4", "#b2df8a", "#33a02c",  "#fb9a99", "#e31a1c", "#fdbf6f", 
               "#ff7f00", "#cab2d6", "#6a3d9a", "#ffff99", "#b15928", "#8dd3c7",  "#ffffb3",  
               "#bebada",  "#fb8072",  "#80b1d3",  "#fdb462",  "#b3de69", "#fccde5",  
               "#d9d9d9",  "#bc80bd",  "#ccebc5",  "#ffed6f", "#e41a1c",  "#377eb8", 
               "#4daf4a",  "#984ea3",  "#ff7f00", "#ffff33",  "#a65628",  "#f781bf",  
               "#999999", "#000000")


library("ggplot2")
library(scales)
relative_ggplot <- ggplot(all_table_m3, aes(x = variable, y = value, fill = Function)) +
  geom_bar(position = "fill", stat = "identity") +
  scale_fill_manual(values = CbPalette) +
  scale_y_continuous(labels = percent_format()) +
  theme(legend.position = "none") +
  guides(fill = guide_legend(ncol=4)) +
  ggtitle("Top 30 protein functions by relative abundance") +
  xlab("Sample ID") + ylab("Relative activity of total sample")

relative_ggplot

absolute_ggplot <- ggplot(all_table_m3, aes(x = variable, y = value, fill = Function)) +
  geom_bar(stat = "identity") +
  scale_fill_manual(values = CbPalette) +
  theme(legend.position = "bottom") +
  guides(fill = guide_legend(ncol=3)) +
  ggtitle("Top 30 protein functions by total abundance") +
  xlab("Sample ID") + ylab("Activity reads per sample")

absolute_ggplot

library(gridExtra)
grid.arrange(relative_ggplot, absolute_ggplot, ncol = 1)
