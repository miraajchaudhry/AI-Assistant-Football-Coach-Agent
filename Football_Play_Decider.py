import pandas as pd # for reading in analyzing data
import numpy as np # for reorganizing and analyzing data

"""# Clean Data
Clean data and make it ready for MDP and Q-learning by only keeping necessary columns. Some columns will be deleted, some will be joined, some will be created.

Function to prepare dataset for markov models. Will only leave data with user given team, down, quarter, and field position. Will modify columns as well
"""

# function to reorganize data for markov models so unecessary data is removed
# function will take in the dataset and user inputted data (quarter, team, and desired outcome)
# function will return updated dataset
def markov_reorganize(data_set, quarter, down, team, field_side):
    # ensure data is sorted in sequential order
    # sort data first by game id, then by quarter, followed by time remaining
    data_set = data_set.sort_values(by=['GameId', 'Quarter', 'Minute', 'Second'], ascending=[True, True, False, False])

    # set an other quarter variable that may need to be used if there aren't enough specific play results within one quarter
    if ((quarter == 1) | (quarter == 3)):
        other_q = quarter + 1
    else:
        other_q = quarter - 1

    # create a data frame with only the necessary data points
    updated_data = pd.DataFrame(data_set[(data_set['OffenseTeam'] == team) & (data_set['Down'] == down) & (data_set['YardLineDirection'] == field_side) & ((data_set['Quarter'] == quarter) | (data_set['Quarter'] == other_q))]
                                [['OffenseTeam', 'Quarter', 'Down', 'ToGo', 'Yards', 'YardLineDirection', 'PlayType', 'Formation', 'IsTouchdown',
                                  'IsInterception', 'IsFumble', 'IsSack']])

    # clean columns so rows with uneccessary data are gone

    # get rid of 'NaN' values
    updated_data = updated_data.dropna(subset=['PlayType'])

    # change quarter 5 to OT for overtime
    updated_data['Quarter'] = np.where(updated_data['Quarter'] == 5, 'OT', updated_data['Quarter'])

    # only need play data for when play was a pass, run, or sramble (all other play types were either equivalent to no play or special teams play)
    #updated_data = updated_data[(updated_data['PlayType'] == 'PASS') | (updated_data['PlayType'] == 'RUSH') | (updated_data['PlayType'] == 'SCRAMBLE') | (updated_data['PlayType'] == 'FIELD GOAL')]
    updated_data = updated_data[(updated_data['PlayType'] == 'PASS') | (updated_data['PlayType'] == 'RUSH')]

    # combine 'IsInterception' and 'IsFumble' into one turnover column; afterwards get rid of two original columns
    updated_data['IsTurnover'] = updated_data['IsInterception'] + updated_data['IsFumble']
    updated_data['IsTurnover'] = np.where(updated_data['IsTurnover'] == 0, False, True)
    updated_data = updated_data.drop(columns=['IsInterception', 'IsFumble'])

    # create new column for negative plays (sack or loss of yards); get rid of sack column
    updated_data['IsNegativePlay'] = np.where((updated_data['IsSack'] == 1) | (updated_data['Yards'] < 0), True, False)
    updated_data = updated_data.drop(columns='IsSack')

    # create new column for next down based on current down, yards to go, and yards gained
    updated_data['NextDown'] = np.where((updated_data['Yards'] < updated_data['ToGo']), updated_data['Down'] + 1, 1)
    updated_data['NextDown'] = np.where(updated_data['IsTouchdown'] == 1, 'TD', updated_data['NextDown'])
    updated_data['NextDown'] = np.where((updated_data['NextDown'] == 5) & (updated_data['Yards'] >= updated_data['ToGo']), 1, updated_data['NextDown'])
    updated_data['NextDown'] = np.where((updated_data['NextDown'] == 5) & (updated_data['Yards'] < updated_data['ToGo']), 'TO', updated_data['NextDown'])
    updated_data['IsTurnover'] = np.where(updated_data['NextDown'] == 'TO', True, updated_data['IsTurnover'])
    #updated_data['NextDown'] = np.where(updated_data['IsTurnover'] == True, 'TO', updated_data['NextDown'])

    #updated_data['NextDown'] = np.where((updated_data['NextDown'] == 5
     # adjust the turnover and next down stats for when offense gos for it on fourth down
    #updated_data['IsTurnover'] = np.where((updated_data['NextDown'] == 5) & (updated_data['Yards'] < updated_data['ToGo']), True, updated_data['IsTurnover'])
    #updated_data['NextDown'] = np.where((updated_data['NextDown'] == 5) & (updated_data['Yards'] < updated_data['ToGo']), "TO", 1)

    # adjust the turnover and next down stats for when offense gos for it on fourth down
    #updated_data['IsTurnover'] = np.where((updated_data['NextDown'] == 5) & (updated_data['Yards'] < updated_data['ToGo']), True, updated_data['IsTurnover'])
    #updated_data['NextDown'] = np.where((updated_data['NextDown'] == 5) & (updated_data['Yards'] < updated_data['ToGo']), "TO", 1)

    updated_data['YardLine'] = updated_data['YardLineDirection']
    #updated_data = updated_data.drop(columns=['Yards'])

    updated_data['YardsToGo'] = 0
    updated_data['YardsToGo'] = np.where(updated_data['ToGo'] <= 5, 'Short', updated_data['YardsToGo'])
    updated_data['YardsToGo'] = np.where(updated_data['ToGo'] <= 10, 'Medium', updated_data['YardsToGo'])
    updated_data['YardsToGo'] = np.where(updated_data['ToGo'] > 10, 'Long', updated_data['YardsToGo'])


    # replace 'IsTouchdown' values with boolean values
    updated_data['IsTouchdown'] = np.where(updated_data['IsTouchdown'] == 1, True, False)

    # new column for field goals
    #updated_data['IsFieldGoal'] = np.where(updated_data['PlayType'] == 'FIELD GOAL', True, False)

    # rearrange columns (makes it easier to read for debugging)
    updated_data = updated_data[['OffenseTeam', 'Quarter', 'Down', 'YardsToGo', 'NextDown', 'YardLine', 'PlayType', 'Formation', 'IsTouchdown', 'IsTurnover', 'IsNegativePlay']]
    #updated_data = updated_data.sort_values(by='Quarter', ascending=True)

    return updated_data

