

$(document).ready(function(){
  let userNameTemp = sessionStorage.getItem('simpsons-trivia-username');
  
  if (userNameTemp){
    $('input[name="name"]').val(userNameTemp);
  } else {
    $('input[name="name"]').val('');
  }


  $('#newgame').on('submit', function(e){
    e.preventDefault();

    let id = $('#newgame').attr('data-id');
    let name = $('input[name="name"]').val();

    if (name){
      sessionStorage.setItem('simpsons-trivia-username', name);
    }

    let data = {
      id: id,
      name: name
    }

    $.ajax({
      url: '/newgame',
      data: data,
      type: 'POST',
      success: function(response) {
        window.location.href = '/trivia/' + id
      },
      error: function(error) {
        console.log(error);
        alert('Umm... Something went wrong')
      }
    });

    return false;
  });

  let answered = false;
  let answers = $('#answers');
  answers.find('figure').on('click', function(){
    let that = $(this);

    if (!answered){
      let data = {
        game_id: answers.attr('data-game'),
        question_id: answers.attr('data-question'),
        answer: parseInt(that.attr('data-index'))
      }

      function responded(response){
        if (response.completed){
          setTimeout(function(){
            window.location.href = '/leader/' + data.game_id;
          }, 800);
        } else {
          setTimeout(function(){
            location.reload();
          }, 800);
        }
      }
      $.ajax({
        url: '/answer',
        data: data,
        type: 'POST',
        dataType: "json",
        success: function(response) {
          if (response.status == 'CORRECT'){
            $('body').addClass('correct_answer');
            responded(response);
          } else if (response.status == 'INCORRECT'){
            $('body').addClass('incorrect_answer');
            responded(response);
          }
        },
        error: function(error) {
          console.log(error);
          alert('Umm... Something went wrong')
        }
      });
      
      answered = true;
    }

    
  })
})