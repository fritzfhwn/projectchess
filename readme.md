# Introduction

Welcome to Project Chess! This project aims to provide an insightful comparison between different chess groups, namely International Masters, FIDE Masters, and Grandmasters. The focus is on analyzing variations in their winning behaviors, results, and the impact of being a streamer within these groups.

# Project Overview

The objective of this project is to delve into the world of chess and understand if there are significant differences among top-tier chess groups. By examining various aspects such as win rates, game outcomes, and the influence of streaming on these players, the aim is to uncover interesting patterns and insights.


# Installation

Although this project has a presence on GitHub, not all files are hosted there due to size constraints. To access the complete set of files and resources necessary for this project, please download them from the cloud repository. This ensures that you have all the necessary components to run the project successfully.

https://fhwiener-my.sharepoint.com/personal/204055_fhwn_ac_at/_layouts/15/onedrive.aspx?id=%2Fpersonal%2F204055%5Ffhwn%5Fac%5Fat%2FDocuments%2Fprojectchess%2Ezip&parent=%2Fpersonal%2F204055%5Ffhwn%5Fac%5Fat%2FDocuments&ga=1


Navigate to the project directory and run pipenv install to set up the project environment. Activate the virtual environment using pipenv shell.

Once the environment is set up and active, you can start the application by running streamlit run main.py in your terminal.

After launching the application, you will be greeted with a user-friendly interface to explore various aspects of chess group analysis. The application provides different modules to analyze winning behaviors, game results, elo progression and the streaming influence on these chess groups.

# Chess.com API Integration

This project integrates with the Chess.com API to access a wide range of data related to chess games, players, and statistics. Below is an overview of the key functionalities provided through these API requests:

### Player Profiles and Stats: 

The program can retrieve detailed profiles of players including their usernames, titles, and country. Additionally, comprehensive statistics like their game history, win/loss records, and Elo ratings across different game formats (e.g., blitz, bullet) can be fetched.

### Game Data: 

Extraction of data on individual games played by users, segmented by month and year. This includes detailed information about each game such as the opening played, game outcome, and player accuracies.

### Leaderboards: 

The application can access leaderboards for various game formats, providing insights into the top players in each category.

### Titled Players: 

The program also has the capability to fetch lists of players holding specific chess titles such as Grandmaster (GM), International Master (IM), etc.