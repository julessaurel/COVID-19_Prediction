# Import necessary libraries
import numpy as np
import pandas as pd
import datetime
import math
import matplotlib.pyplot as plt
import sys

def df_preparer(df,variables, val_share=0.25,test_share=0.2,random_state=0,norm=True):
    
    print('df_preparer triggered')
    
    """
    Prepares the train, test and validation dataframes. 
    Performs the splits and normalizes the data based on the train set.

    Parameters
    ----------
    df : pd.DataFrame
        The raw single-timestamp data for all patients. This df shoul contain the following columns: ['ID','BMI','AGE','DEST',
        'OPNAMETYPE','TIME','VAR','VALUE']
    variables: np.array[str]
        Array with strings representing the variable names to be included in the model (excluding demographics).
    val_share: Optional[float]
        Fraction of patients to be used in the validation set.
    val_share: Optional[float]
        Fraction of patients to be used in the test set.
    random_state: Optional[int]
        Random seed for the train-test/validation-splits. 
    norm: optional:[Bool]
        Flag to turn on normalization by standarziation. 
        
    Returns
    -------
    df_train,df_val,df_test,df_demo_train,df_demo_val,df_demo_test
    type : pd.DataFrame
    """
    
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    
    # create df with Demographics data (BMI and AGE) -- >  df_demo
    
    ids = np.unique(df['ID']) # Unique IDs in raw dataset
    bmi = []
    age =[]
    for i in ids:
        bmi.append(df[df['ID']==i].reset_index()['BMI'][0])
        age.append(df[df['ID']==i].reset_index()['AGE'][0])
    df_demo = pd.DataFrame()
    df_demo['ID'] = ids
    df_demo['BMI'] = bmi
    df_demo['AGE'] = age
    
    
    # Split raw df in training and validation set on patient level:
    ids_train,ids_val = train_test_split(ids, test_size=val_share,random_state=random_state)
    
    df_train_full = df[df['ID'].isin(ids_train)]
    df_val = df[df['ID'].isin(ids_val)]
    
    df_demo_train_full = df_demo[df_demo['ID'].isin(ids_train)]
    df_demo_val = df_demo[df_demo['ID'].isin(ids_val)]

    #split training set in training and testing set
    ids = np.unique(df_train_full['ID'])
    ids_train,ids_test = train_test_split(ids, test_size=test_share,random_state=random_state)
    
    df_train = df_train_full[df_train_full['ID'].isin(ids_train)]
    df_test = df_train_full[df_train_full['ID'].isin(ids_test)]

    df_demo_train = df_demo_train_full[df_demo_train_full['ID'].isin(ids_train)]
    df_demo_test = df_demo_train_full[df_demo_train_full['ID'].isin(ids_test)]
    
    
    
    print('Split train, val en test set: \n original shape: ',df.shape,
          '\n train shape: ',df_train.shape, 'unique patients: ', len(df_train['ID'].unique()),
          '\n Val shape: ',df_val.shape, 'unique patient: ', len(df_val['ID'].unique()),
          '\n Test shape: ',df_test.shape, 'unique patients: ', len(df_test['ID'].unique()))
    
    
    # Normaize data using standardization
    if norm:
                
        df_train_norm = pd.DataFrame() # intialize empty normalized train, val and test set.
        df_val_norm = pd.DataFrame()
        df_test_norm = pd.DataFrame()
        
        for v in variables: # loop trough unique variables
    
            train_idx = (df_train.VARIABLE == v) # Define indices in train set for this variable
            val_idx = (df_val.VARIABLE == v) # Define indices in validation set for this variable
            test_idx = (df_test.VARIABLE == v) # Define indices in test set for this variable
                    
            scaler = StandardScaler()
            scaler.fit(df_train.loc[train_idx,'VALUE'].values.reshape(-1, 1)) # Fit scaler only on training set
            
            temp = df_train.loc[train_idx,'VALUE'].copy() #define temporary copy of Values from training df from only this variable.
            if temp.shape[0] == 0:
                print(v,'not in training set')
            else:
                temp = scaler.transform(temp.values.reshape(-1, 1))
                snip = df_train.loc[train_idx]
                snip = snip.assign(VALUE=temp)
                df_train_norm = pd.concat([df_train_norm,snip],axis=0)
            
            temp = df_val.loc[val_idx,'VALUE'].copy()
            if temp.shape[0] == 0:
                print(v,'not in validation set')
            else:
                temp = scaler.transform(temp.values.reshape(-1, 1))
                snip = df_val.loc[val_idx]
                snip = snip.assign(VALUE=temp)
                df_val_norm = pd.concat([df_val_norm,snip],axis=0)
            
            temp = df_test.loc[test_idx,'VALUE'].copy()
            if temp.shape[0] == 0:
                print(v,'not in test set')
            else:
                temp = scaler.transform(temp.values.reshape(-1, 1))
                snip = df_test.loc[test_idx]
                snip = snip.assign(VALUE=temp)
                df_test_norm = pd.concat([df_test_norm,snip],axis=0)
           
        df_train =df_train_norm    
        df_val =df_val_norm 
        df_test =df_test_norm 
        
        # normalize demographics
        
        df_demo_train_norm = pd.DataFrame()
        df_demo_val_norm = pd.DataFrame()
        df_demo_test_norm = pd.DataFrame()
        
        df_demo_train_norm['ID'] = df_demo_train['ID']
        df_demo_val_norm['ID'] = df_demo_val['ID']
        df_demo_test_norm['ID'] = df_demo_test['ID']
        
        
        for col in ['AGE','BMI']:
            
            scaler = StandardScaler()
            scaler.fit(df_demo_train[col].values.reshape(-1, 1))
            
            temp = df_demo_train.loc[:,col].copy()
            temp = scaler.transform(temp.values.reshape(-1, 1))
            df_demo_train_norm[col] = temp
            
            temp = df_demo_val.loc[:,col].copy()
            temp = scaler.transform(temp.values.reshape(-1, 1))
            df_demo_val_norm[col] = temp
            
            temp = df_demo_test.loc[:,col].copy()
            temp = scaler.transform(temp.values.reshape(-1, 1))
            df_demo_test_norm[col] = temp
          
        df_demo_train = df_demo_train_norm
        df_demo_val = df_demo_val_norm
        df_demo_test = df_demo_test_norm
        
        print('data normalized using standardscaler')
    
    # Make sure dfs for demographics and other variables contain same amount of patients
    assert(len(np.unique(df_train['ID']))==len(np.unique(df_demo_train['ID'])))
    assert(len(np.unique(df_val['ID']))==len(np.unique(df_demo_val['ID'])))
    assert(len(np.unique(df_test['ID']))==len(np.unique(df_demo_test['ID'])))

    # Make sure patients IDs in test/validation set are not present in train set
    assert(any(i in np.unique(df_val['ID']) for i in np.unique(df_train['ID'])) == False)
    assert(any(i in np.unique(df_test['ID']) for i in np.unique(df_train['ID'])) == False)
    assert(any(i in np.unique(df_demo_val['ID']) for i in np.unique(df_demo_train['ID'])) == False)
    assert(any(i in np.unique(df_demo_test['ID']) for i in np.unique(df_demo_train['ID'])) == False)

    return df_train,df_val,df_test,df_demo_train,df_demo_val,df_demo_test
    
    

