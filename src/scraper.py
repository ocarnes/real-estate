import requests, math, json, time, os, random, datetime
import pandas as pd
# import dask.dataframe as dd
# from dask.distributed import Client
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from sql_upload import CloudQuery

class scraper:
    def __init__(self, status='FOR_SALE', cat='cat1'):
        self.main_url = "https://www.zillow.com/"
        self.map_url = self.main_url + "search/GetSearchPageState.htm"
        self.region_url = self.main_url + "search/GetSearchPageCustomRegion.htm"
        self.graph_url = self.main_url + "graphql/"
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.8',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        }
        self.status = status
        self.cat = cat
        # client = Client(...)  # Connect to distributed cluster and override default
        self.init_requests()
        self.get_region_info()

    def init_requests(self):
        self.sesh = requests.Session()
        self.sesh.headers.update(self.headers)
        self.response = self.sesh.get(self.main_url)
        self.captcha()

    def captcha(self):
        time.sleep(1)
        self.response = self.sesh.get(self.main_url)
        if 'captcha' in self.response.url:
            print('Captcha\'d')
            driver = webdriver.Firefox()
            driver.get("https://www.zillow.com/")
            WebDriverWait(driver, 500).until(
                    EC.presence_of_element_located((By.ID, 'search-box-input'))
                ).click()
            driver.find_element_by_id('search-box-input').send_keys('Denver')
            try:
                WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),", CO")]'))
                    ).click()
            except:
                driver.find_element_by_id('search-box-input').clear()
                driver.find_element_by_id('search-box-input').send_keys('Denver')
                WebDriverWait(driver, 300).until(
                        EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),", CO")]'))
                    ).click()
            WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[text()="For sale"]'))
                ).click()
            # driver.find_element_by_xpath('//button[text()="For sale"]').click()
            WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[text()="Map"]'))
                ).click()
            # driver.find_element_by_xpath('//button[text()="Map"]').click()
            win_size = driver.get_window_size()
            driver.maximize_window()
            for _ in range(30):
                for cookie in driver.get_cookies():
                    c = {cookie['name']: cookie['value']}
                    self.sesh.cookies.update(c)
                self.response = self.sesh.get(self.main_url)
                time.sleep(random.randint(1,5))
                actions = ActionChains(driver)
                actions.move_to_element_with_offset(driver.find_element_by_tag_name('body'), 0,0)
                actions.move_by_offset(random.randint(0,win_size['width']), random.randint(0,win_size['height'])).click().perform()
                if self.response.url==self.main_url:
                    print('Un-Captcha\'d!')
                    driver.quit()
                    break
            driver.quit()

    def get_region_info(self):
        # payload = {"clipPolygon": '39.7805083307442,-104.9813175201416|39.77734213036309,-104.98921394348145|39.77285643047229,-104.99573707580566|39.76731486818042,-105.00054359436035|39.76098110792177,-105.00672340393066|39.75517464921777,-105.01187324523926|39.74963166379671,-105.01736640930176|39.74408823235372,-105.02251625061035|39.73722431834756,-105.02423286437988|39.73035972069829,-105.02045631408691|39.72534285163868,-105.0142765045166|39.719797466383696,-105.00809669494629|39.71504392409333,-105.00054359436035|39.71055416666532,-104.99402046203613|39.703422774847795,-104.99402046203613|39.69708314111446,-104.99127388000488|39.69047873671268,-104.98543739318848|39.68598738079136,-104.97857093811035|39.68360948584326,-104.96964454650879|39.68202417705157,-104.96071815490723|39.681495732700114,-104.95213508605957|39.68598738079136,-104.94561195373535|39.69232803363924,-104.9428653717041|39.69893226111142,-104.94389533996582|39.70738475019062,-104.94217872619629|39.71689256280317,-104.93943214416504|39.7245506810479,-104.9370288848877|39.734320148926955,-104.93325233459473|39.74197633162926,-104.93016242980957|39.74883977232624,-104.92775917053223|39.756230405393936,-104.93016242980957|39.76256460260632,-104.93393898010254|39.76942599212873,-104.9370288848877|39.77602283721249,-104.93908882141113|39.7805083307442,-104.9813175201416'}
        payload = {'clipPolygon':'39.78006017403298,-104.94128112449808|39.780324019207704,-104.9455726589219|39.78019209674679,-104.94986419334573|39.78019209674679,-104.95432738914651|39.77979632784667,-104.95861892357034|39.77992825106628,-104.96308211937112|39.78019209674679,-104.96737365379495|39.78019209674679,-104.97183684959573|39.78006017403298,-104.97612838401956|39.77992825106628,-104.98041991844339|39.77979632784667,-104.98471145286722|39.78006017403298,-104.98900298729104|39.781379389790665,-104.99295119896097|39.782434744188116,-104.99707107200784|39.783358166008604,-105.00136260643167|39.783753914423876,-105.0056541408555|39.783753914423876,-105.01011733665628|39.783621998538365,-105.01440887108011|39.78388583005649,-105.01870040550394|39.78454540442603,-105.02299193992776|39.78454540442603,-105.02745513572854|39.78441349005792,-105.03174667015237|39.78428157543692,-105.0360382045762|39.78349008239993,-105.04032973900003|39.784149660563,-105.04462127342386|39.78454540442603,-105.04891280784769|39.782434744188116,-105.05234603538675|39.779532480648804,-105.05028609886331|39.77689395303319,-105.05303268089456|39.77359565126245,-105.05234603538675|39.77056107404021,-105.05062942161722|39.76713052131257,-105.05131606712503|39.76383175171245,-105.05165938987894|39.7605328240685,-105.05200271263284|39.75723373838411,-105.05234603538675|39.75393449466264,-105.0525176967637|39.750503113550174,-105.0525176967637|39.74720354744351,-105.05286101951761|39.743771831057764,-105.05286101951761|39.740339943753966,-105.05286101951761|39.74047194257992,-105.04856948509378|39.740339943753966,-105.04427795066995|39.73981194592186,-105.03998641624612|39.73981194592186,-105.03535155906839|39.73981194592186,-105.03088836326761|39.73981194592186,-105.02642516746683|39.73981194592186,-105.02196197166604|39.740075945343584,-105.01767043724222|39.73756791000524,-105.01475219383401|39.7342677244527,-105.01509551658792|39.730703346575226,-105.01509551658792|39.72753485596066,-105.0137222255723|39.724234190057345,-105.01252059593362|39.72172557829804,-105.00960235252542|39.71895279596661,-105.00702743187112|39.71697216890323,-105.00342254295511|39.71419919545884,-105.00101928367776|39.711426110534596,-104.99861602440042|39.7083887943755,-104.99689941063089|39.70548341031499,-104.9946678127305|39.70310618690297,-104.99157790794534|39.701521325796186,-104.98780135765237|39.6994081210339,-104.98436813011331|39.69716277007356,-104.9811065639512|39.694521087187105,-104.97835998191995|39.69187930319813,-104.9756133998887|39.689633707316986,-104.97235183372659|39.687123837245245,-104.96943359031839|39.685670712869275,-104.96548537864847|39.6850101916796,-104.96119384422464|39.684613875932925,-104.95690230980081|39.684613875932925,-104.95243911400003|39.684613875932925,-104.94797591819925|39.68355702282121,-104.94385604515237|39.68316069873415,-104.93956451072854|39.78006017403298,-104.94128112449808'}
        # self.headers['content-type'] = 'multipart/form-data; boundary=---------------------------1379375077324416132687833734'#----WebKitFormBoundary62ivKtUtqxAojc3G'
        # self.sesh.headers.update(self.headers)
        self.region_response = self.sesh.post(self.region_url, data=payload)
        self.region_id = self.region_response.json()['customRegionId']
        lat_lon = payload['clipPolygon'].split('|')

        lats, lons = [], []
        for line in lat_lon:
             lat, lon = line.split(',')
             lats.append(float(lat))
             lons.append(float(lon))

        west = min(lons)
        east = max(lons)
        south = min(lats)
        north = max(lats)
        self.window = [west, east, south, north]

    def params(self, deltaT="7"):
        parameters = {'searchQueryState': {
                    # "pagination":{},
                    # "usersSearchTerm":"Denver, CO",
                    # "regionSelection":[{"regionId":11093,"regionType":6}],
                    "mapBounds":{
                        "west":self.window[0],
                        "east":self.window[1],
                        "south":self.window[2],
                        "north":self.window[3]},
                    "isMapVisible":False,
                    "filterState":{
                        "isAllHomes":{"value":True}},
                    "isListVisible":False,
                    # "mapZoom":13,
                    "customRegionId":self.region_id,
                    "category":self.cat},
                'wants': {
                    self.cat:["mapResults"]},
                    # "cat2":["total"]},
                'requestId': 1}
        if 'sold' in self.status.lower():
            parameters['searchQueryState']["filterState"].update({
            "isPreMarketForeclosure":{"value":False},
            "isRecentlySold":{"value":True},
            "isForSaleByAgent":{"value":False},
            "isForSaleByOwner":{"value":False},
            "isNewConstruction":{"value":False},
            "isForSaleForeclosure":{"value":False},
            "isComingSoon":{"value":False},
            "isAuction":{"value":False},

            "doz":{"value":deltaT}, # "7" for 7 days, "6m" for 6 months,  max is 36m or just exclude if all results are desired
            # "hoa":{"max":0},
            # "sqft":{"min":1250,"max":3000},
            # "lotSize":{"min":1000,"max":43560},
            # "built":{"min":1900,"max":2005},
            # "isBasementFinished":{"value":True},
            # "isBasementUnfinished":{"value":True},
            # "singleStory":{"value":True},
            # "hasAirConditioning":{"value":True},
            # "hasPool":{"value":True},
            # "isCityView":{"value":True},
            # "isMountainView":{"value":True},
            # "isWaterView":{"value":True},
            # "isParkView":{"value":True},
            "isPreMarketPreForeclosure":{"value":False}})
        elif 'pending' in self.status.lower():
            parameters['searchQueryState']["filterState"].update({
            # "isPreMarketForeclosure":{"value":False},
            "isRecentlySold":{"value":True},
            "isForSaleByAgent":{"value":False},
            "isForSaleByOwner":{"value":False},
            "isNewConstruction":{"value":False},
            "isForSaleForeclosure":{"value":False},
            "isComingSoon":{"value":False},
            "isAuction":{"value":False},
            "doz":{"value":deltaT}, # "7" for 7 days, "6m" for 6 months,  max is 36m or just exclude if all results are desired
            # "hoa":{"max":0},
            # "sqft":{"min":1250,"max":3000},
            # "lotSize":{"min":1000,"max":43560},
            # "built":{"min":1900,"max":2005},
            # "isBasementFinished":{"value":True},
            # "isBasementUnfinished":{"value":True},
            # "singleStory":{"value":True},
            # "hasAirConditioning":{"value":True},
            # "hasPool":{"value":True},
            # "isCityView":{"value":True},
            # "isMountainView":{"value":True},
            # "isWaterView":{"value":True},
            # "isParkView":{"value":True},
            "isPreMarketPreForeclosure":{"value":False}})
        self.parameters = {k: json.dumps(v) if isinstance(v, dict) else v for k,v in parameters.items()}

    def lat_lon_windows(self):
        divider = math.ceil(math.sqrt(self.map_response.json()['categoryTotals'][self.cat]['totalResultCount']/500))+1
        lon_inc = (self.window[0]-self.window[1])/divider
        lat_inc = (self.window[3]-self.window[2])/divider
        self.windows = [[[self.window[1]+(i+1)*lon_inc, self.window[1]+i*lon_inc, self.window[2]+j*lat_inc, self.window[2]+(j+1)*lat_inc] for i in range(divider)] for j in range(divider)]
        print('splitting {} results into {} windows'.format(self.map_response.json()['categoryTotals'][self.cat]['totalResultCount'], len(self.windows)*len(self.windows[0])))

    def scrape_map_points(self, count=0):
        time.sleep(random.randint(1,3))
        self.pull_map_json()
        print('window {}: {} results'.format(count, self.total))
        count += 1
        if self.total < 500:
            return
        self.lat_lon_windows()
        for row in self.windows:
            for window in row:
                self.window = window
                self.scrape_map_points(count)

    def pull_map_json(self):
        time.sleep(1)
        self.params()
        self.map_response = self.sesh.get(self.map_url, params=self.parameters)
        if self.map_response.status_code == 200 and self.map_url in self.map_response.url:
            self.total = self.map_response.json()['categoryTotals'][self.cat]['totalResultCount']
            self.json = self.map_response.json()[self.cat]['searchResults']['mapResults']
            buildings, units = [], []
            for unit in self.json:
                if 'isBuilding' in unit.keys():
                    unit['buildingKey'] = unit['detailUrl'].split('-')[-1].strip('/')
                    buildings.append(unit)
                else:
                    units.append(unit)
            query = CloudQuery()
            query.insert_listing_queries(units)
            print('added units')
            query.insert_building_queries(buildings)
            print('added buildings')
            query.connection.close()
            query.engine.dispose()
            self.find_building_zpids(buildings)
        # self.total = self.response.json()['categoryTotals'][self.cat]['totalResultCount']

    def find_building_zpids(self, buildings):
        query = CloudQuery()
        payload = {"operationName":"BuildingQuery","variables":{"cache":False,"update":False},"queryId":"083bacc1612742b3bba0bdb9287330c2"}
        query.bulk_building_query(buildings)
        buildings = query.values
        for building in buildings:
            time.sleep(random.randint(1,5))
            payload['variables'].update(building['latLong'])
            payload['variables'].update({'buildingKey':	building['buildingKey']})
            try:
                self.response = self.sesh.post(self.graph_url, json=payload)
                building = self.response.json()["data"]["building"]
            except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
                self.captcha()
                self.response = self.sesh.post(self.graph_url, json=payload)
                building = self.response.json()["data"]["building"]
            units = [unit for unit in building["ungroupedUnits"] if unit["listingType"] != "OTHER"]
            query.insert_building_listing_queries(units, building)
        query.connection.close()
        query.engine.dispose()

    def pull_property_json(self):
        query = CloudQuery()
        query.bulk_zpid_query(detailed=True)
        units = query.values
        for unit in units:
            time.sleep(random.randint(1,3))
            payload = {"operationName":"ForSaleShopperPlatformFullRenderQuery",
                    "variables":{"zpid":str(unit['zpid'])},
                    "queryId":"deb1c496899762c92050e49ed7398ce4"}
            try:
                self.response = self.sesh.post(self.graph_url, json=payload)
                details = self.response.json()['data']['property']
            except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
                self.captcha()
                self.response = self.sesh.post(self.graph_url, json=payload)
            details = self.response.json()['data']['property']
            try:
                if details['zpid']:
                    query.insert_listing_detailed([details])
                else:
                    print('No info for zpid {}'.format(unit['zpid']))
            except:
                print('Error for zpid {}'.format(unit['zpid']))
                # print('')
        query.connection.close()
        query.engine.dispose()

if __name__ == '__main__':
    scrape = scraper()
    scrape.scrape_map_points()
    scrape.pull_property_json()
    scrape = scraper(status='SOLD')
    scrape.scrape_map_points()
    scrape.pull_property_json()
    scrape = scraper(cat='cat2')
    scrape.scrape_map_points()
    scrape.pull_property_json()
    scrape = scraper(status='PENDING')
    scrape.scrape_map_points()
    scrape.pull_property_json()
