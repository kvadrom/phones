  var $SCRIPT_ROOT = '';
  function delPhone(){
      $.getJSON($SCRIPT_ROOT + '/_delete_phone', {
        phone: $(this).attr('id'),
        entry: $('div.entry').attr('id')
      }, function(data) {
        getPhones();
      });
      return false;
  }
   function addPhone(){
      $.getJSON($SCRIPT_ROOT + '/_add_phone', {
        number: $('input[name="number"]').val(),
        desc: $('input[name="desc"]').val(),
        entry: $('div.entry').attr('id')
      }, function(data) {
        getPhones();
      });
      return false;
  }
  function editEntry(){
    var id = $('div.entry').attr('id');
    $.ajax({
       // формируем имя запрашиваемой посредством AJAX страницы
       url: $SCRIPT_ROOT + '/entry/edit/'+id,
       success: function(data){
            $('div.entry').empty().html(data);
            getPhones();
       }
    });
  }
  function showEntry(){
    var id = $('div.entry').attr('id');
    $.ajax({
       // формируем имя запрашиваемой посредством AJAX страницы
       url: $SCRIPT_ROOT + '/entry/show/'+id,
       success: function(data){
            $('div.entry').empty().html(data);
            getPhones();
       }
    });
  }
   function updateEntry(){
      $.getJSON($SCRIPT_ROOT + '/_update_entry', {
        title: $('input[name="title"]').val(),
        desc: $('textarea#desc').val(),
        entry: $('div.entry').attr('id')
      }, function(data) {
        showEntry();
      });
      return false;
  }

  function getPhones(){
    var id = $('div.entry').attr('id');
    $('div.phones').load($SCRIPT_ROOT + '/phones/'+id);
  }

function addComment(){
  $.ajax('/_add_comment',{
    parent: $(this).attr('id'),
    text: $('textarea#desc').val(),
    entry: $('div.entry').attr('id')
   }, function(data){
      $(data).insertAfter('a.add_comment');
  });
}

$(document).ready(function(){
            $('a.delete').live('click', delPhone);
            $('a.addphone').live('click',addPhone);
            $('a.edit').live('click',editEntry);
            $('a.update').live('click',updateEntry);
            $('a.add_comment').live('click', addComment);
    
});
