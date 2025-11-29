import asyncio
import requests
from dataclasses import dataclass, fields
from typing import List, Dict
import json
import os
from tqdm.asyncio import tqdm

class MyCustomError(Exception):
    """
    Custom exception for a specific error scenario.
    """
    pass

@dataclass
class Request_Data:
    product_url:str = "https://tiki.vn/api/v2/products/{}"

    review_url:str = "https://tiki.vn/api/v2/reviews?limit=20&include=comments,contribute_info,attribute_vote_summary&sort=score|desc,id|desc,stars|all&page=1&product_id={}&seller_id=1"
    
    request_headers = {
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'Host': "tiki.vn",
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0'
    }

    each_cate_url = "https://tiki.vn/api/personalish/v1/blocks/listings?limit=20&include=advertisement&aggregations=2&version=home-persionalized&category={}&page={}&urlKey={}"

class Crawl_TIKI_data(Request_Data):
    r"""
    level-0-category:
      - "house-life": 1883
      - "electricity-appliance": 1882
      - "laptop-computer": 1846
      - "woman-fashion": 931
      - "woman-slippers": 1703
    """

    LEVEL_0_CATEGORIES = [
        {
            "name": "house-life",
            "id": 1883
        },
        {
            "name": "electricity-appliance",
            "id": 1882
        },
        {
            "name": "laptop-computer",
            "id": 1846
        },
        {
            "name": "woman-fashion",
            "id": 931
        },
        {
            "name": "woman-slippers",
            "id": 1703
        },
        {
            "name": "beauty-health",
            "id": 1520
        }
    ]


    def __init__(self) -> None:
        super().__init__()
    
    @staticmethod
    def product_json_filter(json_data: dict):
        # processing specification field
        
        spec = {}
        for each_dict in json_data["specifications"]: # List[Dict]
            for each_attr in each_dict["attributes"]: # List[Dict]
                spec[each_attr["code"]] = each_attr["value"]
                    
        return_dict = {
                "product_id": json_data["id"],
                "product_name": json_data["name"],
                "price": json_data["price"],
                "review_count":json_data["review_count"],
                "brand_name":json_data["brand"]["name"],
                "seller_id": json_data["current_seller"]["store_id"],
                "seller_name":json_data["current_seller"]["name"],
                "stock":json_data["stock_item"]["qty"],
                "category_name": json_data["categories"]["name"],
                "category_id": json_data["categories"]["id"],
                "image_urls": [ele['small_url'] for ele in json_data["images"]],
                "thumbnail_url": json_data["thumbnail_url"],
                "specifications": spec,
                "description": json_data['description']
        }
        return return_dict
    
    @staticmethod
    def review_json_filter(json_data: dict):
        data = json_data['data']
        if isinstance(data, list) and len(data) != 0:
            return [ele['content'] for ele in data if ele['content'] != ""]
        else:
            raise MyCustomError

    def crawl_single_product(self,product_id:int):
        
        complete_product_url = self.product_url.format(product_id)    
        
        product_reponse = requests.get(
            url= complete_product_url,
            headers= self.request_headers
        )
        review_reponse = requests.get(
            url= self.review_url.format(product_id),
            headers= self.request_headers
        )

        if product_reponse.status_code == 200 and review_reponse.status_code == 200:
            
            try:
                filter_product_data = Crawl_TIKI_data.product_json_filter(json_data= product_reponse.json())
                filter_review_data = Crawl_TIKI_data.review_json_filter(json_data= review_reponse.json())
                return {
                    "product_data": filter_product_data,
                    "review": filter_review_data
                }
            
            except Exception as e:
                print(e)
                return False
        else:
            print(f'error single product, product_id: {product_id}')
            return False

    @staticmethod
    def _header_with_referer(parent_id:int,urlKey:str,**kwarg):
        kwarg.update(Referer = f'https://tiki.vn/{urlKey}/c{parent_id}')
        return kwarg
    
    def crawl_a_category(self,
                         parent_id:int,
                         cate_data_dict: dict, 
                         start_page:int = 1
                         )->List[int]:
        ids_list = []
        last_page = None
        
        
        first_url = self.each_cate_url.format(cate_data_dict["id"], start_page, cate_data_dict["url_path"])
        
        _request_headers = Crawl_TIKI_data._header_with_referer(
                parent_id = parent_id,
                urlKey = cate_data_dict["url_path"],
                **self.request_headers
        )
        
        first_response = requests.get(
            first_url, 
            headers = _request_headers
        )


        if first_response.status_code == 200:
            first_response_dict = first_response.json()
            
            first_page_ids = [each_prod["id"] for each_prod in first_response_dict["data"]]
            ids_list.extend(first_page_ids)
            
            last_page = first_response_dict["paging"]["last_page"]
        
        else:
            print('error with status code: ',first_response.status_code)
        
        if last_page is not None:
            for page_value in range(start_page+1, last_page//4):
                adjust_url = self.each_cate_url.format(cate_data_dict["id"], page_value, cate_data_dict["url_path"])
                
                response = requests.get(
                    adjust_url, 
                    headers = _request_headers
                )
                
                if (response.status_code == 200):
                    data = response.json()["data"]
                    current_page_ids = [each_prod["id"] for each_prod in data]
                    ids_list.extend(current_page_ids)
                else:
                    continue
        
        return ids_list

    
    def crawl_parent_categories(self, parent_id:int):
        r"""

        home-page:
            - level-0-category
        category-page:
            - level-1-category
                - level-2-category
        """
        parent_page_url = f"https://tiki.vn/api/v2/categories?include=children&parent_id={parent_id}"
        
        response = requests.get(parent_page_url, headers = self.request_headers)
            
        if (response.status_code == 200):
            cookies = response.cookies

            parent_categories = response.json()["data"]
            
            total_categories = []
            for each_dict in parent_categories:
                parent_data = {
                    "id":each_dict["id"] ,
                    "url_path":each_dict["url_key"], 
                    "status": 1
                }
                total_categories.append(parent_data)
                
                children_of_current_parent = each_dict.get("children", None)
                if children_of_current_parent is not None:
                    for child in children_of_current_parent:
                        child_data = {
                            "id":child["id"], 
                            "url_path":child["url_key"],
                            "status": 2
                        }
                        total_categories.append(child_data)
                        if len(child["children"]) != 0:
                            for sub_child in child["children"]:
                                sud_child_data = { 
                                    "id":sub_child["id"], 
                                    "url_path":sub_child["url_key"],
                                    "status": 3
                                }
                                total_categories.append(sud_child_data)
        else:
            print("bad request")
        return total_categories        
    
    def forward(self, parent_id: int, master_category_name:str):
        master_id_list = []
        database = []
        
        total_categories = self.crawl_parent_categories(parent_id= parent_id)
        
        for ith, each_category in tqdm(
                enumerate(total_categories), 
                desc=f"{master_category_name}: loop over total category",
                total = len(total_categories)
                ):
            id_list = self.crawl_a_category(parent_id = parent_id,cate_data_dict= each_category)
            
            master_id_list.extend(id_list)
            
            if ith == 3:
                break
        
        for ith, prod_id in tqdm(
                enumerate(master_id_list), 
                desc=f"{master_category_name}: loop over product id",
                total= len(master_id_list)
                ):
            result = self.crawl_single_product(product_id = prod_id)
            
            if not isinstance(result, bool):
                database.append(result)
                
            if len(database) > 20:
                break
                
        return {
            "master_category_name": master_category_name,
            "data": database
        }

async def main():
    obj = Crawl_TIKI_data()

    loop = asyncio.get_running_loop()

    tasks = [loop.run_in_executor(None, obj.forward, ele['id'], ele['name']) for ele in obj.LEVEL_0_CATEGORIES]

    master_data = await asyncio.gather(
        *tasks
    )
    
    
    with open(os.path.join(os.path.dirname(__file__),"master_data.json"), "w", encoding='utf-8') as fp:
        json.dump(master_data, fp, ensure_ascii=False, indent=4)

    
if __name__ == "__main__":
    asyncio.run(main())