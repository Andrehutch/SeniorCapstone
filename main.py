#run command
#gcloud app deploy --project=powerful-bounty-401013 --version 1

#run command
#gcloud app deploy --project=powerful-bounty-401013 --version 1

from flask import Flask, render_template, request
from google.cloud import ndb
import uuid
import logging


app = Flask(__name__)
ndbClient = ndb.Client()
logging.basicConfig(level=logging.INFO)

class GolfPlayer(ndb.Model):
    PlayerName = ndb.StringProperty()
    Handicap = ndb.IntegerProperty()
    PlayerKey = ndb.StringProperty()
    
class ScoreCard(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True)
    scoreCardKey = ndb.StringProperty()
    location = ndb.StringProperty()
    player1 = ndb.KeyProperty(kind="GolfPlayer")
    player2 = ndb.KeyProperty(kind="GolfPlayer")
    player3 = ndb.KeyProperty(kind="GolfPlayer")
    player4 = ndb.KeyProperty(kind="GolfPlayer")
    
class PlayerScore(ndb.Model):
    Player = ndb.KeyProperty(kind="GolfPlayer") #reference the player this score is for
    GameDate = ndb.DateTimeProperty(auto_now=True)
    scoreKey= ndb.StringProperty() #uuid for this particular record
    scorecard = ndb.KeyProperty(kind="ScoreCard") #refernce the specific game by scorecard
    
    hole1 = ndb.IntegerProperty(default=0)
    hole2 = ndb.IntegerProperty(default=0)
    hole3 = ndb.IntegerProperty(default=0)
    hole4 = ndb.IntegerProperty(default=0)
    hole5 = ndb.IntegerProperty(default=0)
    hole6 = ndb.IntegerProperty(default=0)
    hole7 = ndb.IntegerProperty(default=0)
    hole8 = ndb.IntegerProperty(default=0)
    hole9 = ndb.IntegerProperty(default=0)
    
    def totalScore(self):
        score = self.hole1+self.hole2+self.hole3+self.hole4+self.hole5+self.hole6+self.hole7+self.hole8+self.hole9
        return score

@app.route('/')
def index():
    #scoreSheet=save_info(request)
    #return render_template('index.html', GolfScorecard=scoreSheet)
    
    #run query on previous scorecards
    with ndbClient.context():
        gamesQuery = ScoreCard.query()
        games = gamesQuery.fetch()
    
    
    
    return render_template('index.html',previousGames=games)

@app.route('/save_info', methods=['POST'])
def save_info_POST():
    #creates and Array of players fromt he webform
    playerList=save_info(request)
    logging.info("***********made it past playerList")
    
    #tell it what ndb context
    with ndbClient.context():
        #create Scorecard
        scorecard = ScoreCard()
        scorecard.location = ""
        scorecard.scoreCardKey = str(uuid.uuid4())
        
        index = 0
        
        #store each player into the DB
        for player in playerList:
            #create record
            golfPlayer = GolfPlayer()
            golfPlayer.PlayerName = player['player_name']
            golfPlayer.Handicap = int(player['handicap'])
            golfPlayer.PlayerKey = str(uuid.uuid4())
            golfPlayer.put()
            #create playerscore for each player for this particular game
            playerScore = PlayerScore()
            playerScore.Player = golfPlayer.key
            playerScore.scorecard = scorecard.key
            playerScore.scoreKey = str(uuid.uuid4())
            playerScore.put()
            index = index + 1
            player['playerScore'] = playerScore
            #store record
            match index:
                case 1:
                    scorecard.player1 = golfPlayer.key
                case 2:
                    scorecard.player2 = golfPlayer.key
                case 3:
                    scorecard.player3 = golfPlayer.key
                case 4:
                    scorecard.player4 = golfPlayer.key
        #all information for scorecard entered
        scorecard.put()
        
    return render_template('scorecard.html', players=playerList, scorecard=scorecard)
'''
This method will create Player info to be saved
'''
def save_info(request):
    players = []
    for i in range(1, 5): 
        logging.info("****************trying to build object"+str(i))
        data ={}
        data['player_name'] = request.form.get(f'player{i}')
        data['handicap'] = request.form.get('handicap')
        players.append(data)
    return players