"""Function to prepare dataset for q-learning. Will only filter by team, but will modify columns"""

# function to reorganize data for q-learning so unnecessary data is removed
# function will take in the dataset and user inputted team
# function will return updated dataset
def q_reorganize(data_set, team):
    # ensure data is sorted in sequential order
    # sort data first by game id, then by quarter, followed by time remaining
    data_set = data_set.sort_values(by=['GameId', 'Quarter', 'Minute', 'Second'], ascending=[True, True, False, False])

    # create a data frame with inputted team's data
    updated_data = pd.DataFrame(data_set[(data_set['OffenseTeam'] == team)]
                                [['OffenseTeam', 'Quarter', 'Down', 'ToGo', 'Yards', 'YardLineDirection', 'PlayType', 'Formation', 'IsTouchdown',
                                  'IsInterception', 'IsFumble', 'IsSack']])

    # clean columns so rows with uneccessary data are gone

    # get rid of 'NaN' values
    updated_data = updated_data.dropna(subset=['PlayType'])

    # change quarter 5 to OT for overtime
    updated_data['Quarter'] = np.where(updated_data['Quarter'] == 5, 'OT', updated_data['Quarter'])

    # only need play data for when play was a pass, run, or sramble (all other play types were either equivalent to no play or special teams play)
    #updated_data = updated_data[(updated_data['PlayType'] == 'PASS') | (updated_data['PlayType'] == 'RUSH') | (updated_data['PlayType'] == 'SCRAMBLE') | (updated_data['PlayType'] == 'FIELD GOAL')]
    updated_data = updated_data[(updated_data['PlayType'] == 'PASS') | (updated_data['PlayType'] == 'RUSH')]

    # combine 'IsInterception' and 'IsFumble' into one turnover column; afterwards get rid of two original columns
    updated_data['IsTurnover'] = updated_data['IsInterception'] + updated_data['IsFumble']
    updated_data['IsTurnover'] = np.where(updated_data['IsTurnover'] == 0, False, True)
    updated_data = updated_data.drop(columns=['IsInterception', 'IsFumble'])

    # create new column for negative plays (sack or loss of yards); get rid of sack column
    updated_data['IsNegativePlay'] = np.where((updated_data['IsSack'] == 1) | (updated_data['Yards'] < 0), True, False)
    updated_data = updated_data.drop(columns='IsSack')

    # create new column for next down based on current down, yards to go, and yards gained
    updated_data['NextDown'] = np.where((updated_data['Yards'] < updated_data['ToGo']), updated_data['Down'] + 1, 1)
    updated_data['NextDown'] = np.where(updated_data['IsTouchdown'] == 1, 'TD', updated_data['NextDown'])
    updated_data['NextDown'] = np.where((updated_data['NextDown'] == 5) & (updated_data['Yards'] >= updated_data['ToGo']), 1, updated_data['NextDown'])
    updated_data['NextDown'] = np.where((updated_data['NextDown'] == 5) & (updated_data['Yards'] < updated_data['ToGo']), 'TO', updated_data['NextDown'])
    updated_data['IsTurnover'] = np.where(updated_data['NextDown'] == 'TO', True, updated_data['IsTurnover'])
    #updated_data['NextDown'] = np.where(updated_data['IsTurnover'] == True, 'TO', updated_data['NextDown'])

    #updated_data['NextDown'] = np.where((updated_data['NextDown'] == 5
     # adjust the turnover and next down stats for when offense gos for it on fourth down
    #updated_data['IsTurnover'] = np.where((updated_data['NextDown'] == 5) & (updated_data['Yards'] < updated_data['ToGo']), True, updated_data['IsTurnover'])
    #updated_data['NextDown'] = np.where((updated_data['NextDown'] == 5) & (updated_data['Yards'] < updated_data['ToGo']), "TO", 1)

    updated_data['YardLine'] = updated_data['YardLineDirection']
    #updated_data = updated_data.drop(columns=['Yards'])


    updated_data['YardsToGo'] = 0
    updated_data['YardsToGo'] = np.where(updated_data['ToGo'] <= 5, 'Short', updated_data['YardsToGo'])
    updated_data['YardsToGo'] = np.where(updated_data['ToGo'] <= 10, 'Medium', updated_data['YardsToGo'])
    updated_data['YardsToGo'] = np.where(updated_data['ToGo'] > 10, 'Long', updated_data['YardsToGo'])

    # replace 'IsTouchdown' values with boolean values
    updated_data['IsTouchdown'] = np.where(updated_data['IsTouchdown'] == 1, True, False)

    # new column for field goals
    #updated_data['IsFieldGoal'] = np.where(updated_data['PlayType'] == 'FIELD GOAL', True, False)

    # rearrange columns (makes it easier to read for debugging)
    updated_data = updated_data[['OffenseTeam', 'Quarter', 'Down', 'YardsToGo', 'NextDown', 'YardLine', 'PlayType', 'Formation', 'IsTouchdown', 'IsTurnover', 'IsNegativePlay']]

    return updated_data