def prepare_feature_vectors(df,df_train,df_demo,df_demo_train,df_patients,ids_IC_only,ids_events,pred_window,gap,int_neg,int_pos,feature_window,
                        features,label_type='mortality'):
    print('prepare_feature_vectors triggered')

    """
    Samples feature vectors from the input dfs. 

    Parameters
    ----------
    df : pd.DataFrame
        df to sample from.
    df_train: pd.DataFrame
        df containing training set. Imputed values are based on the training set. 
    df_demo: pd.DataFrame
        demograhics df to sample from.
    df_demo_train: pd.DataFrame
        demograhics df containing the training set. Imputed values are based on the training set. 
    pred_window: int
        Size of prediction window in hours
    gap: int
        Size of gap in hours
    int_neg: int
        Interval between samples for the negative class. In hours.
    int_pos: int
        Interval between samples for the positive class. In hours.
    feature_window: int
        Number of most recent assessments to be included in feature vector
    variables: np.array[str]
        Array of strings representing the names of the variables to be included in the model.


    Returns
    -------
    X: matrix [N feature vectors x N variables]
    y: vector [N feature vectors x 1]
    type : np.array
    """

    from datetime import datetime, timedelta

    pos = list() #create empty list for pos labeled feature vectors
    neg = list() #create empty list for neg labeled feature vectors
    
    if label_type == 'mortality':
        print('Label for mortality')
        
        df_pos = df[df['DEST'].contains('died')] 
        df_neg = df[~df['DEST'].contains('died')]

    elif label_type == 'ICU':
        print('label for ICU admission')

        df_pos = df[df['DEPARTMENT'].contains('ICU')] 
        df_neg = df[~df['DEPARTMENT'].contains('ICU')]

    print('pos df:',df_pos.shape, '-->',len(df_pos['ID'].unique()), 'patients')
    print('neg df:',df_neg.shape, '-->',len(df_neg['ID'].unique()), 'patients')

    print('-----Sampling for positive patients-----') 

    count = 0 

    for idx in np.unique(df_pos['ID']): # loop over patients
        # print(idx)
        patient = df_pos[df_pos['ID']==idx].sort_values(by='TIME').reset_index(drop=True) # Extract data of single patient, sort by date

        if label_type == 'ICU':
            t_event = patient[patient['DEPARTMENT']=='IC']['TIME'].min() # define moment of ICU admission as first ICU measurement
        elif label_type == 'mortality':
            t_event = patient['TIME'].max() 
            
            
        if (t_event - patient['TIME'].min()).total_seconds()/3600 < gap: # cannot label patients for which time between start and event is shorter than the gap
            count += 1
        else:

            #For positive feature vectors of positive patient
            ts = []            
            t = t_event - timedelta(hours=gap) #initialize t
            window = pred_window

            for i in range(int(window/int_pos)-1): # Make array with timestamps to sample from, making steps of size 'int_pos'
                ts.append(t)
                t = t - timedelta(hours=int_pos)

            for t in ts: 

                temp = patient[patient['TIME'] <= t].reset_index(drop=True)

                v,med_share,ff_share,med_spec,ff_spec = create_feature_window(temp,df_train,df_demo,df_demo_train,feature_window,features,idx)
                pos.append(v)

            # For Negative feature vectors of positive patients
            ts = []            
            t = t_event - timedelta(hours=gap+pred_window) #initialize t 
            window = (t_event - patient['TIME'].min()).total_seconds()/3600 - pred_window - gap # window to sample from is full window - prediction window and gap

            for i in range(int(window/int_neg)-1): # Make array with timestamps to sample from, making steps of size 'int_neg'
                ts.append(t)
                t = t - timedelta(hours=int_neg)

            for t in ts: 

                temp = patient[patient['TIME'].dt.date <= t].reset_index(drop=True) # Extract snippet before this day

                v,med_share,ff_share,med_spec,ff_spec = create_feature_window(temp,df_train,df_demo,df_demo_train,feature_window,features,idx)
                neg.append(v)

    print('-----Sampling for negative patient-----')

    for idx in np.unique(df_neg['ID']): # loop over patients
        # print(idx)
        patient = df_neg[df_neg['ID']==idx].sort_values(by='TIME').reset_index(drop=True) # Extract data of single patient, sort by date

        if (patient['TIME'].max() - patient['TIME'].min()).total_seconds()/3600 < gap: # cannot label patients with stay shorter than the gap
            count+= 1

        else:
            ts = []            
            t = patient['TIME'].max() #initialize t 
            window = (patient['TIME'].max() - patient['TIME'].min()).total_seconds()/3600 # window to sample from is full window 

            for i in range(int(window/int_neg)-1): # Make array with timestamps to sample from, making steps of size 'int_neg'
                ts.append(t)
                t = t - timedelta(hours=int_neg)

            for t in ts: 

                temp = patient[patient['TIME'].dt.date <= t].reset_index(drop=True) # Extract snippet before this day

                v,med_share,ff_share,med_spec,ff_spec = create_feature_window(temp,df_train,df_demo,df_demo_train,feature_window,features,idx)
                neg.append(v)

    print('number of patients with too little data for feature vector: ', count)            

    pos=np.array([np.array(x) for x in pos])
    neg=np.array([np.array(x) for x in neg])
    print('shape of positive class: ', pos.shape, 'shape of negative class: ', neg.shape)

    X = np.concatenate((pos, neg), axis=0)
    y = np.concatenate((np.ones(pos.shape[0]),np.zeros(neg.shape[0])),axis=0)

    print(X.shape)
    assert(np.isnan(X).any() == False)
    print(y.shape)
    assert(np.isnan(y).any() == False)

    return X, y     
   
    

    
