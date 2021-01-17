from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter


days_omitted = 8
trend_data = 50

df = pd.read_csv("CovidDataset.csv")
#all_cities = set(list(df["Reporting_PHU_City"]))

prediction = {}

def trend_in(city_name):


    city = df.loc[df["Reporting_PHU_City"] == city_name]
    # dates_city = city[['Accurate_Episode_Date']]
    city_data = city.groupby("Accurate_Episode_Date")["_id"].nunique()


    # omit last 8 days and start 1 month before then
    dates_city = city_data.index.astype(str)[-(days_omitted + trend_data) : -days_omitted]


    dailycount_city = city_data.values[-(days_omitted + trend_data) : -days_omitted]
    value = savgol_filter(dailycount_city, 7, 2)  # filter applied to curve
    #value = rolling_mean(dailycount_city, 10)  # filter applied to curve using rolling_mean

    X = np.array(list(range(len(value)))).reshape(-1, 1)
    model = LinearRegression().fit(X, value)
    prediction[city_name] = "INCR" if model.coef_ > 0 else "DECR"

    #plotting cases per day and Line of Best Fit
    plt.plot(out.index, out.to_numpy())
    #plt.plot(out.index, out.to_numpy())
    plt.plot(out.index, [model.coef_*x + model.intercept_ for x in range(len(out.to_numpy()))] )
    plt.xticks(np.arange(0, 60, step=10))  # Set label locations.
    plt.xticks(rotation=45)
    plt.title(f"{city} - {prediction[city]} - {model.coef_}")
    plt.show()

    #return prediction(city_name)
    return model.coef_, prediction[city_name]

print(trend_in("Thunder Bay"))