"""#  Implementing Markov Models
Implenting Markov Models, both the Markov Decision Process (which is mentioned in my proposal and crucial to the final result of my project) and the Hidden Markov Model as Professor Alam stated in his Mid-Project Submission requirements. I had to do Markov Models as my data is of the sequential type. I determined it was of this type as the data includes a row of various data points, but these rows are given in a play-by-play sequence and if this sequence were to become completely random, the data would lose most of its meaning. Additionally, each entry (play) is dependent on the previous play as some plays wouldn't make sense for certain previous plays. For instance, if a team runs a play on first down and fail to pick up a first, the next play cannot be any play other than on second down. Each down and play result is essentially a state and the play type and formation is an action.

Implementing the Markov Decision Process to decide most optimal play for team in given situation
"""

# class to implement Markov Decision Process
# when class object is declared, class will take the processed data and quarter and use them to implement a MDP
class MDP:
    # "constructor" to save necessary values into class and begin process
    def __init__(self, reward, data, quarter):
        # save dataset to class
        self.data = data
        self.quarter = str(quarter)

        # reward dictionary to make it easier to access reward by read next down
        self.rewards = {"Turnover": reward[0], "NegPlay": reward[1], "NextDown": reward[2], "FirstDown": reward[3], "Touchdown": reward[4]}
        # set reward amounts (rewards for each action will depend on the new state)
        self.Touchdown_reward = 10
        self.FirstDown_reward = 5
        self.NextDown_reward = 2.5
        #self.FieldGoal_reward = 5
        self.NegativePlay_reward = -5
        self.Turnover_reward = -10

        self.calculate()

    # function to calculate frequency and probabilities of each state (score, turnover, down) occurring given each action (play type and formation)
    # the function takes no parameters and returns none but will call the decision() function
    def calculate(self):
        temp = pd.DataFrame(self.data[(self.data['PlayType'] == 'RUSH')]).sort_values(by='Quarter', ascending=True)
        formations = temp['Formation'].unique()
        rush_df = pd.DataFrame({'FirstDown':0, 'P(FirstDown)':0, 'NextDown':0, 'P(NextDown)':0, 'Touchdown':0, 'P(Touchdown)':0, 'Turnover':0, 'P(Turnover)':0, 'NegativePlay':0, 'P(NegativePlay)':0, 'TotalPlays':0}, index=formations)
        q = str(self.quarter)
        FD_next = ND_next = TD_next = TO_next = NEG_next = 0
        for each in formations:
            for row in temp.itertuples():
                if (row.Formation == each):
                    if (row.NextDown == '1'):
                        rush_df.loc[each, 'FirstDown'] = rush_df.loc[each, 'FirstDown'] + 1
                    if ((row.NextDown != '1') & (row.NextDown != 'TD') & (row.NextDown != 'TO')):
                        rush_df.loc[each, 'NextDown'] = rush_df.loc[each, 'NextDown'] + 1
                    if (row.IsTouchdown == True):
                        rush_df.loc[each, 'Touchdown'] = rush_df.loc[each, 'Touchdown'] + 1
                    if (row.IsTurnover == True):
                        rush_df.loc[each, 'Turnover'] = rush_df.loc[each, 'Turnover'] + 1
                    if (row.IsNegativePlay == True):
                        rush_df.loc[each, 'NegativePlay'] = rush_df.loc[each, 'NegativePlay'] + 1
                    rush_df.loc[each, 'TotalPlays'] = rush_df.loc[each, 'TotalPlays'] + 1

        for each in formations:
            rush_df.loc[each, 'P_FirstDown'] = rush_df.loc[each, 'FirstDown'] / rush_df.loc[each, 'TotalPlays']
            rush_df.loc[each, 'P_NextDown'] = rush_df.loc[each, 'NextDown'] / rush_df.loc[each, 'TotalPlays']
            rush_df.loc[each, 'P_Touchdown'] = rush_df.loc[each, 'Touchdown'] / rush_df.loc[each, 'TotalPlays']
            rush_df.loc[each, 'P_Turnover'] = rush_df.loc[each, 'Turnover'] / rush_df.loc[each, 'TotalPlays']
            rush_df.loc[each, 'P_NegativePlay'] = rush_df.loc[each, 'NegativePlay'] / rush_df.loc[each, 'TotalPlays']
        #print("\nRUSHING:\n", rush_df)

        temp = pd.DataFrame(self.data[(self.data['PlayType'] == 'PASS')]).sort_values(by='Quarter', ascending=True)
        formations = temp['Formation'].unique()
        pass_df = pd.DataFrame({'FirstDown':0, 'NextDown':0, 'Touchdown':0, 'Turnover':0, 'NegativePlay':0, 'TotalPlays':0}, index=formations)
        q = str(self.quarter)
        FD_next = ND_next = TD_next = TO_next = NEG_next = 0
        for each in formations:
            for row in temp.itertuples():
                if (row.Formation == each):
                    if (row.NextDown == '1'):
                        pass_df.loc[each, 'FirstDown'] = pass_df.loc[each, 'FirstDown'] + 1
                    if ((row.NextDown != '1') & (row.NextDown != 'TD') & (row.NextDown != 'TO')):
                        pass_df.loc[each, 'NextDown'] = pass_df.loc[each, 'NextDown'] + 1
                    if (row.IsTouchdown == True):
                        pass_df.loc[each, 'Touchdown'] = pass_df.loc[each, 'Touchdown'] + 1
                    if (row.IsTurnover == True):
                        pass_df.loc[each, 'Turnover'] = pass_df.loc[each, 'Turnover'] + 1
                    if (row.IsNegativePlay == True):
                        pass_df.loc[each, 'NegativePlay'] = pass_df.loc[each, 'NegativePlay'] + 1
                    pass_df.loc[each, 'TotalPlays'] = pass_df.loc[each, 'TotalPlays'] + 1

        for each in formations:
            pass_df.loc[each, 'P_FirstDown'] = pass_df.loc[each, 'FirstDown'] / pass_df.loc[each, 'TotalPlays']
            pass_df.loc[each, 'P_NextDown'] = pass_df.loc[each, 'NextDown'] / pass_df.loc[each, 'TotalPlays']
            pass_df.loc[each, 'P_Touchdown'] = pass_df.loc[each, 'Touchdown'] / pass_df.loc[each, 'TotalPlays']
            pass_df.loc[each, 'P_Turnover'] = pass_df.loc[each, 'Turnover'] / pass_df.loc[each, 'TotalPlays']
            pass_df.loc[each, 'P_NegativePlay'] = pass_df.loc[each, 'NegativePlay'] / pass_df.loc[each, 'TotalPlays']
        #print("\nPASSING:\n", pass_df)

        # save data frames within class
        self.pass_plays = pass_df
        self.rush_plays = rush_df

        # call class' decision function
        #self.decision()

    # function to make the decision for which play is most optimal in the given situation
    # function takes no arguments but utilizes class' saved variables along with the Bellman equation to determine the play
    # this function is essentially a version of the Bellman equation and outputs a list that contains the most optimal play,
    # the reward value, and the play outcome (the transition state)
    def decision(self):
        discount = 0.4 # as project is supposed to be a simplified play decider meant to be used at amateur level, discount factors will be set to 1 for now
        V_0 = 0 # previous state doesn't matter as project aims to decide best single play in a current situation and not a sequence of plays

        # make an empty list to store the rewards of each possible action going to each state
        # easy way to keep track of results and use them in Bellman equation
        values = []

        for row in self.rush_plays.itertuples():
            val = row.P_FirstDown * (self.rewards['FirstDown'] + (discount * V_0))
            values.append(["Rush to first down", row.Index, val])
            val = row.P_NextDown * (self.rewards['NextDown'] + (discount * V_0))
            values.append(["Rush to next down", row.Index, val])
            val = row.P_Touchdown * (self.rewards['Touchdown'] + (discount * V_0))
            values.append(["Rush to touchdown", row.Index, val])
            val = row.P_Turnover * (self.rewards['Turnover'] + (discount * V_0))
            values.append(["Rush to turnover", row.Index, val])
            val = row.P_NegativePlay * (self.rewards['NegPlay'] + (discount * V_0))
            values.append(["Rush to negative play", row.Index, val])

        for row in self.pass_plays.itertuples():
            val = row.P_FirstDown * (self.rewards['FirstDown'] + (discount * V_0))
            values.append(["Pass to first down", row.Index, val])
            val = row.P_NextDown * (self.rewards['NextDown'] + (discount * V_0))
            values.append(["Pass to next down", row.Index, val])
            val = row.P_Touchdown * (self.rewards['Touchdown'] + (discount * V_0))
            values.append(["Pass to touchdown", row.Index, val])
            val = row.P_Turnover * (self.rewards['Turnover'] + (discount * V_0))
            values.append(["Pass to turnover", row.Index, val])
            val = row.P_NegativePlay * (self.rewards['NegPlay'] + (discount * V_0))
            values.append(["Pass to negative play", row.Index, val])


        max_val = values[0][2]
        max_list = values[0]
        for i in range(1, len(values)):
            if (values[i][2] > max_val):
                max_val = values[i][2]
                max_list = values[i]

        #print("Most optimal play is", max_list)
        #print("Most optimal play is to", max_list[0], "in", max_list[1], "formation")
        return max_list

