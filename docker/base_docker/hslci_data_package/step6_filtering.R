### LOAD PACKAGES ###
library(plyr);
library(dplyr);
library(rpart);
library(mlr3verse);
library(mlr3);
library(pROC);
library(precrec);
library(xgboost);
library(mlr3viz);


### LOAD SUPPLEMENTARY R SCRIPTS 
source("/src/script/count.gaps.R")
source("/src/script/n.lgst.dm.dt.R")
source("/src/script/subset.IQR.R")

args = commandArgs(trailingOnly=TRUE)

## DEFINE PATHS TO TRAINING AND UNLABELED DATA 
training_data_path <- "/src/script/training_data"
unlabeled_data_path <- file.path(args[1], "condition-level_aggregate_data") # This must be the output path from step 5 ending with "/condition-level_aggregate_data"

## LOAD UNLABELED DATA
#BT474.pathways <- list.files('Data/unfiltered_mass_tracks_BT474');
#MCF7.pathways  <- list.files('Data/unfiltered_mass_tracks_MCF7');
unlabeled.pathways <- list.files(unlabeled_data_path, pattern = 'agg_mass_tracks_unfiltered.csv');

#BT474.pathways <- paste0('Data/unfiltered_mass_tracks_BT474/', BT474.pathways);
#MCF7.pathways  <- paste0('Data/unfiltered_mass_tracks_MCF7/', MCF7.pathways);
unlabeled.pathways <- paste0(unlabeled_data_path,'/',unlabeled.pathways);

max.timepoint  <- 381;
#combined.pathways <- c(BT474.pathways, MCF7.pathways);
combined.pathways <- unlabeled.pathways;

## CALCULATE FEATURES FOR UNLABELED DATA
unlabeled.data <- NULL;

for (i in 1:length(combined.pathways)) {
    
    file.data <- read.csv(combined.pathways[i]);
    
    #if (i <= 66) {
    #    file.data$UTrackID <- as.character(paste0("BT",format(file.data$UTrackID,scientific = FALSE)));
    #} else {
    #    file.data$UTrackID <- as.character(paste0("MCF",format(file.data$UTrackID,scientific = FALSE)));
    #}
    
    row.names(file.data)      <- file.data$UTrackID;
    file.data                 <- file.data[, -c(1:2)]; # Remove first 2 label columns 
    file.data                 <- file.data[,1:max.timepoint]; # Trim to max timepoint
    file.data[file.data == 0] <- NA; # Replace 0s with NAs
    
    # Extract features of interest
    count.na            <- as.data.frame(apply(file.data, 1, function(x) sum(is.na(x))));
    initial.size.sample <- as.data.frame(apply(file.data, 1, function(x) median(na.omit(x)[1:2], na.rm = TRUE)));
    sample.IQR     <- as.data.frame(apply(file.data, 1, function(x) IQR(na.omit(x),na.rm = TRUE)));
    start.IQR      <- as.data.frame(apply(file.data, 1, function(x) subset.IQR(x,1,12)));
    end.IQR        <- as.data.frame(apply(file.data, 1, function(x) subset.IQR(x,-12,-1)));
    
    classifier.data <- data.frame(
        UTrackID = row.names(count.na),
        na.count = count.na[,1],
        initial.size.sample = initial.size.sample[,1],
        sample.IQR = sample.IQR[,1],
        start.IQR = start.IQR[,1],
        end.IQR = end.IQR[,1]
        );
    
    unlabeled.data <- rbind(unlabeled.data, classifier.data);
    
    cat('Done processing sample number ', i, 'out of ', length(combined.pathways), '\n');
}
### SAVE FILE ##############################################################
#write.table(unlabeled.data, 'Track Verification/OrganoidClassifier/Data/2022-03-11_OrganoidTracking_unlabeled.classifier.data.txt', sep = '\t')

## LOAD THE MODEL TRAINING DATA
### LOAD TRAINING DATA #################################################################################
# Load the mass track data for the training dataset
BT474.E2            <- read.csv(paste0(training_data_path,'/2021_08_02_BT-474_E2_unfiltered_agg_mass_tracks.csv'));
BT474.B8            <- read.csv(paste0(training_data_path,'/2021_08_02_BT-474_B8_unfiltered_agg_mass_tracks.csv'));
MCF7.E2             <- read.csv(paste0(training_data_path,'/2021_07_24_MCF-7_E2_unfiltered_agg_mass_tracks.csv'));
MCF7.F8             <- read.csv(paste0(training_data_path,'/2021_07_24_MCF-7_F8_unfiltered_agg_mass_tracks.csv'));

#Trim to max.timepoint
max.timepoint = 381; 
BT474.E2            <- BT474.E2[,2:(max.timepoint+2)]; #2: to cut off X column, max+2 due to x and UTrackID columns
BT474.B8            <- BT474.B8[,2:(max.timepoint+2)];
MCF7.E2             <- MCF7.E2[,2:(max.timepoint+2)];
MCF7.F8             <- MCF7.F8[,2:(max.timepoint+2)];

# Load the manually annotated ground truth files for the training dataset
BT474.E2.validation <- read.table(paste0(training_data_path,'/2022-03-09_BT474_E2_unfiltered_manuallabel.txt'), sep = '\t', header = T);
BT474.B8.validation <- read.table(paste0(training_data_path,'/2022-03-09_BT474_B8_unfiltered_manuallabel.txt'), sep = '\t', header = T);
MCF7.E2.validation  <- read.table(paste0(training_data_path,'/2022-03-09_MCF7_E2_unfiltered_manuallabel.txt'), sep = '\t', header = T);
MCF7.F8.validation  <- read.table(paste0(training_data_path,'/2022-03-09_MCF7_F8_unfiltered_manuallabel.txt'), sep = '\t', header = T);