def create_feature_window(df,df_train,df_demo,df_demo_train,n,variables,idx):
    """
    Samples feature vectors from the input dfs. 

    Parameters
    ----------
    df : pd.DataFrame
        df with data of inidividual patient until moment of sampling
    df_train: pd.DataFrame
        df containing training set. Imputed values are based on the training set. 
    df_demo: pd.DataFrame
        demograhics df to sample from.
    df_demo_train: pd.DataFrame
        demograhics df containing the training set. Imputed values are based on the training set. 
    n: int
        feature_window
    variables: np.array[str]
        Array of strings representing the names of the variables to be included in the model.
    idx: str
        patient ID
        
    Returns
    -------
    v: feature vector
    type : np.array
    """
    v = list() #define empty feature vector
        
    df_demo_train = df_demo_train.dropna()
    
    #Add demographics 
    for col in df_demo.columns[1:]:
        
        ff_spec.append(0)
        
        if df_demo.loc[df_demo['ID'] == idx][col].notnull().sum() == 0:
            v.extend(df_demo_train.loc[:,col].median()*np.ones(1))
        else:
            v.extend(df_demo.loc[df_demo['ID'] == idx][col])
    
    # Add labs / vitals
    
    for item in variables: #loop over features
        
        temp = df[df['VARIABLE']==item] # Extract snippet with only this feature
        
        if temp.shape[0] < 1: # If snippet contains none for this feature
            a = np.ones(n)*np.median(df_train[df_train['VARIABLE']==item]['VALUE']) #Impute with median imputer
            v.extend(a)
            
        elif temp.shape[0] < n: # If snippet contains less than n values for feature, impute with most recent value
            a = np.concatenate((temp['VALUE'].tail(temp.shape[0]).values, 
                                np.ones(n-temp.shape[0])*temp['VALUE'].tail(1).values), axis=None)
            v.extend(a)
            
        else: #if snippet contains n or more values, take n most recent values
            a = temp['VALUE'].tail(n).values
            v.extend(a)          
            
    return v