"""Implement Hidden Markov Model to generate sequence of play outcomes that can lead to a TD"""

# class to implement a hidden markov model
# this will be similar to the MDP class as the observed states will be the play results (first down, TD, etc)
# and the hidden states will be the play type, pass or fail
class HMM:
    # "constructor" to save necessary values into class and begin process
    def __init__(self, data, quarter):
        # save dataset to class
        self.data = data
        self.quarter = str(quarter)

        self.calculate()

    def calculate(self):
        plays = ['RUSH', 'PASS']

        # make data frame for probabilities related to hidden states (rush and pass)
        hidden = pd.DataFrame({'Pass-Pass':0.0, 'Pass-Rush':0.0, 'Rush-Pass':0.0, 'Rush-Rush':0.0, 'TotalPlays':0.0}, index=plays)


        # make a data frame for probabilities related to observed states (play results: first down, next down, TD, turnover, negative play)
        observed = pd.DataFrame({'FirstDown':0.0, 'NextDown':0.0, 'Touchdown':0.0, 'Turnover':0.0, 'NegativePlay':0.0, 'TotalPlays':0.0}, index=plays)

        # variable to hold previous play type
        prev = None
        # helper variable
        i = 0
        for row in self.data.itertuples():
            if (i == 0):
                prev = row.PlayType
                i = i + 1
            else:
                if (row.PlayType == 'PASS'):
                    if (prev == 'PASS'):
                        hidden.loc['PASS', 'Pass-Pass'] = hidden.loc['PASS', 'Pass-Pass'] + 1
                    elif (prev == 'RUSH'):
                        hidden.loc['PASS', 'Rush-Pass'] = hidden.loc['PASS', 'Rush-Pass'] + 1
                    hidden.loc['PASS', 'TotalPlays'] = hidden.loc['PASS', 'TotalPlays'] + 1
                elif (row.PlayType == 'RUSH'):
                    if (prev == 'PASS'):
                        hidden.loc['RUSH', 'Pass-Rush'] = hidden.loc['RUSH', 'Pass-Rush'] + 1
                    elif (prev == 'RUSH'):
                        hidden.loc['RUSH', 'Rush-Rush'] = hidden.loc['RUSH', 'Rush-Rush'] + 1
                    hidden.loc['RUSH', 'TotalPlays'] = hidden.loc['RUSH', 'TotalPlays'] + 1
                prev = row.PlayType


            if ((row.PlayType == 'PASS') | (row.PlayType == 'RUSH')):
                if (row.NextDown == '1'):
                    observed.loc[row.PlayType, 'FirstDown'] = observed.loc[row.PlayType, 'FirstDown'] + 1
                elif ((row.NextDown != '1') & (row.NextDown != 'TD') & (row.NextDown != 'TO')):
                    observed.loc[row.PlayType, 'NextDown'] = observed.loc[row.PlayType, 'NextDown'] + 1
                elif (row.IsTouchdown == True):
                    observed.loc[row.PlayType, 'Touchdown'] = observed.loc[row.PlayType, 'Touchdown'] + 1
                elif (row.IsTurnover == True):
                    observed.loc[row.PlayType, 'Turnover'] = observed.loc[row.PlayType, 'Turnover'] + 1
                elif (row.IsNegativePlay == True):
                    observed.loc[row.PlayType, 'NegativePlay'] = observed.loc[row.PlayType, 'NegativePlay'] + 1
                observed.loc[row.PlayType, 'TotalPlays'] = observed.loc[row.PlayType, 'TotalPlays'] + 1

        # turn frequencies into probailities
        for row in hidden.itertuples():
            each = row.Index
            hidden.loc[each, 'Pass-Pass'] = hidden.loc[each, 'Pass-Pass'] / hidden.loc[each, 'TotalPlays']
            hidden.loc[each, 'Pass-Rush'] = hidden.loc[each, 'Pass-Rush'] / hidden.loc[each, 'TotalPlays']
            hidden.loc[each, 'Rush-Pass'] = hidden.loc[each, 'Rush-Pass'] / hidden.loc[each, 'TotalPlays']
            hidden.loc[each, 'Rush-Rush'] = hidden.loc[each, 'Rush-Rush'] / hidden.loc[each, 'TotalPlays']

        for row in observed.itertuples():
            each = row.Index
            observed.loc[each, 'FirstDown'] = observed.loc[each, 'FirstDown'] / observed.loc[each, 'TotalPlays']
            observed.loc[each, 'NextDown'] = observed.loc[each, 'NextDown'] / observed.loc[each, 'TotalPlays']
            observed.loc[each, 'Touchdown'] = observed.loc[each, 'Touchdown'] / observed.loc[each, 'TotalPlays']
            observed.loc[each, 'Turnover'] = observed.loc[each, 'Turnover'] / observed.loc[each, 'TotalPlays']
            observed.loc[each, 'NegativePlay'] = observed.loc[each, 'NegativePlay'] / observed.loc[each, 'TotalPlays']


        # save hidden and observed data frames into class
        self.hidden_states = plays
        self.p_hidden = hidden.drop('TotalPlays', axis=1)
        self.observed_states = ['FirstDown', 'NextDown', 'Touchdown', 'Turnover', 'NegativePlay']
        self.p_observed = observed.drop('TotalPlays', axis=1)

        self.generate_drive()

    # function to generate possible play outcome sequence starting from inputted field side to end in a TD
    # function is based off the observeGenerating() function in hmm.ipynb shared by Professor Alam
    def generate_drive(self):
        # empty list to store the drive plays
        drive = []

        # variable to prevent drive from having 4+ downs before first down or touchdown
        # should always be in range of 1-4; can never be > 4
        current_down = 1

        state = np.random.choice(self.hidden_states, 1, p = [0.5, 0.5])[0]

        observe = np.random.choice(self.observed_states, 1, p = self.p_observed.loc[state].tolist())[0]
        if (observe == 'FirstDown'):
            current_down = 1
        elif ((observe == 'NextDown') & (current_down < 4)):
            current_down = current_down + 1
        drive.append(observe)

        for i in range(15):
            # make list of probability to go to next hidden state based on current state
            # but normalize first
            if (state == 'RUSH'):
                norm = self.p_hidden.loc[state, 'Rush-Rush'] + self.p_hidden.loc[state, 'Rush-Pass']
                hidden_prob = [self.p_hidden.loc[state, 'Rush-Rush'] / norm, self.p_hidden.loc[state, 'Rush-Pass'] / norm]
            else:
                norm = self.p_hidden.loc[state, 'Pass-Rush'] + self.p_hidden.loc[state, 'Pass-Pass']
                hidden_prob = [self.p_hidden.loc[state, 'Pass-Rush'] / norm, self.p_hidden.loc[state, 'Pass-Pass'] / norm]

            state = np.random.choice(self.hidden_states, 1, p = hidden_prob)[0]
            observe = np.random.choice(self.observed_states, 1, p = self.p_observed.loc[state].tolist())[0]

            while ((observe == 'NextDown') & (current_down == 4)):
                observe = np.random.choice(self.observed_states, 1, p = self.p_observed.loc[state].tolist())[0]
            if ((observe == 'NextDown') & (current_down < 4)):
                current_down = current_down + 1
            elif (observe == 'FirstDown'):
                current_down = 1

            drive.append(observe)

            if observe == 'Touchdown':
                break


        print(" ".join(drive))

        # if after all 15 iteration, no TD scored
        if (len(drive) == 15):
            if (drive[14] != 'Touchdown'):
                print("Touchdown unlikely in the sequence")

