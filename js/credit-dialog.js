function purchaseItem(event)
{
    var item_id = event.target.getElementsByClassName('item_id')[0].value;
    var item_name = event.target.getElementsByClassName('item_name')[0].innerHTML;
    var item_value = event.target.getElementsByClassName('sale_price_string')[0].value;

    BootstrapDialog.show({
        title: 'Purchase ' + item_name,
        message: 'Are you sure you wish to purchase a ' + item_name + ' for ' + item_value + '?' +
                 '<br /><br />Purchase on behalf of a shared account? <input type="checkbox" name="use_shared_user" value="1" form="purchase-' + item_id + '" onchange="updateSharedAccount(event)">' +
                 '<br /><div id="item_purchase_shared_account" style="display: none">' +
                 'Account: <select name="shared_account" id="purchase_shared_account" form="purchase-' + item_id + '"></select><br />' +
                 '<input type="text" form="purchase-' + item_id + '" name="description" placeholder="Purchase Description..." required />' +
                 '</div>',
        buttons: [{
            label: 'Purchase',
            action: function(dialogRef) {
                event.target.submit();
                dialogRef.close()
            },
            cssClass: 'btn-warning'
        },
        {
            label: 'Cancel',
            action: function(dialogRef) {
                dialogRef.close();
            }
        }]
    });
    return false;
}

function updateSharedAccount(event)
{
  var select = document.getElementById("purchase_shared_account");
  if (event.target.checked == true)
  {
    document.getElementById('item_purchase_shared_account').style.display = 'inherit';
    shared_users.forEach(function(element, index, array){
      var option = document.createElement('option');
      option.text = element[1];
      option.value = element[0];
      select.add(option);
    });
  }
  else
  {
    var length = select.options.length;
    for (i = 0; i < length; i++) {
        select.options.remove(i);
    }
    document.getElementById('item_purchase_shared_account').style.display = 'none';
  }
}

function customPurchase(event)
{
    var description = event.target.getElementsByClassName('custom-amount-description')[0].value || "";
    var item_value = event.target.getElementsByClassName('custom-amount-input')[0].value;
    description_message = '';
    description_warning = '';
    if (description != '')
    {
        description_message = ', using description <code>' + description + '</code>';
    }
    else
    {
        description_warning = '<br /><b>You have not provided a description. It is highly recommended to use one!</b><br />';
    }
    message = 'Are you sure you wish to perform a custom payment of ' + item_value + 'p' + description_message + '?' + description_warning +
              '<br /><br /><b>Note:</b> It is generally best to purchase items, rather than performing a custom payment<br >' +
              '<b>Only perform a custom payment if it is absolutely necessary!</b>'

    BootstrapDialog.show({
        title: 'Custom Purchase/Donation',
        message: message,
        buttons: [{
            label: 'Purchase',
            action: function(dialogRef) {
                event.target.submit();
                dialogRef.close()
            },
            cssClass: 'btn-warning'
        },
        {
            label: 'Cancel',
            action: function(dialogRef) {
                dialogRef.close();
            }
        }]
    });
    return false;
}