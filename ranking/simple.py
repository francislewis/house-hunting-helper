from databases.sqlite import SQLiteDatabase
from ranking import Ranking
from tqdm import tqdm

class SimpleRank(Ranking):
    """
    The ranking algorithm is to take relative position of the entry based on a mean of the relative price
    and commute time. Then certain things increase the ranking slightly (e.g. bills included) or decrease
    it (e.g. unfurnished)
    :return:
    """
    def __init__(self):
        # Create db object
        db = SQLiteDatabase()

        # Get all ids and
        all_ids = list(db.get_all_property_ids())
        assert len(all_ids) == db.get_entry_count()
        total_entries = len(all_ids)

        for id in tqdm(all_ids):
            property_details = db.fetch_data_by_id(id)
            rank = (db.get_position(id)['price']/total_entries)

            if property_details['bills_included'].lower() == 'True':
                rank = rank * 1.1

            if property_details['furnishing'].lower() == 'unfurnished':
                rank = rank * 0.95

            if property_details['room_type'].lower() == 'studio flat':
                rank = rank * 0.85

            rank = round(rank, 2)

            db.update_column_by_id(id=id, column_name='ranking', new_value=rank)