"""# Q-Learning
Implemented q-learning to determine most optimal play in given situation. Class will analyze dataset and update q-values corresponding to the current state. Once all q-values are updated, it'll choose the max q-value in the user given state.
"""

class Q:
    # class variables that are already determined and needed by all or most functions
    # down dictionary to easily translate between read down and down needed for calculations
    downs = {"1": "FirstDown", "2": "SecondDown", "3": "ThirdDown", "4": "FourthDown", "TD": "Touchdown", "TO": "Turnover"}
    # list of possible states (since q-learning requires all data from team to be read, there will be more states than Markov Model
    states = ['FirstDown', 'SecondDown', 'ThirdDown', 'FourthDown', 'Touchdown', 'Turnover', 'NegativePlay']

    # "constructor" of class
    def __init__(self, reward, data, quarter, down, field_side):
        self.data = data
        self.quarter = int(quarter)
        self.current_down = down
        self.territory = field_side

        # reward dictionary to make it easier to access reward by read next down
        self.rewards = {"Turnover": reward[0], "NegPlay": reward[1], "SecondDown": reward[2], "ThirdDown": reward[2], "FourthDown": reward[2], "FirstDown": reward[3], "Touchdown": reward[4]}

        self.make_Q_Table()

    # function to initialize q-table
    # takes no parameters and will use data to make empty q-table where
    # columns are all the actions taken (will not include all possible actions
    # as not every team has taken each action in given situation)
    # will return no value but will call next function to fill table
    def make_Q_Table(self):
        # find all formations (actions) for when team does a pass in given situation
        pass_formations = self.data[self.data['PlayType'] == 'PASS'][['PlayType', 'Formation']]
        pass_formations = pass_formations['Formation'].unique().tolist()
        for i in range(len(pass_formations)):
            pass_formations[i] = pass_formations[i] + " PASS"

        # find all formations (actions) for when team does a rush in given situation
        rush_formations = self.data[self.data['PlayType'] == 'RUSH'][['PlayType', 'Formation']]
        rush_formations = rush_formations['Formation'].unique().tolist()
        for i in range(len(rush_formations)):
            rush_formations[i] = rush_formations[i] + " RUSH"

        # make list of all possible actions (run and pass)
        actions = pass_formations + rush_formations

        # make data frame with each action as a column, each state as an index, and fill it with all 0s (by default)
        # a data frame will be made for each quarter and each field side (to ensure all possible states are included)
        # for example, 1st down in the 2nd quarter in opponent territory is not the same as 2nd down in overtime in your own territory
        # this code snippet could be sorter, but was written out to show full details of what's happening
        q1_own = pd.DataFrame(0.0, index=self.states, columns=actions)
        q1_opp = pd.DataFrame(0.0, index=self.states, columns=actions)
        q2_own = pd.DataFrame(0.0, index=self.states, columns=actions)
        q2_opp = pd.DataFrame(0.0, index=self.states, columns=actions)
        q3_own = pd.DataFrame(0.0, index=self.states, columns=actions)
        q3_opp = pd.DataFrame(0.0, index=self.states, columns=actions)
        q4_own = pd.DataFrame(0.0, index=self.states, columns=actions)
        q4_opp = pd.DataFrame(0.0, index=self.states, columns=actions)
        OT_own = pd.DataFrame(0.0, index=self.states, columns=actions)
        OT_opp = pd.DataFrame(0.0, index=self.states, columns=actions)

        q1 = [q1_own, q1_opp]
        q2 = [q2_own, q2_opp]
        q3 = [q3_own, q3_opp]
        q4 = [q4_own, q4_opp]
        ot = [OT_own, OT_opp]
        self.q_table = [q1, q2, q3, q4, ot]

        self.fill_Q_Table()

    # function to read through data and fill q-table by using q-learning formula
    # q-values for states "Touchdown", "Turnover", and "NegativePlay" will always stay
    # at 0 as there states are terminating plays meaning that no play can occur at these
    # states, plays can only transition to them. They're still in the table to include all details of what's happening
    def fill_Q_Table(self):
        # set up constant for Q(s, a) equation
        discount = 0.4 # as project is supposed to be a simplified play decider meant to be used at amateur level, discount factors will be set to 1 for now
        learning_rate = 0.3 # this value makes sure agent learns from new experience, but still values older experience as there should be more older plays versus just one new play

        # iterate through data and fill q-table
        # will evaluate the following equation for each play:
        #      Q(s, a) <- Q(s, a) + (learning_rate)[reward + (discount)(max(Q(s', a')) - Q(s, a)]
        for each in self.data.itertuples():
            each_quarter = 5 if (each.Quarter == "OT") else int(each.Quarter)

            each_down = self.downs[str(each.Down)]

            if (each.NextDown == "1"):
                each_next_down = "FirstDown"
            elif (each.NextDown == "2"):
                each_next_down = "SecondDown"
            elif (each.NextDown == "3"):
                each_next_down = "ThirdDown"
            elif (each.NextDown == "4"):
                each_next_down = "FourthDown"
            elif (each.NextDown == "TD"):
                each_next_down = "Touchdown"
            else:
                each_next_down = "Turnover"

            territory = 0 if (each.YardLine == 'OWN') else 1

            each_formation = each.Formation
            each_play_type = each.PlayType

            action = each_formation + " " + each_play_type
            current_q = self.q_table[each_quarter - 1][territory].loc[each_down, action]

            if each.IsNegativePlay == True:
                reward = self.rewards["NegPlay"]
                each_next_down = "NegativePlay"
            else:
                reward = self.rewards[each_next_down]

            max_next_q = self.q_table[each_quarter - 1][territory].loc[each_next_down].max()
            q_value = current_q + (learning_rate) * (reward + ((discount) * (max_next_q)) - current_q)
            self.q_table[each_quarter - 1][territory].loc[each_down, action] = q_value

        '''for i in range(5):
            for j in range(2):
                print("Q", i + 1)
                print("OWN" if j == 0 else "OPP")
                print(self.q_table[i][j])
                print("\n\n\n")'''

    # function to determine most optimal play. Will go to sub-table corresponding to the user's
    # given quarter and field position. Once in this sub-table, it'll look for the row corresponding
    # to the user's inputted down. It'll locate the max q-value in this row and output the corresponding formation
    def make_decision(self):
        territory = 0 if (self.territory == "OWN") else 1
        # find max q-value in table corresponding to given situation
        max_q = self.q_table[self.quarter - 1][territory].loc[self.downs[str(self.current_down)]].max() # get the max value
        max_action = self.q_table[self.quarter - 1][territory].loc[self.downs[str(self.current_down)]].idxmax() # get action of max value

        return [max_action, max_q]

        #return f"Most optimal play is a {max_action} due to a q-value of {max_q}"

