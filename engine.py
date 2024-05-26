import http.client
import json

def find(obj: json, target: str):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == target:
                return value
            else:
                result = find(value, target)
                if result is not None:
                    return result
    elif isinstance(obj, list):
        for item in obj:
            result = find(item, target)
            if result is not None:
                return result
    return None


def intify(input_var):
    try:
        return int(input_var)
    except ValueError:
        return None


def send_request(sectionCodes):
    sectionCodes = intify(sectionCodes)
    conn = http.client.HTTPSConnection("api.peterportal.org")

    headers = {
        'Content-Type': "application/json",
    }

    conn.request("GET", f"/rest/v0/schedule/soc?term=2024%20Fall&sectionCodes={sectionCodes}", headers=headers)
    res = conn.getresponse()
    data = res.read()

    data_jsonify = json.loads(data)

    sectionType: str = find(data_jsonify, "sectionType")
    courseTitle: str = find(data_jsonify, "courseTitle")
    courseTitleTotal = sectionType.upper() + " " + courseTitle

    sectionTimeDays: str = find(data_jsonify, "days")
    sectionTimeTime: str = find(data_jsonify, "time")
    sectionTime = sectionTimeDays + " " + sectionTimeTime

    maxCapacity = intify(find(data_jsonify, "maxCapacity"))
    totalEnrolled = intify(find(data_jsonify, "totalEnrolled"))
    status = find(data_jsonify, "status")

    whetherFull: bool = (maxCapacity - totalEnrolled) <= 0

    return courseTitleTotal, sectionTime, maxCapacity, totalEnrolled, status, whetherFull