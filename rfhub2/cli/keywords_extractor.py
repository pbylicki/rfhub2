from collections import Counter
from datetime import datetime
from xml.etree import ElementTree as et

input_file = r"F:\Docs\Desktop\rfhub2\tests\fixtures\statistics\output.xml"
FMT = "%Y%m%d %H:%M:%S.%f"
FMT2 = "%Y-%m-%d %H:%M:%S.%f"

# execution_time = et.parse(input_file).getroot().attrib.get('generated')
execution_time = datetime.strftime(
    datetime.strptime(et.parse(input_file).getroot().attrib.get("generated"), FMT), FMT2
)

xml_keywords = et.parse(input_file).findall(".//kw")

keywords = [
    {
        "name": ".".join(
            (xml_keyword.attrib.get("library"), xml_keyword.attrib.get("name"))
        ),
        "elapsed": int(
            1000
            * (
                datetime.strptime(
                    max(
                        tag.attrib.get("endtime")
                        for tag in xml_keyword.iter()
                        if tag.tag == "status"
                    ),
                    FMT,
                )
                - datetime.strptime(
                    min(
                        tag.attrib.get("starttime")
                        for tag in xml_keyword.iter()
                        if tag.tag == "status"
                    ),
                    FMT,
                )
            ).total_seconds()
        ),
    }
    for xml_keyword in xml_keywords
    if xml_keyword.attrib.get("library") is not None
]

# times_used = Counter(keyword['name'] for keyword in keywords)

statistics = [
    {
        "collection": k.split(".")[0],
        "keyword": k.split(".")[1],
        "execution_time": execution_time,
        "times_used": v,
        "total_elapsed": 0,
        "min_elapsed": None,
        "max_elapsed": None,
    }
    for k, v in Counter(keyword["name"] for keyword in keywords).items()
]

for stat in statistics:
    for keyword in keywords:
        if keyword["name"] == ".".join((stat["collection"], stat["keyword"])):
            stat["total_elapsed"] += keyword["elapsed"]
            if not stat["min_elapsed"] or keyword["elapsed"] < stat["min_elapsed"]:
                stat["min_elapsed"] = keyword["elapsed"]
            if not stat["max_elapsed"] or keyword["elapsed"] > stat["max_elapsed"]:
                stat["max_elapsed"] = keyword["elapsed"]


print(statistics)

# for k in statistics:
#     print(f'''INSERT INTO "statistics" ("collection", "keyword", times_used, total_elapsed_time) VALUES('{k["name"].split('.')[0]}', '{k["name"].split('.')[1]}', {k["times_used"]}, {k["total_elapsed_time"]});''')
