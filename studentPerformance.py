"""
studentPerformance.py
"""

import os
import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt




class Performance:
    """
    class Performance contains 3 functions:
        - performance_query
        - summary_func
        - summary_vis
    """
    
    def __init__(self):
        pass
    
    
    def performance_query(self, test_id, sid):
        """
        Retrieves test results for all students and specific student.
        
        Args:
            - test_id (str): Test identifier ('m', 'f1', 'f2', 'f3', 'f4', 's')
            - sid (int): Student research ID
        
        Returns:
            full_results, student_results, sid, test_name
        """
        test_dict = {
            'm': 'test_mock',
            's': 'test_summ',
            'f1': 'test_1',
            'f2': 'test_2',
            'f3': 'test_3',
            'f4': 'test_4'
        }

        test_name = {
            'm': 'Mock Test',
            's': 'Summative Test',
            'f1': 'Formative 1',
            'f2': 'Formative 2',
            'f3': 'Formative 3',
            'f4': 'Formative 4'
        }

        # Connect to databse
        conn = sqlite3.connect('CWDatabase.db')      
        table = test_dict[test_id] 
        display_name = test_name[test_id]

        # SQLite3 query
        query = f"""
        SELECT *
        FROM {table}
        """

        full_results = pd.read_sql_query(query, conn) # Executes query

        # Drops unnecessary columns
        full_results.drop(columns=['started_on', 'completed'], inplace=True)
        student_results = full_results[full_results['research_id'] == sid].drop(columns='research_id')
        full_results.drop(columns='research_id', inplace=True)

        conn.close() # Close connection

        return full_results, student_results, sid, display_name
    
    def summary_func(self, full_results, student_results, sid, test_name):
        """
        Creates a summary table which contains the student's and average
        score achieved in the selected test
        
        Args: 
        - full_results (pd df):  contains all student's results
        - student_results (pd df): containing selected student scores
        - sid (int): variable storing selected student
        - test_id (str): variable storing selected test

        Returns:
        - student_summary: summary table of sid vs average performance
        """
        # Calculate averages
        avg_summary = round(full_results.mean(), 0).astype(int)
        
        # Transpose student results 
        student_summary = student_results.transpose()
        
        # Rename and add columns
        student_summary.rename(columns={student_summary.columns[0]: 'mark'}, 
                               inplace = True)
        student_summary['avg_mark'] = avg_summary.values
        student_summary['difference'] = (student_summary['mark'] - student_summary['avg_mark'])
        
        # Print table of summary
        print('=' * 65)
        print(f'        Summary of Results for Student {sid} for {test_name}')
        print('=' * 65)
        print(f"{'':<15} | {'Student':>10} | {'Average':>10} | {'Difference':>10}")
        print('-' * 65)
        
       
        for quest, row in student_summary.iterrows():
            print(f"{quest.capitalize():<15} | {row['mark']:>10} | {row['avg_mark']:>10.0f} | {row['difference']:>10.0f}")
        
        print('=' * 65)
        
        return student_summary

        
    def performance_vis(self, sid, student_summary, test_name):
        """
        Visualises score results of student and test average
        
        Args:
            - student_summary (pd df): df containing student + avg results  
            - sid (int): variable storing selected student
            - test_name (str): variable storing selected test
        
        Returns:
            Barplot chart visualizing student_summary results
        """
        vis = student_summary.transpose()
        x_names = vis.columns.str.capitalize() # More appealing col names

        y_axis_stu = vis.iloc[0] # Extract student {sid} scores
        y_axis_avg = vis.iloc[1] # Extract avg student scores

        width = 0.35 # bar width
        x = np.arange(len(x_names)) # array for x-axis
        fig, ax = plt.subplots(figsize=(10,5))



        bars_stu = plt.bar(x + width/2, y_axis_stu, 
                           width = width, label= 'Student', color = 'purple')
        bars_avg =plt.bar(x - width/2, y_axis_avg,
                           width = width, label= 'Average', color = 'gold')


        plt.xticks(x, x_names, rotation= 45) # ensure xlabels are from col names
        plt.ylabel('Score')
        plt.title(f'Student {sid} vs Average Scores')
        plt.legend()
        plt.tight_layout()
        plt.show()

        


def main(test_id= None, sid= None):
    """
    main function of module containing validators

    Args:
        - test_id (str): test identifier (default set to none.
                        If none is true, prints guide to selecting test)
        - sid (int): unique student identification (default set to none)
    """
    test_name = {
            'm': 'Mock Test',
            's': 'Summative Test',
            'f1': 'Formative 1',
            'f2': 'Formative 2',
            'f3': 'Formative 3',
            'f4': 'Formative 4'
        }

    valid_tests = ['m', 'f1', 'f2', 'f3', 'f4', 's'] # test validator
    
    p2 = Performance()
    

    if test_id is None:
        print('Please select one of the following tests')
        print(test_name)
        test_id = input('Please enter a test_id: ')
        if test_id not in valid_tests: # test validator
            print(f'Error: "{test_id}" is not a valid test ID')
            return
    

    
    if sid is None:
        sid = int(input('Please enter the student id: '))
     
    full_results, student_results, sid, test_name = p2.performance_query(test_id, sid)

    if student_results.empty: # sid validator
        print(f'Error: No results found for "Student {sid}" on {test_name}')
    else:
        student_summary = p2.summary_func(full_results, student_results, 
                                          sid, test_name)
        p2.performance_vis(sid, student_summary, test_name )

def test_module():
    """Function tests the main functions in Performance class"""
    p = Performance()
    
    # Test performance_query with valid inputs
    full_results, student_results, sid, test_name = p.performance_query('m', 101)
    assert not full_results.empty, "performance_query failed"
    assert test_name == 'Mock Test', "test_name mapping failed"
    
    # Test summary_func
    if not student_results.empty:
        summary = p.summary_func(full_results, student_results, sid, test_name)
        assert 'mark' in summary.columns, "summary_func failed"
        assert 'difference' in summary.columns, "difference calculation failed"
    
    print("All tests passed!")


if __name__ == '__main__':
    main()