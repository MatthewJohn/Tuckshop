LOGGED_IN_USER = null;
RESET_TIMER = null;
RELOAD_PAGE = null;
DIALOGUE_REF = null;

function ran_col(class_name) { //function name
    var colours = ['#92F22A','#3D8EB9','#60646D', '#FEC606', '#9E58DC',
                   '#81E2E6', '#331B17', '#95A5A6', '#F7A3A2', '#FF7300']; //Set your colors here
    var items = document.getElementsByClassName(class_name);
    for (i = 0, len = items.length; i < len; i++) {
      items[i].style.background = colours[Math.floor(Math.random() * colours.length)];
    }

}

function show_users()
{
  $('#user-login').show();
  $('#item-select').hide();
  ran_col('user-object');
}

$(document).ready(function (){
  show_users();
  reset_timer();
});

function show_items() {
  $('#user-login').hide();
  $('#item-select').show();
}

function select_user(user_obj)
{
  username = $(user_obj).attr('data-uid');
  name = $(user_obj).attr('data-name');
  DIALOGUE_REF = BootstrapDialog.show({
      size: BootstrapDialog.SIZE_LARGE,
      title: '',
      animate: false,
      message: '<p class="login-dialog-text">Are you sure you wish to login as <b>' + name + ' (' + username + ')</b>?</p>',
      buttons: [{
          label: 'Yes',
          action: function(dialogRef) {
              LOGGED_IN_USER = username;
              show_items();
              dialogRef.close();
          },
          cssClass: 'btn-warning touch-button-large'
      },
      {
          label: 'No',
          action: function(dialogRef) {
              dialogRef.close();
          },
          cssClass: 'btn-info touch-button-large'
      }]
  });
  return false;
}

function select_item(item_obj)
{
  DIALOGUE_REF = BootstrapDialog.show({
      size: BootstrapDialog.SIZE_LARGE,
      title: 'Purchase item: ' + $(item_obj).attr('data-name'),
      message: '<img src="/item-image/' + $(item_obj).attr('data-item-id') + '" class="purchase-image" />' +
               '<p class="login-dialog-text">' + $(item_obj).attr('data-name') + '<br />' +
               'Price: ' + $(item_obj).attr('data-sale-price-string') + '<br />Quantity: 1</p>' +
               '<form method="post" id="purchase-item"><input type="hidden" name="username" value="' + LOGGED_IN_USER + '" />' +
               '<input type="hidden" name="item_id" value="' + $(item_obj).attr('data-item-id') + '" />' +
               '<input type="hidden" name="sale_price" value="' + $(item_obj).attr('data-sale-price') + '" /></form>',
      animate: false,
      buttons: [{
          label: 'Purchase',
          action: function(dialogRef) {
              $('#purchase-item').submit();
              dialogRef.close();
          },
          cssClass: 'btn-warning touch-button-large'
      },
      {
          label: 'Cancel',
          action: function(dialogRef) {
              dialogRef.close();
          },
          cssClass: 'btn-info touch-button-large'
      }]
  });
  return false;
}

function reset_page()
{
  RESET_TIMER = null;
  LOGGED_IN_USER = null;
  show_users();
  if (DIALOGUE_REF) {
    DIALOGUE_REF.close();
  }
}

function reload_page()
{
  location.reload();
}

function reset_timer(timer) {
  if (RESET_TIMER) {
    clearInterval(RESET_TIMER);
  }
  // Reset login after 30 seconds
  RESET_TIMER = setTimeout(reset_page, 30000);

  if (RELOAD_PAGE) {
    clearInterval(RELOAD_PAGE);
  }
  // Reload page every 30 minutes
  RELOAD_PAGE = setTimeout(reload_page, 1800000);
}
