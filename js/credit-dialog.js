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