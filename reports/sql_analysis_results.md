# SQL Analysis Results


## Q1. What is total revenue (and profit)?  (1 rows)
|   total_revenue |   total_profit |   profit_margin |
|----------------:|---------------:|----------------:|
|     6.89052e+07 |    1.63968e+07 |           0.238 |

## Q2. Top 10 products by revenue  (10 rows)
| product_name          | category         |     revenue |   profit |   margin |
|:----------------------|:-----------------|------------:|---------:|---------:|
| CoreX Computer 3      | Technology       | 3.89036e+06 |   283137 |   0.0728 |
| CoreX Computer 4      | Technology       | 3.66907e+06 |   289196 |   0.0788 |
| CoreX Computer 1      | Technology       | 3.15451e+06 |   255433 |   0.081  |
| CoreX Computer 2      | Technology       | 2.38323e+06 |   205822 |   0.0864 |
| Oakline Office Desk 5 | Furniture        | 1.97482e+06 |   539425 |   0.2732 |
| Oakline Office Desk 3 | Furniture        | 1.77648e+06 |   475358 |   0.2676 |
| Oakline Office Desk 6 | Furniture        | 1.76706e+06 |   501493 |   0.2838 |
| Oakline Chair 2       | Furniture        | 1.73388e+06 |   562595 |   0.3245 |
| Lumina Appliance 1    | Home & Lifestyle | 1.67805e+06 |   472643 |   0.2817 |
| CoreX Phone 3         | Technology       | 1.60267e+06 |   133641 |   0.0834 |

## Q3. Which categories generate the highest profit?  (4 rows)
| category         |     revenue |      profit |   margin |   orders |
|:-----------------|------------:|------------:|---------:|---------:|
| Furniture        | 2.4374e+07  | 7.20336e+06 |   0.2955 |    13805 |
| Home & Lifestyle | 1.16034e+07 | 4.11481e+06 |   0.3546 |    19620 |
| Technology       | 2.61529e+07 | 3.24265e+06 |   0.124  |    16943 |
| Office Supplies  | 6.77484e+06 | 1.83602e+06 |   0.271  |    23945 |

## Q4. Which customers have spent the most?  (10 rows)
|   customer_id | customer_name     | customer_segment   | region   |   total_spend |   orders |
|--------------:|:------------------|:-------------------|:---------|--------------:|---------:|
|           173 | Linda Garcia      | Corporate          | East     |        857087 |      310 |
|           897 | Patricia Williams | Corporate          | East     |        564382 |      234 |
|          1375 | Andrew Williams   | Corporate          | West     |        561242 |      218 |
|           433 | Linda Robinson    | Corporate          | East     |        520515 |      192 |
|          1788 | Charles Allen     | Corporate          | South    |        504387 |      201 |
|          1173 | Melissa Walker    | Small Business     | West     |        498077 |      203 |
|          1349 | Barbara Sanchez   | Corporate          | Central  |        472962 |      174 |
|           119 | Matthew Thompson  | Corporate          | West     |        423119 |      176 |
|            59 | Justin Jones      | Corporate          | South    |        412021 |      141 |
|          1180 | William Williams  | Corporate          | South    |        390483 |      143 |

## Q5. What is monthly revenue?  (48 rows)
| month   |          revenue |
|:--------|-----------------:|
| 2021-01 | 924428           |
| 2021-02 |      1.03831e+06 |
| 2021-03 |      1.15089e+06 |
| 2021-04 | 874901           |
| 2021-05 |      1.23899e+06 |
| 2021-06 |      1.18885e+06 |
| 2021-07 | 895869           |
| 2021-08 |      1.49272e+06 |
| 2021-09 |      1.517e+06   |
| 2021-10 |      1.31835e+06 |

## Q6. Month-over-month revenue growth (window function)  (48 rows)
| month   |          revenue |   change_abs |   growth_pct |
|:--------|-----------------:|-------------:|-------------:|
| 2021-01 | 924428           |        nan   |       nan    |
| 2021-02 |      1.03831e+06 |     113883   |        12.32 |
| 2021-03 |      1.15089e+06 |     112583   |        10.84 |
| 2021-04 | 874901           |    -275992   |       -23.98 |
| 2021-05 |      1.23899e+06 |     364085   |        41.61 |
| 2021-06 |      1.18885e+06 |     -50137.4 |        -4.05 |
| 2021-07 | 895869           |    -292979   |       -24.64 |
| 2021-08 |      1.49272e+06 |     596847   |        66.62 |
| 2021-09 |      1.517e+06   |      24281   |         1.63 |
| 2021-10 |      1.31835e+06 |    -198643   |       -13.09 |

