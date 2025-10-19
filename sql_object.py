from dataclasses import dataclass


@dataclass
class SqlObject:

    upsert_user_profile_query: str = """
        INSERT INTO user_data
        (user_id, prdcer_dataset, prdcer_lyrs, prdcer_ctlgs, draft_ctlgs)
            VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (user_id) DO UPDATE
        SET prdcer_dataset = $2, 
            prdcer_lyrs = $3, 
            prdcer_ctlgs = $4, 
            draft_ctlgs = $5; 
    """

    fetch_population_data_query: str = """
        SELECT 
            "Main_ID",
            "Grid_ID", 
            "Level",
            "Population_Count",
            "Male_Population",
            "Female_Population", 
            "Population_Density_KM2",
            "Median_Age_Total",
            "Median_Age_Male",
            "Median_Age_Female",
            density,
            geometry,
            ST_Distance(geometry::geography, ST_MakePoint($2, $1)::geography) as distance
        FROM schema_marketplace.population_all_features_v12
        WHERE ST_DWithin(
            geometry::geography,
            ST_MakePoint($2, $1)::geography,
            $3
        )
        ORDER BY distance
        LIMIT 1000;
    """
    
    fetch_income_data_query: str = """
        SELECT 
            income,
            geometry,
            low_income_score,
            medium_income_score,
            high_income_score,
            ST_Distance(geometry::geography, ST_MakePoint($2, $1)::geography) as distance
        FROM schema_marketplace.area_income_all_features_v12
        WHERE ST_DWithin(
            geometry::geography,
            ST_MakePoint($2, $1)::geography,
            $3
        )
        ORDER BY distance
        LIMIT 1000;
    """
    

