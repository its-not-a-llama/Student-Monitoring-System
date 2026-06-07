"""
CWPreprocessing.py


This module:
- Imports CSV files
- Cleans and preprocesses the data
- Exports test data into tables inside an SQlite DB file
"""

# Import needed libraries
import os
import pandas as pd
import numpy as np
import sqlite3

# List which stores names of all test files
test_list = [
    'TestResult/Formative_Mock_Test.csv', 
    'TestResult/Formative_Test_1.csv', 
    'TestResult/Formative_Test_2.csv', 
    'TestResult/Formative_Test_3.csv',
    'TestResult/Formative_Test_4.csv',
    'TestResult/SumTest.csv'
]


class Preprocess:
    """
    Preprocess class contains 3 functions:
    - load_csv
    - clean_data
    - sql_export
    """

    def __init__(self):
        pass

    def load_csv(self, test_list):
        """
        Reads csv files and returns six dataframes

        Args:
            test_list: list containing csv files to be imported
        
        Returns:
            Pandas df corresponding to item in list 
        """
        test_mock = pd.read_csv(test_list[0])
        test_1 = pd.read_csv(test_list[1])
        test_2 = pd.read_csv(test_list[2])
        test_3 = pd.read_csv(test_list[3])
        test_4 = pd.read_csv(test_list[4])
        test_summ = pd.read_csv(test_list[5])

        return test_mock, test_1, test_2, test_3, test_4, test_summ

    def clean_data(self, test):
        """
        This function:
        - creates a copy of test, stored as test_clean
        - drops unwanted columns
        - convert columns to appropriate data types
        - standardises grade and question results
        - renames columns to snakecase
        - returns cleaned version of raw data

        Args:
            test: pd df of test
                    
        Returns:
            cleaned dataframe
        """

        test_clean = test.copy()

        # Drop unwanted columns
        dropped_cols = ['State', 'Time taken']
        test_clean.drop(columns = dropped_cols, inplace = True, 
                        errors = 'ignore')


        # Convert datetime columns
        date_cols = ['Started on', 'Completed']
        for col in date_cols:
            if col in test_clean.columns:
                 test_clean[col] = pd.to_datetime(
                     test_clean[col],  errors = 'coerce', format = 'mixed')

        # Convert numeric columns and fill N/A value with 0
        for col in test_clean.columns:
            if col not in date_cols:
                test_clean[col] = pd.to_numeric(test_clean[col], 
                                                errors = 'coerce').fillna(0)

        # Slashed Cols Q1 / 100
        slashed_cols = [col for col in test_clean.columns if '/' in col]
        for col in slashed_cols:
            # Standardisation
            denominator = int(col.split('/')[-1]) # Scores extractor
            numerator = test_clean[col]
            test_clean[col] = ((numerator/denominator) * 10000).astype(int)
            # Slashed cols renaming to snake_case
            renamed_cols = col.split('/')[0].strip().replace(' ', '').lower()
            test_clean = test_clean.rename(columns = {col: renamed_cols})



        # Rename non-slashed numeric columns
        for col in test_clean.columns:
            renamed_cols2 = col.replace(' ', '_').lower()
            test_clean = test_clean.rename(columns = {col: renamed_cols2})
        
        # Keep highest score first
        test_clean = test_clean.sort_values(['research_id', 'grade'], 
                                            ascending = [True, False])
        test_clean = test_clean.drop_duplicates(subset= 'research_id', 
                                                keep='first')

        return test_clean

    def sql_export(self, clean_test, table):
        """
        This function:
        - creates a db file
        - exports cleaned dfs into sql files and adds them to db file

        Args:
            clean_test: df, cleaned df of raw data       
            table: dictionary containing table names to be assigned from cleaned
            df
        
        Returns:
            table(s) to be stored inside db file (CWDatabase.db)
        """
        conn = sqlite3.connect('CWDatabase.db')
        
        for df, name in zip(clean_test, table):
            df.to_sql(name, conn, if_exists = 'replace', index= False)

        conn.close()


def main():
    """
    Main function
    """
    p = Preprocess()

    # Load CSVs
    test_mock, test_1, test_2, test_3, test_4, test_summ = p.load_csv(test_list)

    # Clean all dataframes 
    clean_test_mock = p.clean_data(test_mock)
    clean_test_1 = p.clean_data(test_1)
    clean_test_2 = p.clean_data(test_2)
    clean_test_3 = p.clean_data(test_3)
    clean_test_4 = p.clean_data(test_4)
    clean_test_summ = p.clean_data(test_summ)

    clean_test = [
        clean_test_mock, clean_test_1, clean_test_2,
        clean_test_3, clean_test_4, clean_test_summ
    ]

    table = ['test_mock', 'test_1', 'test_2', 'test_3', 'test_4', 'test_summ']

    # Export to SQL
    p.sql_export(clean_test, table)

def test_module():
    """
    This function tests main functions in Preprocess class
    """

    p = Preprocess()
    
    # Test load_csv
    dfs = p.load_csv(test_list)
    assert len(dfs) == 6, "load_csv failed"
    
    # Test clean_data
    clean = p.clean_data(dfs[0])
    assert 'State' not in clean.columns, "clean_data failed"
    assert clean['research_id'].duplicated().sum() == 0, "duplicates remain"
    
    # Test sql_export
    clean_all = [p.clean_data(df) for df in dfs]
    tables = ['test_mock', 'test_1', 'test_2', 'test_3', 'test_4', 'test_summ']
    p.sql_export(clean_all, tables)
    assert os.path.exists('CWDatabase.db'), "sql_export failed"
    
    print("All tests passed!")


if __name__ == "__main__":
    main()
