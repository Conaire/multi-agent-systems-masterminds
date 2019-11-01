var DEBUG = false;
var baseUrl = "http://127.0.0.1:5000/";

ko.components.register('mastermind-game', {
  template: {
    element: 'mastermind-game-template'
  },
  viewModel: MastermindComponent
});

function MastermindComponent(params) {

    if(params.isComputer){
        window.computerMaster = this;

    }else{
        window.playerMaster = this;
    }

  var self = this,
    params = _.extend({
      colors: 6, // difference colors to use
      rows: 10,
      controlObservable: null, // an observable passed from the main viewmodes which will control starting/pausing/stopping the game
      win: 3,
      isComputer: false
    }, params || {}),
    //colors = ['red', 'blue', 'white', 'green', 'black', 'yellow'],
    colors = ['red', 'blue', 'green', 'yellow'],

      letter_to_color = {'r' : "red" ,'g' : "green",'b': "blue",'y': "yellow"},


    utils = {
      randomColor: function() {
        return colors[Math.floor(Math.random() * colors.length)];
      },
      populateWinningSequence: function() { // generate a new group of colors to be matched
        self.winningSequence(self.winRange.map(utils.randomColor));
      },

        populatePlayerSequence: function() { // generate a new group of colors to be matched
            if(!params.isComputer){
                ret = window.prompt("Please enter three colors from \n 'red',  'green', 'blue', 'yellow'. \n eg 'red blue blue'");
                //var ret = "red green blue";
                var colors = ret.split(" ");
                console.log(colors);
                self.playerSequence(colors)
            }
        },

      resetGame: function() {
        self.playing(false);
        self.revealing(false);
        self.selectedIndex(0);
        self.winningSequence.removeAll();
        self.historySequence.removeAll();
        self.playingSequence.removeAll();
        self.playerSequence.removeAll();
        self.pegSequence.removeAll();
        self.playerPegSequence.removeAll();
      },
      testForMatch: function(sequence) {
        var q = sequence.slice(), //self.winningSequence().slice(),
          rq = self.playingSequence(),
          testColor = function(color, i) {
            return color === q[i];
          },
          matches = rq.filter(testColor),
          misses = _.reject(rq, testColor),
          misplaced = [];
        matches.forEach(function(c, i) {
          q.splice(q.indexOf(c), 1);
        });
        misses.forEach(function(c) {
          var k = q.indexOf(c);
          if (k >= 0) {
            q.splice(k, 1);
            misplaced.push(c);
          }
        });

        return {
          correct: matches.length,
          misplaced: misplaced.length
        };

      }
    };

  _.extend(self, { // properties and methods available to the template
    DEBUG: ko.observable(DEBUG),
    revealing: ko.observable(false), // reveal the winning combo
    playing: ko.observable(false),
      isComputer: ko.observable(params.isComputer),
    selectedIndex: ko.observable(0),// the selected marble crater which will apply a clicked color
    rowRange: _.range(params.rows).reverse(),// [9,8,7,..,0]
    winRange: _.range(params.win),// [0,1,2,3]
    winningSequence: ko.observableArray(),
    playingSequence: ko.observableArray(),
    pegSequence: ko.observableArray(),
    playerPegSequence: ko.observableArray(),
    historySequence: ko.observableArray(),
      playerSequence: ko.observableArray(),
    colors: colors,



     startGame: function(){




        $.get(baseUrl + "get_comp_code", function(data){

            console.log(data);
            console.log(data.code);

            var winSequence = data.code.split("").map(function(x){  return letter_to_color[x] } );

            console.log(winSequence);


            $("#computer_know").html("");
            $("#computer_states").html("");
            $("#you_know").html("");
            $("#you_states").html("");


            self.doStartGame(null, null, winSequence, null)


        });

     },

    doStartGame: function(x, y, winSequence, pSequence) {
      utils.resetGame();


      if(pSequence){
          //console.dir(winSequence);
          console.dir(pSequence);
          //self.winningSequence(winSequence);
          self.playerSequence(pSequence);
      }else{
          //utils.populateWinningSequence();
          utils.populatePlayerSequence();
      }

        self.winningSequence(winSequence);



        if(!params.isComputer){

          self.playing(true);
      }



      if(!params.isComputer){
          computerMaster.doStartGame(null, null, self.playerSequence().slice(), self.winningSequence().slice())
      }


    },
    endGame: function( isWinner , isGameOver) {


      self.playing(false);
      self.revealing(true);
      if( isWinner ){

          if(params.isComputer){
              alert("Computer wins!");
             // playerMaster.endGame();

              playerMaster.endGame(false, true)

          }else{
              alert("You win!");
            //  computerMaster.endGame();

              computerMaster.endGame(false, true)

          }


      }else{

          if(!params.isComputer && !isGameOver){
              computerMaster.submitRow()
          }

      }






    },
    getPegClass: function(row, index) {
      var matches = self.pegSequence()[params.rows - row - 1];
      if (matches && matches.hasOwnProperty('correct')) {
        return index < matches.correct ? 'correct' : index < matches.correct + matches.misplaced ? 'misplaced' : '';
      }
    },

      getPlayerPegClass: function(row, index) {
          var matches = self.playerPegSequence()[params.rows - row - 1];
          if (matches && matches.hasOwnProperty('correct')) {
              return index < matches.correct ? 'correct' : index < matches.correct + matches.misplaced ? 'misplaced' : '';
          }
      },

    setColor: function(color) { // a colored marble was clicked
      var index = self.selectedIndex(),
        rq = self.playingSequence();
      rq[index] = color;
      self.playingSequence(rq);
     // if (_.reject(rq, _.isUndefined).length === params.win) { // full tray
     // } else {
      if( rq.length < params.win ){
        var i = rq.indexOf(undefined);
        i = i >= 0 ? i : rq.length;
        self.selectedIndex(i);
      }
    },

      submitRow: function(){




            var that = self;

            var code = self.playerSequence().slice().map(function(x){ return x[0]  }).join("")
            var guessCode = self.playingSequence().slice().map(function(x){ return x[0]  }).join("")


            var data = JSON.stringify({"data":{"user_guess_code": guessCode, "user_code": code}});

            $.post({url: baseUrl + "filter_invalid_states_and_guess",   contentType: "application/json",  data: data, success: function(d){

                var cgc = d.comp_guess_code;


                var computerGuessCode = cgc.split("").map(function(x){  return letter_to_color[x] } );


                $("#computer_know").html(d.comp_know);
                $("#computer_states").html(that.getStateNames(d.comp_states));
                $("#you_know").html(d.user_know);
                $("#you_states").html(that.getStateNames(d.user_states));


                that.doSubmitRow(computerGuessCode)


            }});


      },


      getStateNames: function(input){

          Object.filter = function( obj, predicate) {
              var result = {}, key;
              // ---------------^---- as noted by @CMS,
              //      always declare variables with the "var" keyword

              for (key in obj) {
                  if (obj.hasOwnProperty(key) && !predicate(obj[key])) {
                      result[key] = obj[key];
                  }
              }

              return result;
          };


          var states = Object.filter(input, function(x){ return x === 1 });




          return Object.keys(states).join(", ");

      },



    doSubmitRow: function(computerGuessCode) {


        if(params.isComputer){

            //self.playingSequence(["red", "red", "red"]);
            //self.playingSequence(self.winningSequence().slice());
            //alert("Computer loading");

            self.playingSequence(computerGuessCode);

        }

      var matches = utils.testForMatch(self.winningSequence());

      var playerMatches=   utils.testForMatch(self.playerSequence());

      self.historySequence.push(self.playingSequence.slice());
      self.pegSequence.push(matches);
      self.playerPegSequence.push(playerMatches);


      self.playingSequence.removeAll();
      //console.log('matches', matches);
      if (matches.correct === params.win || self.historySequence().length >= params.rows) {
        self.endGame(matches.correct === params.win);
      } else {
        self.selectedIndex(0);


        if(!params.isComputer){
            self.playing(false);
            computerMaster.doSubmitRow(computerGuessCode)

        }else{
            playerMaster.playing(true);
        }

      }





    }
  });
  //computed observables
  self.rowMaster = ko.pureComputed(function() {
    var pq = self.historySequence(),
      nil = function() {
        return null;
      };
    return self.rowRange.map(function(i) {
      var ret = {
        current: i === pq.length,
        colors: []
      };
      if (i < pq.length) {
        ret.colors = pq[i];
      } else if (pq.length === i) {
        ret.colors = self.winRange.map(function(k) {
          return self.playingSequence()[k] || null;
        });
      } else {
        ret.colors = self.winRange.map(nil);
      }
      return ret;
    });
  });
  self.fullPlayerTray = ko.pureComputed(function() {
    return self.playingSequence().length === params.win;
  });
}

function VM() {
  var self = this;
  self.mastermindControl = ko.observable('stop');
}

window.onload = function() {
  ko.applyBindings(new VM());
}




