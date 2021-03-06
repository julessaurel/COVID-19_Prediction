# COVID-19_Prediction

## Introduction
In their paper in the BMJ Supportive & Palliative Care in July 2020 [1], Parchure and colleagues propose a model to detect mortality in patients with COVID-19 infection based on multiple features including patient demographics, laboratory test results and vital parameters. 
The primary outcome of interest was in- hospital death within 20–84 hours from the time of prediction.

## Sampling strategy
For every patient, **daily** feature vectors daily feature vectors starting from admission date until the date of discharge or death were build.
For these feature vectors, the three most recent recorded assessments from time-series data that were available when each feature vector was created, were used.

<img src="https://raw.githubusercontent.com/JimSmit/COVID-19_Prediction/main/images/pos_label.PNG" width="300">
<img src="https://raw.githubusercontent.com/JimSmit/COVID-19_Prediction/main/images/neg_label.PNG" width="300">

Feature vectors were only labeled positive if the 'event' (patient's death is this case) occured somewhere between 20 and 84 hours after the timestamp of the feature vector (the time of prediction). That means, this sampling strategy forces a model to predict a patient death in a prediction window of 64 hours, with a gap of 20 hours between the moment of prediction and the start of the prediction window. 

**Feature window**: 3 most recent accessments of variable (so actual window size depends on variable availability).
**gap**: 20 hours.
**prediction window**: 64 hours.

<img src="https://raw.githubusercontent.com/JimSmit/COVID-19_Prediction/main/images/windows.png" width="500">

About these sizes, the authors write the following:

"For pragmatic reasons, we defined near- term outcomes as those occurring between 20 and 84 hours from the prediction time. Approximately a day (20 hours) would **allow time for providers for manual assessment by clinicians, trying interventions to prevent further deterioration and for performing the goals- of- care and/or palliative care consultations to develop an indi- vidualised plan of care after their clinical assessment**. The 3 days horizon (72 hours) was extended by 12 hours for **operational reasons of accommodating a complete day at a hospital until evening**."

Furthermore, the authors write the following about their labeling srategy:

"The interval between the time of discharge and the time of generating each feature vector was generated daily for each patient. If the discharge disposition was ‘Expired (ie, dead)’ and the interval was between 20 and 84 hours, we labelled the feature vectors as positive. If the discharge disposition was ‘Not Expired’ and the interval was between 20 and 84 hours, we labelled the feature vectors negative. **We excluded the remaining feature vectors from our cohort."**

Thus, feature vectors were sampled daily between 20 and 84 hours before the moment of discharge. If a patient was dead at moment of discharge, the feature vector was labeled poitive, and negative otherwise. And **no** feature vectors were kept which were sampled **outside** this 20-84 hours interval before discharge.

Below is a schematic overview of this sampling strategy:

<img src="https://raw.githubusercontent.com/JimSmit/COVID-19_Prediction/main/images/sampling_startegy_parchure.png" width="700">



## Modeling
As the distribution of positive and negative feature vectors was imbalanced, the negative feature samples were drandomly downsampled untill bith classes were balanced. 
A Random Forest was trained. Model hyperparameters were optimized using the following search spaces.

<img src="https://raw.githubusercontent.com/JimSmit/COVID-19_Prediction/main/images/hyper.PNG" width="500">

## Results
The authors report the following results.

<img src="https://raw.githubusercontent.com/JimSmit/COVID-19_Prediction/main/images/results.PNG" width="600">
<img src="https://raw.githubusercontent.com/JimSmit/COVID-19_Prediction/main/images/results_plot.PNG" width="600">

## Model Implementation
In this post, a Python implementation is presented to train and validate a model in the same fashion as being done in the discussed paper. Therby, some extra implementations are added:
- The size of the feature window (i.e. the number of most recent recorded assessments from time-series data to be included in the feature vector), prediction window and gap can be varied.
- The sampling strategy can be varied as well. As the paper describes a sampling strategy that only includes feature vectors sampled within 20 and 84 hours from the moment of discharge, the performance of the model is likely to be overestimated, as we remain uninformed about the model's performance on feature vectors sampled earlier during hospitalization. 

For example, would the model be able to distinguish between a feature vector sampled from a patient who eventually dies, 1 sampled 72 hours before disharge (so labeled positive) and 1 96 hours before discharge (so labeled negative)? In this implementation, we include feature vectors sampled during the whole stay of a patient, were the sampling frequency can be tuned for negative and positve feature vectors. We implementen the parameters 'int_neg' and 'int_pos' as the intervals (in hours) between every feeature vector being sampled for the negative and positive class respectively. 

<img src="https://raw.githubusercontent.com/JimSmit/COVID-19_Prediction/main/images/sampling_startegy_new.png" width="700">



1. Parchure P, Joshi H, Dharmarajan K, Freeman R, Reich DL, Mazumdar M, et al. Development and validation of a machine learning-based prediction model for near-term in-hospital mortality among patients with COVID-19. BMJ Support Palliat Care. 2020 Sep; 
