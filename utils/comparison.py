import time
import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression, LassoCV, LogisticRegression
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.feature_selection import SelectKBest, f_regression, f_classif, VarianceThreshold, RFE, mutual_info_regression, mutual_info_classif
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import cross_val_score

def get_model_factory(model_type: str, is_classification: bool = False):
    if is_classification:
        if model_type in ("linear", "ridge"):
            return lambda: LogisticRegression(max_iter=1000, random_state=42)
        elif model_type == "mlp":
            return lambda: MLPClassifier(hidden_layer_sizes=(64,32), max_iter=500, random_state=42, early_stopping=True)
        else:
            return lambda: LogisticRegression(max_iter=1000, random_state=42)
    else:
        if model_type == "ridge":
            return lambda: Ridge(alpha=1.0)
        elif model_type == "mlp":
            return lambda: MLPRegressor(hidden_layer_sizes=(64,32), max_iter=500, random_state=42, early_stopping=True)
        else:
            return lambda: LinearRegression()

def run_comparison_method(method_name: str, X, y, k: int, model_factory, cv: int, is_classification: bool = False, seed: int = 42):
    t0 = time.perf_counter()
    try:
        X_filled = X.fillna(X.mean(numeric_only=True))

        if method_name == "SelectKBest":
            score_func = f_classif if is_classification else f_regression
            skb = SelectKBest(score_func, k=min(k, X.shape[1]))
            skb.fit(X_filled, y)
            sel = list(X.columns[skb.get_support()])
        elif method_name == "LassoCV":
            if is_classification:
                from sklearn.linear_model import LogisticRegressionCV
                lasso = LogisticRegressionCV(cv=5, random_state=seed, max_iter=5000, penalty='l1', solver='liblinear')
                lasso.fit(X_filled, y)
                coefs = lasso.coef_[0] if lasso.coef_.ndim > 1 else lasso.coef_
                sel = [c for c, coef in zip(X.columns, coefs) if abs(coef) > 1e-6]
            else:
                lasso = LassoCV(cv=5, random_state=seed, max_iter=5000).fit(X_filled, y)
                sel = [c for c, coef in zip(X.columns, lasso.coef_) if abs(coef) > 1e-6]
        elif method_name == "RFE":
            estimator = LogisticRegression(max_iter=1000, random_state=seed) if is_classification else LinearRegression()
            rfe = RFE(estimator, n_features_to_select=min(k, X.shape[1]))
            rfe.fit(X_filled, y)
            sel = list(X.columns[rfe.get_support()])
        elif method_name == "VarianceThreshold":
            var = X.var(numeric_only=True)
            sel = list(var.nlargest(k).index)
        elif method_name == "MutualInfo_topK":
            mi_func = mutual_info_classif if is_classification else mutual_info_regression
            mi = mi_func(X_filled, y, random_state=seed)
            mi_rank = pd.Series(mi, index=X.columns).sort_values(ascending=False)
            sel = list(mi_rank.index[:k])
        elif method_name == "RandomForest_topK":
            estimator = RandomForestClassifier(n_estimators=100, random_state=seed) if is_classification else RandomForestRegressor(n_estimators=100, random_state=seed)
            rf = estimator.fit(X_filled, y)
            imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
            sel = list(imp.index[:k])
        else:
            sel = []

        scoring = 'accuracy' if is_classification else 'neg_mean_squared_error'
        metric = None
        if sel:
            scores = cross_val_score(model_factory(), X[sel], y, cv=cv, scoring=scoring, n_jobs=-1)
            metric = float(scores.mean())
            if not is_classification:
                metric = -metric  # convert to positive MSE

        t1 = time.perf_counter()
        return {"selected": sel, "mse": metric, "time": t1 - t0}
    except Exception as e:
        t1 = time.perf_counter()
        return {"selected": [], "mse": None, "time": t1 - t0}