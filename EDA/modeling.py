import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.linear_model import LinearRegression,Ridge, Lasso, RidgeCV, LassoCV
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate
from sklearn.feature_selection import RFE

from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.ensemble import GradientBoostingClassifier as GB
from sklearn.linear_model import LogisticRegression as LR
from sklearn.neural_network import MLPClassifier as MLP
from sklearn.neighbors import KNeighborsClassifier as KN
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier as GPC
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier as DT
from sklearn.ensemble import AdaBoostClassifier as ABC
from sklearn.naive_bayes import GaussianNB as GNB
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV

def load_data():
    # df_reso = pd.read_pickle('data/df_reso.pkl')
    # df_price_hist = pd.read_pickle('data/df_price_hist.pkl')
    # df_sold = pd.read_pickle('data/df_sold.pkl')
    df_sold_detailed = pd.read_pickle('../data/df_sold_detailed.pkl')
    return df_sold_detailed

def filter_data(df):
    df = df.drop_duplicates(keep="first").reset_index(drop=True)
    df.dropna(inplace=True, thresh=10)
    df.dropna(axis=0,subset= ['latitude'],inplace=True)
    df = df[['bathrooms', 'bedrooms', 'homeType',
           'latitude','livingArea',
           'longitude', 'lotSize',  'taxAssessedValue','yearBuilt',
           'zipcode', 'price']]
    df.dropna(inplace=True)
    return df

def dummy_data(df):
    property_dummies = ['CONDO','MULTI_FAMILY','SINGLE_FAMILY','TOWNHOUSE']
    df[property_dummies] = pd.get_dummies(df['homeType'])[property_dummies]
    dums = pd.get_dummies(df['zipcode'])
    df[dums.columns] = dums
    df.pop('homeType')
    df.pop('zipcode')
    return df

def tranform_data(df):
    df = dummy_data(df)
    X = df.copy() # Attribute data
    y = X.pop('price') # Housing prices
    colNames = X.columns # Feature names
    y = y.astype(np.float64)
    X = X.astype(np.float64)
    ss = StandardScaler()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    X_train = ss.fit_transform(X_train)
    X_test = ss.transform(X_test)
    return X_train, X_test, y_train, y_test

def run_models(X_train, X_test, y_train, y_test):
    lin = LinearRegression()
    r = Ridge()
    l = Lasso()
    rcv = RidgeCV()
    lcv = LassoCV()
    # xg = xgb.XGBClassifier(random_state=1,learning_rate=0.01)
    rf = RF()
    lr = LR()
    gb = GB()
    mlp = MLP()
    kn = KN()
    svc = SVC()
    gpc = GPC()
    rbf = RBF()
    dt = DT()
    abc = ABC()
    gnb = GNB()
    names = ['Linear Regression',
            'Ridge',
            'Lasso',
            # 'XGBoost',
            'Random Forest',
             # 'Logistic Regression',
             # 'Gradient Boosting Classifier',
             # 'MLP Classifier',
             # 'KNeighbors Classifier',
             # 'SVC',
             # 'Gaussian Process Classifier',
             'Decision Tree Classifier',
             'AdaBoost Classifier',
             'Gaussian Naive Bayes']
    models = [lin, r, l, rf,dt,abc,gnb] #lr,gb,gpc, xg,mlp,kn,svc,

    for name, model in zip(names, models):
        check_model(name, model,X_train,y_train,X_test,y_test)
        # check_basics(name, model, X_train,y_train,X_test,y_test)

def check_model(name, model,X_train,y_train,X_test,y_test):
    model.fit(X_train,y_train)
    print("{} train score: {}".format(name, model.score(X_train,y_train)))
    print("{} test score: {}".format(name, model.score(X_test,y_test)))
    print('\n')


if __name__ == '__main__':
    df = load_data()
    df = filter_data(df)
    X_train, X_test, y_train, y_test = tranform_data(df)
    run_models(X_train, X_test, y_train, y_test)