## TRAIN THE MODEL
#unlabeled.data <- read.table('Data/2022-03-09_OrganoidTracking_unlabeled.classifier.data.txt', sep = '\t', header = T);
#unlabelled.data <- read.tabdelimited('Data/2022-03-07_OrganoidTracking_unlabelled.classifier.data.txt');

## Combine wells for ML training set
# Change all UTrackID columns to character, add cell line label before UTrackID
BT474.E2.validation$UTrackID <- as.character(paste0("BT",format(BT474.E2.validation$UTrackID,scientific = FALSE)));
BT474.B8.validation$UTrackID <- as.character(paste0("BT",format(BT474.B8.validation$UTrackID,scientific = FALSE)));
MCF7.E2.validation$UTrackID  <- as.character(paste0("MCF",format(MCF7.E2.validation$UTrackID,scientific = FALSE)));
MCF7.F8.validation$UTrackID  <- as.character(paste0("MCF",format(MCF7.F8.validation$UTrackID,scientific = FALSE)));

BT474.E2$UTrackID <- as.character(paste0("BT",format(BT474.E2$UTrackID,scientific = FALSE)));
BT474.B8$UTrackID <- as.character(paste0("BT",format(BT474.B8$UTrackID,scientific = FALSE)));
MCF7.E2$UTrackID  <- as.character(paste0("MCF",format(MCF7.E2$UTrackID,scientific = FALSE)));
MCF7.F8$UTrackID  <- as.character(paste0("MCF",format(MCF7.F8$UTrackID,scientific = FALSE)));

# Combine validation data
combined.validation <- bind_rows(list(BT474.E2.validation,BT474.B8.validation,MCF7.E2.validation,MCF7.F8.validation))

# Add ground truth column as binary 1 or 0
combined.validation$ground.truth[combined.validation$BinaryLabel == TRUE] <- 1;
combined.validation$ground.truth[combined.validation$BinaryLabel == FALSE] <- 0;

# Combine mass data
mass.data                 <- bind_rows(list(BT474.E2,BT474.B8,MCF7.E2,MCF7.F8));
row.names(mass.data)      <- mass.data$UTrackID;
mass.data                 <- mass.data[, -1]; #Remove UTrackID column
mass.data[mass.data == 0] <- NA; # Replace 0s with NAs

# Extract features of interest in training dataset
count.na            <- as.data.frame(apply(mass.data, 1, function(x) sum(is.na(x))));
initial.size.sample <- as.data.frame(apply(mass.data, 1, function(x) median(na.omit(x)[1:2], na.rm = TRUE)));
sample.IQR     <- as.data.frame(apply(mass.data, 1, function(x) IQR(na.omit(x),na.rm = TRUE)));
start.IQR      <- as.data.frame(apply(mass.data, 1, function(x) subset.IQR(x,1,12)));
end.IQR        <- as.data.frame(apply(mass.data, 1, function(x) subset.IQR(x,-12,-1)));

# Create dataframe of features of interest and labels for ML analysis
classifier.data <- data.frame(
    UTrackID = row.names(count.na),
    na.count = count.na[,1],
    initial.size.sample = initial.size.sample[,1],
    sample.IQR = sample.IQR[,1],
    start.IQR = start.IQR[,1],
    end.IQR = end.IQR[,1]
    
    );

classifier.data <- merge(
    x = combined.validation[, c('UTrackID', 'ground.truth')],
    y = classifier.data,
    by.x = 'UTrackID',
    by.y = 'UTrackID',
    all.x = TRUE,
    all.y = TRUE
    );

# Set labels as a factor variable
classifier.data$ground.truth <- factor(classifier.data$ground.truth);

## TRAIN THE ML MODEL
# Train the mL model
task        <- as_task_classif(classifier.data[, c(2:ncol(classifier.data))], target = 'ground.truth');
learner     <- lrn('classif.xgboost', predict_type = 'prob', eval_metric = 'logloss' );
resampling  <- rsmp('cv', folds = 3); # 3-folds is standard
rr          <- resample(task, learner, resampling, store_models = TRUE);

pred <- learner$train(task)$predict(task);

# Extracted model results
model.results <- data.frame(
    CV.score = rr$aggregate(msr('classif.acc')),
    true.pos.rate = rr$aggregate(msr('classif.tpr')),
    false.dis.rate = rr$aggregate(msr('classif.fdr')),
    true.pos = pred$confusion[1,1],
    true.neg = pred$confusion[2,2],
    false.pos = pred$confusion[1,2],
    false.neg = pred$confusion[2,1]
    );

# CV score is your best measurement of model accuracy
cat(paste0('Cross-validation score (CV): ', model.results$CV.score));

### PLOT ROC  ######################################################################
autoplot(pred, type = 'roc');

## APLY TRAINED MODEL TO FULL DATASET
viability.preds <- predict(learner, unlabeled.data[,c(2:ncol(unlabeled.data))]);
table(viability.preds);

well.predictions <- data.frame(
    UTrackID = unlabeled.data$UTrackID,
    Model.pred = viability.preds
    );

write.table(well.predictions, paste0(unlabeled_data_path,'/organoid_track_validity_prediction.txt'), sep = '\t')