from api.database.conn import get_conn, get_mongo_db
from api.monitoring.poto import get_poto
from api.utils.deepriceutils import get_sensor_collections

con = get_conn()
client, db = get_mongo_db()


class MonitoringManager:

    def collect_last(self, _poto_id):
        cursor = con.cursor()
        _poto = get_poto(_poto_id, cursor)
        _ref = _poto["ref"]
        cursor.close()
        return self.collact_details(_ref)

    def collact_details(self, ref):
        result = {}
        for collection_name in get_sensor_collections():
            collection = db[collection_name]

            latest_data = collection.find_one(
                {"ref": ref},
                sort=[("timestamp", -1)]
            )

            if latest_data and "data" in latest_data:
                raw_data  = latest_data["data"]
                formatted_data = {}
                for key, value in raw_data.items():
                    if isinstance(value, (int, float)):
                        num = float(value)
                        num = round(num, 2)
                        print(num)
                        formatted_data[key] = f"{num:.2f}"
                    else:
                        formatted_data[key] = value
                result[collection_name] = formatted_data
        return result