## Q7. Which customers have made more than 5 purchases?  (1,111 rows)
|   customer_id | customer_name     | customer_segment   |   order_count |   total_spend |
|--------------:|:------------------|:-------------------|--------------:|--------------:|
|           173 | Linda Garcia      | Corporate          |           310 |        857087 |
|           897 | Patricia Williams | Corporate          |           234 |        564382 |
|          1375 | Andrew Williams   | Corporate          |           218 |        561242 |
|          1173 | Melissa Walker    | Small Business     |           203 |        498077 |
|          1788 | Charles Allen     | Corporate          |           201 |        504387 |
|           433 | Linda Robinson    | Corporate          |           192 |        520515 |
|           119 | Matthew Thompson  | Corporate          |           176 |        423119 |
|          1349 | Barbara Sanchez   | Corporate          |           174 |        472962 |
|          1553 | Rebecca Hernandez | Small Business     |           167 |        386160 |
|          1363 | Brittany Harris   | Corporate          |           145 |        340052 |

## Q8. What is the average order value (AOV)?  (1 rows)
|   avg_order_value |
|------------------:|
|            2074.9 |

## Q9. Which regions have the highest profit margin?  (4 rows)
| region   |     revenue |      profit |   margin |
|:---------|------------:|------------:|---------:|
| Central  | 1.18996e+07 | 2.85153e+06 |   0.2396 |
| South    | 1.77288e+07 | 4.24344e+06 |   0.2394 |
| East     | 1.93994e+07 | 4.62674e+06 |   0.2385 |
| West     | 1.98775e+07 | 4.67513e+06 |   0.2352 |

## Q10. Products with high sales but low profit (revenue > $1.5M, margin < 15%)  (6 rows)
| product_name     | category   |     revenue |   profit |   margin |
|:-----------------|:-----------|------------:|---------:|---------:|
| CoreX Computer 3 | Technology | 3.89036e+06 |   283137 |   0.0728 |
| CoreX Computer 4 | Technology | 3.66907e+06 |   289196 |   0.0788 |
| CoreX Computer 1 | Technology | 3.15451e+06 |   255433 |   0.081  |
| CoreX Computer 2 | Technology | 2.38323e+06 |   205822 |   0.0864 |
| CoreX Phone 3    | Technology | 1.60267e+06 |   133641 |   0.0834 |
| CoreX Phone 6    | Technology | 1.55583e+06 |   120306 |   0.0773 |

## Q11. Customers who have not purchased recently (no order in last 90 days)  (617 rows)
|   customer_id | customer_name    | customer_segment   | last_order_date   |   days_since_last |
|--------------:|:-----------------|:-------------------|:------------------|------------------:|
|           107 | Michael Wilson   | Consumer           | 2021-01-01        |              1460 |
|           114 | Charles Martinez | Consumer           | 2021-01-03        |              1458 |
|          1032 | Ashley Rodriguez | Corporate          | 2021-01-26        |              1435 |
|           239 | Susan Lewis      | Consumer           | 2021-02-04        |              1426 |
|          1529 | Robert Martin    | Consumer           | 2021-03-16        |              1386 |
|           397 | Brandon Young    | Consumer           | 2021-03-24        |              1378 |
|          1266 | Patricia King    | Corporate          | 2021-05-11        |              1330 |
|          1644 | Ashley Johnson   | Consumer           | 2021-05-15        |              1326 |
|            37 | Justin Johnson   | Consumer           | 2021-05-19        |              1322 |
|            47 | Scott Wilson     | Home Office        | 2021-05-25        |              1316 |

## Q12. What percentage of revenue comes from the top 10 customers?  (1 rows)
|   top10_revenue |   total_revenue |   top10_pct |
|----------------:|----------------:|------------:|
|     5.20427e+06 |     6.89052e+07 |        7.55 |

## Q13. Segment behaviour: AOV and margin by customer segment  (4 rows)
| customer_segment   |   orders |     aov |     revenue |   margin |
|:-------------------|---------:|--------:|------------:|---------:|
| Corporate          |    14611 | 2535.52 | 3.70464e+07 |   0.2375 |
| Small Business     |     6814 | 2241.53 | 1.52738e+07 |   0.2366 |
| Home Office        |     5431 | 1592.48 | 8.64877e+06 |   0.2411 |
| Consumer           |     6353 | 1249.21 | 7.93625e+06 |   0.2392 |

## A1. Rank products by revenue WITHIN each category (ROW_NUMBER / DENSE_RANK)  (101 rows)
| category   | product_name          |     revenue |   cat_rank |
|:-----------|:----------------------|------------:|-----------:|
| Furniture  | Oakline Office Desk 5 | 1.97482e+06 |          1 |
| Furniture  | Oakline Office Desk 3 | 1.77648e+06 |          2 |
| Furniture  | Oakline Office Desk 6 | 1.76706e+06 |          3 |
| Furniture  | Oakline Chair 2       | 1.73388e+06 |          4 |
| Furniture  | Oakline Office Desk 4 | 1.5857e+06  |          5 |
| Furniture  | Oakline Table 1       | 1.5552e+06  |          6 |
| Furniture  | Oakline Chair 4       | 1.50832e+06 |          7 |
| Furniture  | Oakline Table 2       | 1.41367e+06 |          8 |
| Furniture  | Oakline Table 3       | 1.34668e+06 |          9 |
| Furniture  | Oakline Chair 3       | 1.26397e+06 |         10 |

