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
        message = 'Are you sure that you wish to add \u00A3' + amount + ' to the account of ' + uid + '?<br/ >' +
                  'Alter Float: <input type="checkbox" name="affect_float" form="credit_change_' + uid + '"" checked /><br />' +
                  '<b>Note:</b> Check the \'Alter Float\' checkbox if physical money is entering the tuckshop.<br />' +
                  'For Example, if a user is giving money in order to credit their account.<br />' +
                  'De-check this box if no physical money is being transfered to/from the tuckshop, e.g. an alteration is being made the user\'s balance.';
        document.getElementById('action_' + uid).value = 'credit';
    }
    else
    {
        message = 'Are you sure that you wish to remove \u00A3' + amount + ' from the account of ' + uid + '?<br/ >' +
                  'Alter Float: <input type="checkbox" name="affect_float" form="credit_change_' + uid + '"" /><br />' +
                  '<b>Note:</b> Check the \'Alter Float\' checkbox if physical money is leaving the tuckshop.<br />' +
                  'For Example, if a user is being given money in order from their account.<br />' +
                  'De-check this box if no physical money is being transfered to/from the tuckshop, e.g. an alteration is being made the user\'s balance.';;
        document.getElementById('action_' + uid).value = 'debit';
    }

    if (document.getElementById('credit_change_description_' + uid).value == "")
    {
        message += "<br /><b>You have not supplied a description</b><br />" +
                   "It strongly recommended to use a description when making credit changes!";
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