# AI-Assistant-Football-Coach-Agent

## Description
Developed a python AI agent that retrives and processes play-by-play NFL data and then analyzs this dataset to determine the most efficient play and formation a team's offense should run in user selected in-game situations (eg. quarter, down, field position). 

## Features
- Jupyter Notebook highlights entire workflow of the project
- EDA section to find and visualize patterns and trends in the dataset
- Feature engineering to select necessary features for the agent
- User inputs team, quarter, down, and starting field position
- Markov decision process-based implementation to decide play and formation
- q-learning-based implementation to decide play and formation
- Hidden Markov model to generate drive ideas (series of plays likely to end in a touchdown given user input)
- Comparative analysis to compare two implementations
- Reward manipulation analysis on q-learning implementation


## Tech Stack
- Python
- pandas
- NumPy
- Matplotlib
- Jupyter Notebook

## Algorithms
- q-learning (reinforcement learning)
- Markov decision process
- Hidden Markov model

## Prerequisites
- Python installed
- Required packages: 'pandas', 'NumPy'
  
## Installation

## Usage
1) Start program
2) Input team and in-game situation as instructed; press 'enter'
3) Program will output play for each implmentation
4) Program will generate up to 10 drive "ideas"
