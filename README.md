# AI-Assistant-Football-Coach-Agent

## Description
Developed a python program that retrives and processes play-by-play NFL data and then analyzs this dataset to determine the most efficient play a team's offense should run in user selected in-game situations (eg. quarter, down, field position). Feature engineering was performed to prepare the dataset which was analyzed using two separate implementations: the Markov decision process and q-learning. Each method was implemented using object-oriented programming and pandas dataframes were utilized to store the relevant values for each method. The results of each implementation was analyzed and compared, which led to the q-learning implementation being deemed more "realistic". Reward manipulation was conducted on the q-learning implementation to get a better udnerstadning of q-values and the information they hold, as well as to showcase how the program can be reconfigured for different use cases (eg. to find plays likely to result in a score, find plays likely to result in a turnover, etc.). A drive generation feature was added on, which utilizes the hidden Markov model to generate different series of play results (or drives in football terms) that are likely to end in the team scoring based on the user's selected in-game situation. 

## Tech Stack
- Python
- pandas
- NumPy
- Matplotlib
- Object-oriented programming

## Algorithms
- q-learning (reinforcement learning)
- Markov decision process
- Hidden Markov model

## Prerequisites
- Python installed
- Required packages: 'pandas', 'NumPy', 'Matplotlib'
  
## Installation

## Usage
1) Start program
2) Input team and in-game situation as instructed; press 'enter'
3) Program will output play for each implmentation
4) Program will generate up to 5 drive "ideas" (sequence of play results to end in a touchdown)
