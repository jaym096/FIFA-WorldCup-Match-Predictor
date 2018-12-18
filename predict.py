import pandas as pd

#============== First Round ===================#
def predict_firstRound(ranking, final_dataset, logreg):
    
    # Obtained from https://fixturedownload.com/results/fifa-world-cup-2018
    fixtures = pd.read_csv('data/fixtures.csv')

    #List for storing the group stage games
    pred_set = []
    
    # Add columns with ranking position of each team
    fixtures.insert(1, 'first_position', fixtures['Home Team'].map(ranking.set_index('Team')['Position']))
    fixtures.insert(2, 'second_position', fixtures['Away Team'].map(ranking.set_index('Team')['Position']))
    
    # We only need the group stage games, so we have to slice the dataset
    fixtures = fixtures.iloc[:48, :]
    
    # Loop to add teams to new prediction dataset based on the ranking position of each team
    for index, row in fixtures.iterrows():
        if row['first_position'] < row['second_position']:
            pred_set.append({'home_team': row['Home Team'], 'away_team': row['Away Team'], 'winning_team': None})
        else:
            pred_set.append({'home_team': row['Away Team'], 'away_team': row['Home Team'], 'winning_team': None})
            
    pred_set = pd.DataFrame(pred_set)
    backup_pred_set = pred_set
    
    # Get dummy variables and drop winning_team column
    pred_set = pd.get_dummies(pred_set, prefix=['home_team', 'away_team'], columns=['home_team', 'away_team'])
    
    # Add missing columns compared to the model's training dataset
    missing_cols = set(final_dataset.columns) - set(pred_set.columns)
    for c in missing_cols:
        pred_set[c] = 0
    pred_set = pred_set[final_dataset.columns]
    
    # Remove winning team column
    pred_set = pred_set.drop(['winning_team'], axis=1)
    
    predictions = logreg.predict(pred_set)
    for i in range(fixtures.shape[0]):
        print(backup_pred_set.iloc[i, 1] + " and " + backup_pred_set.iloc[i, 0])
        if predictions[i] == 1:
            print("Winner: " + backup_pred_set.iloc[i, 1])
        elif predictions[i] == 0:
            print("Tie")
        elif predictions[i] == 2:
            print("Winner: " + backup_pred_set.iloc[i, 0])
        print('Probability of ' + backup_pred_set.iloc[i, 1] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set)[i][1]))
        print('Probability of Tie: ', '%.3f'%(logreg.predict_proba(pred_set)[i][0]))
        print('Probability of ' + backup_pred_set.iloc[i, 0] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set)[i][2]))
        print("")
#===============================================#
    

#============== Other Rounds ===================#
def clean_and_predict(matches, ranking, final, logreg):

    # Initialization of auxiliary list for data cleaning
    positions = []

    # Loop to retrieve each team's position according to FIFA ranking
    for match in matches:
        positions.append(ranking.loc[ranking['Team'] == match[0],'Position'].iloc[0])
        positions.append(ranking.loc[ranking['Team'] == match[1],'Position'].iloc[0])
    
    # Creating the DataFrame for prediction
    pred_set = []

    # Initializing iterators for while loop
    i = 0
    j = 0

    # 'i' will be the iterator for the 'positions' list, and 'j' for the list of matches (list of tuples)
    while i < len(positions):
        dict1 = {}

        # If position of first team is better, he will be the 'home' team, and vice-versa
        if positions[i] < positions[i + 1]:
            dict1.update({'home_team': matches[j][0], 'away_team': matches[j][1]})
        else:
            dict1.update({'home_team': matches[j][1], 'away_team': matches[j][0]})

        # Append updated dictionary to the list, that will later be converted into a DataFrame
        pred_set.append(dict1)
        i += 2
        j += 1

    # Convert list into DataFrame
    pred_set = pd.DataFrame(pred_set)
    backup_pred_set = pred_set

    # Get dummy variables and drop winning_team column
    pred_set = pd.get_dummies(pred_set, prefix=['home_team', 'away_team'], columns=['home_team', 'away_team'])

    # Add missing columns compared to the model's training dataset
    missing_cols2 = set(final.columns) - set(pred_set.columns)
    for c in missing_cols2:
        pred_set[c] = 0
    pred_set = pred_set[final.columns]

    # Remove winning team column
    pred_set = pred_set.drop(['winning_team'], axis=1)

    # Predict!
    predictions = logreg.predict(pred_set)
    for i in range(len(pred_set)):
        print(backup_pred_set.iloc[i, 1] + " and " + backup_pred_set.iloc[i, 0])
        if predictions[i] == 2:
            print("Winner: " + backup_pred_set.iloc[i, 1])
        elif predictions[i] == 1:
            print("Tie")
        elif predictions[i] == 0:
            print("Winner: " + backup_pred_set.iloc[i, 0])
        print('Probability of ' + backup_pred_set.iloc[i, 1] + ' winning: ' , '%.3f'%(logreg.predict_proba(pred_set)[i][2]))
        print('Probability of Tie: ', '%.3f'%(logreg.predict_proba(pred_set)[i][1])) 
        print('Probability of ' + backup_pred_set.iloc[i, 0] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set)[i][0]))
        print("")
#===============================================#
