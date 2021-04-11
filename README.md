# README
## Intro ##
[This project is in progress]

This project was created out of my frustration at not being able to gain access to the RESO api without Real Estate Broker credentials. This product is not intended for commercial use and is simply a snapshot of a small section of the Denver real estate market over the past 3 years. Listings are scraped from Zillow using regional boundaries and run through a model created to detect undervalued properties. Further details can be found below.

### Contents ###
* [Data collection](#data-collection)
* [Data Storage](#data-storage)
* [Data cleaning](#data-cleaning)
<!-- * [Feature selection](#feature-selection)
* [Recommendations](#recommendations)
* [Recommendation optimization](#recommendation-optimization)
* [Production](#production) -->
* [To Do](#to-do)

## Data Collection ##
Data is scraped from Zillow a few times a day using containerized web scraping scripts run on Kubernetes.
1. Scraping container: The scraping is mostly performed using Python's requests package and data upload is performed with sqlalchemy. I've also included a little selenium script that runs if a captcha is detected.
2. Authentication container: image for running Cloud SQL proxy to connect the scraping container to Cloud SQL.

## Data Storage ##
Data is uploaded from raw json format into a postgres instance on Cloud SQL. Some fields are converted to string and integer type table columns while others are left as JSONB formatted columns. The three tables currently include results from:
1. Map Queries (Table name: 'listings_query') - json of all the little dots populated on Zillow's result map. Note: condos are grouped within one building so the initial map query json has to be split into individual listings and grouped building listings, which leads us to...
2. Building Queries (Table name: 'building_query') - json of all units within a building that are listed as 'FOR_SALE' or 'SOLD'. Individual condo listings can be pulled from this and added on the the Map Queries table mentioned previously.
3. Detailed Listing results (Table name: 'listings_detailed') - json for each individual listing with further listing details not included in Map Queries (ex: listing description)

## Data Cleaning ##

<!-- ## Feature Selection ##

## Recommendations ##

## Recommendation Optimization ##

## Production ## -->

## To Do ##
1. Cross check previous 'FOR_SALE' listings against current 'FOR_SALE' listings and update accordingly
2. Make 'daysOnZillow' a calculated column
3. Freeze 'daysOnZillow' after listing marked sold (calculate based on priceHistory)

## Additional features to consider from denver.gov ##
1. [School distance and rating](https://www.greatschools.org/school?id=00506&state=CO)
2. [Proximity to parks](https://www.denvergov.org/opendata/dataset/city-and-county-of-denver-parks)
3. [Proximity to dog parks](https://www.denvergov.org/opendata/dataset/city-and-county-of-denver-dog-parks)
4. [Is it registered as short term rental](https://www.denvergov.org/opendata/dataset/city-and-county-of-denver-str-host-list-of-active-short-term-rentals)
5. [Equity Index](https://www.denvergov.org/opendata/dataset/city-and-county-of-denver-equity-index-2020-neighborhood)
6. [Site development plans](https://www.denvergov.org/opendata/dataset/city-and-county-of-denver-site-development-plans)


## References ##
1. [SQL Alchemy Tutorial](https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_sql_expressions.htm)
2. [Cloud SQL - Kubernetes Sidecar tutorial](https://medium.com/google-cloud/connecting-cloud-sql-kubernetes-sidecar-46e016e07bb4)


<!-- docker build -t zillowScrape -->
<!-- docker tag zillowScrape gcr.io/$plenary-era-308716/zillowScrape -->
