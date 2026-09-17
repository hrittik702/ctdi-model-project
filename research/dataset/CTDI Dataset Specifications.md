# CTDI Paper Dataset Specification 

**Reference Document**: Yangwen Yu, Victor O. K. Li, Jacqueline C. K. Lam, Kelvin Chan, Qi Zhang, *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, **IEEE Transactions on Big Data**, vol. 11, no. 5, pp. 2442–2455, Sept.–Oct. 2025. DOI: [CTDI Paper](https://doi.org/10.1109/TBDATA.2025.3533882)  
**Date Created**: 2026-09-16  
## 1. Air Quality Specification

| Parameter              | Paper Specification                                                                                          | Status                                                                                                                                  |
| :--------------------- | :----------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| Source Organization    | Hong Kong Environmental Protection Agency (HKEPD) Database                                                   | *Air pollution data from the EPD of HKSAR database. Accessed: Aug. 31, 2022. Available: https://cd.epic.epd.gov.hk/EPICDI/air/station/* |
| Number of Stations     | 16 stations                                                                                                  | Table I lists *"16 stations"*.                                                                                                          |
| Date Range             | 01 Jan, 2019 to 31 Dec, 2021                                                                                 | Ok                                                                                                                                      |
| Temporal Resolution    | 1 hour                                                                                                       | Ok                                                                                                                                      |
| Target Variables       | 5 criteria air pollutants: $\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{NO}_2$, $\text{SO}_2$, $\text{O}_3$   | Also contain NOX, CO                                                                                                                    |
| Units                  | $\mu\text{g/m}^3$ for all 5 pollutants                                                                       | Ok                                                                                                                                      |
| Total Measured Items   | $2,104,320$ potential values ($16 \text{ stations} \times 26,304 \text{ hours} \times 5 \text{ pollutants}$) | Ok                                                                                                                                      |
| Missingness Statistics | 55,875 missing items (2.46% arithmetic mean missing rate)                                                    | *There are 55,875 missing data items, which corresponds to an arithmetic mean missing data rate of 2.46%.*                              |

## 2. Meteorology Specification

| Parameter           | Paper Specification                                                                                                                                                                          | Status                                                                                                                                                                                                                               |
| :------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Source Organization | Hong Kong Observatory Open Database                                                                                                                                                          | *Hong Kong Observatory Open Database. Accessed: Aug. 31, 2022. [Online]. Available: https://www.hko.gov.hk/en/abouthko/opendata_intro.htm"*                                                                                          |
| Number of Stations  | 47 stations                                                                                                                                                                                  | Table I lists Number of Data Nodes as *"47 stations"* under Meteorology.                                                                                                                                                             |
| Date Range          | 01 Jan, 2019 to 31 Dec, 2021                                                                                                                                                                 | Ok                                                                                                                                                                                                                                   |
| Temporal Resolution | 10 min (native observation frequency)                                                                                                                                                        | *10 min* for all six meteorological variables.                                                                                                                                                                                       |
| Exact Six Variables | 1. Pressure<br>2. Relative humidity<br>3. Temperature<br>4. Visibility<br>5. Wind direction<br>6. Wind speed                                                                                 | Meteorology in Table I. Visibility is definitively Variable 4. Rainfall is NOT present.                                                                                                                                              |
| Units               | 1. Pressure: $\text{hPa}$<br>2. Relative humidity: $\%$<br>3. Temperature: $^\circ\text{C}$<br>4. Visibility: $\text{km}$<br>5. Wind direction: $\text{N/A}$<br>6. Wind speed: $\text{km/h}$ | Table I explicitly records these exact units.                                                                                                                                                                                        |
| Spatial Processing  | Inverse Distance Weighting (IDW) with squared distance weighting ($p=2$)                                                                                                                     | Equation (1): $u'_j = \frac{\sum_{i=1}^N w_{ij} u_i}{\sum_{i=1}^N w_{ij}}$ if $d(i, j) \neq 0$, and $u'_j = u_i$ if $d(i, j) = 0$, where $w_{ij} = \frac{1}{d(i, j)^p}$ and $p=2$. Mapped to the 16 air quality monitoring stations. |

## 3. Traffic Specification

| Parameter               | Paper Specification                                                    | Status                                                                                                                                                          |
| :---------------------- | :--------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Source Organization     | Hong Kong Traffic Speed Map (City Dashboard Version) Database          | *Hong Kong Traffic Speed Map. Accessed: Aug. 31, 2022. [Online]. Available: https://data.gov.hk/en-data/dataset/hk-ogcio-da_div_02-citydashboard-traffic-speed* |
| Number of Roads / Links | 607 roads                                                              | Table I specifies Number of Data Nodes as *"607 roads"* under Traffic.                                                                                          |
| Date Range              | 01 Jan, 2019 to 31 Dec, 2021                                           | Ok                                                                                                                                                              |
| Temporal Resolution     | 5min                                                                   | *5min* for both traffic variables.                                                                                                                              |
| Exact Variables         | 1. Traffic speed<br>2. Traffic congestion                              | ***Traffic volume is NOT present* Using traffic congestion**                                                                                                    |
| Units                   | 1. Traffic speed: $\text{km/h}$<br>2. Traffic congestion: $\text{N/A}$ | Table I explicitly records these exact units.                                                                                                                   |
| Spatial Processing      | Inverse Distance Weighting (IDW, $p=2$)                                | Mapped from the 607 road locations to the 16 air quality monitoring stations.                                                                                   |
| Temporal Aggregation    | Averaged over the hour                                                 | Twelve 5-minute readings per hour averaged to 1-hour values.                                                                                                    |

## Final Dataset Tensor Structure

| Parameter                | Paper Specification                                                                                                | Status                                                                                                                                                                                                                              |
| :----------------------- | :----------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tensor Rank & Shape      | $X_{\text{raw}} \in \mathbb{R}^{s \times t \times c} = \mathbb{R}^{16 \times 26,304 \times 13}$                    | *After spatial interpolation, the size of the original data tensor $s \times t \times c = 16 \times 26304 \times 13$.*                                                                                                              |
| Total Numerical Elements | $5,471,232$ items                                                                                                  | *The original dataset hence consists of 5,471,232 items in total."* ($16 \times 26,304 \times 13 = 5,471,232$).                                                                                                                     |
| Channel Decomposition    | $c = c_1 + c_2 = 5 + 8 = 13$ channels                                                                              | $c_1 = 5$ criteria air pollutants; $c_2 = 8$ urban factors (6 meteorological + 2 traffic).                                                                                                                                          |
| Temporal Segmentation    | Sliding window of fixed size 24 hours with stride of 1 hour ($X \in \mathbb{R}^{s \times t_d \times c}, t_d = 24$) | A sliding window of fixed size 24 in the time dimension is used to extract the 24-hour tensor $X \in \mathbb{R}^{s \times t_d \times c}$, where $t_d = 24$ ... A sliding stride of 1 h then moves the window in 1-hour increments.* |
| Dataset Splits           | Random 80 / 10 / 10 split (Train / Validation / Test)                                                              | *Next, we used a random 80/10/10 split of the raw dataset as the training set, the validation set, and the test set.*                                                                                                               |
<div class="figure figure-two">

<div class="figure-item">

<img src="../air pollution hour vs missing.png">

<div class="figure-label">(a) Actual</div>

</div>

<div class="figure-item">

<img src="fig_07_missing_proportion_by_hour_pie.png">

<div class="figure-label">(b) Downloaded</div>

</div>

<div class="figure-caption">
Fig. 1. Comparison of actual and predicted values.
</div>

</div>
<div class="figure figure-two">

<div class="figure-item">

<img src="../Screenshot_2026-09-16_15-02-33.png">

<div class="figure-label">(a) Actual</div>

</div>

<div class="figure-item">

<img src="fig_06_missing_by_hour_year.png">

<div class="figure-label">(b) Downloaded</div>

</div>

<div class="figure-caption">
Fig. 1. Comparison of actual and predicted values.
</div>

</div>
<div class="figure figure-two">

<div class="figure-item">

<img src="air pollutant by missing.png">

<div class="figure-label">(a) Actual</div>

</div>

<div class="figure-item">

<img src="fig_08_missing_proportion_by_pollutant_pie.png">

<div class="figure-label">(b) Downloaded</div>

</div>

<div class="figure-caption">
Fig. 1. Comparison of actual and predicted values.
</div>

</div>

<div class="figure figure-two">

<div class="figure-item">

<img src="air - station vs missing.png">

<div class="figure-label">(a) Actual</div>

</div>

<div class="figure-item">

<img src="fig_09_missing_proportion_by_station_pie.png">

<div class="figure-label">(b) Downloaded</div>

</div>

<div class="figure-caption">
Fig. 1. Comparison of actual and predicted values.
</div>

</div>
