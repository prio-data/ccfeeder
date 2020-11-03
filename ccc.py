import sys
import os
import json
from typing import List
from datetime import date
import logging

import pydantic
import fiona
import fire
import topojson
import requests

class Config(pydantic.BaseModel):
    url: str
    username: str
    password: str
    keep: List[str] = ["CNTRY_NAME","GWCODE","ISOAL2"]

def main(shapefile="shapes/cshapes.shp",year = None,alpha = .01,beta = .1,conf="config.json",debug=True):
    with open(conf) as f:
        config = Config(**json.load(f))

    if debug:
        logging.basicConfig(level = logging.INFO)

    if year is None:
        logging.warning("No year provided, using current year")
        year = date.today().year

    if not os.path.exists("cache/topo.json"):
        logging.info("Creating topology data")
        logging.info("Reading country data from file")
        countries = [*fiona.collection(shapefile)]
        maxyear = max([c["properties"]["GWEYEAR"] for c in countries])

        exists = lambda c: c["properties"]["GWSYEAR"]<=year and c["properties"]["GWEYEAR"]==maxyear
        countries = [c for c in countries if exists(c)] 

        for c in countries:
            c["properties"] = {k:v for k,v in c["properties"].items() if k in config.keep}

        logging.info("Topologizing")
        countries = topojson.Topology(countries)

        logging.info("Simplifying")
        topologies = {}
        for name,metric in (("large",alpha),("small",beta)):
            topologies[name] = json.loads(countries.toposimplify(metric).to_geojson())

        with open("cache/topo.json","w") as f:
            json.dump(topologies,f)
    else:
        logging.warning("Using cache")
        with open("cache/topo.json") as f:
            topologies = json.load(f)
    
    with requests.Session() as client:
        handshake = client.get(config.url)
        logging.info("Authenticating")
        login = client.post(os.path.join(config.url,"accounts","login")+"/",{
                "username":config.username,
                "password":config.password,
                "csrfmiddlewaretoken": client.cookies["csrftoken"]
            })
        assert login.status_code == 200

        logging.info("Uploading")
        url = os.path.join(config.url,"api","updatecountries")+"/"

        headers = {
                "Content-Type":"application/json",
                "X-CSRFToken":client.cookies["csrftoken"]
            }
        r = client.post(url, json=topologies, headers=headers)
        print(r.content)
    logging.info("Done!")

if __name__ == "__main__":
    fire.Fire(main)
