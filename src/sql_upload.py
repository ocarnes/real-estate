import sqlalchemy, os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, String, Boolean, Float, DateTime
from sqlalchemy.dialects.postgresql import JSON, JSONB
import pandas as pd

class CloudQuery:
    def __init__(self):
        self.SQL_HOST = os.environ.get("SQL_HOST", None) # Defaults to using localhost/Cloud SQL Proxy
        self.DB_PORT  = os.environ.get("DB_PORT", 5432)
        self.DB_USER  = os.environ.get("DB_USER", None)
        self.DB_PASS  = os.environ.get("DB_PASS", None)
        self.DB_NAME  = os.environ.get("DB_NAME", None)
        self.engine = sqlalchemy.create_engine(
                # Equivalent URL:
                # postgres://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
                sqlalchemy.engine.url.URL(
                    drivername="postgresql",
                    username=self.DB_USER,  # e.g. "my-database-user"
                    password=self.DB_PASS,  # e.g. "my-database-password"
                    host=self.SQL_HOST,  # e.g. "127.0.0.1"
                    port=self.DB_PORT,  # e.g. 5432
                    database=self.DB_NAME  # e.g. "my-database-name"
                ),
            )
        self.connection = self.engine.connect()
        self.meta = sqlalchemy.MetaData()
        self.meta.reflect(bind=self.engine)
        self.values = []

    def _create_SQL_tables(self):
        self.meta = sqlalchemy.MetaData(self.connection)
        sqlalchemy.Table("listings_detailed", self.meta,
        	Column("zpid", Integer, primary_key = True),
            Column("DateAdded", DateTime),
            Column("DateModified", DateTime),
        	Column("city", String),
        	Column("state", String),
        	Column("homeStatus", String),
        	Column("bedrooms", Integer),
        	Column("bathrooms", Integer),
        	Column("price", Integer),
        	Column("yearBuilt", Integer),
        	Column("streetAddress", String),
        	Column("zipcode", String),
        	Column("priceHistory", JSONB),
        	Column("longitude", Float),
        	Column("latitude", Float),
        	Column("description", String),
        	Column("hdpUrl", String),
        	Column("livingArea", Integer),
        	Column("homeType", String),
        	Column("zestimate", Integer),
        	Column("rentZestimate", Integer),
        	Column("parcelId", String),
        	Column("resoFacts", JSONB),
        	Column("taxAssessedValue", Integer),
        	Column("taxAssessedYear", Integer),
        	Column("dateSold", Integer),
        	Column("lotSize", Integer),
        	Column("monthlyHoaFee", Integer),
            Column("parentRegion", JSONB),
        	Column("propertyTaxRate", Float),
        	Column("taxHistory", JSONB),
        	Column("buildingId", String),
        	Column("daysOnZillow", Integer),
        	Column("isListedByOwner", Boolean),
        	Column("pageViewCount", Integer),
        	Column("favoriteCount", Integer),
        	Column("isIncomeRestricted", Boolean))

        sqlalchemy.Table("listings_query", self.meta,
        	Column("zpid", Integer, primary_key = True),
            Column("DateAdded", DateTime),
            Column("DateModified", DateTime),
        	Column("address", String),
        	Column("price", String),
        	Column("beds", Integer),
        	Column("baths", Float),
        	Column("area", Integer),
        	Column("latLong", JSONB),
        	Column("statusType", String),
        	Column("listingType", String),
        	Column("hdpData", JSONB),
        	Column("detailUrl", String),
        	Column("info1String", String),
        	Column("brokerName", String))

        sqlalchemy.Table("building_query", self.meta,
            Column("buildingId", String, primary_key = True),
            Column("buildingKey", String),
            Column("DateAdded", DateTime),
            Column("DateModified", DateTime),
        	Column("unitCount", Integer),
        	Column("isBuilding", Integer),
        	Column("address", String),
        	Column("latLong", JSONB),
        	Column("statusType", String),
        	Column("listingType", String),
        	Column("detailUrl", String))

        self.meta.create_all()

    def _drop_tables(self):
         base = declarative_base()
         for tableName in sqlalchemy.inspect(self.connection).get_table_names():
             table = self.meta.tables.get(tableName)
             base.metadata.drop_all(self.connection, [table], checkfirst=True)

    def insert_building_queries(self, buildings):
        self.currentTable = self.meta.tables["building_query"]
        self.values = []
        for building in buildings:
            self.values.append({"buildingKey":building["buildingKey"],
            "DateAdded":pd.Timestamp.now(),
            "DateModified":pd.Timestamp.now(),
            "address":building["address"],
            "buildingId":building["buildingId"],
            "unitCount":building["unitCount"],
            # "isBuilding":building["isBuilding"],
            "latLong":building["latLong"],
            "statusType":building["statusType"],
            "listingType":building["listingType"],
            "detailUrl":building["detailUrl"]})
        self.bulk_building_query()
        if self.values:
            command = self.currentTable.insert().values(self.values)
            self.connection.execute(command)

    def insert_building_listing_queries(self, units, building):
        self.currentTable = self.meta.tables["listings_query"]
        self.values = []
        for unit in units:
            self.values.append({"zpid":unit["zpid"],
            "DateAdded":pd.Timestamp.now(),
            "DateModified":pd.Timestamp.now(),
            "address":building["fullAddress"],
            "price":unit["price"],
            "beds":unit["beds"],
            "baths":unit["baths"],
            "area":unit["sqft"],
            "latLong":{"latitude": building["latitude"], "longitude": building["longitude"]},
            "statusType":unit["listingType"],
            "detailUrl":unit["hdpUrl"],
            "info1String":unit["listingMetadata"]["BuildingDataG"],
            "brokerName":unit["listingMetadata"]["BuildingDataH"],
            "hdpData":{"hdpData":
                        {"homeInfo": {"zpid": unit["zpid"],
                            "zipcode": building["zipcode"],
                            "city": building["city"],
                            "state": building["state"],
                            "latitude": building["latitude"],
                            "longitude": building["longitude"],
                            "price": unit["price"],
                            "dateSold": unit["lastSoldAt"],
                            "bathrooms": unit["baths"],
                            "bedrooms": unit["beds"],
                            "livingArea": unit["sqft"],
                            "homeType": building["buildingType"],
                            "buildingName": building["buildingName"],
                            "homeStatus": unit["listingType"],
                            "listing_sub_type": unit["listing_sub_type"],
                            "unitNumber":unit["unitNumber"],
                            "lotId": building["lotId"],
                            "isLowIncome":building["isLowIncome"],
                            "isSeniorHousing":building["isSeniorHousing"],
                            "isStudentHousing":building["isStudentHousing"],
                            "bdpUrl":building["bdpUrl"]}}}})
        self.bulk_zpid_query()
        if self.values:
            command = self.currentTable.insert().values(self.values)
            self.connection.execute(command)

    def insert_listing_queries(self, units):
        self.currentTable = self.meta.tables["listings_query"]
        self.values = []
        for unit in units:
            self.values.append({"zpid":unit["zpid"],
                "DateAdded":pd.Timestamp.now(),
                "DateModified":pd.Timestamp.now(),
                "address":unit["address"],
                "price":unit["price"],
                "beds":unit["beds"],
                "baths":unit["baths"],
                "area":unit["area"],
                "latLong":unit["latLong"],
                "statusType":unit["statusType"],
                "hdpData":unit["hdpData"],
                "detailUrl":unit["detailUrl"],
                "info1String":unit["info1String"] if "info1String" in unit.keys() else None,
                "brokerName":unit["brokerName"] if "brokerName" in unit.keys() else None})
        self.bulk_zpid_query()
        if self.values:
            command = self.currentTable.insert().values(self.values)
            self.connection.execute(command)

    def insert_listing_detailed(self, units):
        self.currentTable = self.meta.tables["listings_detailed"]
        self.values = []
        for unit in units:
            self.values.append({
                "zpid":unit["zpid"],
                "DateAdded":pd.Timestamp.now(),
                "DateModified":pd.Timestamp.now(),
                "city":unit["city"],
                "state":unit["state"],
                "homeStatus":unit["homeStatus"],
                "bedrooms":unit["bedrooms"],
                "bathrooms":unit["bathrooms"],
                "price":unit["price"],
                "yearBuilt":unit["yearBuilt"],
                "streetAddress":unit["streetAddress"],
                "zipcode":unit["zipcode"],
                "priceHistory":{i: unit["priceHistory"][i] for i in range(len(unit["priceHistory"]))},
                "longitude":unit["longitude"],
                "latitude":unit["latitude"],
                "description":unit["description"],
                "hdpUrl":unit["hdpUrl"],
                "livingArea":unit["livingArea"],
                "homeType":unit["homeType"],
                "zestimate":unit["zestimate"],
                "rentZestimate":unit["rentZestimate"],
                "parcelId":unit["parcelId"],
                "resoFacts":unit["resoFacts"],
                "taxAssessedValue":unit["taxAssessedValue"],
                "taxAssessedYear":unit["taxAssessedYear"],
                # "dateSold":pd.to_datetime(unit['dateSold'],unit='ms'),
                "lotSize":unit["lotSize"],
                "monthlyHoaFee":unit["monthlyHoaFee"],
                "parentRegion":unit["parentRegion"],
                "propertyTaxRate":unit["propertyTaxRate"],
                "taxHistory":{i: unit["taxHistory"][i] for i in range(len(unit["taxHistory"]))},
                "buildingId":unit["buildingId"],
                "daysOnZillow":unit["daysOnZillow"],
                "isListedByOwner":unit["isListedByOwner"],
                "pageViewCount":unit["pageViewCount"],
                "favoriteCount":unit["favoriteCount"],
                "isIncomeRestricted":unit["isIncomeRestricted"]})
        self.bulk_zpid_query()
        if self.values:
            command = self.currentTable.insert().values(self.values)
            self.connection.execute(command)
            print('added {}'.format(unit["zpid"]))

    def zpid_query(self, zpid):
        command = self.currentTable.select().where(self.currentTable.c.zpid==zpid)

        self.result = self.connection.execute(command)

    def update_tables(self, unit):
        self.currentTable = self.meta.tables["listings_detailed"]
        command = self.currentTable.update().where(self.currentTable.c.zpid==unit["zpid"]).values(
                        DateModified=pd.Timestamp.now(),
                        priceHistory = {i: unit["priceHistory"][i] for i in range(len(unit["priceHistory"]))},
                        pageViewCount = unit["pageViewCount"],
                        favoriteCount = unit["favoriteCount"],
                        daysOnZillow = unit["daysOnZillow"],
                        homeStatus = unit["homeStatus"],
                        zestimate = unit["zestimate"],
                        rentZestimate = unit["rentZestimate"]
                        )
        self.connection.execute(command)
        self.currentTable = self.meta.tables["listings_query"]
        command = self.currentTable.update().where(self.currentTable.c.zpid==unit["zpid"]).values(
                        DateModified=pd.Timestamp.now(),
                        statusType = unit["homeStatus"]
                        )
        self.connection.execute(command)

    def bulk_zpid_query(self, detailed=False):
        if detailed == True:
            command = self.meta.tables["listings_query"].select()
            self.result = self.connection.execute(command)
            zpids = [row[0] for row in self.result]
            self.values = [[{'zpid':z}][0] for z in zpids]
            self.currentTable = self.meta.tables["listings_detailed"]
        else:
            zpids = (item['zpid'] for item in self.values)
        command = self.currentTable.select().where(self.currentTable.c.zpid.in_(zpids))

        self.result = self.connection.execute(command)
        zpids_in_table = [row[0] for row in self.result]
        self.values = [value for value in self.values if int(value['zpid']) not in zpids_in_table]

    def bulk_building_query(self, buildings=None):
        if buildings:
            self.values = buildings
        buildingIds = (item['buildingId'] for item in self.values)
        self.currentTable = self.meta.tables["building_query"]
        command = self.currentTable.select().where(self.currentTable.c.buildingId.in_(buildingIds))

        self.result = self.connection.execute(command)
        bKeys_in_table = [row[0] for row in self.result]
        self.values = [value for value in self.values if value['buildingId'] not in bKeys_in_table]
