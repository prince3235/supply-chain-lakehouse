from pyspark.sql import DataFrame
from pyspark.sql.functions import col

class SilverValidator:
    def __init__(self, constraints: dict = None):
        """
        :param constraints: Dictionary mapping columns to their validation constraints.
                            e.g. {"product_id": {"not_null": True, "type": "int"}}
        """
        self.constraints = constraints or {}

    def validate(self, df: DataFrame) -> tuple[DataFrame, DataFrame]:
        """
        Evaluates the dataframe against the constraints.
        Returns a tuple: (valid_df, invalid_df)
        """
        if not self.constraints:
            # If no constraints, all records are valid, invalid is empty
            empty_schema = df.schema
            return df, df.sparkSession.createDataFrame([], empty_schema)
            
        valid_condition = None
        
        for column, rules in self.constraints.items():
            if rules.get("not_null"):
                col_cond = col(column).isNotNull()
                if valid_condition is None:
                    valid_condition = col_cond
                else:
                    valid_condition = valid_condition & col_cond
                    
            # In a real system, you could add range checks, regex, etc.
            
        if valid_condition is None:
            empty_schema = df.schema
            return df, df.sparkSession.createDataFrame([], empty_schema)
            
        valid_df = df.filter(valid_condition)
        invalid_df = df.filter(~valid_condition)
        
        return valid_df, invalid_df
