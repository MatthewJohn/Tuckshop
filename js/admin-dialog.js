function confirmPayUser(uid, amount)
{
    BootstrapDialog.show({
        message: 'Are you sure you wish to pay ' + uid + ' \u00A3' + amount + ' for stock',
        buttons: [{
            label: 'Pay',
            action: function(dialogRef) {
                document.getElementById('pay_' + uid).submit();
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
}
function handlePayEnter(event, uid, amount)
{
    if (event.keyCode == 13)
    {
        confirmPayUser(uid, amount);
        return false;
    }
    return event.keyCode != 13;
}

function confirmCreditChange(uid, amount, description, credit)
{
    if (credit)
    {
        message = 'Are you sure that you wish to add ' + amount + 'p to the account of ' + uid;
        document.getElementById('action_' + uid).value = 'credit';
    }
    else
    {
        message = 'Are you sure that you wish to remove ' + amount + 'p from the account of ' + uid;
        document.getElementById('action_' + uid).value = 'debit';
    }
    BootstrapDialog.show({
        message: message,
        buttons: [{
            label: 'Accept',
            action: function(dialogRef) {
                document.getElementById('credit_change_' + uid).submit();
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
}