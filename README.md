Todo
====

* Backend:
  * Split into seperate files
* Nigthly emails about lack of payment when buyer out of credit

### From Review:

* ad:
  * Add Float page:
    * Items: name, stock quantity, cost, sale price
    * Allow quantity adjust
    * Total float value
  * Add CSV export
  * Change method of paying inv. transactions
 * Confirmation message about adding stock
 * Admin page confirmations
 * Order payments by 'sold out', 
 * Stock being used in incorrect order
 * Fully pay one item, null transaction for next stock tranasaction
 * Desciprtion for custom amount pay
 * Change custom amount pay disabnle option
 * Add description to balance adjust
 * Change stock paying transaction (Twix x 10) to (Twix * 10)
 * Not fully payed -> Partially Paid
 * Fully Paid -> Fully Paid
 * Partial Payament -> (in installments)

 * Move stock transactions to new table
 * Add stock credit

## Future

* Setup RFID/scanner systems
* Use input device monitoring
* Setup on raspberry pi
* Allow export of purchases to CSV

##Done
* Find templating system:
  * Use one of the following: https://wiki.python.org/moin/Templating
* Setup user panel:
  * See balance
* Implement LDAP authentication
* Backend:
  * Split classes into seperate files
  * Complete inventory work
* Setup user panel:
  * Chose items to purchase/general items
* Setup Admin panel
  * Add items
  * View/Edit transaction history and rebuild credit cache
* Setup Admin panel
  * Add monies to user accounts
