import pandas as pd
pd.set_option('display.max_colwidth', None)
import xlwings as xw









def fx_goalieflag(playerdata):
    if 'GA' in playerdata.columns:
        goalieflag = True
    else:
        goalieflag = False
    return goalieflag














playerslist = []  # Empty list to store player names
seasonlist = []
players_upload_acttion = input('Press 1 to manually input player names.\nPress 0 if you have a list of players on desktop: ' )

if players_upload_acttion == "1":
    while True:
        full_name = input("Enter the player's name (or '0' to stop): ")
        
        if full_name == '0':
            break
        
        playerslist.append(full_name)  # Add the full name to the list of players
        players = pd.DataFrame()
        players['player'] = playerslist

else:
    file_path = r'C:\Users\thoma\Desktop\NHL_SCRAPE\Players.csv'
    try:
        playerslist = pd.read_csv(file_path)
        # Display the first few rows of the DataFrame
        
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    players = pd.DataFrame()
    players['player'] = playerslist['Players']
    

season = str(input('input the season you want to see data for: '))

players['player'] = players['player'].str.lower()
players[['first', 'last']] = players['player'].str.split(pat=' ', n=1, expand=True)
players['firstlastname'] = players['last'].str[0]
players['first5lastname'] = players['last'].str[:5]
players['first2firstname'] = players['first'].str[:2]

players['url'] = f'https://www.hockey-reference.com/players/'+players['firstlastname']+'/'+players['first5lastname']+players['first2firstname']+'01/gamelog/'+season













namelist = players['player']


playerreport = xw.Book()

sheetnames = []
for name in namelist:
    playerreport.sheets.add(name=name)
    sheetnames.append(name)

master = playerreport.sheets.add(name='Master')

teamtotal = pd.DataFrame()

for index, row in players.iterrows():
    player = row['player']
    playerurl = row['url']



    playerdatatemp = pd.read_html(playerurl)

        

    

    playerdata = playerdatatemp[0]


    playerdata.columns = playerdata.columns.droplevel(level=0)
    wastrow = [20,41,62,83]
    for row in wastrow:
        if row in playerdata.index:
            playerdata.drop(index = row, inplace = True)



    playerdata = playerdata.drop(columns=['Age', 'Tm', 'Unnamed: 5_level_1'], axis=1)







    playerdata.rename(columns={'Unnamed: 7_level_1': 'w/l'}, inplace=True)



    playerdata['FantPoint'] = ((playerdata.iloc[:, 5].astype(int))*3) + ((playerdata.iloc[:, 6].astype(int))*2) + (playerdata.iloc[:, 16].astype(int)) + ((playerdata.iloc[:, 21].astype(int))*0.25) + ((playerdata.iloc[:, 17].astype(int))*0.25) + ((playerdata.iloc[:, 22].astype(int))*0.25)

    
    total_goals = playerdata.iloc[:, 5].astype(int).sum()
    total_pts = playerdata.iloc[:, 7].astype(int).sum()
    total_asst = playerdata.iloc[:, 6].astype(int).sum()
    total_shots = playerdata.iloc[:, 17].astype(int).sum()
    total_blocks = playerdata.iloc[:, 22].astype(int).sum()
    total_hit = playerdata.iloc[:, 21].astype(int).sum()
    total_shp = playerdata.iloc[:, 16].astype(int).sum()
    total_fantpoint = (total_goals*3) + (total_asst*2) + (total_shp) + (total_shots*0.25) + (total_hit*0.25) + (total_blocks*0.25)
    teamtotal = pd.concat([teamtotal, pd.DataFrame({'player': [player], 
                                                    'FanPoints': [total_fantpoint], 
                                                    'Shots': [total_shots], 
                                                    'Goals': [total_goals], 
                                                    'Assists': [total_asst],  
                                                    'Blocks': [total_blocks], 
                                                    'Hits': [total_hit], 
                                                    'SHP': [total_shp],
                                                    'Points': [total_pts]})], 
                                                    ignore_index=True)



    ws = playerreport.sheets[player] 
    
    ws.range('A1').options(index=False).value = playerdata
master.range('A1').options(index=False).value = teamtotal

playerreport.sheets['Sheet1'].delete() 
playerreport.save('C:/Users/thoma/Desktop/NHL_SCRAPE/playerreport.xlsx')
playerreport.close()   