@app.route('/scorecard/<scorecardkey>', methods=['GET'])
def scorecard_GET(scorecardkey):
    data = {}#request.args.getlist('data')
    #load scorecard
    with ndbClient.context():
        #get scorecard by its key
        # scorecard = ScoreCard() #this is for context
        scorecardQuery = ScoreCard.query().filter(ScoreCard.scoreCardKey==scorecardkey)
        scorecard = scorecardQuery.fetch(1)[0] # fetches just 1 record,at instance 0  
        
        #now get players
        #now set up to display on scorecard
        
        #now we updated the records so refetch the playerlist
        playerList = []
        data ={}
        player=scorecard.player1.get()
        data['player_name'] = player.PlayerName
        data['handicap']= player.Handicap
        playerList.append(data)
        
        data ={}
        player=scorecard.player2.get()
        data['player_name'] = player.PlayerName
        data['handicap']= player.Handicap
        playerList.append(data)
        
        data ={}
        player=scorecard.player3.get()
        data['player_name'] = player.PlayerName
        data['handicap']= player.Handicap
        playerList.append(data)
        
        data ={}
        player=scorecard.player4.get()
        data['player_name'] = player.PlayerName
        data['handicap']= player.Handicap
        playerList.append(data)
        #requery for each playerScore
        playerScoreQuery = PlayerScore.query().filter(PlayerScore.Player==scorecard.player1)
        playerList[0]['playerScore'] = playerScoreQuery.fetch(1)[0]
        
        playerScoreQuery = PlayerScore.query().filter(PlayerScore.Player==scorecard.player2)
        playerList[1]['playerScore'] = playerScoreQuery.fetch(1)[0]
        
        playerScoreQuery = PlayerScore.query().filter(PlayerScore.Player==scorecard.player3)
        playerList[2]['playerScore'] = playerScoreQuery.fetch(1)[0]
        
        playerScoreQuery = PlayerScore.query().filter(PlayerScore.Player==scorecard.player4)
        playerList[3]['playerScore'] = playerScoreQuery.fetch(1)[0]
        return render_template('scorecard.html', players=playerList, scorecard=scorecard)  


@app.route('/scorecard/<scorecardkey>', methods=['POST'])
def scorecard_POST(scorecardkey):
    data = {}#request.args.getlist('data')
    #load scorecard
    with ndbClient.context():
        #get scorecard by its key
        # scorecard = ScoreCard() #this is for context
        scorecardQuery = ScoreCard.query().filter(ScoreCard.scoreCardKey==scorecardkey)
        scorecard = scorecardQuery.fetch(1)[0] # fetches just 1 record,at instance 0  
        
        #get playerscore sheet
        logging.info("trying to update key:"+request.form.get("PlayerScoreKey"))
        playerScoreQuery = PlayerScore.query().filter(PlayerScore.scoreKey==request.form.get('PlayerScoreKey'))
        playerScore = playerScoreQuery.fetch(1)[0]
        
        playerScore.hole1 = int(request.form.get('hole1'))
        playerScore.hole2 = int(request.form.get('hole2'))
        playerScore.hole3 = int(request.form.get('hole3'))
        playerScore.hole4 = int(request.form.get('hole4'))
        playerScore.hole5 = int(request.form.get('hole5'))
        playerScore.hole6 = int(request.form.get('hole6'))
        playerScore.hole7 = int(request.form.get('hole7'))
        playerScore.hole8 = int(request.form.get('hole8'))
        playerScore.hole9 = int(request.form.get('hole9'))



        #update the score
        playerScore.put() 
        #now get players
        #now set up to display on scorecard
        
        #now we updated the records so refetch the playerlist
        playerList = []
        data ={}
        player=scorecard.player1.get()
        data['player_name'] = player.PlayerName
        data['handicap']= player.Handicap
        playerList.append(data)
        
        data ={}
        player=scorecard.player2.get()
        data['player_name'] = player.PlayerName
        data['handicap']= player.Handicap
        playerList.append(data)
        
        data ={}
        player=scorecard.player3.get()
        data['player_name'] = player.PlayerName
        data['handicap']= player.Handicap
        playerList.append(data)
        
        data ={}
        player=scorecard.player4.get()
        data['player_name'] = player.PlayerName
        data['handicap']= player.Handicap
        playerList.append(data)
        #requery for each playerScore
        playerScoreQuery = PlayerScore.query().filter(PlayerScore.Player==scorecard.player1)
        playerList[0]['playerScore'] = playerScoreQuery.fetch(1)[0]
        
        playerScoreQuery = PlayerScore.query().filter(PlayerScore.Player==scorecard.player2)
        playerList[1]['playerScore'] = playerScoreQuery.fetch(1)[0]
        
        playerScoreQuery = PlayerScore.query().filter(PlayerScore.Player==scorecard.player3)
        playerList[2]['playerScore'] = playerScoreQuery.fetch(1)[0]
        
        playerScoreQuery = PlayerScore.query().filter(PlayerScore.Player==scorecard.player4)
        playerList[3]['playerScore'] = playerScoreQuery.fetch(1)[0]
        
    '''
    scorecard = {
        # Initialize an empty scorecard for each player
        player: {f"hole_{i+1}": None for i in range(9)} for player in data
    }
    '''
    return render_template('scorecard.html', players=playerList, scorecard=scorecard)            

if __name__ == '__main__':
    app.run(debug=True)
