"""
testResults.py

This module:
- Fetches all test tables
- Creates and executes a SQL query that 
- Prints results table for selected student
- Visualises aforementioned results
"""

import os
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt

class Test:
    """
    class Test contains 3 functions:
    - test_query
    - test_summary
    - test_vis
    """

    def __init__(self):
        pass

    def test_query(self, sid):
        """
        This function:
        - Connects to CWDatabase.db
        - Creates a cursor allowing python to interact with SQLite
        - Shows tables in db
        - Creates and executes a query which joins all tables together
        - Asks for student number, stored as sid

        Args:
            sid: (int) of student's id
        
        Returns:
            Pandas df containing grade of all tests
        """

        conn = sqlite3.connect('CWDatabase.db') # Create connection

        query_1 = """
        SELECT m.research_id AS student_ID, m.grade AS mock, 
        COALESCE(t1.grade, 0) AS formative_1,
        COALESCE(t2.grade, 0) AS formative_2,
        COALESCE(t3.grade, 0) AS formative_3, 
        COALESCE(t4.grade, 0) AS formative_4, 
        COALESCE(s.grade, 0) AS summative
        FROM test_mock as m
        LEFT JOIN test_1 as t1 on m.research_id = t1.research_id
        LEFT JOIN test_2 as t2 on m.research_id = t2.research_id
        LEFT JOIN test_3 as t3 on m.research_id = t3.research_id
        LEFT JOIN test_4 as t4 on m.research_id = t4.research_id
        LEFT JOIN test_summ as s on m.research_id = s.research_id
        WHERE m.research_id = ?
        """
        results = pd.read_sql_query(query_1, conn, params=(sid,)) # Execute query
        conn.close() # Close connection

        return results, sid

    def test_summary(self, results, sid):
        """ 
        Generates a summary table of student's performance across all tests
        
        Args:
            results: df containig test scores and SID

        Retruns:
            summary: summary table containing results of sid + associated grade
            results    
        """
        # More friendly display names
        results = results.rename(columns = {
        'mock': 'Mock',
        'formative_1': 'Formative 1',
        'formative_2': 'Formative 2',
        'formative_3': 'Formative 3',
        'formative_4': 'Formative 4',
        'summative': 'Summative'
        })

        # Summary table 
        results.drop(columns= 'student_ID', inplace = True)
        summary = results.transpose()
        summary.rename(columns = {0: 'Grade'}, inplace = True)
        print('=' * 45)
        print(f'       Summary of Results of Student {sid}')
        print('=' * 45)
        for test, row in summary.iterrows():
            print(f'{test:>23} | {row['Grade']}') 

        return results, sid


    def test_vis(self, results, sid):
        """
        Function which visualises results of selected student
        Args:
            results: df containing test score and SID
            sid: student ID

        Returns:
            visualization of grades x tests of selected student
        """
        plt.figure(figsize= (10,7))
        plt.plot(results.columns, results.values[0], marker= 'o')
        plt.xlabel('Test Type')
        plt.ylabel('Grade')
        plt.title(f'Student {sid} Report Card')
        plt.xticks(rotation = 45)
        plt.grid(True)
        plt.show()

def main(sid = None):
    """
    Main funciton containing validators

    Args:
        - sid (int): student id (default set to None)
    """

    if sid == None: 
        sid = int(input('Please enter the student\'s ID: '))
    t = Test()
    results, sid = t.test_query(sid)
    if results.empty: # sid validator
        print(f'Student {sid} is invalid, please select a valid student ID')
    else:
        results, sid = t.test_summary(results, sid)
        t.test_vis(results, sid)

def test_module():
    """Function tests the main functions in Test class"""
    t = Test()
    
    # Test test_query with valid student
    results, sid = t.test_query(101)
    assert isinstance(results, pd.DataFrame), "test_query failed"
    
    # Test test_query with invalid student
    results_invalid, _ = t.test_query(99999)
    assert results_invalid.empty, "invalid student should return empty"
    
    # Test test_summary
    results, sid = t.test_query(101)
    if not results.empty:
        summary_results, _ = t.test_summary(results, sid)
        assert 'Mock' in summary_results.columns, "test_summary failed"
    
    print("All tests passed!")


if __name__=="__main__":
    main()



