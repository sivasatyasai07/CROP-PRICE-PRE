import pandas as pd
import json
from sqlalchemy.orm import Session
from app.models import RawMarketPrice
from typing import List, Dict, Any

def ingest_csv_data(file_path: str, db: Session) -> List[RawMarketPrice]:
    df = pd.read_csv(file_path)
    
    # Required/Expected columns: State/UT, District, Market, Commodity Group, Commodity, Date, Arrival Quantity, Min Price, Modal Price, Max Price
    column_mapping = {
        'State/UT': 'state',
        'State': 'state',
        'District': 'district',
        'Market': 'original_market',
        'Commodity Group': 'commodity_group',
        'Commodity': 'original_commodity',
        'Date': 'observation_date',
        'Arrival Quantity': 'arrival_quantity_raw',
        'Min Price': 'min_price_raw',
        'Modal Price': 'modal_price_raw',
        'Max Price': 'max_price_raw'
    }
    
    raw_records = []
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        
        raw_obj = RawMarketPrice(
            source="csv_upload",
            source_record_id=f"row_{idx+1}",
            state=str(row_dict.get('State/UT', row_dict.get('State', 'Andhra Pradesh'))),
            district=str(row_dict.get('District', '')),
            original_market=str(row_dict.get('Market', '')),
            original_commodity=str(row_dict.get('Commodity', '')),
            commodity_group=str(row_dict.get('Commodity Group', 'Vegetables')),
            observation_date=str(row_dict.get('Date', '')),
            arrival_quantity_raw=str(row_dict.get('Arrival Quantity', '')) if pd.notna(row_dict.get('Arrival Quantity')) else None,
            min_price_raw=str(row_dict.get('Min Price', '')) if pd.notna(row_dict.get('Min Price')) else None,
            modal_price_raw=str(row_dict.get('Modal Price', '')) if pd.notna(row_dict.get('Modal Price')) else None,
            max_price_raw=str(row_dict.get('Max Price', '')) if pd.notna(row_dict.get('Max Price')) else None,
            raw_payload=json.dumps({k: str(v) for k, v in row_dict.items() if pd.notna(v)})
        )
        raw_records.append(raw_obj)
        
    db.bulk_save_objects(raw_records)
    db.commit()
    return raw_records