## A2. Running total of monthly revenue (cumulative 2021-2024)  (48 rows)
| month   |          revenue |    running_total |
|:--------|-----------------:|-----------------:|
| 2021-01 | 924428           | 924428           |
| 2021-02 |      1.03831e+06 |      1.96274e+06 |
| 2021-03 |      1.15089e+06 |      3.11363e+06 |
| 2021-04 | 874901           |      3.98853e+06 |
| 2021-05 |      1.23899e+06 |      5.22752e+06 |
| 2021-06 |      1.18885e+06 |      6.41637e+06 |
| 2021-07 | 895869           |      7.31224e+06 |
| 2021-08 |      1.49272e+06 |      8.80495e+06 |
| 2021-09 |      1.517e+06   |      1.0322e+07  |
| 2021-10 |      1.31835e+06 |      1.16403e+07 |

## A3. Top 2 customers by spend in each region  (8 rows)
| region   | customer_name     |   spend |
|:---------|:------------------|--------:|
| Central  | Barbara Sanchez   |  472962 |
| Central  | Barbara Sanchez   |  292157 |
| East     | Linda Garcia      |  857087 |
| East     | Patricia Williams |  564382 |
| South    | Charles Allen     |  504387 |
| South    | Justin Jones      |  412021 |
| West     | Andrew Williams   |  561242 |
| West     | Melissa Walker    |  498077 |

## A4. First and last purchase per customer + days between (LAG/LEAD)  (1,502 rows)
|   customer_id | first_purchase   | last_purchase   |   total_orders |   avg_gap_days |
|--------------:|:-----------------|:----------------|---------------:|---------------:|
|           872 | 2023-12-17       | 2023-12-19      |              2 |              2 |
|           173 | 2021-01-06       | 2024-12-19      |            310 |              4 |
|           767 | 2024-11-21       | 2024-11-25      |              2 |              4 |
|           897 | 2021-01-15       | 2024-12-19      |            234 |              6 |
|          1375 | 2021-01-03       | 2024-12-29      |            218 |              6 |
|           433 | 2021-01-20       | 2024-12-12      |            192 |              7 |
|          1173 | 2021-01-01       | 2024-12-29      |            203 |              7 |
|          1788 | 2021-01-24       | 2024-12-26      |            201 |              7 |
|           119 | 2021-01-13       | 2024-12-30      |            176 |              8 |
|          1349 | 2021-01-11       | 2024-12-25      |            174 |              8 |

## A5. RFM-style segmentation in SQL: Recency / Frequency / Monetary scores  (1,648 rows)
|   customer_id |   recency_score |   frequency_score |   monetary_score |
|--------------:|----------------:|------------------:|-----------------:|
|             6 |               5 |                 5 |                5 |
|             7 |               5 |                 5 |                5 |
|            32 |               5 |                 5 |                5 |
|            59 |               5 |                 5 |                5 |
|            69 |               5 |                 5 |                5 |
|            84 |               5 |                 5 |                5 |
|            95 |               5 |                 5 |                5 |
|           106 |               5 |                 5 |                5 |
|           109 |               5 |                 5 |                5 |
|           115 |               5 |                 5 |                5 |

## A6. Discount effect: margin by discount band (CASE)  (5 rows)
| discount_band   |   lines |     revenue |            profit |   margin |
|:----------------|--------:|------------:|------------------:|---------:|
| No discount     |   33031 | 2.38137e+07 |       7.65054e+06 |   0.3213 |
| 0-10%           |   25133 | 1.69197e+07 |       4.85737e+06 |   0.2871 |
| 10-20%          |   27191 | 1.67135e+07 |       3.42455e+06 |   0.2049 |
| 20-30%          |   14480 | 7.75052e+06 |  769023           |   0.0992 |
| 30%+            |    8210 | 3.70786e+06 | -304653           |  -0.0822 |

## A7. Weekly sales pattern (weekday share of revenue)  (7 rows)
| day_of_week   |     revenue |   pct |
|:--------------|------------:|------:|
| Sunday        | 1.01029e+07 | 14.66 |
| Wednesday     | 9.95788e+06 | 14.45 |
| Friday        | 9.95571e+06 | 14.45 |
| Saturday      | 9.90923e+06 | 14.38 |
| Monday        | 9.81456e+06 | 14.24 |
| Tuesday       | 9.61646e+06 | 13.96 |
| Thursday      | 9.54851e+06 | 13.86 |

## A8. Contribution of top 20% of products to revenue (Pareto check)  (1 rows)
|   top20_revenue |   total_revenue |   share_pct |   products_included |
|----------------:|----------------:|------------:|--------------------:|
|     3.76191e+07 |     6.89052e+07 |        54.6 |                  20 |