def balancer(X,y,undersampling=True):
    print('balancer triggered')
    """
    Balences classes.

    Parameters
    ----------
    X: np.array
        matrix [N feature vectors x N variables] with feature vectors
    y: np.array
        label vector [N feature vectors x 1]
    undersampling: optional: bool
        if True, use random undersampling. If False, use random oversampling.
    
    Returns
    -------
    X_bal: np.array
        balanced matrix [N feature vectors x N variables] with feature vectors
    y_bal: np.array
        balanced label vector [N feature vectors x 1]
    type : np.array
    """
    import imblearn
    from imblearn.under_sampling import RandomUnderSampler
    from imblearn.over_sampling import RandomOverSampler

    if undersampling:
        undersample = RandomUnderSampler(sampling_strategy='majority')
        print('Rebalance classes by random undersampling')
        X_bal, y_bal = undersample.fit_resample(X, y)
    else:
        
        oversample = RandomOverSampler(sampling_strategy='minority')
        print('Rebalance classes by random oversampling')
        X_bal, y_bal = oversample.fit_resample(X, y)
    
    print('After balancing: \n shape X',X_bal.shape,'n pos',sum(y_bal), 'n neg', len(y_bal)-sum(y_bal))
    return X_bal, y_bal




def train_model(X_train,y_train,X_test,y_test,model):
    print('train_model triggered')
    
    """
    Balences classes.

    Parameters
    ----------
    X_train: np.array
        Train set featurematrix [N feature vectors x N variables] with feature vectors
    y_train: np.array
        Train set label vector [N feature vectors x 1]
    X_test: np.array
        Test set featurematrix [N feature vectors x N variables] with feature vectors
    y_test: np.array
        Test set label vector [N feature vectors x 1]
    model: str
        model type: "LR" or "RF"
    
    Returns
    -------
    clf_ret: object
        trained classifier to be returned
    train_auc: float
        Area under the curve for model's performance on the train set
    explainer: object
        explainer for Shapley values based on the trained classifier
    """
    
    from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    import shap
    
    if model == 'RF':
        
        
        n_estimators = [500,600] # Number of trees in random forest
        max_features = ['auto', 'log2',0.33] # Number of features to consider at every split
        max_depth = [3,5,7,9,11] # Maximum number of levels in tree, make not to deep to prevent overfitting
        
        param_grid = {'n_estimators': n_estimators,
                       'max_features': max_features,
                        'max_depth': max_depth
                       }
        
        clf = RandomForestClassifier()
        
    elif model == 'LR':
        
        param_grid = {'penalty':['l1', 'l2'],'C': [0.001,0.01,0.1,1,10,100,1000],
                       'solver': ['liblinear']}
        clf = LogisticRegression(max_iter=1000)
        
    rf_grid = GridSearchCV(estimator = clf, param_grid = param_grid,
                                   cv = 10, verbose=0, n_jobs = -1)
    
    rf_grid.fit(X_train, y_train)
    print(rf_grid.best_params_)
    
    clf.fit(X_train, y_train)
    print(clf.classes_)
    print('Performance on test set with unoptimized model:')
    base_auc,_,_,_,_,_,_ = evaluate_metrics(clf, X_test, y_test)
    
    clf_opt = rf_grid.best_estimator_
    print('Perfromance on test set with optimized model:')
    opt_auc,_,_,_,_,_,_ = evaluate_metrics(clf_opt, X_test,y_test)
    
    print('Improvement of {:0.2f}%.'.format( 100 * (opt_auc - base_auc) / opt_auc))
    
    #Pick the model with best performance on the test set
    if opt_auc > base_auc:
        clf_ret = clf_opt
    else:
        clf_ret = clf

    train_auc = max(opt_auc,base_auc)
    explainer = shap.TreeExplainer(clf_ret)

    
    return clf_ret,train_auc,explainer


