"""
UnderPerforming.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

class Underperform:
    """ 
    Filters, analyses and visualises underperforming students, this class has 7 
    functions:
    - underperf_query
    - test_filter
    - test_stats
    - underperf_func
    - underperf_vis
    - quality_check
    - correlation_analysis
    
    """
    def __init__(self):
        pass

    def underperf_query(self):
        """
        This function creates and executes an SQLite query which merges tables
        to create a pandas df with all grades. Even after applying fillna(),
        students with no attempts on a test will have null value as a left
        join is used. Coalesce function is used to impute null values with 0.

        Args:
            NONE
        
        Returns:
            results (pd df): df containing students' grades of all tests
        """
        conn = sqlite3.connect('CWDatabase.db')
        cursor = conn.cursor()


        all_tests_query = """
        SELECT m.research_id AS student_ID, m.grade AS mock,
        t1.grade AS formative_1,
        t2.grade AS formative_2,
        t3.grade AS formative_3, 
        t4.grade AS formative_4, 
        s.grade AS summative
        FROM test_mock as m
        LEFT JOIN test_1 as t1 on m.research_id = t1.research_id
        LEFT JOIN test_2 as t2 on m.research_id = t2.research_id
        LEFT JOIN test_3 as t3 on m.research_id = t3.research_id
        LEFT JOIN test_4 as t4 on m.research_id = t4.research_id
        LEFT JOIN test_summ as s on m.research_id = s.research_id
        """

        results = pd.read_sql_query(all_tests_query, conn) # Executes query
        conn.close()

        results = results.rename(
            columns={
                'student_ID': 'Student ID',
                'mock': 'Mock',
                'formative_1': 'Formative 1',
                'formative_2': 'Formative 2',
                'formative_3': 'Formative 3',
                'formative_4': 'Formative 4',
                'summative': 'Summative',
            })

        return results


    def test_filter(self, results):
        """ 
        This function:
        - removes students who haven't attempted a significant amount of
        formative tests
        
        Args:
            results (pd df): df containing the grades across all tests for every
                            student
        
        Returns:
            results (pd df): cleaned results after filtering
        
        """
        formative_cols = ['Formative 1', 'Formative 2', 'Formative 3', 
                          'Formative 4']
        
        # Remove students who have completed less than 3 tests
        results.dropna(subset = formative_cols, thresh = 3, inplace = True)
        results.fillna(0, inplace = True)
        return results


    def test_stats(self, results):
        """ 
        Calculates and prints the 1st and 2nd moment of all tests
        Assigns z-scores to each summative score
        Returns results with added z-score column

        Methodology: 
            As the symmetry and tailedness of the summative test's results
            are close to ideal metrics of normal distribution, z-score 
            transformation are reliable to interpret scores, hence, gauge
            underperformance.

        Args: 
            results(pd df)
        
        Returns:
            - results (pd df): df appended with summative zscore column
            - test_summary (pd df): selected test performance of student vs avg
            
        """

        test_cols = ['Mock', 'Formative 1', 'Formative 2', 'Formative 3',
                      'Formative 4', 'Summative']
        mean = results[test_cols].mean() # Calculates mean
        sd = results[test_cols].std() # Calculates sd

        results['Summative_zscore'] = round(
            (results['Summative'] - mean['Summative']) / sd['Summative'], 1)

        test_summary = pd.concat([mean, sd], axis=1)
        test_summary.columns = ['Mean Score', 'Standard Deviation']

        print('==============================================')
        print('          Statistical Summary of Tests')
        print('==============================================')
        print(round(test_summary,0))
        print(' ' *3,'.' *46)

        print(' ' *3, f'  The Skewness of the Summative test is: {results["Summative"].skew():.2f}')
        print(' ' *3,f'  The Kurtosis of the Summative test is: {results["Summative"].kurtosis():.2f}')
        print(' ' *3,'.' *46)

        return results


    def underperf_func(self, results):
        """
        This function selects underperforming students (zscore < -1)
        returns a df of students sorted by lowest score

        Args:
            results (pd df)
        
        Returns:
            underperforming (pd df): df containing underperforming students 
            sorted by lowest grade first
        """

        # Filter students with z-score of less than -1
        underperforming = results[results['Summative_zscore'] < -1]
        # Sort by worst performance
        underperforming = underperforming.sort_values(by='Summative_zscore',
                                                       ascending=True)

        print(f'There are a total of {underperforming["Student ID"].count()} underperforming students.')

        return underperforming

    def underperf_table(self, underperforming):
        """
        This function prints a table of underperforming students and highlights
        the lowest formative score for each student

        Args:    
            underperforming(pd df)
        
        Returns:
            table
        """
        formative_cols = ['Formative 1', 'Formative 2', 'Formative 3', 'Formative 4']
        
        print('=' * 65)
        print('Student ID | Form 1 | Form 2 | Form 3 | Form 4')
        print('=' * 65)

        for _, row in underperforming.iterrows():
            scores = row[formative_cols]
            lowest = scores.min()
            
            output = [f"{int(s)}*" if s == lowest else str(int(s)) for s in scores]
            print(f"{int(row['Student ID']):<10} | {output[0]:>6} | {output[1]:>6} | {output[2]:>6} | {output[3]:>6}")

        print('=' * 65)
        print('* = lowest formative score')

    def underperf_vis(self, underperforming):
        """
        Visualises underperforming students' formative grades as a heatmap.

        Args:
            underperforming(pd df)

        Returns:
            Heatmap showing all students' formative performance
        """
        formative_cols = ['Formative 1', 'Formative 2', 'Formative 3',
                           'Formative 4']

        # Assign students and the data columns
        students = underperforming['Student ID']
        data = underperforming[formative_cols].values

        fig, ax = plt.subplots(figsize=( 10, 12))
        # Map data into heatmap and configure colour, size
        hmap = ax.imshow(data, cmap= 'Spectral', aspect='auto')
        plt.colorbar(hmap, label='Grade')

        ax.set_xticks(np.arange(len(formative_cols)))
        ax.set_yticks(np.arange(len(students)))
        ax.set_xticklabels(formative_cols)
        ax.set_yticklabels(students)
        ax.set_xlabel('Test Type')
        ax.set_ylabel('Student ID')
        ax.set_title('Underperforming Students - Formative Results')

        for i in range(len(students)):
            for j in range(len(formative_cols)):
                ax.text(j, i, int(data[i, j]), color = 'black', weight = 'bold')

        plt.tight_layout()
        plt.show()

    def quality_check(self, results):
        """
        Shows statistical features of earlier tests and adds average score 
        per student.

        Args:
            results(pd df)
        
        Returns:
            - tests_quality(pd df): df containing skew and kurtosis of each test
            - printed summary guide to interpret results
        """
        tests = ['Mock', 'Formative 1', 'Formative 2', 
                 'Formative 3', 'Formative 4']

        skew = round(results[tests].skew(), 2)
        kurt = round(results[tests].kurtosis(), 2)
        tests_quality = pd.concat([skew, kurt],
                                   axis=1, keys =['Skewness', 'Kurtosis'])
        
        
        # Print test quality table
        print(' ' *7 ,'='*60)
        print(' ' *7, f'{'Test':<15} | {'Skewness':>15} | {'Kurtosis':>15}')
        print(' ' *7 ,'='*60)
        for exam, row in tests_quality.iterrows():
            print(' '*7, 
                  f'{exam:<15} | {row['Skewness']:>15} | {row['Kurtosis']:>15}')
        
        
        # Interpretation for results
        print(
            f"""
        {'='*80}
        Skewness Analysis:
        --------------------
            Zero: test has appropriate difficulty
                  Most students scored average, equal number scoring very high and low

        Positive: test was likely difficult
                  Most students scored poorly, only a few achieved high scores

        Negative: test was likely easy
                  Most students scored well, only a few scored very low
        {'='*80}
        Kurtosis Analysis:
        --------------------
         Mesokurtic (≈3): Moderate number of outliers, well-balanced scores

        Leptokurtic (>3): Large number of outliers, heavy cluster around the mean

        Platykurtic (<3): Fewer outliers, student scores are more spread out
        {'='*80}
        
        """)
        


        return round(tests_quality, 2)

    def correlation_analysis(self, results):
        """
        This function analyzes correlation between formative average and 
        summative performance using Pearson's correlation coefficient.

        Cohen's guidelines and adaptation for social sciences is used here where 
        lower correlation thresholds are given more weights relative to natural 
        sciences.
        This is due to factors such as human variability and system complexity

        Interpretation:

        - r < 0.3: Weak effect
        - 0.3 < r < 0.5: Moderate positive effect
        - r > 0.5: Strong corellation

        Args:
            results (pd df)
        
        Results:
            - correlation: df showing correlatiion between average of formative 
            and summative tests
            - print conditional statement to interpret results
        """

        tests = ['Mock', 'Formative 1', 'Formative 2',
                  'Formative 3', 'Formative 4']
        results['formative_avg'] = results[tests].mean(axis=1)

        correlation = results['formative_avg'].corr(results['Summative'])

        print('==============================================')
        print('   Correlation: Formative Avg vs Summative')
        print('==============================================')
        print(f'Correlation coefficient: {correlation:.3f}')

        if correlation >= 0.5:
            print('Strong positive correlation')
        elif correlation > 0.3:
            print('Moderate positive correlation')
        else:
            print('Weak correlation')

        print('==============================================')



def main():
    u = Underperform()
    results = u.underperf_query()
    results = u.test_filter(results)
    results = u.test_stats(results)
    print(' ')
    underperforming = u.underperf_func(results)
    u.underperf_table(underperforming)
    u.underperf_vis(underperforming)
    print(' ')
    u.correlation_analysis(results)
    u.quality_check(results)

def test_module():
    """Function tests the main functions in Underperform class"""
    u = Underperform()
    
    # Test underperf_query
    results = u.underperf_query()
    assert not results.empty, "underperf_query failed"
    assert 'Student ID' in results.columns, "column rename failed"
    
    # Test test_filter
    filtered = u.test_filter(results)
    assert filtered.isnull().sum().sum() == 0, "test_filter failed"
    
    # Test test_stats
    stats_results = u.test_stats(filtered)
    assert 'Summative_zscore' in stats_results.columns, "test_stats failed"
    
    # Test underperf_func
    underperforming = u.underperf_func(stats_results)
    assert isinstance(underperforming, pd.DataFrame), "underperf_func failed"
    
    print("All tests passed!")


if __name__ == "__main__":
    main()
