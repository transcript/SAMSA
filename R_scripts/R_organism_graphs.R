# R_organism_graphs.R
# Created 3/08/2017, by Sam Westreich
# Last updated 3/28/2017

library(data.table)
library("ggplot2")
library(scales)
library(gridExtra)
library(reshape2)

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

all_table <- control_table_trimmed
all_table <- merge(all_table, exp_table_trimmed, by = 0, all = TRUE)
rownames(all_table) <- all_table[,1]
all_table[is.na(all_table)] <- 0
all_table[, "Total"] <- rowSums(all_table[,c(2:length(all_table))])
all_table <- all_table[ with(all_table, order(-Total)), ]
names(all_table)[names(all_table) == 'Row.names'] <- 'Organism'
all_table$Organism <- substring(all_table$Organism, 2, nchar(all_table$Organism)-1)

# continue here to include only the top 30 most abundant organisms
all_table <- rbind(all_table[1:29,], all_table[nrow(all_table),])
all_table <- all_table[, -ncol(all_table)]

# melt here rearranges the shape for turning into a stacked bar graph
all_table_m <- melt(cbind(all_table, Organism = rownames(all_table)), id.vars = c('Organism'))

CbPalette <- c("#a6cee3", "#1f78b4", "#b2df8a", "#33a02c",  "#fb9a99", "#e31a1c", "#fdbf6f", 
               "#ff7f00", "#cab2d6", "#6a3d9a", "#ffff99", "#b15928", "#8dd3c7",  "#ffffb3",  
               "#bebada",  "#fb8072",  "#80b1d3",  "#fdb462",  "#b3de69", "#fccde5",  
               "#d9d9d9",  "#bc80bd",  "#ccebc5",  "#ffed6f", "#e41a1c",  "#377eb8", 
               "#4daf4a",  "#984ea3",  "#ff7f00", "#ffff33",  "#a65628",  "#f781bf",  
               "#999999", "#000000")


relative_ggplot <- ggplot(all_table_m, aes(x = variable, y = value, fill = Organism)) +
  geom_bar(position = "fill", stat = "identity") +
  scale_fill_manual(values = CbPalette) +
  scale_y_continuous(labels = percent_format()) +
  theme(legend.position = "none") +
  guides(fill = guide_legend(ncol=4)) +
  ggtitle("Top 30 functions by relative abundance") +
  xlab("Sample ID") + ylab("Relative activity of total sample")

relative_ggplot

absolute_ggplot <- ggplot(all_table_m3, aes(x = variable, y = value, fill = Organism)) +
  geom_bar(stat = "identity") +
  scale_fill_manual(values = CbPalette) +
  theme(legend.position = "bottom") +
  guides(fill = guide_legend(ncol=3)) +
  ggtitle("Top 30 organisms by total abundance") +
  xlab("Sample ID") + ylab("Activity reads per sample")

absolute_ggplot

grid.arrange(relative_ggplot, absolute_ggplot, ncol = 1)