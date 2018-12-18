import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def changeType(data):
    return_list = []
    for i in range(len(data)):
        temp = str(data[i])
        return_list.append(temp)
    return return_list
    
def counter(wt,ch):
    ct = 0
    for i in range(len(wt)):
        if wt[i] == ch:
            ct = ct + 1
    return ct

def getData(argument):
    #First let us gather all the data from various sources
    #Since we are interested in predicting only matches 
    #from round of 16, We are going to combine the data 
    #of all the matches before round of 16 to data (from kaggle)
    #as it does not includes matches of wc 2018

    #Data from football-data.co.uk
    raw_data = pd.read_excel("data/internationals.xlsx", sheet_name=None)
    raw_wcData = raw_data['World_Cup_2018']
    
    #Data from Kaggle    
    results = pd.DataFrame(pd.read_csv('data/results.csv'))
    results = results.drop(['city', 'country'], axis=1)

    # Obtained from https://us.soccerway.com/teams/rankings/fifa/?ICID=TN_03_05_01    
    ranking = pd.read_csv('data/fifa_rankings.csv')      
    
    #We will remove the matches of round of 16 
    #from data (football-data.co.uk)        
    if(argument == 1):
        wc18 = raw_wcData
    if(argument == 2):
        wc18 = raw_wcData[:-8]
    else:
        wc18 = raw_wcData
    hg = list(wc18['HGFT'])
    ag = list(wc18['AGFT'])
    ht = list(wc18['Home'])
    ht = changeType(ht)
    at = list(wc18['Away'])
    at = changeType(at)
    comp = list(wc18['Competition'])
    comp = changeType(comp)
    raw_dt = list(wc18['Date'])


    #Convert Timestamp into Date
    dt = []
    for i in range(len(raw_dt)):
        t = raw_dt[i]
        w = str(t.date())
        dt.append(w)
        
    #Merge two data         
    for row in itertools.izip_longest(dt,ht,at,hg,ag,comp):
        new_row = list(row)
        results = results.append(pd.Series(new_row, index=['date','home_team','away_team', 'home_score', 'away_score', 'tournament']), ignore_index=True)

    #Include Quater and semi final matches
    if(argument == 4):
        quat = pd.DataFrame(pd.read_csv('data/Quat_Matches.csv'))
        quat = quat.drop(['city', 'country'], axis=1)
        results = pd.concat((results, quat))
    if(argument == 5):
        quat = pd.DataFrame(pd.read_csv('data/Quat_Matches.csv'))
        quat = quat.drop(['city', 'country'], axis=1)
        results = pd.concat((results, quat))
        semi = pd.DataFrame(pd.read_csv('data/Quat_Matches.csv'))
        semi = semi.drop(['city', 'country'], axis=1)
        results = pd.concat((results, semi))
    results = results.reset_index(drop=True)


    #(H=Home, A=Away, D=Draw)
    #Adding new column for "winning_team" of the match
    winner = []
    for i in range(len(results['home_team'])):
        if results['home_score'][i] > results['away_score'][i]:
            winner.append(results['home_team'][i])
        elif results['home_score'][i] < results['away_score'][i]:
            winner.append(results['away_team'][i])
        else:
            winner.append('Tie')
    results['winning_team'] = winner

    # Adding new column for "goal difference" in matches
    results['goal_difference'] = np.absolute(results['home_score'] - results['away_score'])
    
    return results, ranking


def DataExplorer():
    ''' To understand the nature and various aspects of the data '''
    
    results, fixtures, ranks, match_wc18 = getData()

    #What is the win rate for home teams?
    no_of_matches = results.shape[0]
    no_of_features = results.shape[1] - 1
    wt = results['winning_team']
    no_of_HomeWins = counter(wt,1)
    no_of_Draws = counter(wt,0)
    no_of_AwayWins = counter(wt,2)
    
    #calculating win rate for home teams
    win_rate = (float(no_of_HomeWins)/(no_of_matches)) * 100
    
    print "no.of matches : ",no_of_matches
    print "no.of features : ",no_of_features
    print "no.of matches won by Home teams : ",no_of_HomeWins
    print "win rate : ",win_rate
    
    
    #plotting the data
    x = np.arange(3)
    yaxis = ['Home', 'Away', 'Draw']
    xaxis = [no_of_HomeWins,no_of_AwayWins,no_of_Draws]
    plt.bar(x,xaxis,align='center', alpha=0.5)
    plt.xticks(x,yaxis)
    plt.show()


def DataPreprocessor(results, wc_teams, arguments):
        
    # Filter the 'results' dataframe to show only teams in this(2018) years' world cup, from 1930 onwards
    df_teams_home = results[results['home_team'].isin(wc_teams)]
    df_teams_away = results[results['away_team'].isin(wc_teams)]
    df_teams = pd.concat((df_teams_home, df_teams_away))
    df_teams.drop_duplicates()
    print df_teams.count()
    
    # Loop for creating a new column 'year'
    year = []
    for row in df_teams['date']:
        year.append(int(row[:4]))
    df_teams['match_year'] = year
        
    # Slicing the dataset to see how many matches took place from 1930 onwards (the year of the first ever World Cup)
    df_teams30 = df_teams[df_teams.match_year >= 1930]
    
    #Drop all the unwanted columns
    #, 'goal_difference', 'home_score', 'away_score'
    if(arguments == 3 or arguments == 5):
        df_teams30 = df_teams30.drop(['date', 'tournament', 'match_year', 'goal_difference', 'away_score'], axis=1)
    if(arguments == 4):
        df_teams30 = df_teams30.drop(['date', 'tournament', 'match_year', 'away_score'], axis=1)
    if(arguments == 2):
        df_teams30 = df_teams30.drop(['date', 'tournament', 'match_year', 'home_score', 'away_score'], axis=1)
    #df_teams30 = df_teams30.drop(['date', 'tournament', 'match_year', 'away_score'], axis=1)
    df_teams30 = df_teams30.reset_index(drop=True)
    df_teams30.loc[df_teams30.winning_team == df_teams30.home_team, 'winning_team']= 1
    df_teams30.loc[df_teams30.winning_team == 'Tie', 'winning_team']= 0
    df_teams30.loc[df_teams30.winning_team == df_teams30.away_team, 'winning_team']= 2
    
    final = df_teams30    
    final = pd.get_dummies(final, prefix = ['home_team','away_team'], columns=['home_team','away_team'])
    
    return final
    