def evaluate_metrics(model, test_features, test_labels):
     
    """
    Calculates evaluation metrics

    Parameters
    ----------
    model: object
        Trained model
    test_features: np.array
        feature matrix for set to be evalutated [N feature vectors x M variables] 
    test_labels: np.array
        label vector for set to be evaluated [N feature vectors x 1] 
    
    Returns
    -------
    auc: float
        Area under the ROC curve 
    tn: int
        Number of true negatives
    fp: int
        numer of false positives
    fn: int
        number of false negatives
    tp: int
        number of true positives
    precision: np.array
        array with precisions for different threshold values
    recall: np.array
        array with recalls for different threshold values
    """
    from sklearn.metrics import roc_auc_score
    from sklearn.metrics import confusion_matrix
    from sklearn.metrics import precision_recall_curve
    
    predictions = model.predict_proba(test_features)[:,1]
    auc = roc_auc_score(test_labels, predictions)
    tn, fp, fn, tp = confusion_matrix(test_labels, model.predict(test_features)).ravel()
    
    print('Model Performance:',auc)
    print('TN:',tn,'FP:',fp,'FN:',fn,'TP:',tp)
    print('sens:',np.round(tp/(tp+fn),2),'spec:',np.round(tn/(tn+fp),2))
    print('Recall:',np.round(tp/(tp+fn),2),'Pecision:',np.round(tp/(tp+fp),2))
    
    precision, recall, thresholds = precision_recall_curve(test_labels, predictions)
    
    return auc,tn, fp, fn, tp,precision,recall
    
def plot_PR_curve(precision,recall):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    plt.plot(precision,recall)
    plt.xlabel('Precision')
    plt.ylabel('Recall')
    
    plt.savefig('PR_curve')
    
def plot_roc_curve(clf,X_val,y_val):
    import matplotlib.pyplot as plt
    from sklearn import metrics
    fig = plt.figure()
    metrics.plot_roc_curve(clf, X_val, y_val)
    plt.savefig('ROC_curve')

