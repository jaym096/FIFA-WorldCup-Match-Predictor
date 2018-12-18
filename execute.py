import predict as pred
import static_groups as sg
import dataWrangler as dw
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression


def Level_sel(argument):
    switcher = {
        1: sg.wc_teams(),
        2: sg.group_of_16(),
        3: sg.quaters_group(),
        4: sg.semis_group(),
        5: sg.finals_group()
    }
    return switcher.get(argument, "Invalid")

if __name__ == "__main__":
    
    print "1. First round Matches"
    print "2. round of 16 Matcehs"
    print "3. Quater Final Matches"
    print "4. Semi Final Matches"
    print "5. Final Match"
    argument = input("Select any one to get the result of the stage: ")
    matches = Level_sel(argument)
    
    results, rankings = dw.getData(argument)

    #Now let's get the list of teams that participated in WC
    wc_teams = sg.wc_teams()
    
    final_dataset = dw.DataPreprocessor(results, wc_teams, argument)
    
    #Separate into feature set and target variable
    x_all = final_dataset.drop(['winning_team'], axis=1)
    y_all = final_dataset['winning_team']
    y_all = y_all.astype('int')
    
    # Separate train and test sets
    X_train, X_test, y_train, y_test = train_test_split(x_all, y_all, test_size=0.3, random_state=42)
    
    
    #========== Training and Evaluation ============#
    #1. Using Logistic Regression
    logreg = LogisticRegression()
    logreg.fit(X_train, y_train)
    score = logreg.score(X_train, y_train)
    score2 = logreg.score(X_test, y_test)
    print "Training set accuracy: ",score
    print "Test set accuracy: ",score2
    
    if(argument == 1):
        pred.predict_firstRound(rankings, final_dataset, logreg)
    else:
        pred.clean_and_predict(matches, rankings, final_dataset, logreg)