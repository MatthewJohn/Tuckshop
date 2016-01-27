function purchaseItem(event)
{
    var item_name = event.target.getElementsByClassName('item_name')[0].innerHTML;
    var item_value = event.target.getElementsByClassName('sale_price_string')[0].value;

    BootstrapDialog.show({
        message: 'Are you sure you wish to purchase a ' + item_name + ' for ' + item_value + '?',
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