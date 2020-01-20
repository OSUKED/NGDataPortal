"""
Imports
"""
import json
import pandas as pd
import warnings
import requests

"""
Main Scripts
"""
#with open('stream_to_resource_id.json', 'r') as fp:
#    stream_2_id_map = json.load(fp)
    
stream_2_id_map = {"contracted-energy-volumes-and-data": "6c33447d-4e15-448d-9ed0-4516a35657a4", "firm-frequency-response-auction-results": "340ae31e-b010-46fc-af87-e89778d438ef", "fast-reserve-tender-reports": "7f9357b2-0591-45d9-8e0d-0bd7d613a5ff", "balancing-services-charging-report-bcr": "06806fef-a9b8-40d7-bbb5-105d662eac14", "current-balancing-services-use-of-system-bsuos-data": "2c05a930-13c2-400f-bd3b-a7e6fb9f61cf", "weekly-wind-availability": "bb375594-dd0b-462b-9063-51e93c607e41", "mbss": "eb3afc32-fe39-4f33-8808-95b4463e20f8", "firm-frequency-response-market-information": "fa1c517f-44e5-470f-813c-5f690dc463fe", "balancing-services-use-of-system-bsuos-daily-cost": "b19a3594-3647-4d06-a119-7d97d538d496", "outturn-voltage-costs": "1b47a532-9f22-49c1-ae2a-d84dcc6d7408", "fast-reserve-market-information-reports": "37e68cbc-ac83-4e52-b10c-b4c49553365f", "bsuos-monthly-cost": "0d638634-1285-41ac-b965-d0e06964a302", "bsuos-monthly-forecast": "a7c7711a-fac4-4bb9-bf23-abea5a2ea616", "short-term-operating-reserve-stor": "ef2bbb5f-ee5c-40c3-bd4b-5a36d1d5f5dc", "system-frequency-data": "f0933bdd-1b0e-4dd3-aa7f-5498df1ba5b9", "short-term-operating-reserve-tender-reports": "88ef0c84-83c5-4c84-9846-6fd44d8a6037", "daily-wind-availability": "7aa508eb-36f5-4298-820f-2fa6745ae2e7", "historic-demand-data": "11252656-007c-45a4-87db-9d5cc6e8535a", "weekly-opmr": "693ca90e-9d48-4a29-92ad-0bf007bba5c2", "daily-opmr": "0eede912-8820-4c66-a58a-f7436d36b95f", "2-day-ahead-demand-forecast": "cda26f27-4bb6-4632-9fb5-2d029ca605e1", "day-ahead-constraint-flows-and-limits": "d7d4ea81-c14d-41a0-8ed2-f281ae9df8d7", "disaggregated-bsad": "48fbc6ea-381e-40d6-9633-d1be09a89a0b", "aggregated-bsad": "cfb65cd4-e41c-4587-9c78-31004827bee6", "balancing-services-adjustment-data-forward-contracts": "7ce8164f-0f0c-4940-b821-ca232e2eefaf", "thermal-constraint-costs": "d195f1d8-7d9e-46f1-96a6-4251e75e9bd0", "daily-demand-update": "177f6fa4-ae49-4182-81ea-0c6b35f26ca6", "balancing-services-use-of-system-bsuos-daily-forecast": "c1be6c7c-c36d-46cb-8038-098075599bb0", "obligatory-reactive-power-service-orps-utilisation": "d91e4fd2-1f27-4d0b-8473-b4b19af7f3dc", "7-day-ahead-national-forecast": "70d3d674-15a6-4e41-83b4-410440c0b0b9", "firm-frequency-response-post-tender-reports": "e692dc29-e94c-4be7-8067-4fc6af8bab22", "upcoming-trades": "48f96ddb-1038-4760-8a39-608713ba163f", "day-ahead-wind-forecast": "b2f03146-f05d-4824-a663-3a4f36090c71", "1-day-ahead-demand-forecast": "aec5601a-7f3e-4c4c-bf56-d8e4184d3c5b", "embedded-wind-and-solar-forecasts": "db6c038f-98af-4570-ab60-24d71ebd0ae5", "generation-mix-national": "0a168493-5d67-4a26-8344-2fe0a5d4d20b"}

class Wrapper():
    def __init__(self, stream):
        self.stream = stream
        self.resource_id = stream_2_id_map[self.stream]
        
    def NG_request(self, params={}):    
        url_root = 'https://national-grid-admin.ckan.io/api/3/action/datastore_search'

        params.update({'resource_id':self.resource_id})

        if 'sql' in params.keys():
            url_root += '_sql'

        r = requests.get(url_root, params=params)

        return r

    def raise_(self, err_txt, error=ValueError): 
        raise error(err_txt)

    def check_request_success(self, r_json):
        if r_json['success'] == False:
            err_msg = r_json['error']['message']
            self.raise_(err_msg)

    date_between = lambda self, dt_col, start_date, end_date: f'SELECT * from "{self.resource_id}" WHERE "{dt_col}" BETWEEN \'{start_date}\'::timestamp AND \'{end_date}\'::timestamp ORDER BY "{dt_col}"' 
    date_less_than = lambda self, dt_col, date: f'SELECT * from "{self.resource_id}" WHERE "{dt_col}" < \'{date}\'::timestamp ORDER BY "{dt_col}"' 
    date_greater_than = lambda self, dt_col, date: f'SELECT * from "{self.resource_id}" WHERE "{dt_col}" > \'{date}\'::timestamp ORDER BY "{dt_col}"' 

    def form_dt_rng_sql_query(self, dt_col, start_date=None, end_date=None):
        start_end_date_exist = (start_date!=None, end_date!=None)

        func_map = {
            (False, False) : {'error' : 'A start and/or end date should be passed'},
            (True, True) : self.date_between(dt_col, start_date, end_date),
            (False, True) : self.date_less_than(dt_col, end_date),
            (True, False) : self.date_greater_than(dt_col, start_date),
        }

        sql = func_map[start_end_date_exist]

        if not isinstance(sql, str):
            self.raise_(sql['error'])

        return sql

    def query_API(self, params={}, start_date=None, end_date=None, dt_col=None, sql='', return_raw=False):
        ## Handling SQL queries
        if start_date or end_date:
            if sql != '':
                warnings.warn('The start and end date query will overwrite the provided SQL')

            if not dt_col:
                warnings.warn('If a start or end date has been provided the \'dt_col\' parameter must be provided')

            sql = self.form_dt_rng_sql_query(dt_col, start_date=start_date, end_date=end_date)
            params.update({'sql':sql})

        elif sql != '':
            params.update({'sql':sql})
            
        elif 'sql' in params.keys():
            params.pop('sql')

        ## Making the request
        r = self.NG_request(params=params)

        if return_raw == True:
            return r

        ## Checking and parsing the response
        r_json = r.json()
        self.check_request_success(r_json)

        df = pd.DataFrame(r_json['result']['records'])

        return df

    
if __name__ == "__main__":
    main()