"""# main program"""

# main program to ask user for information and begin play deciding model
def main():
    error = 0

    # read in data
    data = pd.read_csv('pbp-2024.csv')

    # make a list of all teams in data set
    teams = data['OffenseTeam'].unique()

    # list of downs
    downs = [1, 2, 3, 4]

    # ask user for required inputs
    print("Welcome to the football assistant coach agent!\n-----------------------------------------------------------\n")
    print("This agent will help you decide the most optimal play to run in a given situation, assuming you've decided to run an offensive play\n")
    print("After deciding two possible plays, using two separate implementations, it'll provide a sequence of play results that are likely to end in a touchdown\n")
    print("When prompted please enter the current quarter, down, your team, and your field position\n")
    print("\tPlease note:")
    print("\t\t1. Valid quarters are 1, 2, 3, 4, and 5 (for overtime); while valid downs are 1-4\n")
    print("\t\t2. Your team should be abbreviated as one of the following:\n", teams)
    print("\n\t\t3. Field position should be either 'OPP' for opponent side or 'OWN' for own side, midfield can be either\n")
    print("\t\t4. Please separate each value with a space\n")

    # save user input
    quarter, down, team, field_side = input("Please Enter Your Data: ").split()

    # ensure user has inputted valid quarter
    if ((quarter != '1') & (quarter != '2') & (quarter != '3') & (quarter != '4') & (quarter != '5')):
        print("\nERROR: Invalid quarter\n")
        exit()

    if int(down) not in downs:
        print("Only 1, 2, 3, or 4 are valid downs")
        quit()

    if team.upper() not in teams:
        print("\nERROR: Invalid team\n")
        exit()


    # clean data; one filtered data for markov models, one for q-learning
    markov_data = markov_reorganize(data, int(quarter), int(down), team.upper(), field_side.upper())
    q_data = q_reorganize(data, team.upper())

    # list of rewards in [Turnover, Negative Play, Next Down, First Down, Touchdown]
    rewards1 = [-10, -5, 2.5, 5, 10]
    rewards2 = [-7, 0, 0, 3.5, 7] # values next down and negative plays as non-rewarding
    rewards3 = [-10, -5, 0, 10, 10] # values first downs as much as touchdowns
    rewards4 = [-10, -5, 0, 10, 5] # values first downs more than touchdowns


    test = Q(rewards1, q_data, quarter, down, field_side.upper())
    print("Best play according to Q-learning:", test.make_decision()[0])
    test = MDP(rewards1, markov_data, quarter)
    print("Best play according to MDP:", test.decision()[1], test.decision()[0])

    print("\nPotential TD drives")
    for i in range(10):
        print("Drive #", i + 1)
        test = HMM(markov_data, quarter)
        print("\n")

if __name__ == "__main__":
	main()